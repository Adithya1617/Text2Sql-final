# 🧠 Local Orchestrator

**Local NL → SQL with RBAC, Governance, and Audit Logging**

A powerful, offline-first natural language to SQL query orchestrator designed for banking systems with role-based access control, security guards, and comprehensive audit logging.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Security Features](#security-features)
- [Database Schema](#database-schema)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

Local Orchestrator is an enterprise-grade natural language to SQL query system that operates completely offline using local AI models. It's specifically designed for banking and financial institutions that require:

- **Security**: Role-based access control and SQL injection prevention
- **Compliance**: Comprehensive audit logging and query validation
- **Reliability**: Comprehensive error handling and validation
- **Performance**: Caching and query optimization
- **Offline Operation**: No external API dependencies

The system converts natural language questions into SQL queries, executes them safely, and provides results through both a REST API and a Streamlit web interface.

## ✨ Features

### 🔐 Security & Access Control
- **Role-Based Access Control (RBAC)**: `analyst`, `viewer`, `admin` roles
- **SQL Injection Prevention**: Comprehensive input validation and sanitization
- **Read-Only Queries**: Automatic blocking of INSERT, UPDATE, DELETE operations
- **Query Limits**: Configurable result size limits (default: 100 rows)
- **Schema Validation**: Ensures queries only reference existing tables and columns

### 🤖 AI-Powered SQL Generation
- **Local LLM Integration**: Uses Ollama with sqlcoder7b:latest model
- **AI-Powered**: Advanced LLM-based SQL generation
- **Few-Shot Learning**: Banking domain-specific examples for better accuracy
- **Query Classification**: Automatic complexity estimation and planning

### 📊 Banking Domain Expertise
- **Pre-built Banking Schema**: Customers, accounts, transactions, branches, employees
- **Domain-Specific Templates**: Optimized for financial queries
- **Sample Data**: Realistic banking scenarios for testing

### 🛡️ Governance & Compliance
- **Audit Logging**: Complete query history with user, role, and timestamp
- **Query Validation**: Multi-layer validation pipeline
- **Performance Monitoring**: Execution time tracking and optimization
- **Error Handling**: Graceful degradation and user feedback

### 🚀 Performance & Reliability
- **Caching System**: Schema and query result caching
- **Connection Pooling**: Efficient database connection management
- **Timeout Protection**: Configurable query execution timeouts
- **Error Handling**: Comprehensive validation and error recovery

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │   FastAPI API   │    │   Core Pipeline │
│   (Port 8501)   │◄──►│   (Port 8000)   │◄──►│                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   SQL Guards    │    │   SQL Agent     │
                       │   (Security)    │    │   (LLM + Fall)  │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Executors     │    │   Audit Log     │
                       │   (SQLite)      │    │   (Database)    │
                       └─────────────────┘    └─────────────────┘
```

### Core Components

1. **Pipeline Orchestrator** (`app/graph/pipeline.py`)
   - Manages the complete query execution flow
   - Handles intent parsing, planning, and execution
   - Coordinates between different components

2. **SQL Agent** (`app/models/sql_agent.py`)
   - Natural language to SQL conversion
   - LLM integration with Ollama/sqlcoder7b:latest
   - LLM-powered SQL generation system

3. **Security Guards** (`app/guards/sql_guard.py`)
   - SQL injection prevention
   - Read-only query enforcement
   - Result size limiting

4. **Query Executor** (`app/executors/sqlite_exec.py`)
   - Safe SQL execution
   - Error handling and timeout protection
   - Performance monitoring

5. **Audit System** (`app/utils/audit.py`)
   - Complete query logging
   - User activity tracking
   - Compliance reporting

## 🛠️ Technology Stack

### Backend
- **Python 3.9+**: Core runtime
- **FastAPI**: High-performance web framework
- **SQLite**: Embedded database
- **SQLGlot**: SQL parsing and validation
- **Pydantic**: Data validation and serialization

### AI & ML
- **LangChain**: LLM orchestration framework
- **Ollama**: Local LLM server
- **sqlcoder7b:latest**: SQL-focused 7B model

### Frontend
- **Streamlit**: Interactive web interface
- **Pandas**: Data manipulation and display

### Development Tools
- **UV**: Fast Python package manager
- **Pytest**: Testing framework
- **Black**: Code formatting
- **Ruff**: Linting and formatting

### Dependencies
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
streamlit>=1.37.0
langchain>=0.2.0
langchain-community>=0.2.0
sqlglot>=23.0.0
pydantic>=2.0.0
python-dotenv>=1.0.0
openai>=1.40.0
pandas>=2.3.2
openpyxl>=3.1.5
langchain-ollama>=0.3.7
```

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- Ollama installed and running locally
- CodeLlama 13B model downloaded

### Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai/download

# Pull the model
ollama pull sqlcoder7b:latest
```

### Install Local Orchestrator
```bash
# Clone the repository
git clone <repository-url>
cd local-orchestrator-final

# Install dependencies using UV (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### Initialize Database
```bash
# Set up the banking database with sample data
python setup/init_db.py
```

## 🚀 Quick Start

### Option 1: Run Both Services (Recommended)
```bash
# Start both frontend and backend
uv run python run_app.py
```

### Option 2: Run Services Separately
```bash
# Terminal 1: Start backend
make run-backend
# or
uv run uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
make run-frontend
# or
uv run streamlit run app/ui/streamlit_app.py --server.port 8501
```

### Option 3: Using Makefile
```bash
# Install dependencies
make install

# Run both services
make run-both

# Run tests
make test

# Clean up
make clean
```

## 📱 Usage

### Web Interface
1. Open your browser and navigate to `http://localhost:8501`
2. Enter your user name and select your role
3. Type your question in natural language
4. Click "Ask" to generate and execute SQL
5. View results, SQL query, and execution details

### API Usage
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me top 5 customers by balance",
    "role": "analyst",
    "user": "john_doe"
  }'
```

### Example Questions
- "Show me all customers with their email addresses"
- "Find all transactions above $1000"
- "List customers and their account balances"
- "Show top 5 customers by total balance"
- "Find all deposits in the last 30 days"
- "Show branch performance by total deposits"

## 🔌 API Reference

### Endpoints

#### POST `/ask`
Convert natural language to SQL and execute the query.

**Request Body:**
```json
{
  "question": "string",
  "role": "string (analyst|viewer|admin)",
  "user": "string"
}
```

**Response:**
```json
{
  "explanation": "string (SQL query)",
  "guard_reason": "string (security validation result)",
  "table": {
    "columns": ["array of column names"],
    "rows": ["array of result rows"],
    "elapsed_sec": "float (execution time)",
    "error": "string (if any)"
  }
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok"
}
```

## 🔒 Security Features

### SQL Injection Prevention
- **Pattern Blocking**: Blocks dangerous SQL keywords (INSERT, UPDATE, DELETE, DROP, etc.)
- **Input Validation**: Comprehensive input sanitization
- **Schema Validation**: Ensures queries only reference existing tables/columns

### Access Control
- **Role-Based Permissions**: Different access levels for different user types
- **Query Restrictions**: Viewers get limited access to sensitive data
- **Audit Trail**: Complete logging of all user activities

### Query Safety
- **Read-Only Enforcement**: Only SELECT queries are allowed
- **Result Limiting**: Automatic LIMIT clauses to prevent large result sets
- **Timeout Protection**: Configurable execution time limits

## 🗄️ Database Schema

### Core Tables

#### `branches`
- Branch information and location
- Manager relationships
- Creation and update timestamps

#### `customers`
- Customer personal information
- Branch associations
- National ID and contact details

#### `employees`
- Employee information and positions
- Branch assignments
- Salary and hire date

#### `accounts`
- Account details and balances
- Customer relationships
- Interest rates and status

#### `transactions`
- Transaction records
- Account and employee associations
- Amount, type, and timestamps

#### `logs`
- Audit trail for all queries
- User, role, and execution details
- Raw and sanitized SQL storage

### Views
- `viewer_customers`: Sanitized customer view for restricted users

## 🧪 Development

### Project Structure
```
app/
├── api/           # FastAPI REST endpoints
├── executors/     # Database execution layer
├── graph/         # Pipeline orchestration
├── guards/        # Security and validation
├── models/        # AI models and SQL generation
├── ui/            # Streamlit web interface
└── utils/         # Shared utilities
```

### Key Development Commands
```bash
# Install development dependencies
uv sync --extra dev

# Run tests with coverage
uv run pytest tests/ --cov=app --cov-report=html

# Format code
uv run black app/ tests/

# Lint code
uv run ruff check app/ tests/

# Type checking
uv run mypy app/
```

### Adding New Features
1. **Enhanced LLM Prompts**: Update prompts in `app/models/sql_agent.py`
2. **Security Rules**: Extend `app/guards/sql_guard.py`
3. **API Endpoints**: Add to `app/api/main.py`
4. **UI Components**: Modify `app/ui/streamlit_app.py`

## 🧪 Testing

### Test Structure
```
tests/
├── unit/          # Unit tests for individual components
├── integration/   # End-to-end API and UI tests
└── conftest.py    # Test configuration and fixtures
```

### Running Tests
```bash
# All tests
uv run pytest

# Specific test category
uv run pytest tests/unit/
uv run pytest tests/integration/

# With coverage
uv run pytest --cov=app --cov-report=html

# Specific test file
uv run pytest tests/unit/test_sql_agent.py
```

### Test Coverage
- **Unit Tests**: Individual component testing
- **Integration Tests**: API and database interaction testing
- **Security Tests**: SQL injection and access control validation
- **Performance Tests**: Query execution time and resource usage

## 🚀 Deployment

### Production Considerations
- **Database**: Consider PostgreSQL for production use
- **Caching**: Implement Redis for better performance
- **Monitoring**: Add Prometheus/Grafana for observability
- **Security**: Enable HTTPS and additional authentication
- **Scaling**: Use multiple worker processes

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000 8501

CMD ["python", "run_app.py"]
```

### Environment Variables
```bash
# API Configuration
API_URL=http://localhost:8000
API_HOST=0.0.0.0
API_PORT=8000

# Database Configuration
DATABASE_URL=sqlite:///app/data.db

# Security Configuration
SECRET_KEY=your-secret-key
DEBUG=false
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain test coverage above 80%
- Use meaningful commit messages

### Testing Requirements
- All new features must have tests
- Maintain or improve test coverage
- Ensure integration tests pass
- Validate security features work correctly

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Adithya Vardhan** - Initial work - [you@example.com](mailto:you@example.com)

## 🙏 Acknowledgments

- **Ollama Team** for local LLM infrastructure
- **LangChain** for AI orchestration framework
- **FastAPI** for high-performance web framework
- **Streamlit** for interactive web interface

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the test cases for usage examples

## 🔄 Version History

- **v0.1.0** - Initial release with core functionality
- **v0.4.0** - Enhanced security and audit features
- **Latest** - Pure LLM-based system with enhanced performance optimizations

---

**⚠️ Important Note**: This system is designed for internal use and development. Ensure proper security measures are in place before deploying to production environments.
