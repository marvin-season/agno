"""Tests to verify potential bugs in Knowledge Protocol implementation."""

from typing import Set
from unittest.mock import MagicMock, patch

import pytest

from agno.filters import EQ
from agno.knowledge.document import Document


class TestBug1ValidateFiltersTypeMismatch:
    """Bug #1: _validate_filters() returns original list instead of validated valid_filters."""

    @pytest.fixture
    def knowledge(self):
        """Create Knowledge instance."""
        from agno.knowledge.knowledge import Knowledge

        return Knowledge()

    def test_validate_filters_with_dict_removes_invalid(self, knowledge):
        """Dict filters should have invalid keys removed."""
        filters = {"region": "us", "invalid_key": "value"}
        valid_metadata: Set[str] = {"region", "year"}

        valid, invalid = knowledge._validate_filters(filters, valid_metadata)

        assert isinstance(valid, dict), "Should return dict for dict input"
        assert "region" in valid, "Valid key should be kept"
        assert "invalid_key" not in valid, "Invalid key should be removed"
        assert "invalid_key" in invalid, "Invalid key should be in invalid list"

    def test_validate_filters_with_list_removes_invalid(self, knowledge):
        """List filters should have invalid items removed."""
        filters = [
            EQ("region", "us"),
            EQ("invalid_key", "value"),
        ]
        valid_metadata: Set[str] = {"region", "year"}

        valid, invalid = knowledge._validate_filters(filters, valid_metadata)

        # BUG #1: Code returns original `filters` list, not filtered `valid_filters`
        assert isinstance(valid, list), "Should return list for list input"
        valid_keys = [f.key for f in valid]
        assert "region" in valid_keys, "Valid key should be kept"
        # This assertion will FAIL if bug exists - invalid key not removed
        assert "invalid_key" not in valid_keys, "Invalid filter should be removed from list"


class TestBug3TimerNotProtected:
    """Bug #3: Timer not protected from exceptions in search tools - FIXED."""

    def test_search_tool_handles_exception_gracefully(self):
        """Search tool catches exceptions and returns error message."""
        from agno.knowledge.knowledge import Knowledge

        knowledge = Knowledge()
        knowledge.vector_db = MagicMock()
        knowledge.search = MagicMock(side_effect=Exception("Search failed"))

        tool = knowledge._create_search_tool(async_mode=False)

        # Exception should be caught, not propagated
        result = tool.entrypoint(query="test query")

        assert isinstance(result, str)
        assert "error" in result.lower()
        assert "Search failed" in result

    def test_search_tool_with_filters_handles_exception(self):
        """Search tool with filters catches exceptions and returns error message."""
        from agno.knowledge.knowledge import Knowledge

        knowledge = Knowledge()
        knowledge.vector_db = MagicMock()
        knowledge.search = MagicMock(side_effect=Exception("Database connection failed"))

        tool = knowledge._create_search_tool_with_filters(async_mode=False)

        # Exception should be caught, not propagated
        result = tool.entrypoint(query="test query")

        assert isinstance(result, str)
        assert "error" in result.lower()
        assert "Database connection failed" in result


class TestBug5FilterMergeError:
    """Bug #5: Missing error handling when merging dict and list filters."""

    def test_merge_dict_and_list_filters_raises_valueerror(self):
        """Merging dict filters with list filters should raise ValueError."""
        from agno.utils.knowledge import get_agentic_or_user_search_filters

        agentic_filters = {"region": "us"}  # Dict from agentic filtering
        user_filters = [EQ("year", 2024)]  # List from user

        # This raises ValueError - confirming the incompatibility exists
        with pytest.raises(ValueError):
            get_agentic_or_user_search_filters(agentic_filters, user_filters)


class TestBug8SilentFilterLoss:
    """Bug #8: Invalid filter objects are silently ignored."""

    def test_invalid_filter_type_silently_dropped(self):
        """Invalid filter objects are dropped without warning."""
        from agno.knowledge.knowledge import Knowledge

        knowledge = Knowledge()
        knowledge.vector_db = MagicMock()
        knowledge.search = MagicMock(return_value=[Document(content="test doc", name="doc1")])

        tool = knowledge._create_search_tool_with_filters(async_mode=False)

        # Create an invalid filter object (not dict, not FilterExpr)
        class InvalidFilter:
            def __init__(self):
                self.something = "invalid"

        invalid_filter = InvalidFilter()

        # The search tool processes filters in lines 3204-3208:
        #   if isinstance(filt, dict): filters_dict.update(filt)
        #   elif hasattr(filt, "key") and hasattr(filt, "value"): ...
        #   # No else clause - silently skipped!

        with patch("agno.knowledge.knowledge.log_warning") as mock_warn:
            # Pass mix of valid and invalid filters
            tool.entrypoint(query="test", filters=[{"valid": "filter"}, invalid_filter])

            # BUG #8: No warning logged for invalid filter
            # After fix, should log warning
            # Currently this will show bug exists (no warning called)
            warning_calls = [
                call
                for call in mock_warn.call_args_list
                if "invalid" in str(call).lower() or "skip" in str(call).lower()
            ]

            if not warning_calls:
                pytest.xfail("Bug #8: Invalid filters silently dropped without warning")


class TestBugConfirmation:
    """Summary tests to confirm bug fixes work."""

    def test_bug3_fixed_exception_handled(self):
        """Confirm Bug #3 is fixed - search exceptions return error message."""
        from agno.knowledge.knowledge import Knowledge

        knowledge = Knowledge()
        knowledge.vector_db = MagicMock()
        knowledge.search = MagicMock(side_effect=RuntimeError("DB Error"))

        tool = knowledge._create_search_tool(async_mode=False)

        # Exception should NOT propagate - should return error string
        result = tool.entrypoint(query="test")

        assert isinstance(result, str)
        assert "DB Error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
