from typing import Union
from fastapi import Depends
from pydantic import BaseModel

from models.question import Evaluation, Options, Question, QuestionFactory

from .database import Database, BaseRepository


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
        result = await self._db.insert(self._collection, evaluation.dict())
        if not result:
            return None
        return result

    async def list_evaluations(self, query):
        result = await self._db.find(self._collection, query)
        return self.format_evaluations_results(result)

    async def list_evaluation_by_id(self, id):
        return await self._db.find_one(self._collection, id)

    async def list_one_evaluation(self, query):
        question = await self._db.find_one(self._collection, query)
        if question:
            return self.format_evaluations_results([question])
        return None

    async def update(self, mongo_id: str, data: Union[BaseModel, dict]):
        if isinstance(data, BaseModel):
            data_dict = data.dict(exclude_none=True)
        else:
            data_dict = data
        await self._db.update(self._collection, mongo_id, data_dict)

    async def delete_question(self, id) -> Evaluation | None:
        await self._db.delete(self._collection, id)
