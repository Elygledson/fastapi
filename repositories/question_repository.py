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
                type=result["type"],
                content=result["content"],
                level=result["level"],
                school=result["school"],
                course=result["course"],
                teacher=result["teacher"],
                title=result["title"]
            )
            evaluations.append(evaluation)
        return evaluations

    def create_evaluation(self, evaluation):
        logger.warn('create evaluation')
        evaluation_data = evaluation.dict()
        evaluation_data.pop('id', None)
        result = self._db.insert(self._collection, evaluation_data)
        logger.info(result)
        if not result:
            return None
        return result

    def list_evaluations(self, query):
        logger.warn('list evaluation')
        result = self._db.find(self._collection, query)
        logger.info(result)
        return self.format_evaluations_results(result)

    def list_evaluation_by_id(self, id):
        logger.warn('list evaluation by id')
        return self._db.find_one(self._collection, id)

    def list_one_evaluation(self, query):
        logger.warn('list one evaluation')
        question = self._db.find_one(self._collection, query)
        logger.info(question)
        if question:
            return self.format_evaluations_results([question])
        return None

    def update(self, mongo_id: str, data: Union[BaseModel, dict]):
        if isinstance(data, BaseModel):
            data_dict = data.dict(exclude_none=True)
            data_dict.pop('id', None)
        else:
            data_dict = data
            data_dict.pop('id', None)
        self._db.update(self._collection, mongo_id, data_dict)

    def delete_question(self, id):
        self._db.delete(self._collection, id)
