from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .sample_data import sample_products
from .services.catalogue import CatalogueService
from .services.intent import build_intent_provider
from .services.payments import SimulatedRazorpayAdapter
from .services.policy import PolicyEngine
from .services.workflow import CommerceWorkflow


class SearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=500)


class SelectRequest(BaseModel):
    product_id: str = Field(min_length=3, max_length=100)


class ConfirmationRequest(BaseModel):
    confirmed: bool


products = sample_products()
catalogue = CatalogueService()
workflow = CommerceWorkflow(
    products=products,
    intent_provider=build_intent_provider(settings.ai_provider, settings.openai_model),
    catalogue=catalogue,
    policy=PolicyEngine(settings.max_order_value_inr),
    payments=SimulatedRazorpayAdapter(),
)

app = FastAPI(
    title="AgentReady Commerce Gateway",
    version="1.0.0",
    description=(
        "Synthetic-data demonstration of merchant trust and transaction governance "
        "for agentic commerce. No real payment is created."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

static_dir = Path(__file__).resolve().parents[2] / "frontend"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "agentready",
        "version": "1.0.0",
        "synthetic_data": True,
        "ai_provider": settings.ai_provider,
    }


@app.get("/api/catalogue/analysis")
def catalogue_analysis() -> dict:
    return catalogue.analyse(products)


@app.get("/api/catalogue/manifest")
def commerce_manifest() -> dict:
    return catalogue.manifest(products)


@app.get("/api/products")
def list_products() -> dict:
    return {"synthetic_data": True, "products": [product.to_dict() for product in products]}


@app.post("/api/commerce/search")
def start_search(request: SearchRequest) -> dict:
    return workflow.start(request.query).to_dict()


@app.post("/api/commerce/{session_id}/select")
def select_product(session_id: str, request: SelectRequest) -> dict:
    try:
        return workflow.select(session_id, request.product_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/commerce/{session_id}/confirm")
def confirm_order(session_id: str, request: ConfirmationRequest) -> dict:
    try:
        return workflow.confirm(session_id, request.confirmed).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.post("/api/commerce/{session_id}/execute")
def execute_order(session_id: str) -> dict:
    try:
        return workflow.execute(session_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@app.get("/api/commerce/{session_id}")
def get_session(session_id: str) -> dict:
    try:
        return workflow.get(session_id).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

