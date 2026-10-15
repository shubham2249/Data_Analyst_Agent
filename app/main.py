from fastapi import FastAPI
from app.api.routes import router


app = FastAPI(
    title= "InsightIQ",
    description= "AI powered Data Analyst Agent",
    version= "0.1.0",
)

app.include_router(
    router,
    prefix="/api",
)


@app.get("/health")
def health_check():

    return {
        "status": "ok",
        "service": "InsightIQ",
    }