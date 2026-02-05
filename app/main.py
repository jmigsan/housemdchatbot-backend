from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.websocket import router as websocket_router
from app.api.utils import router as utils_router
from app.dependencies import get_gemini_client, get_housemd_client, get_deepinfra_client, get_pinecone_index

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML models and other dependencies
    print("Eager loading dependencies...")
    get_gemini_client()
    get_housemd_client()
    get_deepinfra_client()
    get_pinecone_index()
    print("Dependencies loaded.")
    yield
    # Clean up the ML models and answer resources
    print("Cleaning up dependencies...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="House MD Chatbot API",
        description="A backend for the House MD Chatbot frontend.",
        lifespan=lifespan
    )

    app.include_router(websocket_router)
    app.include_router(utils_router)

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)