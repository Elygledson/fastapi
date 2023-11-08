
from fastapi import APIRouter
from models.request import Request
from fastapi.responses import JSONResponse
from models.request import  QuestionType, Request
from question_generators.mcq import MultipleChoiceQuestion

router = APIRouter()

@router.post('/text/questions')
def generate_questions_from_text(request: Request):
      rules = request.rules
      num = request.num
      question_type = request.type
      return handle(question_type, rules, num)

def handle(question_type, rules, num):
    generated_questions = []
    try:
        if question_type == QuestionType.multiple_choice_question:
            mcq_questions = MultipleChoiceQuestion()
            generated_questions = mcq_questions.generate(rules)
        return JSONResponse(content={'questions': generated_questions['questions'], "message": "Questões geradas com sucesso!"})
    except Exception as e:
        print(e)
        return JSONResponse(content={'message': 'Erro ao gerar as questões.'}, status_code=500)
