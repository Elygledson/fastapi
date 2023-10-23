
from models.request import Question, QuestionType, Request
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from models.request import Request
from question_generators.mcq import MultipleChoiceQuestion
from question_generators.speech_to_text import SpeechToText

router = APIRouter()


@router.post('/text/questions')
def generate(request: Request):
    text = request.content
    num = request.num
    question_type = request.type
    return handle(question_type, text, num)


@router.post('/transcription/questions')
def generate_questions_from_url(request: Request):
    url = request.content
    num = request.num
    question_type = request.type
    transcription = SpeechToText.get_transcription_from_youtube(url)
    return handle(question_type, transcription, num)


def handle(question_type, text, num):
    generated_questions = []
    try:
        if question_type == QuestionType.multiple_choice_question:
            mcq_questions = MultipleChoiceQuestion()
            generated_questions = mcq_questions.generate(
                text, num)
            generated_questions = [{ 'question': question['question'], 'options': question['options'].split('\n'), 'answer': question['answer'] } for question in generated_questions]
        return JSONResponse(content={'questions': generated_questions, "message": "Questões geradas com sucesso!"})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
