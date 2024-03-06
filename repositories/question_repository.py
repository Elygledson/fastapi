from typing import Union
from fastapi import Depends
from pydantic import BaseModel
import logging

from models.question import Evaluation, Options, Question

from .database import Database, BaseRepository

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class QuestionRepository(BaseRepository):
    def __init__(self, db: Database = Depends()):
        super().__init__(db)

    @property
    def _collection(self):
        return 'questions'

    def format_evaluations_results(self, results):
        evaluations = []
        for result in results:
            questions = [
                Question(
                    context=q['context'],
                    question=q["question"],
                    options=[Options(**opt) for opt in q["options"]],
                    answer=q["answer"]
                )
                for q in result["questions"]
            ]
            evaluation = Evaluation(
                questions=questions,
                id=str(result["_id"]),
                date=result["date"],
                school=result["school"],
                course=result["course"],
                title=result["title"]
            )
            evaluations.append(evaluation)
        return evaluations

    async def create_evaluation(self, evaluation):
        logger.warn('create evaluation')
        result = await self._db.insert(self._collection, evaluation.dict())
        logger.info(result)
        if not result:
            return None
        return result

    async def list_evaluations(self, query):
        logger.warn('list evaluation')
        result = await self._db.find(self._collection, query)
        logger.info(result)
        return []

    async def list_evaluation_by_id(self, id):
        logger.warn('list evaluation by id')
        return await self._db.find_one(self._collection, id)

    async def list_one_evaluation(self, query):
        logger.warn('list one evaluation')
        question = await self._db.find_one(self._collection, query)
        logger.info(question)
        if question:
            return self.format_evaluations_results([question])
        return None

    async def update(self, mongo_id: str, data: Union[BaseModel, dict]):
        if isinstance(data, BaseModel):
            data_dict = data.dict(exclude_none=True)
        else:
            data_dict = data
        await self._db.update(self._collection, mongo_id, data_dict)

    async def delete_question(self, id):
        await self._db.delete(self._collection, id)
