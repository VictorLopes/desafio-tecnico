from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.endpoints import leads
from app.db.mongodb import connect_to_mongo, close_mongo_connection, db_client
from app.models.lead import LEAD_COLLECTION
import logging

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    if db_client.db is not None:
        await db_client.db[LEAD_COLLECTION].create_index("email", unique=True)
        logging.info("Ensured unique index on email field.")
    yield
    await close_mongo_connection()


app = FastAPI(title="Leads API", lifespan=lifespan)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "Error", "data": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first_error = errors[0].get("msg", "Validation Error")
        if first_error.startswith("Value error, "):
            first_error = first_error.replace("Value error, ", "")
    else:
        first_error = "Invalid request data"

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"status": "Error", "data": first_error},
    )


app.include_router(leads.router, prefix="/leads", tags=["leads"])
