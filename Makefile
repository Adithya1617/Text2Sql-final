.PHONY: help install test run-backend run-frontend run-both clean

help: ## Show this help message
	@echo "Local Orchestrator - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies using uv
	uv sync

test: ## Run tests
	uv run pytest tests/ -v

run-backend: ## Run only the FastAPI backend
	uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend: ## Run only the Streamlit frontend
	uv run streamlit run app/ui/streamlit_app.py --server.port 8501

run-both: ## Run both frontend and backend (recommended)
	uv run python run_app.py

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
