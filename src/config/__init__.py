"""
Configuration package - Multi-market configuration
"""
from .base_config import BaseConfig, TechnicalParams
from .india_config import IndiaConfig, BTSTCriteria, SwingCriteria, BTST_EXCLUDED_SECTORS, SWING_PREFERRED_SECTORS
from .australia_config import AustraliaConfig, AustraliaSwingCriteria

__all__ = [
    'BaseConfig',
    'TechnicalParams',
    'IndiaConfig',
    'BTSTCriteria',
    'SwingCriteria',
    'BTST_EXCLUDED_SECTORS',
    'SWING_PREFERRED_SECTORS',
    'AustraliaConfig',
    'AustraliaSwingCriteria'
]
