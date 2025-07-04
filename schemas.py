"""
Pydantic schemas for enforcing data contracts in optimization functions.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, Any, Union
import logging

logger = logging.getLogger(__name__)

class OptimizationResult(BaseModel):
    """
    Base class for optimization results with common validation.
    """
    
    model_config = ConfigDict(extra="allow")  # Allow additional fields like user data
        
    @field_validator('*', mode='before')
    @classmethod
    def validate_no_none_in_data_fields(cls, v, info):
        """Ensure no None values in non-meta fields"""
        field_name = info.field_name if info.field_name else 'unknown'
        if field_name.startswith('_'):
            return v  # Meta fields can be None
        if v is None:
            raise ValueError(f"None value not allowed in data field: {field_name}")
        return v

class MemoryOptimizedResult(OptimizationResult):
    """
    Schema for memory-optimized results.
    Enforces that no None values exist in non-meta fields.
    """
    optimization: str = Field(..., description="Optimization strategy used", alias="_optimization")
    compressed: bool = Field(..., description="Whether data was compressed", alias="_compressed")
    
    @classmethod
    def validate_output(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that memory optimization properly removed None values.
        
        Args:
            data: Dictionary to validate
            
        Returns:
            Validated dictionary
            
        Raises:
            ValueError: If None values found in non-meta fields
        """
        # Check for None values in non-meta fields
        none_fields = [k for k, v in data.items() 
                      if not k.startswith("_") and v is None]
        
        if none_fields:
            logger.error("None values found after memory optimization: %s", none_fields)
            raise ValueError(f"Memory optimization failed: None values in {none_fields}")
        
        # Validate required meta fields
        if data.get("_optimization") != "memory":
            raise ValueError("Memory optimization must have _optimization='memory'")
        if data.get("_compressed") is not True:
            raise ValueError("Memory optimization must have _compressed=True")
            
        return data

class PerformanceOptimizedResult(OptimizationResult):
    """Schema for performance-optimized results."""
    optimization: str = Field(..., description="Optimization strategy used", alias="_optimization")
    timestamp: float = Field(..., description="Optimization timestamp", alias="_timestamp")

class AccuracyOptimizedResult(OptimizationResult):
    """Schema for accuracy-optimized results."""
    optimization: str = Field(..., description="Optimization strategy used", alias="_optimization")
    precision_level: str = Field(..., description="Precision level", alias="_precision_level") 