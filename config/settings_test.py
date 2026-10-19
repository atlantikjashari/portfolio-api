"""Test settings: production-like (DEBUG=False) with a throwaway secret key."""
import os

os.environ.setdefault("SECRET_KEY", "test-only-secret-key-that-is-long-enough-for-hs256")

from .settings import *  # noqa: E402,F403
