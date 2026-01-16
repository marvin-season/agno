"""
Bug #5 Simple Demo: Shows the exact failure point

No database required - just demonstrates the filter merge crash.
"""

from agno.filters import EQ
from agno.utils.knowledge import get_agentic_or_user_search_filters

print("=" * 60)
print("Bug #5: Mixing dict + list filters")
print("=" * 60)

# Scenario: User has both types of filters
# -----------------------------------------

# Agentic filtering extracts this from user query "Show Q1 data"
agentic_filters = {"quarter": "Q1", "data_type": "sales"}
print(f"\n1. Agentic filters (dict): {agentic_filters}")

# User provides hard-coded list filters
user_filters = [EQ("region", "north_america")]
print(f"2. User filters (list): {user_filters}")

# The merge function tries to combine them
print("\n3. Attempting to merge...")

try:
    merged = get_agentic_or_user_search_filters(agentic_filters, user_filters)
    print(f"   ✅ Merged filters: {merged}")
except ValueError as e:
    print(f"   ❌ CRASH! ValueError: {e}")
    print("\n" + "=" * 60)
    print("This is Bug #5!")
    print("=" * 60)
    print("""
The function `get_agentic_or_user_search_filters()` raises ValueError
when one filter is dict and the other is list.

This happens inside `_create_search_tool_with_filters()` at lines 3200-3218
and is NOT caught, causing the agent to crash.

FIX: Wrap the merge call in try/except and handle gracefully.
""")
