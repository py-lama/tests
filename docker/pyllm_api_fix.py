#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyLLM API - REST API for LLM operations

This module provides a FastAPI server for interacting with LLM models.
"""

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

# Use relative import instead of absolute import
from .models import ModelManager

# Create FastAPI app
app = FastAPI(
    title="PyLLM API",
    description="""
    PyLLM API - A REST API for interacting with LLM models.
    
    This API provides endpoints for querying LLM models and fixing code.
    """,
    version="0.1.0"
)

# Initialize model manager
model_manager = None

# Define request models
class QueryRequest(BaseModel):
    prompt: str
    model: str = "llama3"
    max_tokens: int = 1000
    temperature: float = 0.7

class CodeFixRequest(BaseModel):
    code: str
    error_message: str
    is_logic_error: bool = False
    attempt: int = 1
    prompt_type: Optional[str] = None

# Helper function to extract Python code from LLM response
def extract_python_code(text):
    """
    Extract Python code from markdown code blocks.
    
    Args:
        text (str): The text containing markdown code blocks.
        
    Returns:
        str: The extracted Python code.
    """
    import re
    
    # Try to extract code from markdown code blocks
    pattern = r'```(?:python)?\n([\s\S]*?)\n```'
    matches = re.findall(pattern, text)
    
    if matches:
        # Return the first code block found
        return matches[0].strip()
    
    # If no code blocks found, return the original text
    # This handles cases where the LLM might not use markdown formatting
    return text.strip()

# API endpoints
@app.post("/query")
async def query_model(request: QueryRequest):
    """
    Query an LLM model with a prompt
    """
    global model_manager
    if model_manager is None:
        model_manager = ModelManager()
    
    try:
        response = model_manager.query_model(request.prompt, request.model, request.max_tokens, request.temperature)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fix-code")
async def fix_code(request: CodeFixRequest):
    """
    Fix Python code using LLM
    """
    global model_manager
    if model_manager is None:
        model_manager = ModelManager()
    
    # Determine the type of error
    error_type = "logic" if request.is_logic_error else "syntax"
    
    # Create a prompt based on the error type and attempt number
    prompt_templates = {
        "syntax": {
            1: """
            Fix the following Python code that has a syntax error:
            
            ```python
            {code}
            ```
            
            Error message:
            ```
            {error_message}
            ```
            
            Please provide only the corrected code without explanations.
            """,
            2: """
            The previous attempt to fix this Python code didn't work. Please try again with a different approach:
            
            ```python
            {code}
            ```
            
            Error message:
            ```
            {error_message}
            ```
            
            Analyze the error carefully and provide only the corrected code without explanations.
            """,
            3: """
            This is the third attempt to fix this Python code. Please provide a completely different solution:
            
            ```python
            {code}
            ```
            
            Error message:
            ```
            {error_message}
            ```
            
            Focus on fixing the specific error mentioned and provide only the corrected code.
            """
        },
        "logic": {
            1: """
            Fix the following Python code that has a logic error:
            
            ```python
            {code}
            ```
            
            Problem description:
            ```
            {error_message}
            ```
            
            Please provide only the corrected code without explanations.
            """,
            2: """
            The previous attempt to fix this Python code with a logic error didn't work. Please try again:
            
            ```python
            {code}
            ```
            
            Problem description:
            ```
            {error_message}
            ```
            
            Analyze the logic carefully and provide only the corrected code without explanations.
            """,
            3: """
            This is the third attempt to fix this Python code with a logic error. Please provide a completely different approach:
            
            ```python
            {code}
            ```
            
            Problem description:
            ```
            {error_message}
            ```
            
            Think step by step about the logic and provide only the corrected code.
            """
        }
    }
    
    # Use custom prompt if provided
    if request.prompt_type and request.prompt_type in prompt_templates:
        prompt_template = prompt_templates[request.prompt_type].get(request.attempt, prompt_templates[request.prompt_type][1])
    else:
        prompt_template = prompt_templates[error_type].get(request.attempt, prompt_templates[error_type][1])
    
    # Format the prompt
    prompt = prompt_template.format(code=request.code, error_message=request.error_message)
    
    try:
        # Query the model
        response = model_manager.query_model(prompt, "llama3", 2000, 0.5)
        
        # Extract code from the response
        fixed_code = extract_python_code(response)
        
        return {"fixed_code": fixed_code, "full_response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Check if the API is running
    
    This endpoint provides a simple health check to verify that the API is operational.
    It can be used by monitoring systems to check the service status.
    
    Example response:
    ```json
    {
        "status": "healthy",
        "version": "0.1.0",
        "service": "PyLLM API"
    }
    ```
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "PyLLM API"
    }

def start_server(host="0.0.0.0", port=8001):
    """Start the PyLLM API server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
