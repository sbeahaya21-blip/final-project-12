"""FastAPI application entry point."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.views.invoice_views import router as invoice_router
from app.views.erpnext_views import router as erpnext_router
from app.exceptions import (
    InvoiceNotFoundError,
    InvalidInvoiceFormatError,
    ParsingError
)

app = FastAPI(
    title="Invoice Parser and AI Anomaly Detection",
    description="API for parsing invoices and detecting anomalies/fraud",
    version="1.0.0"
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests for debugging."""
    import logging
    logger = logging.getLogger(__name__)
    method = request.method
    path = request.url.path
    logger.info(f"Request: {method} {path}")
    if "submit-to-erpnext" in path:
        print(f"[MIDDLEWARE] {method} {path}")  # Always visible
    response = await call_next(request)
    if response.status_code == 404 and "submit-to-erpnext" in path:
        print(f"[MIDDLEWARE] 404 response for {method} {path}")
    return response

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(invoice_router)
app.include_router(erpnext_router)

# Mount static files for UI (React app)
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")


# Exception handlers
@app.exception_handler(InvoiceNotFoundError)
async def invoice_not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    from fastapi import status
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc)}
    )


@app.exception_handler(InvalidInvoiceFormatError)
async def invalid_format_handler(request, exc):
    from fastapi.responses import JSONResponse
    from fastapi import status
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.exception_handler(ParsingError)
async def parsing_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    from fastapi import status
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - serve React app."""
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    # Fallback if React app not built yet
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Invoice Parser & Anomaly Detection</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 40px; text-align: center; }
            .message { max-width: 600px; margin: 0 auto; padding: 20px; background: #f0f0f0; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="message">
            <h1>Invoice Parser & Anomaly Detection</h1>
            <p>Frontend not built yet. Please run:</p>
            <pre>cd frontend && npm install && npm run build</pre>
            <p>Or access the API documentation at <a href="/docs">/docs</a></p>
        </div>
    </body>
    </html>
    """

# Serve React app for all frontend routes (SPA routing)
@app.get("/invoices", response_class=HTMLResponse)
@app.get("/invoices/{path:path}", response_class=HTMLResponse)
async def serve_react_app():
    """Serve React app for frontend routes."""
    index_path = Path("static/index.html")
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Frontend not built</h1><p>Run: cd frontend && npm run build</p>")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "invoice-parser"}
