from textwrap import dedent

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

tags_metadata = [
    {
        "name": "Tasks",
        "description": "Create, read, update, and delete tasks. Task titles must be unique.",
    },
]

app = FastAPI(
    title="Task CRUD API",
    description=dedent("""
        A task management API built with **FastAPI**, **Pydantic**, and **SQLAlchemy**.

        ## Features
        - Create, view, update, and delete tasks
        - Duplicate task titles are rejected with **409 Conflict**
        - Partial updates with `PATCH`: only the fields you send are changed

        ## Quick Start
        1. Create a task with `POST /tasks`
        2. List all tasks with `GET /tasks`
        3. Update or delete a task using its `id`
    """),
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# Reusable error response docs
NOT_FOUND = {
    404: {
        "description": "No task exists with this ID",
        "content": {"application/json": {"example": {"detail": "Task not found"}}},
    }
}
VALIDATION_ERROR = {
    422: {"description": "Invalid input, such as a missing field or a non-integer ID"}
}
CONFLICT = {
    409: {
        "description": "A task with this title already exists",
        "content": {
            "application/json": {
                "example": {"detail": "A task with this title already exists"}
            }
        },
    }
}


@app.post(
    "/tasks",
    response_model=schemas.TaskResponse,
    status_code=201,
    tags=["Tasks"],
    summary="Create a new task",
    responses={**CONFLICT, **VALIDATION_ERROR},
)
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    """
    Create a new task.

    - **title**: required, and must be unique
    - Returns the created task with its new `id`
    - Returns **409** if a task with the same title already exists
    """
    # Reject duplicates with 409 Conflict before touching the database
    existing = db.query(models.Task).filter(models.Task.title == task.title).first()
    if existing:
        raise HTTPException(status_code=409, detail="A task with this title already exists")

    db_task = models.Task(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@app.get(
    "/tasks",
    response_model=list[schemas.TaskResponse],
    tags=["Tasks"],
    summary="List all tasks",
)
def list_tasks(db: Session = Depends(get_db)):
    """
    Retrieve every task in the database.

    - Returns an empty list if no tasks exist
    - No parameters required
    """
    return db.query(models.Task).all()


@app.get(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
    summary="Get a single task",
    responses={**NOT_FOUND, **VALIDATION_ERROR},
)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Retrieve one task by its ID.

    - **task_id**: the ID of the task to fetch
    - Returns **404** if the task doesn't exist
    """
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch(
    "/tasks/{task_id}",
    response_model=schemas.TaskResponse,
    tags=["Tasks"],
    summary="Partially update a task",
    responses={**NOT_FOUND, **VALIDATION_ERROR},
)
def update_task(task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    """
    Update some or all fields of an existing task.

    - **task_id**: the ID of the task to update
    - Only fields included in the request body are changed
    - Omitted fields keep their current values
    - Returns **404** if the task doesn't exist
    """
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    # exclude_unset=True skips fields the client didn't send,
    # so omitted fields aren't overwritten with None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    db.commit()
    db.refresh(task)
    return task


@app.delete(
    "/tasks/{task_id}",
    status_code=204,
    tags=["Tasks"],
    summary="Delete a task",
    responses={**NOT_FOUND, **VALIDATION_ERROR},
)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Permanently delete a task.

    - **task_id**: the ID of the task to delete
    - Returns no body on success (**204**)
    - Returns **404** if the task doesn't exist
    """
    task = db.get(models.Task, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()