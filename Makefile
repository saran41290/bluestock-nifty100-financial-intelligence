# Nifty 100 Financial Intelligence Platform Makefile

.PHONY: load ratios test report dashboard api clean

PYTHON = python
PYTEST = pytest

load:
	$(PYTHON) scripts/load_database.py

ratios:
	$(PYTHON) -m src.analytics.ratio_engine

test:
	$(PYTEST) --html=reports/pytest_report.html --self-contained-html

report:
	$(PYTHON) -m src.reports.tearsheet
	$(PYTHON) -m src.reports.sector_report
	$(PYTHON) -m src.reports.portfolio_summary

dashboard:
	streamlit run src/dashboard/app.py

api:
	uvicorn src.api.main:app --reload --port 8000

clean:
	powershell -Command "Get-ChildItem -Path . -Include __pycache__, *.pyc, .pytest_cache -Recurse -Force | Remove-Item -Recurse -Force"
