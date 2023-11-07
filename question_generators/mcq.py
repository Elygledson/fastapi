import json

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

import openai
import json

from config.environment import config

openai.api_key = config.get('OPENAI_API_KEY')

class MultipleChoiceQuestion:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.0, model_name='gpt-3.5-turbo', max_tokens=1000)

    def generate(self, text, num):
        response_schemas = [
            ResponseSchema(
                name="description", description="""A multiple choice question generated from input text snippet."""),
            ResponseSchema(
                name="options", description="Possible choices for the multiple choice question."),
            ResponseSchema(
                name="answer", description="Correct answer for the question.")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = ChatPromptTemplate(messages=[HumanMessagePromptTemplate.from_template("""Given a text input, generate {limit} multiple choice questions
                    from it along with the correct answer.
                    \n{format_instructions}\n{user_prompt}""")],
                                    input_variables=["user_prompt", "limit"],
                                    partial_variables={"format_instructions": format_instructions})
        user_query = prompt.format_prompt(user_prompt=text, limit=num)
        user_query_output = self.llm(user_query.to_messages())
        print(type(user_query_output.content), )
        content = user_query_output.content.replace('```json', '')
        content = content.replace('}','},')
        content = content.replace(',\n```', '')
        return json.loads(f'[{content}]')
    
    def generate_using_openai(self, content, limit):
        mcq_function = [
        {
            "name": "create_mcq",
            "description": f"Generate {limit} multiple choice questions from the input text with four candidate options. Three options are incorrect and one is correct. Indicate the correct option after each question.",
            "parameters": {
                "type": "object",
                "properties": {
                    "questions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question":{"type": "string", 
                                            "description": "A multiple choice question extracted from the input text."},
                                 
                                "options":{"type": "array",
                                           "items":{"type":"string",
                                                    "description": "Candidate option for the extracted multiple choice question."} 
                                            },
                                 
                                "answer":{"type": "string", 
                                          "description": "Correct option for the multiple choice question."}
                            }                            
                          }
                        }
                    }
                },
                "required": ["questions"]
            }
        ]
        response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": content}],
            functions=mcq_function,
            function_call={"name": "create_mcq"},
        )
        return json.loads(response['choices'][0]['message']['function_call']['arguments'])
