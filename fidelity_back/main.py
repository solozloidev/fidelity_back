import uvicorn
from fastapi import FastAPI

app = FastAPI(
    title="Fidelity Backend",
    description="This is the backend for the Fidelity project",
    version="0.1",
    docs_url="/docs",
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="localhost", port=5000, reload=True)
