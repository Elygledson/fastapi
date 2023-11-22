from fastapi import HTTPException
from fastapi.responses import JSONResponse
from langchain.chat_models import ChatOpenAI
from config.environment import config
from models.request import QuestionFactory
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate

import re
import openai
import json

openai.api_key = config.get('OPENAI_API_KEY')


class QuestionUseCase:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', max_tokens=512)

    def generate_mcq(self, question: QuestionFactory):
        try:
            formatted_question  = f"""
            Não gere alternativas do tipo "Nenhuma das alternativas anteriores", "Todas as alternativas anteriores" ou alternativas sarcásticas.
            Na questão é proibido usar palavras como "mais adequado" "mais acertiva"
            Nível de dificuldade: {question.level}, 
            Capacidade: {question.capacity}, 
            Conhecimento: {question.knowledge}, 
            Número de questões: {question.question_num}, 
            Contexto: {question.context}, 
            Número de alternativas: {question.num_options}."""
            if question.question_num > 10:
                raise HTTPException(status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
            mcq_function = [
                {
                    "name": "create_mcq",
                    "description": f"Gere questões de múltipla escolha com base nas regras fornecidas",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "context": {
                                            "type": "string",
                                            "description": "Um contexto antes de gerar a questão"
                                        },
                                        "question": {
                                            "type": "string",
                                            "description": "Uma pergunta de múltipla escolha extraída das regras de entrada."
                                        },
                                        "options": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "Opção do candidato para a questão de múltipla escolha extraída."
                                            }
                                        },
                                        "answer": {
                                            "type": "string",
                                            "description": "Opção correta para a questão de múltipla escolha."
                                        },
                                        "justifications": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "Uma curta justificativa para cada alternativa da questão de múltipla escolha ."
                                                }
                                        },
                                    }
                                }
                            }
                        },
                        "required": ["questions"]
                    }
                }
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": formatted_question }],
                functions=mcq_function,
                function_call={"name": "create_mcq"},
            )
            questions = json.loads(
                response['choices'][0]['message']['function_call']['arguments'])
            return JSONResponse(content={'questions': questions['questions'], "message": "Questões geradas com sucesso!"})
        except Exception as e:
            print(e)
            return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)

    def generate_boolquest(self, question: QuestionFactory):
        try:
            formatted_question  = f"""
            Forneça um contexto antes de gerar a questão
            Na questão é proibido usar palavras como "mais adequado" "mais acertiva"
            Nível de dificuldade: {question.level}, 
            Capacidade: {question.capacity}, 
            Conhecimento: {question.knowledge}, 
            Número de questões: {question.question_num}, 
            Contexto: {question.context}"""
            if question.question_num > 10:
                raise HTTPException(status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
            bool_function = [
                {
                    "name": "create_boolquest",
                    "description": "Gere questões verdadeira ou falso escolha com base nas regras dadas com duas opções de candidato, levando em consideração taxonomia revisada. Uma opção está correta. Indique a opção correta para cada questão.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "questions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                          "context": {
                                            "type": "string",
                                            "description": "Um contexto antes de gerar a questão"
                                        },
                                        "question": {
                                            "type": "string",
                                            "description": "Uma pergunta extraída das regras de entrada."
                                        },
                                        "options": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "Opção Verdadeiro ou Falso para a questão booleana extraída."
                                            }
                                        },
                                        "answer": {
                                            "type": "string",
                                            "description": "Opção correta para a questão de Verdadeiro ou Falso."
                                        },
                                        "justifications": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "Uma curta justificativa para cada alternativa da questão de múltipla escolha ."
                                                }
                                        },
                                    }
                                }
                            }
                        },
                        "required": ["questions"]
                    }
                }
            ]

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": formatted_question}],
                functions=bool_function,
                function_call={"name": "create_boolquest"},
            )
            questions = json.loads(
                response['choices'][0]['message']['function_call']['arguments'])
            return JSONResponse(content={'questions': questions['questions'], "message": "Questões geradas com sucesso!"})
        except Exception as e:
            print(e)
            return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
        
    def generate(self, question: QuestionFactory):
        formatted_question  = f"""
        Não deve ser gerado alternativas do tipo "Nenhuma das alternativas anteriores", "Todas as alternativas anteriores" ou alternativas sarcásticas.
        Na questão é proibido usar palavras como "mais adequado" "mais acertiva"
        Nível de dificuldade: {question.level}, 
        Capacidade: {question.capacity}, 
        Conhecimento: {question.knowledge}, 
        Número de questões: {question.question_num}, 
        Contexto: {question.context}, 
        Número de alternativas: {question.num_options}."""
        if question.question_num > 10:
           raise HTTPException(status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
        response_schemas = [
            ResponseSchema(
                name="context", type='string', description="""Um contexto para a questão."""),
            ResponseSchema(
                name="question", type='string', description="""uma pergunta de múltipla escolha gerada a partir do trecho de texto de entrada."""),
            ResponseSchema(
                name="options", type='array', description="escolhas possíveis para a questão de múltipla escolha. Três opções estão incorretas e uma está correta."),
            ResponseSchema(
                name="answer", type='string', description="opção correta para a questão de múltipla escolha."),
            ResponseSchema(
                name="justifications", type='array', description="uma pequena justificativa para cada alternativa.")
        ]
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = ChatPromptTemplate(messages=[HumanMessagePromptTemplate.from_template("""Dado uma texto, gere questões de múltipla escolha a partir dele junto com a resposta correta.
                                                                                       \n{format_instructions}\n{user_prompt}""")],
                                    input_variables=["user_prompt"],
                                    partial_variables={"format_instructions": format_instructions})
        user_query = prompt.format_prompt(user_prompt=formatted_question)
        user_query_output = self.llm(user_query.to_messages())
        json_string = re.search(r'```json\n(.*?)```',user_query_output.content, re.DOTALL).group(1)
        return json.loads(f'[{json_string}]')
