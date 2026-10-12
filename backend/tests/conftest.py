"""Runs before any test module is imported.

Environment variables override backend/.env, so these values guarantee that
tests never use real credentials or a real database, never call a real AI
service, and are not affected by rate limits or local configuration.
"""

import os

os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["ENVIRONMENT"] = "development"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"
os.environ["DATABASE_URL"] = "postgresql+psycopg://test:test@localhost:5432/test"
os.environ["SUPABASE_URL"] = "https://test-project.supabase.co"
os.environ["SUPABASE_SECRET_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""