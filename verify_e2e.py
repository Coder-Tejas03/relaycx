#!/usr/bin/env python3
"""
Root-level runner for Live End-to-End verification suite.
Delegates to backend/tests/test_phase9_live_e2e.py with proper sys.path resolution.
Tests against the live running server at http://localhost:8000.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
TESTS_DIR = os.path.join(BACKEND_DIR, "tests")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

os.chdir(BACKEND_DIR)

from test_phase9_live_e2e import run_live_e2e_verification

if __name__ == "__main__":
    run_live_e2e_verification()
