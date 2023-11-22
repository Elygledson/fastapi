
from fastapi import APIRouter, Depends
from models.request import Question, QuestionFactory, QuestionType
from usecase.question_usecase import QuestionUseCase
from routers.auth import verify_jwt_token

question = APIRouter()

@question.post('/text/questions', dependencies=[Depends(verify_jwt_token)])
def generate_question(question: QuestionFactory,  question_usecase: QuestionUseCase = Depends()):
    if question.type == QuestionType.boolean_question:
        return question_usecase.generate_boolquest(question)
    else:
        return question_usecase.generate_mcq(question)
    
@question.post('/transcription/questions', dependencies=[Depends(verify_jwt_token)])
def generate(question: Question, question_usecase: QuestionUseCase = Depends()):
    return question_usecase.generate(question.content, question.num)