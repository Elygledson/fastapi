from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class QuestionType(str, Enum):
    multiple_choice_question = 'multiple_choice'
    boolean_question = 'boolean'


class Level(str, Enum):
    EASY = 'Fácil'
    MEDIUM = 'Médio'
    HARD = 'Difícil'

    def __str__(self):
        return self.value


class NumOptions(str, Enum):
    FOUR = 'Quatro'
    FIVE = 'Cinco'


class QuestionFactory(BaseModel):
    type: QuestionType = Field(
        ..., description="O tipo de questão a ser gerada múltipla escolha ou Verdadeiro/Falso.")
    content: str = Field(
        ..., description="Material de apoio para geração das questões.")
    level: Level = Field(
        ..., description="O nível de dificuldade do item.")
    question_num: int = Field(
        default=1, description="O número de questões a serem geradas.")
    num_options: Optional[NumOptions] = Field(
        default=NumOptions.FOUR, description="O número de opções para cada questão de múltipla escolha.")


class Options(BaseModel):
    description: str
    justification: str


class Question(BaseModel):
    question: str
    options: List[Options]
    answer: str


class Evaluation(BaseModel):
    id: str
    questions: List[Question]
    date: str = Field(..., description="Data de criação da avaliação")
    school: str = Field(..., description="Nome da escola")
    course: str = Field(..., description="Nome da disciplina")
    title: str = Field(..., description="Título da avaliação")
