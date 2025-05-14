#!/usr/bin/env python3
"""
Script to initialize the database for DocuAgent.

This script creates the database tables and populates them with initial data.
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt

# Add the parent directory to the path so we can import from app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.session import Base, engine
from app.models.user import User
from app.models.template import Template


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("init_db")


def init_db():
    """Initialize the database."""
    logger.info(f"Initializing database at {settings.SQLALCHEMY_DATABASE_URI}")

    # Create tables
    Base.metadata.create_all(engine)
    logger.info("Created tables")

    # Create session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Create default user if it doesn't exist
        default_user = db.query(User).filter(User.username == "admin").first()
        if not default_user:
            # Hash password
            password = "password"
            password_hash = bcrypt.hashpw(
                password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            default_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=password_hash,
                api_key="dev_api_key",
            )
            db.add(default_user)
            db.commit()
            db.refresh(default_user)
            logger.info("Created default user")

        # Create default template if it doesn't exist
        default_template = db.query(Template).filter(
            Template.template_id == "template_invoice_standard"
        ).first()
        if not default_template:
            default_template = Template(
                template_id="template_invoice_standard",
                user_id=default_user.id,
                name="Standard Invoice",
                description="Template for standard invoices",
                document_type="invoice",
                fields={
                    "invoice_number": {
                        "type": "string",
                        "required": True,
                        "extraction_hints": ["Invoice Number", "Invoice #", "Invoice No"]
                    },
                    "date": {
                        "type": "date",
                        "required": True,
                        "extraction_hints": ["Date", "Invoice Date"]
                    },
                    "total_amount": {
                        "type": "currency",
                        "required": True,
                        "extraction_hints": ["Total", "Amount Due", "Total Due"]
                    },
                    "line_items": {
                        "type": "table",
                        "required": False,
                        "columns": [
                            {"name": "description", "type": "string"},
                            {"name": "quantity", "type": "number"},
                            {"name": "unit_price", "type": "currency"},
                            {"name": "total", "type": "currency"}
                        ]
                    }
                },
            )
            db.add(default_template)
            db.commit()
            logger.info("Created default template")

        logger.info("Database initialization complete")

    finally:
        db.close()


def main():
    """Main function."""
    try:
        init_db()
        return 0
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
