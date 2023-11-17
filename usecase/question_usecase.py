from fastapi.responses import JSONResponse
from langchain.chat_models import ChatOpenAI
from config.environment import config
from models.request import QuestionFactory

import openai
import json


openai.api_key = config.get('OPENAI_API_KEY')


class QuestionUseCase:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo')

    def generate_mcq(self, question: QuestionFactory):
        try:
            formatted_question  = f'Dificuldade: {question.difficulty}, Capacidade: {question.capacity}, Padrão de desempenho: {question.performance_standard}, Conhecimento: {question.knowledge}, NúmeroDeQuestões: {question.question_num}, Contexto: {question.context}, NumeroDeAlternativas: {question.alternatives_num}.'
            mcq_function = [
                {
                    "name": "create_mcq",
                    "description": f"Gere questões de múltipla escolha com base nas regras dadas com {question.alternatives_num} opções de candidato, levando em consideração taxonomia revisada. Dentre as {question.alternatives_num} opções, apenas uma está correta. Indique a opção correta para cada questão.",
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
                                        }
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
            question = f'Dificuldade: {question.difficulty}, Capacidade: {question.capacity}, Padrão de desempenho: {question.performance_standard}, Conhecimento: {question.knowledge}, NúmeroDeQuestões: {question.question_num},Contexto: {question.context}.'
            quest_function = [
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
                                        }
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
                messages=[{"role": "user", "content": question}],
                functions=quest_function,
                function_call={"name": "create_boolquest"},
            )
            questions = json.loads(
                response['choices'][0]['message']['function_call']['arguments'])
            return JSONResponse(content={'questions': questions['questions'], "message": "Questões geradas com sucesso!"})
        except Exception:
            return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
