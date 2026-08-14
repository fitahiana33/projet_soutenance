import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import routers
from app.core.database import SessionLocal, init_db
from app.core.seed import seed_admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smart_erp")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database tables...")
    try:
        init_db()
        db = SessionLocal()
        try:
            seed_admin(db)
            logger.info("Admin seed checked successfully.")
        except Exception as seed_err:
            logger.error(f"Error during admin seed: {seed_err}")
        finally:
            db.close()
    except Exception as db_err:
        logger.error(f"Error initializing database: {db_err}")

    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title="Smart ERP Intelligent API",
    version="1.0.0",
    lifespan=lifespan
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Une erreur interne s'est produite sur le serveur. Veuillez réessayer plus tard."
        }
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits dev access from any local origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for router in routers:
    app.include_router(
        router,
        prefix="/api/v1"
    )


@app.get("/")
def root():
    return {
        "message": "Smart ERP Intelligent API fonctionne",
        "version": "1.0.0",
        "status": "online"
    }
