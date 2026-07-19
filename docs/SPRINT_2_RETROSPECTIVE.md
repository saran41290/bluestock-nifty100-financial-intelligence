
# Sprint 2 Retrospective

**Project:** Nifty100 Financial Analytics Platform

**Sprint:** Sprint 2 – Financial Ratio Engine

**Duration:** Day 08 – Day 14

**Status:** ✅ Completed

---

# Sprint Goal

Develop a robust Financial Ratio Engine capable of calculating key financial KPIs for every company and every financial year, while handling real-world financial edge cases and maintaining production-quality code.

---

# Objectives

The sprint focused on:

- Building a reusable financial ratio calculation engine
- Supporting multiple financial statement datasets
- Handling incomplete and inconsistent financial data
- Producing analytics-ready datasets
- Maintaining high unit test coverage
- Preparing the project for dashboard integration

---

# Features Implemented

## Profitability Ratios

Implemented:

- Net Profit Margin
- Operating Profit Margin
- Return on Equity (ROE)
- Return on Assets (ROA)
- Return on Capital Employed (ROCE)

Features:

- Zero division protection
- Negative equity handling
- Financial sector compatibility
- Standardized result objects

---

## Leverage Ratios

Implemented:

- Debt-to-Equity Ratio
- Interest Coverage Ratio
- Asset Turnover Ratio
- Net Debt

Features:

- Debt-free company detection
- Negative equity handling
- Zero asset protection
- Risk classification

---

## CAGR Engine

Implemented:

- Revenue CAGR
- PAT CAGR
- EPS CAGR

Supported Periods:

- 3 Year
- 5 Year
- 10 Year

Edge Cases Handled:

- Positive → Positive
- Positive → Loss
- Loss → Profit
- Loss → Loss
- Zero Base
- Insufficient History

---

## Cash Flow KPIs

Implemented:

- Free Cash Flow
- CFO Quality Score
- CapEx Intensity
- FCF Conversion
- Capital Allocation Pattern

Capital Allocation Classification:

- Reinvestor
- Shareholder Returns
- Growth Funded by Debt
- Cash Accumulator
- Liquidating Assets
- Distress Signal
- Mixed
- Pre-Revenue

---

## SQLite Integration

Implemented:

- Financial ratio persistence
- Dynamic UPSERT support
- Automatic schema compatibility
- Bulk insertion workflow

Generated approximately:

- 995 Financial Ratio Records

---

## Validation

Implemented validations for:

- Missing financial values
- Zero denominators
- Invalid CAGR periods
- Negative financial scenarios
- Missing historical records
- Invalid ratios

---

# Testing

Implemented comprehensive pytest-based unit tests.

## Profitability

- 10 Tests
- All Passed

## Leverage

- 12 Tests
- All Passed

## CAGR

- 10 Tests
- All Passed

## Cash Flow

- 19 Tests
- All Passed

---

## Overall Test Summary

| Module          |        Tests |
| --------------- | -----------: |
| Profitability   |           10 |
| Leverage        |           12 |
| CAGR            |           10 |
| Cash Flow       |           19 |
| **Total** | **51** |

Result:

```
51 Passed
0 Failed
```

---

# Challenges Faced

## Financial Data Quality

Issues:

- Missing values
- Null records
- Zero denominators
- Inconsistent reporting periods

Solution:

Created reusable helper methods for:

- Safe numeric conversion
- Percentage calculations
- Rounding
- Validation

---

## CAGR Edge Cases

Challenge:

Traditional CAGR formulas fail when:

- Base value is zero
- Values become negative
- Companies move from loss to profit

Solution:

Introduced flag-based result objects instead of producing mathematically invalid values.

---

## SQLite Integration

Challenge:

Schema evolution caused insertion failures.

Solution:

Implemented dynamic SQL generation with UPSERT support and automatic column handling.

---

# Code Quality Improvements

Implemented:

- Dataclasses for result models
- Type hints throughout the analytics layer
- Reusable helper functions
- Modular architecture
- Static utility methods
- Consistent naming conventions
- Comprehensive inline documentation

---

# Deliverables Completed

- Financial Ratio Engine
- Profitability Module
- Leverage Module
- CAGR Engine
- Cash Flow KPI Engine
- SQLite Integration
- Validation Framework
- Unit Test Suite
- Analytics-ready outputs

---

# Lessons Learned

During this sprint, several important engineering practices were reinforced:

- Financial calculations require robust validation rather than assuming ideal input data.
- Separating calculation logic from persistence improves maintainability and testability.
- Consistent result objects simplify downstream analytics and dashboard integration.
- Comprehensive unit tests help identify API mismatches early and increase confidence during refactoring.
- Handling edge cases explicitly leads to more reliable financial analytics.

---

# Sprint Metrics

| Metric                      | Value |
| --------------------------- | ----: |
| Modules Developed           |     4 |
| Major KPI Categories        |     4 |
| Financial KPIs Implemented  |   15+ |
| Capital Allocation Patterns |     8 |
| Ratio Records Generated     |  ~995 |
| Unit Tests                  |    51 |
| Test Success Rate           |  100% |

---

# Outcome

Sprint 2 successfully delivered a production-ready Financial Ratio Engine capable of generating standardized financial metrics across the available Nifty100 datasets.

The analytics layer is modular, well-tested, resilient to real-world financial data inconsistencies, and ready for downstream reporting and dashboard development.

---

# Next Sprint

Sprint 3 will focus on:

- Dashboard dataset generation
- Business analytics views
- Power BI integration
- Financial insights
- Executive dashboards
- End-to-end reporting pipeline
