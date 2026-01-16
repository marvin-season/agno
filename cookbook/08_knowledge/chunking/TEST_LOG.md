# Chunking Cookbook Test Log

## Test Session: 2026-01-16

### csv_row_chunking.py

**Status:** PASS

**Description:** Tests row-based chunking for CSV data where each row becomes a separate document/chunk. Uses IMDB movie dataset.

**Result:** Successfully loaded 1,001 movie records in batches of 100. Agent correctly answered query about "Guardians of the Galaxy" with accurate movie details (director, cast, rating, revenue).

---

### recursive_chunking.py

**Status:** PASS

**Description:** Tests text-based splitting using hierarchy of separators (paragraphs, lines, sentences, spaces). Uses Thai Recipes PDF.

**Result:** Created 14 chunks (one per PDF page). Agent returned 2 complete Thai curry recipes (Massaman and Green Curry) with full ingredients and directions.

---

### document_chunking.py

**Status:** PASS

**Description:** Tests keeping each document as a single chunk with no splitting. Uses Thai Recipes PDF.

**Result:** Created 14 chunks (one per PDF page). Agent returned Massaman Curry recipe with tips. Note: With PDFReader, each page is treated as a document, so chunk count matches page count.

---

### agentic_chunking.py

**Status:** PASS

**Description:** Tests LLM-powered chunking that identifies semantic boundaries. Makes API calls during chunking (higher cost but better quality). Uses Thai Recipes PDF.

**Result:** Created 14 chunks (one per PDF page). Agent returned 2 recipes with tips. Note: For this PDF where each page is naturally one recipe, all chunking strategies produce similar results.

---

## Observations

All four cookbooks passed successfully. Notable finding: The Thai Recipes PDF produces 14 chunks across all three PDF-based strategies because PDFReader treats each page as a separate document, and each page is already a complete recipe (naturally chunked by the PDF structure). A denser document would better showcase the differences between chunking strategies.
