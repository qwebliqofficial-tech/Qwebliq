from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class ClientCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class InquiryRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    company: str = Field(default="", max_length=120)
    budget: str = Field(default="", max_length=60)
    message: str = Field(min_length=10, max_length=3000)


class NewsletterRequest(BaseModel):
    email: EmailStr


class CalculatorRequest(BaseModel):
    project_type: Literal["website", "ecommerce", "brand", "growth"]
    timeline: Literal["standard", "accelerated"]
    pages: int = Field(ge=1, le=50)


class ContentCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    category: str = Field(default="Studio note", max_length=60)
    excerpt: str = Field(min_length=10, max_length=500)


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=100)
    industry: str = Field(min_length=2, max_length=80)
    summary: str = Field(min_length=10, max_length=500)
    live_url: str = Field(default="", max_length=400)