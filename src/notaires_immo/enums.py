"""Enumerations for API coded values.

All enums use ``_missing_`` to tolerate unknown codes gracefully — an unknown code
returns an enum member whose value is the raw string, rather than raising ValueError.
This means the library stays usable if the API adds new codes before this package is
updated.  Check ``member.name.startswith("UNKNOWN")`` to detect unrecognised values.
"""

from __future__ import annotations

from enum import Enum


class PropertyType(str, Enum):
    """``typeBiens`` codes (confirmed empirically, 2026-06-29)."""

    MAISON = "MAI"
    APPARTEMENT = "APP"
    TERRAIN = "TER"
    IMMEUBLE = "IMM"
    GARAGE = "GAR"
    DIVERS = "DIV"

    @classmethod
    def _missing_(cls, value: object) -> "PropertyType":
        obj = str.__new__(cls, str(value))
        obj._value_ = str(value)
        obj._name_ = f"UNKNOWN({value})"
        return obj


class TransactionType(str, Enum):
    """``typeTransactions`` codes."""

    VENTE = "VENTE"
    VNI = "VNI"      # Vente notariale interactive
    VAE = "VAE"      # Vente aux enchères (auction)
    LOCATION = "LOCATION"

    @classmethod
    def _missing_(cls, value: object) -> "TransactionType":
        obj = str.__new__(cls, str(value))
        obj._value_ = str(value)
        obj._name_ = f"UNKNOWN({value})"
        return obj


class TernaryFlag(str, Enum):
    """Three-state boolean used throughout the API.

    The API never returns plain ``true``/``false`` for feature flags; it always uses
    this ternary.  Treat ``INCONNU`` as "unknown / not provided", never as ``False``.
    """

    OUI = "OUI"
    NON = "NON"
    INCONNU = "INCONNU"

    @classmethod
    def _missing_(cls, value: object) -> "TernaryFlag":
        obj = str.__new__(cls, str(value))
        obj._value_ = str(value)
        obj._name_ = f"UNKNOWN({value})"
        return obj

    @property
    def is_yes(self) -> bool:
        return self is TernaryFlag.OUI

    @property
    def is_no(self) -> bool:
        return self is TernaryFlag.NON

    @property
    def is_known(self) -> bool:
        return self is not TernaryFlag.INCONNU


class DpeClass(str, Enum):
    """Energy or GES class (A–G) as used in DPE ratings."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"

    @classmethod
    def _missing_(cls, value: object) -> "DpeClass":
        obj = str.__new__(cls, str(value))
        obj._value_ = str(value)
        obj._name_ = f"UNKNOWN({value})"
        return obj
