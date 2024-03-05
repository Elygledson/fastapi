from requests import HTTPError
from fastapi import  HTTPException
from config.environment import config
from fastapi.responses import JSONResponse
from models.question import QuestionFactory
from langchain.chat_models import ChatOpenAI

import json
import openai
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


openai.api_key = config.get('OPENAI_API_KEY')

class QuestionUseCase:
    async  def generate_mcq(self, question: QuestionFactory, max_retries=3):
        for _ in range(max_retries):
            try:
                system_instructions = f"""
                Você é um gerador de questões de múltipla escolha, seu objetivo é gerar questões de múltipla escolha com base no contexto fornecido:
                Questão:
                Questão que será gerada
                Respostas:
                descrição: descrição da questão gerada
                justificativa: (Correto/Incorreto) justificativa da questão
                resposta: descrição da questão gerada(alternativa correta)
                """
                instructions = f"""
                Context: {question.content},
                Nível de dificuldade: {question.level.value}, 
                Número de questões: {question.question_num}, 
                Número de alternativas: {question.num_options}."""
                print(question.level.value)
                if question.question_num > 10:
                    raise HTTPException(
                        status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
                mcq_function = [
                    {
                        "name": "create_mcq",
                        "description": "Gere questões de múltipla escolha com base nas regras fornecidas, além disso, procure ser criativo na geração das questões.",
                        "parameters": {
                                "type": "object",
                                "properties": {
                                    "questions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "question": {
                                                    "type": "string",
                                                    "description": "Uma pergunta de múltipla escolha com base no contexto fornecido."
                                                },
                                                "options": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "description": {
                                                                "type": "string",
                                                                "description": "As alternativas são possibilidades de resposta para a situação-problema apresentada, sendo uma absolutamente correta, o gabarito, e as demais, os distratores plausíveis. "
                                                            },
                                                            "justify": {
                                                                "type": "string",
                                                                "description": "Justificativa para a opção de resposta."
                                                            },
                                                        },
                                                        "required": ["description", "justify"]
                                                    }
                                                },
                                                "answer": {
                                                    "type": "string",
                                                    "description": "Opção correta para a questão de múltipla escolha."
                                                },
                                            },
                                            "required": ["question", "options", "answer"]
                                        }
                                    }
                                },
                            "required": ["questions"]
                        }
                    }
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_instructions},
                              {"role": "user", "content": instructions}],
                    functions=mcq_function,
                    function_call={"name": "create_mcq"},
                )
                questions = json.loads(
                    response['choices'][0]['message']['function_call']['arguments'])
                return questions['questions']
            except HTTPError as http_err:
                logger.info(http_err)
                raise HTTPException(
                    status_code=500, detail='Erro ao gerar as questões.')
            except Exception as e:
                logger.info(e)
                continue
        return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)

    def generate_boolquest(self, question: QuestionFactory, max_retries=3):
        for _ in range(max_retries):
            try:
                system_instructions = f"""
                Você é um gerador de verdadeiro ou falso, seu objetivo é gerar questões de verdadeiro ou falso com base nas regras fornecidas, além disso, procure ser criativo nos tópicos acerca das questões.
                Exemplo de questão de verdadeiro ou falso:
                Questão:
                Questão que será gerada
                Respostas:
                descrição: (Verdadeiro/Falso)
                justificativa: justificativa da questão
                resposta: descrição da questão gerada(alternativa correta)
                """
                instructions = f"""
                Context: {question.content},
                Nível de dificuldade: {question.level}, 
                Número de questões: {question.question_num}, 
                Número de alternativas: {question.num_options}."""
                if question.question_num > 10:
                    raise HTTPException(
                        status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
                bool_function = [
                    {
                        "name": "create_boolquest",
                        "description": "Gere questões verdadeira ou falso escolha com base nas regras dadas com duas opções de candidato.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "questions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "question": {
                                                "type": "string",
                                                "description": "Uma pergunta verdadeira ou falso com base no contexto fornecido."
                                            },
                                            "options": {
                                                "type": "array",
                                                "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "description": {
                                                                "type": "string",
                                                                "description": "As alternativas são possibilidades de resposta para a situação-problema apresentada, sendo uma absolutamente correta, o gabarito, e as demais, os distratores plausíveis. "
                                                            },
                                                            "justify": {
                                                                "type": "string",
                                                                "description": "Justificativa para a opção de resposta."
                                                            },
                                                        },
                                                    "required": ["description", "justify"]
                                                }
                                            },
                                            "answer": {
                                                "type": "string",
                                                "description": "Opção correta para a questão de Verdadeiro ou Falso."
                                            },
                                        },
                                        "required": ["question", "options", "answer"]
                                    }
                                }
                            },
                            "required": ["questions"]
                        }
                    }
                ]

                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_instructions},
                              {"role": "user", "content": instructions}],
                    functions=bool_function,
                    function_call={"name": "create_boolquest"},
                )
                questions = json.loads(
                    response['choices'][0]['message']['function_call']['arguments'])
                return questions['questions']
            except HTTPError as http_err:
                logger.info(http_err)
                raise HTTPException(
                    status_code=500, detail='Erro ao gerar as questões.')
            except Exception as e:
                logger.info(e)
                continue
        return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
