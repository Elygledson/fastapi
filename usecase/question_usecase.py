from fastapi import HTTPException
from fastapi.responses import JSONResponse
from langchain.chat_models import ChatOpenAI
from config.environment import config
from models.request import QuestionFactory,QuestionFactorySenaiPlay
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
import os
import logging
from pytube import YouTube
import whisper

import re
import openai
import json

openai.api_key = config.get('OPENAI_API_KEY')
logging.basicConfig(level=logging.INFO)
modelT = whisper.load_model("base")


class QuestionUseCase:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=1.0, model_name='gpt-3.5-turbo', max_tokens=512)

    def generate_mcq(self, question: QuestionFactory):
        try:
            formatted_question  = f"""
            Forneça um contexto antes de gerar a questão
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
            "description": "Gere questões de múltipla escolha com base nas regras fornecidas, além disso, procure ser criativo nos tópicos acerca das questões.",
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
                                        "type": "object",
                                        "properties": {
                                            "description": {
                                                "type": "string",
                                                "description": "Descrição da opção de resposta."
                                            },
                                            "justify": {
                                                "type": "string",
                                                "description": "Justificativa para a opção de resposta."
                                            },
                                            "is_correct": {
                                                "type": "boolean",
                                                "description": "Indica se a opção é a correta."
                                            }
                                        },
                                        "required": ["description", "justify", "is_correct"]
                                    }
                                }
                            },
                            "required": ["context", "question", "options"]
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
            return questions['questions']
        except Exception:
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
                                            "description": "Crie um contexto descrevendo uma situação problema para a questão. É proibido o contexto em que: faça propaganda para evidenciar uma marca,desrespeite proibições já previstas na legislação brasileira vigente, aborda conteúdos polêmicos, utilize nomes fictícios jocosos ou identifique pessoas em geral e contenha estereótipos e preconceitos de condição social, regional, étnico-racial, de gênero, de orientação sexual, de idade ou de linguagem, assim como de qualquer outra forma de discriminação ou de violação de direitos. Não utilize pronomes pessoas como eu/tu/ele/nós/vós/eles/elas ou 'Você' na criação do contexto."
                                        },
                                        "question": {
                                            "type": "string",
                                            "description": "Uma pergunta extraída das regras de entrada."
                                        },
                                        "options": {
                                            "type": "array",
                                            "items": {
                                                "type": "string",
                                                "description": "As alternativas são possibilidades de resposta para a situação-problema apresentada, alternativas do tipo Verdadeiro ou Falso."
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
                                                "description": "Uma curta justificativa para as duas alternativas da questão."
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
            return questions['questions']
        except Exception:
            return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
        
    def generate(self, question: QuestionFactory):
        formatted_question  = f"""
        Nível de dificuldade: {question.level}, 
        Capacidade: {question.capacity}, 
        Conhecimento: {question.knowledge}, 
        Número de questões: {question.question_num}, 
        Contexto: {question.context}, 
        Número de alternativas: {question.num_options}."""
        if question.question_num > 10:
           raise HTTPException(status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
        response_schemas = [
        ResponseSchema(name="context", type='string', description="""Crie um contexto descrevendo uma situação problema para a questão. É proibido o contexto em que: faça propaganda para evidenciar uma marca,desrespeite proibições já previstas na legislação brasileira vigente, aborda conteúdos polêmicos, utilize nomes fictícios jocosos ou identifique pessoas em geral e contenha estereótipos e preconceitos de condição social, regional, étnico-racial, de gênero, de orientação sexual, de idade ou de linguagem, assim como de qualquer outra forma de discriminação ou de violação de direitos. Não utilize pronomes pessoas como eu/tu/ele/nós/vós/eles/elas ou 'Você' na criação do contexto.
        """),
        ResponseSchema(name="question", type='string', description="""Gere uma pergunta de múltipla escolha com base nas regras definidas, 
                É ele quem enuncia e explica o que se espera que o estudante faça. O comando deverá ser obrigatoriamente relacionado ao contexto apresentado. Deve-se apresentar na forma de uma frase que determina o que o estudante deve procurar entre os recursos cognitivos mobilizados para solucionar o problema apresentado no contexto. O comando(que é a pergunta norteadora) deve do item de ser escrito na forma de uma pergunta, em que o respondente resolve o problema e seleciona entre as alternativas a que responde corretamente. ser formulado de modo claro, objetivo e direto, sem apresentar informações adicionais ou complementares. O comando estar associado à capacidade avaliada, estar obrigatoriamente relacionado ao contexto apresentado anteriomente e ser suficiente para que o aluno somente com o contexto e o comando já visualize a resposta correta. 
                Vale ressaltar que é proibido no comando expressões:
                “É correto afirmar que”
                “Assinale a alternativa correta”,
                “Qual das alternativas...”
                “A alternativa que indica...”, pois dificulta a criação de quatro situações plausíveis nas alternativas; 
                A utilização de termos como: sempre, nunca, todo, totalmente, absolutamente, completamente, somente, ou outras palavras semelhantes; e a utilização de sentença negativa, tais como, não, incorreto, errado, pois dificulta a compreensão, induzindo o aluno ao erro pela falta de entendimento.
                """),
        ResponseSchema(name="options", type='array', description="As alternativas são possibilidades de resposta para a situação-problema apresentada, sendo uma absolutamente correta, o gabarito, e as demais, os distratores plausíveis. A plausibilidade implica que essas respostas, embora não sejam corretas, são razoáveis ou admitidas do ponto de vista do aluno que não adquiriu, ainda, o domínio do conhecimento abordado. Idealmente, o distrator(Justificativa da resposta errada) deve representar o processo de construção da aprendizagem ainda não consolidado. Essa alternativas devem se escolhas possíveis para a questão de múltipla escolha."),
        ResponseSchema(name="answer", type='string', description="opção correta para a questão de múltipla escolha."),
        ResponseSchema(name="justifications", type='array', description=" Todas as alternativas devem ser justificadas(Distratores), mesmo a correta(Promotor), sendo que, geralmente, a justificativa está associada ao processo de desenvolvimento da capacidade. ")]
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas)
        format_instructions = output_parser.get_format_instructions()
        prompt = ChatPromptTemplate(messages=[HumanMessagePromptTemplate.from_template("""Dado uma texto, gere questões de múltipla escolha a partir dele junto com a resposta correta.\n{format_instructions}\n{user_prompt}""")],
                                    input_variables=["user_prompt"],
                                    partial_variables={"format_instructions": format_instructions})
        user_query = prompt.format_prompt(user_prompt=formatted_question)
        user_query_output = self.llm(user_query.to_messages())
        json_string = re.search(r'```json\n(.*?)```',user_query_output.content, re.DOTALL).group(1)
        return json.loads(f'[{json_string}]')

class SenaiPlay:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0.0, model_name='gpt-3.5-turbo', max_tokens=512)

    def get_text(self, question: QuestionFactorySenaiPlay):
        # Check if URL is provided
        if question.url != '':
            output_text_transcribe = ''

        # Download video and convert to audio
        yt = YouTube(question.url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=".")

        # Get file size of downloaded audio
        file_stats = os.stat(out_file)
        logging.info(f'Size of audio file in Bytes: {file_stats.st_size}')

        # Check if the file size is within limit for transcription
        if file_stats.st_size <= 30000000:
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            audio_file = new_file

            # Transcribe audio using the model
            result = modelT.transcribe(audio_file)
            os.remove(audio_file)
            return { 'transcription': result['text'].strip() }
            
        else:
            # Error if the video is too long for transcription
            error_message = 'Videos for transcription on this space are limited to about 1.5 hours. ' \
                            'Sorry about this limit but some joker thought they could stop this tool ' \
                            'from working by transcribing many extremely long videos.'
            logging.error(error_message)

    def generate_mcq_sp(self, question: QuestionFactorySenaiPlay):
        try:
            transcription = self.get_text(question)

            formatted_question = f"""
            Número de questões: {question.question_num}, 
            Número de alternativas: {question.num_options}."""

            if question.question_num > 10:
                raise HTTPException(status_code=400, detail="O número de questões deve ser menor ou igual a 10.")
            
            mcq_function = [
                {
                    "name": "create_mcq",
                    "description": f"Gere questões de múltipla escolha com base nas regras fornecidas e com base na transcrição.",
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
                messages=[
                    {"role": "user", "content": formatted_question},
                    {"role": "user", "content": transcription['transcription']}
                ],
                functions=mcq_function,
                function_call={"name": "create_mcq"},
            )
            questions = json.loads(
                response['choices'][0]['message']['function_call']['arguments']
            )
            return questions['questions']
        except Exception:
            return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
