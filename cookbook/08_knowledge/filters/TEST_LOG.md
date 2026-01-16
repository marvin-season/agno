# Filters Cookbook Test Log

## Test Session: 2026-01-16

### filtering.py

**Status:** PASS

**Description:** Basic per-query filtering using dict filters. Loads 4 CSV files with different metadata (sales, survey, financial data), then queries with filters like `{"region": "north_america", "data_type": "sales"}`.

**Result:** Found 10 documents, agent correctly reported Q1 2024 North America sales data with revenue breakdown by product category.

---

### filtering_defaults_on_agent.py

**Status:** PASS

**Description:** Sets default filters at Agent initialization level using `knowledge_filters` parameter. All queries automatically get filtered without specifying per-query.

**Result:** Found 5 documents (due to max_results=5). Response correctly scoped to "Q1 2024 North America" data.

---

### agentic_filtering.py

**Status:** PASS

**Description:** Enables `enable_agentic_knowledge_filters=True` so the LLM extracts filters from natural language queries automatically.

**Result:** LLM correctly extracted `{'region': 'north_america'}` from query "...in the region north_america". Found 10 documents with correct regional filtering. Response time was 47.3s (includes LLM filter extraction).

---

### async_filtering.py

**Status:** PASS

**Description:** Demonstrates async knowledge operations with both dict filters and FilterExpr list filters. Uses CV documents (DOCX files).

**Result:** Both query types worked correctly. Dict filter `{"user_id": "jordan_mitchell"}` and list filter `[IN("user_id", ["jordan_mitchell"])]` both returned 1 document with Jordan Mitchell's CV data.

---

### filtering_with_conditions_on_agent.py

**Status:** PASS

**Description:** Demonstrates complex filter expressions using IN, NOT, and AND operators.

**Result:**
- IN operator: Returned North America data correctly
- NOT operator: Returned Europe data (excluded North America)
- AND operator: Returned Europe sales data (sales AND NOT North America)

---

### filtering_with_invalid_keys.py

**Status:** PASS

**Description:** Uses LanceDB to demonstrate behavior when invalid filter keys are provided (e.g., "location" instead of "region").

**Result:** Found 0 documents as expected. Agent responded gracefully asking for more context rather than crashing. This is intentional behavior demonstrating graceful handling of invalid filters.

---

### bug5_demo.py & bug5_simple_demo.py

**Status:** N/A (Debug scripts)

**Description:** Debug scripts for Bug #5 - crash when mixing dict filters (from agentic filtering) with list filters (from user). These are untracked debugging files.

**Result:** Bug confirmed present - ValueError when merging dict + list filters. These files document the issue for future fix.

---

## Summary

All production cookbooks in the filters folder pass successfully. The bug demo files document a known issue (Bug #5) with mixing filter types that is under investigation.

Key patterns demonstrated:
- Dict filters: `{"region": "north_america"}`
- List filters: `[IN("region", ["north_america"])]`
- Complex expressions: `AND(EQ("key", "value"), NOT(EQ("key2", "value2")))`
- Agentic filtering: LLM extracts filters from natural language
