
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from requests import HTTPError
from models.question import Evaluation, QuestionFactory, QuestionType
from question_generators.question import QuestionUseCase
from repositories.question_repository import QuestionRepository
import logging


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

question = APIRouter()


@question.post('/questions')
def generate_question(question: QuestionFactory,  question_usecase: QuestionUseCase = Depends()):
    if question.type == QuestionType.boolean_question:
        return question_usecase.generate_boolquest(question)
    else:
        return question_usecase.generate_mcq(question)


@question.post("/evaluations")
async def create_evaluation(evaluation: Evaluation,  question_repository: QuestionRepository = Depends()):
    try:
        evaluation_id = await question_repository.create_evaluation(evaluation)
        return {"evaluation_id": str(evaluation_id), "message": "Avaliação salva com sucesso!"}
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=500, detail="Falha ao salvar avaliação.")


@question.get("/evaluations")
async def get_evaluations(question_repository: QuestionRepository = Depends()):
    try:
        evaluations = await question_repository.list_evaluations({})
        return evaluations
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=500, detail="Falha ao salvar avaliação.")


@question.get("/evaluations/{evaluation_id}")
async def get_evaluations(evaluation_id: str, question_repository: QuestionRepository = Depends()):
    try:
        evaluation = await question_repository.list_one_evaluation({"_id": ObjectId(evaluation_id)})
        if evaluation == None:
           raise HTTPException(
                status_code=404, detail="Avaliação não encontrada.")
        return evaluation
    except HTTPException as httpException:
            raise httpException
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=500, detail="Falha ao obter avaliação.")


@question.delete("/evaluations/{evaluation_id}")
async def delete_evaluation(evaluation_id: str, question_repository: QuestionRepository = Depends()):
    try:
        await question_repository.delete(evaluation_id)
        return {'message': 'Avaliação excluída com sucesso.'}
    except Exception as e:
        logger.info(e)
        raise HTTPException(
            status_code=500, detail="Falha ao remover avaliação.")
