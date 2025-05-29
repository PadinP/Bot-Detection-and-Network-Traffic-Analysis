from fastapi import FastAPI
import uvicorn
from app.routers import bot_detection,capture_data,orchestrate

app = FastAPI()
# app.include_router(capture_data.router)
# app.include_router(bot_detection.router)
app.include_router(orchestrate.router)

if __name__ == "__main__":  
    uvicorn.run("main:app", port=8001, reload=True)

