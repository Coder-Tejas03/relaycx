#!/usr/bin/env python3
"""
Root-level runner for Phase 1 verification suite (updated for Phase 2 structured references).
Delegates to backend/tests/verify_phase1.py with proper sys.path resolution.
"""

import os
import sys

# Ensure backend directory is on sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
TESTS_DIR = os.path.join(BACKEND_DIR, "tests")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)
if TESTS_DIR not in sys.path:
    sys.path.insert(0, TESTS_DIR)

# Change CWD to backend so relative paths work cleanly
os.chdir(BACKEND_DIR)

from verify_phase1 import run_verification

if __name__ == "__main__":
    run_verification()
