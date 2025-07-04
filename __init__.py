"""
ScriptSynthCore - A full-spectrum blockchain API toolkit
by Commander Zkaedi
"""

__version__ = "0.1.0"
__author__ = "Commander Zkaedi (iDeaKz)"

from .core import compute_heavy, BlockchainAPI, SolidityHandler
from .utils import vector_embedding_optimizer, checkpoint_system

__all__ = [
    "compute_heavy",
    "BlockchainAPI", 
    "SolidityHandler",
    "vector_embedding_optimizer",
    "checkpoint_system"
] 