from fastapi.middleware.cors import CORSMiddleware
from repositories.database import Database
from routers.question import question
from config.environment import config
from fastapi import FastAPI
import asyncio

app = FastAPI()

app.include_router(question, prefix='/api')

Database.initialize(config.get('COLLECTION'))

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

if __name__ == "__main__":
    asyncio.run(app.run_task(host="0.0.0.0", port=8000))
