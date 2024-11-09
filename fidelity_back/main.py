import uvicorn
from auth.auth import router as auth_router
from fastapi import FastAPI
from routes.timezone import router as timezone_router
from routes.user import router as user_router
from routes.user_role import router as user_role_router

app = FastAPI(
    title="Fidelity Backend",
    description="This is the backend for the Fidelity project",
    version="0.1",
    docs_url="/docs",
)


api_v1 = FastAPI(
    title="Fidelity Backend v1",
    description="Version 1 of the Fidelity Backend API",
)

app.mount("/v1", api_v1)

api_v1.include_router(auth_router)
api_v1.include_router(user_role_router)
api_v1.include_router(user_router)
api_v1.include_router(timezone_router)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=5000, reload=True)
