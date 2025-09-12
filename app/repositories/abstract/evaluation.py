from abc import ABC, abstractmethod
from datetime import date
from app.models import Evaluation
from typing import List, Tuple


class EvaluationRepository(ABC):
    """
    Defines the interface all EvaluationRepository implementations must follow.
    """

    @abstractmethod
    async def create_evaluation(self, task_id: int, user_id: int, grade: int) -> None:
        pass

    @abstractmethod
    async def get_user_evaluations(
        self, user_id: int, start: date, end: date
    ) -> Tuple[List[Evaluation], float]:
        pass
