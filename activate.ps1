# Quick Start Helper for Windows PowerShell

# Activate virtual environment
.\ask-your-data-env\Scripts\activate

Write-Host "✓ Virtual environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Available commands:" -ForegroundColor Cyan
Write-Host "  python verify_installs.py          - Verify all dependencies"
Write-Host "  pytest tests/ -v                   - Run tests (when available)"
Write-Host "  streamlit run src/ui/app.py        - Start Streamlit UI"
Write-Host "  uvicorn src.api.main:app --reload  - Start FastAPI backend"
Write-Host ""
Write-Host "📂 Current Sprint: Sprint 1 - Foundation" -ForegroundColor Yellow
Write-Host "✅ Ticket 1: Environment Setup (COMPLETE)"
Write-Host "⏳ Ticket 2: Data Ingestion (NEXT)"
Write-Host ""
