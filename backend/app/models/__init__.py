"""
Re-exporta todos os models para que o alembic/env.py
os registre na Base.metadata com um único import.
"""

from app.models.alert import Alert, AlertSeverity, AlertType
from app.models.earthquake import Earthquake
from app.models.volcano import Volcano

__all__ = [
    "Alert",
    "AlertSeverity",
    "AlertType",
    "Earthquake",
    "Volcano",
]
