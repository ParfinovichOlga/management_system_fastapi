from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from typing import Annotated
from datetime import date
from app.dependencies import get_evaluation_repository, get_task_repository
from app.repositories.abstract.evaluation import EvaluationRepository
from app.repositories.abstract.task import TaskRepository
from .auth import get_current_user_strict
from ..schemas import CreateEvaluation, EvaluationOut
from ..services import tasks, evaluations

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/{task_id}", status_code=status.HTTP_201_CREATED)
async def create_evaluation(
    ev_repo: Annotated[EvaluationRepository, Depends(get_evaluation_repository)],
    task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    create_evaluation: CreateEvaluation,
    task_id: Annotated[int, Path(gt=0)],
):
    ev_service = evaluations.EvaluationService(ev_repo)
    task_service = tasks.TaskService(task_repo)
    if user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only manager can evaluate tasks.",
        )
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    if task.status.value != "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only done task can be evaluated",
        )
    if not task.assigned_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Nobody assigned to task"
        )
    await ev_service.create_evaluation(
        task.id, task.assigned_to, create_evaluation.grade
    )


@router.get("/", status_code=status.HTTP_200_OK)
async def my_evaluations(
    ev_repo: Annotated[EvaluationRepository, Depends(get_evaluation_repository)],
    user: Annotated[dict, Depends(get_current_user_strict)],
    date_start: date,
    date_end: date,
):
    ev_service = evaluations.EvaluationService(ev_repo)
    if date_start > date_end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The end date must be later than the start date",
        )
    evs, avg_ev = await ev_service.get_user_evaluations(
        user["id"], date_start, date_end
    )
    return {
        "Evaluations": [EvaluationOut.model_validate(ev) for ev in evs],
        "Avarage evaluation": avg_ev,
    }
