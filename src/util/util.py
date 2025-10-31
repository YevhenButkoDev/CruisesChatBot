# This module is kept for backward compatibility
# New utility functions are organized in specific modules:
# - date_utils.py for date-related utilities
# - cruise_utils.py for cruise-related utilities
# - agent_utils.py for agent-related utilities

from .date_utils import validate_and_correct_date_range

__all__ = ['validate_and_correct_date_range']
