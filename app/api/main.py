from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List
import time
import logging
from contextlib import asynccontextmanager

# Import your modules
from ..graph.pipeline import run_pipeline
from ..utils.logger import get_logger

logger = get_logger("fastapi_main")

# Lifespan management for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Banking Query API starting up...")
    
    # Initialize any required services
    try:
        # Test database connection
        from ..executors.sqlite_exec import run_sql
        test_result = run_sql("SELECT 1 as test")
        if test_result.get("error"):
            logger.error(f"Database connection failed: {test_result['error']}")
        else:
            logger.info("✅ Database connection verified")
    except Exception as e:
        logger.error(f"❌ Startup database test failed: {e}")
    
    # Initialize pipeline and clear cache
    try:
        from ..graph.pipeline import initialize_pipeline
        initialize_pipeline()
        logger.info("✅ Pipeline initialized with fresh cache")
    except Exception as e:
        logger.warning(f"⚠️ Pipeline initialization issue: {e}")
    
    # Test LLM connection
    logger.info("🧪 Testing LLM integration...")
    try:
        from ..models.sql_agent import question_to_sql
        logger.info("🔌 Attempting LLM connection...")
        test_sql = question_to_sql("SELECT 1 as test")
        logger.info("✅ LLM integration verified successfully")
        logger.info(f"📊 Test response: {test_sql[:50]}...")
    except Exception as e:
        logger.warning(f"⚠️ LLM integration issue: {e}")
        logger.info("💡 Make sure Ollama is running and sqlcoder7b:latest is pulled")
    
    logger.info("🎯 API ready to serve requests")
    
    yield
    
    # Shutdown
    logger.info("🛑 Banking Query API shutting down...")

# Create FastAPI app with enhanced configuration
app = FastAPI(
    title="AI-Powered Banking Query API",
    description="""
    Advanced Natural Language to SQL conversion API for banking systems.
    
    ## Features
    - 🤖 AI-powered SQL generation using CodeLlama:13b
    - 🛡️ Multi-layer security validation
    - 📊 Role-based access control
    - 🤖 AI-powered SQL generation
    - 📈 Performance monitoring
    - 🏦 Banking-specific optimizations
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, description="Natural language question about banking data")
    role: str = Field(default="analyst", description="User role: analyst, viewer, or admin")
    user: str = Field(default="anonymous", description="User identifier for audit logging")

class AskResponse(BaseModel):
    explanation: str = Field(description="Generated SQL query")
    guard_reason: str = Field(description="Security validation reason")
    table: Dict[str, Any] = Field(description="Query results with columns, rows, and metadata")
    success: bool = Field(description="Whether the query executed successfully")
    execution_time: float = Field(description="Total execution time in seconds")

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    services: Dict[str, str]
    version: str

# Dependency for request validation
async def validate_role(request: AskRequest) -> AskRequest:
    """Validate user role"""
    valid_roles = ["analyst", "viewer", "admin"]
    if request.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    return request

# Main query endpoint
@app.post("/ask", response_model=AskResponse, summary="Execute Natural Language Query")
async def ask_question(request: AskRequest = Depends(validate_role)):
    """
    Convert natural language question to SQL and execute against banking database.
    
    ## Query Examples:
    - "List all customers and their branch names"
    - "Show transactions that occurred on weekends"
    - "Find customers with both credit and loan accounts"
    - "Top 5 branches by deposit amount"
    
    ## Roles:
    - **analyst**: Full access to all data
    - **viewer**: Limited access with data masking
    - **admin**: Full access plus administrative functions
    """
    start_time = time.time()
    
    try:
        logger.info(f"🔄 Processing query from {request.user} ({request.role}): {request.question[:80]}...")
        logger.debug(f"Full question: {request.question}")
        
        # Execute pipeline
        logger.info("🚀 Executing pipeline...")
        result = run_pipeline(
            question=request.question,
            role=request.role,
            user=request.user
        )
        
        execution_time = time.time() - start_time
        
        # Log pipeline results
        logger.info(f"📊 Pipeline completed - SQL generated: {bool(result.get('sql'))}")
        if result.get('sql'):
            logger.info(f"🔍 Generated SQL: {result.get('sql', '')[:100]}...")
        
        # Determine success
        table_data = result.get("table", {})
        success = not bool(table_data.get("error"))
        
        # Prepare response
        response_data = {
            "explanation": result.get("sql", ""),
            "guard_reason": result.get("guard_reason", ""),
            "table": table_data,
            "success": success,
            "execution_time": round(execution_time, 3)
        }
        
        if success:
            row_count = len(table_data.get("rows", []))
            logger.info(f"✅ Query completed successfully in {execution_time:.3f}s - {row_count} rows returned")
        else:
            error_msg = table_data.get("error", "Unknown error")
            logger.warning(f"⚠️ Query completed with error in {execution_time:.3f}s: {error_msg}")
            
        return AskResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Query processing failed after {execution_time:.3f}s: {str(e)}")
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal server error during query processing",
                "message": str(e),
                "execution_time": round(execution_time, 3)
            }
        )

# Health check endpoint
@app.get("/health", response_model=HealthResponse, summary="System Health Check")
async def health_check():
    """Get system health status and service availability"""
    
    services = {}
    
    # Check database
    try:
        from ..executors.sqlite_exec import run_sql
        result = run_sql("SELECT 1 as health_check")
        services["database"] = "healthy" if not result.get("error") else "error"
    except Exception:
        services["database"] = "error"
    
    # Check LLM service
    try:
        from ..models.sql_agent import question_to_sql
        services["llm"] = "healthy"  # If import succeeds, LLM integration is available
    except Exception:
        services["llm"] = "unavailable"
    
    overall_status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        services=services,
        version="2.0.0"
    )

@app.post("/admin/clear-cache")
async def clear_cache_endpoint():
    """Clear the pipeline cache manually"""
    try:
        from ..graph.pipeline import clear_pipeline_cache
        result = clear_pipeline_cache()
        logger.info("🗑️ Cache cleared via API endpoint")
        return {
            "success": True,
            "message": "Cache cleared successfully",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
    except Exception as e:
        logger.error(f"❌ Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

@app.post("/admin/test-llm")
async def test_llm_endpoint():
    """Test LLM integration directly"""
    try:
        from ..models.sql_agent import question_to_sql
        logger.info("🧪 Testing LLM via admin endpoint")
        
        test_question = "SELECT 1 as test"
        start_time = time.time()
        
        result = question_to_sql(test_question)
        execution_time = time.time() - start_time
        
        logger.info(f"✅ LLM test completed in {execution_time:.3f}s")
        
        return {
            "success": True,
            "question": test_question,
            "generated_sql": result,
            "execution_time": round(execution_time, 3),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
    except Exception as e:
        logger.error(f"❌ LLM test failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM test failed: {str(e)}")

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    )

# Startup message
@app.on_event("startup")
async def startup_event():
    """Log startup completion"""
    logger.info("🎯 AI-Powered Banking Query API is ready!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )