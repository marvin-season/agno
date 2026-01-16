"""
Bug #5 Demo: Mixing agentic filters (dict) with user list filters crashes

This cookbook demonstrates what happens when a user:
1. Enables agentic filtering (which generates dict filters from LLM)
2. Also provides knowledge_filters as a list of FilterExpr

Expected: Should merge filters gracefully or use one type
Actual: Crashes with ValueError
"""

from agno.agent import Agent
from agno.filters import EQ
from agno.knowledge.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.vectordb.pgvector import PgVector

# Step 1: Setup knowledge base
# -----------------------------
vector_db = PgVector(
    table_name="bug5_demo",
    db_url="postgresql+psycopg://ai:ai@localhost:5532/ai",
)

knowledge = Knowledge(
    name="Sales Knowledge Base",
    vector_db=vector_db,
)

# Load sample data with metadata
knowledge.insert(
    text="Q1 2024 North America sales were $1.2M with 15% growth",
    metadata={"region": "north_america", "quarter": "Q1", "year": 2024},
)
knowledge.insert(
    text="Q1 2024 Europe sales were $800K with 10% growth",
    metadata={"region": "europe", "quarter": "Q1", "year": 2024},
)
knowledge.insert(
    text="Q2 2024 North America sales were $1.5M with 20% growth",
    metadata={"region": "north_america", "quarter": "Q2", "year": 2024},
)

# Step 2: Create agent with BOTH agentic filtering AND list filters
# ------------------------------------------------------------------
# User wants:
# - Agentic filtering: LLM extracts filters from query (e.g., "Q1" -> {"quarter": "Q1"})
# - Hard-coded filter: Always restrict to north_america region

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    knowledge=knowledge,
    search_knowledge=True,
    enable_agentic_knowledge_filters=True,  # Generates DICT filters
    debug_mode=True,
)

# Step 3: Make a query with list filters
# --------------------------------------
print("=" * 60)
print("Attempting to combine agentic filters + list filters...")
print("=" * 60)

try:
    # User provides list filters at query time
    # Agentic filtering will generate dict filters from the query
    # When they try to merge -> ValueError!

    agent.print_response(
        "What were Q1 sales?",  # Agentic will extract {"quarter": "Q1"}
        knowledge_filters=[EQ("region", "north_america")],  # User provides LIST
        markdown=True,
    )

    print("\n✅ Success! (Bug is fixed)")

except ValueError as e:
    print(f"\n❌ CRASH! ValueError: {e}")
    print("\nThis is Bug #5 - the agent can't merge dict + list filters")

except Exception as e:
    print(f"\n❌ CRASH! {type(e).__name__}: {e}")
