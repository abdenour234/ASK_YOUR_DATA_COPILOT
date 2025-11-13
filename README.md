# Ask Your Data — Intelligent BI Copilot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent Natural Language to SQL copilot that interprets queries, generates SQL, executes on DuckDB, and produces interactive visualizations with narrative insights.

## 🎯 Project Goals

- **Natural Language Understanding**: Parse user questions using Llama 3.1 (Ollama)
- **Smart SQL Generation**: Convert intents to safe, parameterized SQL queries
- **Fast Analytics**: Execute on DuckDB with dbt-managed transformations
- **Interactive Visualization**: Auto-recommend Plotly charts with AI-generated narratives
- **RAG-Enhanced Context**: FAISS-powered glossary lookup for domain-specific terms

## 🏗️ Architecture

```
User Query → Intent Parser → RAG Glossary → SQL Generator → DuckDB
                                                              ↓
                                            Streamlit UI ← Chart Recommender
```

**Tech Stack**:
- **Database**: DuckDB (in-memory analytics)
- **Transformations**: dbt-core with dbt-duckdb adapter
- **NLP**: Llama 3.1 via Ollama
- **RAG**: FAISS vector search
- **API**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Visualization**: Plotly

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- Ollama (for Llama 3.1) — [Install Guide](https://ollama.ai/)

### Installation

```powershell
# Clone the repository
git clone https://github.com/yourusername/ask-your-data-copilot.git
cd ask-your-data-copilot

# Create virtual environment
python -m venv ask-your-data-env
.\ask-your-data-env\Scripts\activate  # Windows
# source ask-your-data-env/bin/activate  # Unix/Mac

# Install dependencies
pip install -r requirements.txt

# Verify installation
python verify_installs.py
```

### Initial Setup

```powershell
# Download Olist dataset (Sprint 1 - Ticket 2)
# Place CSVs in data/raw/

# Run dbt transformations
cd dbt
dbt deps
dbt run
dbt test

# Build RAG glossary index
python glossary/build_index.py
```

### Running the Application

```powershell
# Start Streamlit UI
streamlit run src/ui/app.py

# In separate terminal, start FastAPI backend
uvicorn src.api.main:app --reload --port 8000
```

Visit `http://localhost:8501` for the Streamlit interface.

## 📁 Project Structure

```
ask_your_data/
├── data/                    # Raw & processed datasets
│   ├── raw/                 # Olist CSVs
│   └── processed/           # DuckDB files
├── dbt/                     # dbt project
│   ├── models/              # SQL models
│   │   ├── staging/         # Raw data staging
│   │   └── marts/           # Business logic layer
│   ├── tests/               # Data quality tests
│   └── dbt_project.yml      # dbt configuration
├── glossary/                # RAG glossary
│   ├── business_terms.yaml  # Domain vocabulary
│   ├── build_index.py       # FAISS index builder
│   └── index.faiss          # Vector index (generated)
├── src/
│   ├── ingest/              # Data ingestion
│   ├── nlp/                 # NL parsing & intents
│   ├── sql/                 # SQL generation & safety
│   ├── charts/              # Chart recommendations
│   ├── api/                 # FastAPI routes
│   └── ui/                  # Streamlit app
├── tests/                   # Unit & integration tests
├── .github/
│   └── copilot-instructions.md  # AI coding guidelines
├── Dockerfile               # Production deployment
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧩 Development Sprints

**Sprint 1 — Foundation** (Tickets 1-4)
- ✅ Environment setup & dependency installation
- ⏳ Data ingestion (Olist → DuckDB)
- ⏳ dbt transformations
- ⏳ RAG glossary with FAISS

**Sprint 2 — Core Features** (Tickets 5-8)
- ⏳ NL intent parsing (Llama 3.1)
- ⏳ SQL generation & execution
- ⏳ Chart recommendation + narratives
- ⏳ Streamlit UI integration

**Sprint 3 — Production** (Tickets 9-12)
- ⏳ Unit testing & evaluation
- ⏳ Performance optimization
- ⏳ Dockerization
- ⏳ Documentation & demo

## 🧪 Testing

```powershell
# Run all tests
pytest tests/

# With coverage report
pytest --cov=src tests/

# Specific test module
pytest tests/test_sql_generation.py -v
```

## 📊 Dataset

**Olist Brazilian E-Commerce** (Kaggle):
- 100k orders (2016-2018)
- Customer, product, seller, payment, review data
- Geolocation information

Tables ingested: `orders`, `customers`, `products`, `sellers`, `order_items`, `payments`, `reviews`

## 🔐 Security

- **SQL Injection Prevention**: Parameterized queries only (no string interpolation)
- **Query Validation**: Block DDL/DML operations (DROP, DELETE, UPDATE)
- **Read-Only Mode**: DuckDB connection limited to SELECT statements

## 🐳 Docker Deployment

```powershell
# Build image
docker build -t ask-your-data:latest .

# Run container
docker run -p 8501:8501 -p 8000:8000 ask-your-data:latest
```

## 🤝 Contributing

See `.github/copilot-instructions.md` for AI-assisted development guidelines.

**Development Workflow**:
1. Activate virtual environment
2. Check out new branch for ticket
3. Follow sprint/ticket sequence
4. Add tests for new features
5. Update documentation

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Dataset**: Olist Brazilian E-Commerce (Kaggle)
- **LLM**: Llama 3.1 (Meta AI) via Ollama
- **Tools**: DuckDB, dbt Labs, Streamlit, FastAPI

---

**Status**: Sprint 1 in progress (Environment setup complete ✅)

For detailed AI coding guidelines, see [.github/copilot-instructions.md](.github/copilot-instructions.md)
