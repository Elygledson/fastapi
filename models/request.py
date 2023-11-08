from pydantic import BaseModel, Field
from enum import Enum


class QuestionType(str, Enum):
    multiple_choice_question = 'multiple_choice'
    boolean_question = 'boolean'

class Difficulty(str, Enum):
    hard = 'Difícil'
    easy = 'Fácil'
    medium = 'Médio'


class Rules(BaseModel):
    capacity: str
    knowledge: str
    difficulty: Difficulty
    performance_standard: str


class Request(BaseModel):
    type: QuestionType = Field(description='Tipo de questão a ser gerada')
    num: int = Field(
        default=3, description="Quantidade de questões a serem geradas")
    rules: Rules = Field(description='Regras estabelecidas para a geração de questões')
    
