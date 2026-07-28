"""
Test Python file for CodeSlim GitHub PR Bot live audit verification.
Contains unused dead imports (sys, os, math, re) to test automatic cleanup.
"""

import sys
import os
import math
import re

def calculate_doubled_value(value: int) -> int:
    """Calculate doubled integer value."""
    return value * 2
