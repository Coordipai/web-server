import secrets
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi import security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.openapi.docs import get_swagger_ui_html

import src.models  # noqa: F401
from src.database import initialize_database
from exceptions.handler import register_exception_handlers
from src.config import FRONTEND_URL
from src.agent import chain, tool
from src.config.middleware import jwt_authentication_middleware
from src.config.database import initialize_database
from src.config.config import FRONTEND_URL, SWAGGER_PASSWORD, SWAGGER_USERNAME
from src.response.error_definitions import BaseAppException
from src.response.handler import exception_handler

# Import routers
from auth.router import router as auth_router
from project.router import router as project_router
from user.router import router as user_router


app = FastAPI(
    title="Coordipai Web Server",
    description="",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

initialize_database()
app.add_exception_handler(BaseAppException, exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(jwt_authentication_middleware)

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, SWAGGER_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, SWAGGER_PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return True


@app.get("/docs", include_in_schema=False)
async def get_documentation(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Secure API Docs")
<<<<<<< HEAD


@app.get("/store_vector")
def store_vector():

    texts = ["banana1 ", "banana1? banana2"]
    metadatas = [{"source": "banana1"}, {"source": "banana1? banana2"}]
    tool.add_text_data_tool(texts, metadatas=metadatas)

    query = "banana1"
    results = tool.search_data_tool(query, k=2)
    print(f"현재 벡터 저장 개수: {len(tool.vector_db.get()['documents'])}")


    for res in results:
        print("내용: ", res.page_content)
        print("메타데이터: ", res.metadata)

    return results


@app.get("/generate_issues")
async def generate_issues():
    """
    Generate issues using the agent executor.
    """

    executor = chain.CustomAgentExecutor()
    result = await executor.generate_issues()
    return result
=======
>>>>>>> main


# Include routers
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(user_router)
