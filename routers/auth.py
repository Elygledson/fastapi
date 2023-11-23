from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

# Configuração do APIRouter
auth = APIRouter()  

# Dependência para autenticação JWT
security = HTTPBearer()

# Define as configurações do token
JWT_SECRET = "yourjwtsecret"  
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME_MINUTES = 30

# Inicializa o contexto para hashing de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication error"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


# Função para criar token JWT
def create_jwt_token(username: str) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME_MINUTES)
    payload = {"sub": username, "exp": expiration}
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token

# Função de verificação do token


def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        payload = jwt.decode(credentials.credentials,
                             JWT_SECRET, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Rota para gerar o token JWT


@auth.get("/token", tags=['Authentication'], description='Rota para gerar o token JWT')
def get_token(username: str, password: str):
    # Valida o usuário e senha
    if username != "admin" or password != "admin":
        raise HTTPException(
            status_code=401, detail="Usuário ou senha inválidos")

    # Cria o token JWT
    token = create_jwt_token(username)
    return {"access_token": token, "token_type": "bearer"}


