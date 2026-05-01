"""
Pydantic models for request validation
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, validator


class LoginRequest(BaseModel):
    """Login request validation"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6, max_length=255)


class ForgotPasswordRequest(BaseModel):
    """Forgot password request validation"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request validation"""
    token: str = Field(..., min_length=32, max_length=64)
    new_password: str = Field(..., min_length=6, max_length=255)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class CreateUserRequest(BaseModel):
    """Create user request validation"""
    name: str = Field(..., min_length=2, max_length=255)
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=255)
    email: Optional[EmailStr] = None
    role: str = Field(default="seller", pattern="^(seller|admin)$")


class MaterialFilterRequest(BaseModel):
    """Material filter request validation"""
    industry: str = Field(default="all")
    solution: str = Field(default="all")


class MaterialSelectionRequest(BaseModel):
    """Material selection request validation"""
    filename: str = Field(..., min_length=1, max_length=255)


class MaterialListRequest(BaseModel):
    """Material list update request validation"""
    materials: List[str] = Field(default_factory=list)


class AnalyzeRequest(BaseModel):
    """Analyze pitch request validation"""
    seller_name: str = Field(..., min_length=2, max_length=120)
    materials: List[str] = Field(...)
    
    @validator('seller_name')
    def clean_seller_name(cls, v):
        """Clean and validate seller name"""
        return v.strip()
    
    @validator('materials')
    def validate_materials(cls, v):
        """Validate materials list"""
        if not v:
            raise ValueError('At least one material must be selected')
        # Remove duplicates while preserving order
        seen = set()
        cleaned = []
        for item in v:
            if item and item not in seen:
                seen.add(item)
                cleaned.append(item)
        return cleaned


class CreateMaterialRequest(BaseModel):
    """Create material request validation"""
    title: str = Field(..., min_length=2, max_length=255)
    filename: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=2, max_length=20)
    industry: str = Field(..., min_length=2, max_length=100)
    solution: str = Field(..., min_length=2, max_length=100)
    description: str = Field(default="", max_length=1000)
    sort_order: int = Field(default=0, ge=0)


class UpdateMaterialRequest(BaseModel):
    """Update material request validation"""
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    filename: Optional[str] = Field(None, min_length=1, max_length=255)
    file_type: Optional[str] = Field(None, min_length=2, max_length=20)
    industry: Optional[str] = Field(None, min_length=2, max_length=100)
    solution: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    sort_order: Optional[int] = Field(None, ge=0)
    active: Optional[bool] = None

# Made with Bob
