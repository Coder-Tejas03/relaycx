#!/usr/bin/env python3
"""
Root-level runner for Phase 2 verification suite.
Delegates to backend/tests/verify_phase2.py with proper sys.path resolution.
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

from verify_phase2 import run_phase2_verification

if __name__ == "__main__":
    run_phase2_verification()
