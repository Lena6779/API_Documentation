from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    # min_length=1 rejects empty titles; FastAPI returns 422 automatically
    title: str = Field(min_length=1)
    description: Optional[str] = None
    completed: bool = False

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Write API documentation",
                    "description": "Add summaries, docstrings, and error responses",
                    "completed": False,
                }
            ]
        }
    )


# All fields optional so PATCH can update just one field at a time
class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    completed: Optional[bool] = None

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"completed": True}
            ]
        }
    )


class TaskResponse(BaseModel):
    # from_attributes lets Pydantic read values directly from SQLAlchemy objects
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "title": "Write API documentation",
                    "description": "Add summaries, docstrings, and error responses",
                    "completed": False,
                }
            ]
        },
    )

    id: int
    title: str
    description: Optional[str] = None
    completed: bool