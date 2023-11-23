from fastapi.middleware.cors import CORSMiddleware
from routers.question import question
from routers.auth import auth
from fastapi import FastAPI

import uvicorn

app = FastAPI(title="Question Generator",
              description='API para geração de questões (MVP)',
              version='1.0.0')

app.include_router(question, prefix='/api')
app.include_router(auth, prefix='/api')


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host='127.0.0.1', port=8000,
                log_level='info', reload=False)
