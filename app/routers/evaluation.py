from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from ..backend.db_depends import get_db
from .auth import get_current_user_strict
from ..schemas import CreateEvaluation, EvaluationOut
from ..crud import tasks, evaluations

router = APIRouter(
    prefix='/evaluation',
    tags=['evaluation']
)


@router.post('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def create_evaluation(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        create_evaluation: CreateEvaluation,
        task_id: Annotated[int, Path(gt=0)]):
    if user['role'] != 'manager':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Only manager can evaluate tasks.'
        )
    task = await tasks.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    if task.status.value != 'done':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Only done task can be evaluated'
        )
    if not task.assigned_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Nobody assigned to task'
        )
    await evaluations.create_evaluation(
        db, task.id, task.assigned_to, create_evaluation.grade
    )


@router.get('/', status_code=status.HTTP_200_OK)
async def my_evaluations(
        db: Annotated[AsyncSession, Depends(get_db)],
        user: Annotated[dict, Depends(get_current_user_strict)],
        date_start: date, date_end: date):
    evs, avg_ev = await evaluations.get_user_evaluations(
        db, user['id'], date_start, date_end)
    return {
        'Evaluations': [EvaluationOut.model_validate(ev) for ev in evs],
        'Avarage evaluation': avg_ev
        }
