from pydantic import BaseModel
from enum import Enum
from typing import Optional


class QuestionType(str, Enum):
    multiple_choice_question = 'multiple_choice'
    boolean_question = 'boolean'


class Level(str, Enum):
    very_easy = 'Muito Fácil'
    easy = 'Fácil'
    medium = 'Médio'
    hard = 'Difícil'
    very_hard = 'Muito Difícil'
                                         

class NumOptions(str, Enum):
    FOUR = 'Quatro'
    FIVE = 'Cinco'


class QuestionFactory(BaseModel):
    type: QuestionType
    capacity: str
    knowledge: str
    level: Level
    function: str
    subfunction: str
    question_num: int = 1
    num_options: Optional[NumOptions] = NumOptions.FOUR
    context: Optional[str] = None


class QuestionFactorySenaiPlay(BaseModel):
    url: str
    type: QuestionType = QuestionType.multiple_choice_question
    question_num: int = 1
    num_options: Optional[NumOptions] = NumOptions.FOUR
