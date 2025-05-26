from fastmcp import FastMCP
import os
import uvicorn
from fastapi import FastAPI
from starlette.responses import JSONResponse
import threading

# Get port from environment variable for Digital Ocean compatibility
port = int(os.environ.get("PORT", 9783))

# Create FastAPI app for health checks
app = FastAPI()

# Create FastMCP instance
mcp = FastMCP("calculation")

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@mcp.tool()
def Math(a:float,b:float,operation:str):
    """
    add, subtract, multiply and divide two numbers.
    Args:
        a (float): first number
        b (float): second number
        operation (str): operation to perform, one of 'add', 'subtract', 'multiply', 'divide'
    Returns:
        float: result of the operation
    Raises:
        ValueError: if operation is not one of the allowed values
    """
    print("Tool run")
    if operation == 'add':
        return a + b
    elif operation == 'subtract':
        return a - b
    elif operation == 'multiply':
        return a * b
    elif operation == 'divide':
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError("Invalid operation. Allowed values are: 'add', 'subtract', 'multiply', 'divide'")

@mcp.prompt()
def Prompt(Operation:str):
    """ Generate the prompt for the Math tool."""
    return f"Perform the operation: {Operation}. You can use the Math tool to do this. The operation should be one of 'add', 'subtract', 'multiply', 'divide'. and in the end print work has been done by the tool."

@mcp.resource("guide://math-operations")
def math_operations_text() -> str:
    """
    Reads a plain text file with math operation descriptions and returns its content.
    """
    file_path = "u.txt"  
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error loading math operations guide: {str(e)}"

if __name__=="__main__":
    # Run the MCP server in a separate thread
    def run_mcp():
        mcp.run(transport="sse", host="0.0.0.0", port=9784)
    
    # Start the MCP server thread
    mcp_thread = threading.Thread(target=run_mcp)
    mcp_thread.daemon = True
    mcp_thread.start()
    
    # Run the FastAPI app in the main thread
    uvicorn.run(app, host="0.0.0.0", port=port)