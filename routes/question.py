
from fastapi import APIRouter
from models.request import Request
from fastapi.responses import JSONResponse
from models.request import  QuestionType, Request
from question_generators.mcq import MultipleChoiceQuestion
from question_generators.speech_to_text import SpeechToText

router = APIRouter()


# @router.post('/text/questions')
# def generate_from_text(request: Request):



# @router.post('/transcription/questions')
# def generate_questions_from_url(request: Request):
#     url = request.content
#     num = request.num
#     question_type = request.type
#     transcription = SpeechToText.get_transcription_from_youtube(url)
#     return handle(question_type, transcription, num)


@router.post('/text/questions')
def generate_questions_from_text(request: Request):
      content = request.content
      num = request.num
      question_type = request.type
      return handle(question_type, content, num)

def handle(question_type, content, num):
    generated_questions = []
    try:
        if question_type == QuestionType.multiple_choice_question:
            mcq_questions = MultipleChoiceQuestion()
            print(num)
            generated_questions = mcq_questions.generate_using_openai(content, num)
        return JSONResponse(content={'questions': generated_questions['questions'], "message": "Questões geradas com sucesso!"})
    except:
        return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
