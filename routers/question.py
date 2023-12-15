
from fastapi import APIRouter, Depends
from models.request import QuestionFactorySenaiPlay, QuestionFactory, QuestionType
from usecase.question_usecase import QuestionUseCase,SenaiPlay

question = APIRouter()

@question.post('/text/questions')
def generate_question(question: QuestionFactory,  question_usecase: QuestionUseCase = Depends()):
    if question.type == QuestionType.boolean_question:
        return question_usecase.generate_boolquest(question)
    else:
        return question_usecase.generate_mcq(question)
    
@question.post('/transcription/questions')
def generate(question: QuestionFactorySenaiPlay, question_usecase: SenaiPlay = Depends()):
    return question_usecase.generate_mcq_sp(question)

@question.post('/transcription')
def get_text(question: QuestionFactorySenaiPlay, question_usecase: SenaiPlay = Depends()):
    return question_usecase.get_text(question)
