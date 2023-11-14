from pydantic import BaseModel
from enum import Enum


class QuestionType(str, Enum):
    multiple_choice_question = 'multiple_choice'
    boolean_question = 'boolean'

class Difficulty(str, Enum):
    very_easy = 'Muito Fácil'
    easy = 'Fácil'
    medium = 'Médio'
    hard = 'Difícil'
    very_hard = 'Muito Difícil'

class QuestionFactory(BaseModel):
    type: QuestionType
    capacity: str
    knowledge: str
    difficulty: Difficulty
    performance_standard: str
    question_num: int

