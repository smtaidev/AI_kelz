from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from app.services.email.email_schema import EmailError

app = FastAPI(
    title="AI Analysis API",
    description="API for AI-powered analysis of email generation and todo list creation",
    version="1.0.0"
)

router = APIRouter()

from app.services.email.email_router import router as email_router
from app.services.todo_list.todo_list_router import router as todo_router

router.include_router(email_router, prefix="/email", tags=["email"])
router.include_router(todo_router, prefix="/todo", tags=["todo"])

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the AI Analysis API",
       
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API is running normally"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=EmailError(
            error_code=f"HTTP_{exc.status_code}",
            message=str(exc.detail)
        ).dict()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)