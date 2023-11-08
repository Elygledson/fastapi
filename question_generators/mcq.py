from langchain.chat_models import ChatOpenAI

import openai
import json

from config.environment import config
from models.request import Rules

openai.api_key = config.get('OPENAI_API_KEY')

class MultipleChoiceQuestion:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.0, model_name='gpt-3.5-turbo')
        
    def generate(self, rules: Rules):
        rules = f'Dificuldade: {rules.difficulty}, Capacidade: {rules.capacity}, Padrão de desempenho: {rules.performance_standard}, Conhecimento: {rules.knowledge}.'
        mcq_function = [
            {
                "name": "create_mcq",
                "description": f"Gere uma questão de múltipla escolha com base nas regras dadas com quatro opções de candidato. Três opções estão incorretas e uma está correta. Indique a opção correta para cada questão.",
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
            messages=[{"role": "user", "content": rules}],
            functions=mcq_function,
            function_call={"name": "create_mcq"},
        )
        return json.loads(response['choices'][0]['message']['function_call']['arguments'])
