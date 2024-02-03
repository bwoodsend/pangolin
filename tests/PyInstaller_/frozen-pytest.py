"""
Freeze pytest.main() with pangolin included.
"""
import sys
import pangolin

import pytest

sys.exit(pytest.main(sys.argv[1:] + ["--no-cov", "--tb=native"]))
