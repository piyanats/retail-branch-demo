# app/config.py

import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""

    # ========================================================================
    # Google Cloud Platform
    # ========================================================================
    PROJECT_ID: str = os.getenv("PROJECT_ID", "")
    DATASET_ID: str = os.getenv("DATASET_ID", "retail_branches")
    GCS_BUCKET: str = os.getenv("GCS_BUCKET", "")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    BIGQUERY_LOCATION: str = os.getenv("BIGQUERY_LOCATION", "asia-southeast1")

    # ========================================================================
    # Google OAuth 2.0
    # ========================================================================
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    OAUTH_REDIRECT_URI: str = os.getenv(
        "OAUTH_REDIRECT_URI",
        "http://localhost:8000/auth/callback"
    )

    # ========================================================================
    # Session Management
    # ========================================================================
    SESSION_SECRET: str = os.getenv("SESSION_SECRET", "")
    SESSION_MAX_AGE: int = int(os.getenv("SESSION_MAX_AGE", "86400"))

    # ========================================================================
    # Email Service
    # ========================================================================
    SENDGRID_API_KEY: str = os.getenv("SENDGRID_API_KEY", "")
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@retailbranch.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "Retail Branch System")
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true"

    # ========================================================================
    # Application Settings
    # ========================================================================
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    APP_NAME: str = os.getenv("APP_NAME", "Retail Branch Management System")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # ========================================================================
    # Security Settings
    # ========================================================================
    ALLOWED_EMAIL_DOMAINS: List[str] = os.getenv(
        "ALLOWED_EMAIL_DOMAINS", ""
    ).split(",") if os.getenv("ALLOWED_EMAIL_DOMAINS") else []

    ENABLE_RATE_LIMITING: bool = os.getenv("ENABLE_RATE_LIMITING", "true").lower() == "true"
    RATE_LIMIT_REQUESTS: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    # ========================================================================
    # Notification Settings
    # ========================================================================
    NOTIFICATION_TIMEZONE: str = os.getenv("NOTIFICATION_TIMEZONE", "Asia/Bangkok")

    # ========================================================================
    # File Upload Settings
    # ========================================================================
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10 MB
    ALLOWED_FILE_TYPES: List[str] = os.getenv(
        "ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png,xlsx"
    ).split(",")

    # ========================================================================
    # Logging Settings
    # ========================================================================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ========================================================================
    # Computed Properties
    # ========================================================================
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    # ========================================================================
    # Validation
    # ========================================================================
    def validate(self):
        """Validate required settings"""
        required_settings = [
            "PROJECT_ID",
            "GOOGLE_CLIENT_ID",
            "GOOGLE_CLIENT_SECRET",
            "SESSION_SECRET",
        ]

        missing = [s for s in required_settings if not getattr(self, s)]

        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Validate SESSION_SECRET length
        if len(self.SESSION_SECRET) < 32:
            raise ValueError("SESSION_SECRET must be at least 32 characters long")

# Initialize settings
settings = Settings()

# Validate settings on startup (production only)
if settings.is_production:
    settings.validate()
