
from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


#Auth 
class RegisterRequest(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=80, pattern=r"^\w+$")]
    email:    EmailStr
    password: Annotated[str, Field(min_length=8, max_length=128)]
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    username: Annotated[str, Field(min_length=1, max_length=80)]
    password: Annotated[str, Field(min_length=1)]


class ChangePasswordRequest(BaseModel):
    old_password: Annotated[str, Field(min_length=1)]
    new_password: Annotated[str, Field(min_length=8, max_length=128)]

    @model_validator(mode="after")
    def passwords_differ(self) -> "ChangePasswordRequest":
        if self.old_password == self.new_password:
            raise ValueError("New password must differ from the current one.")
        return self


# Resume 
class ResumeUploadMeta(BaseModel):
    """Optional metadata that can accompany a file upload."""
    email: EmailStr | None = None
    send_report: bool = False


# Job 
class JobCreateRequest(BaseModel):
    title:       Annotated[str, Field(min_length=2, max_length=200)]
    company:     str | None = None
    description: Annotated[str, Field(min_length=50)]

    @field_validator("description")
    @classmethod
    def description_long_enough(cls, v: str) -> str:
        if len(v.split()) < 15:
            raise ValueError("Job description must contain at least 15 words.")
        return v


# Evaluation 
class EvaluationRequest(BaseModel):
    resume_id: Annotated[int, Field(gt=0)]
    job_id:    Annotated[int, Field(gt=0)]
    # Optional override: pass job description inline instead of by ID
    job_description: str | None = None

    @model_validator(mode="after")
    def requires_job_ref(self) -> "EvaluationRequest":
        if not self.job_id and not self.job_description:
            raise ValueError("Provide either job_id or job_description.")
        return self


#Pagination 
class PaginationParams(BaseModel):
    page:     Annotated[int, Field(ge=1)]   = 1
    per_page: Annotated[int, Field(ge=1, le=100)] = 20
