"""
Models Package
Contains SQLAlchemy ORM models for database tables.

All models are imported here for easy access and to ensure
they are registered with SQLAlchemy before migrations.
"""

from backend.models.user import User
from backend.models.resource import Resource
from backend.models.booking import Booking
from backend.models.message import Message
from backend.models.review import Review

# Export all models
__all__ = [
    'User',
    'Resource',
    'Booking',
    'Message',
    'Review',
]
