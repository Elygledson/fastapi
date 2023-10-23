import os
import re
import json

from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

os.environ["OPENAI_API_KEY"] = "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"


class MultipleChoiceQuestion:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.0, model_name='gpt-3.5-turbo', max_tokens=1000)

    def generate(self, text, num):
        response_schemas = [
            ResponseSchema(
                name="question", description="""A multiple choice question generated from input text snippet."""),
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
        json_string = re.search(r'```json\n(.*?)```',
                                user_query_output.content, re.DOTALL).group(1)
        return json.loads(f'[{json_string}]')
