"""Instrument specification supporting spot forex, CFDs, and exchange-traded contracts."""

from datetime import datetime, time
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class AssetClass(StrEnum):
    """Asset class category."""

    SPOT_FOREX = "spot_forex"
    EXCHANGE_DERIVATIVE = "exchange_derivative"  # Futures / exchange-traded contracts
    CFD = "cfd"
    COMMODITY = "commodity"


class MarginModel(StrEnum):
    """Margin calculation model."""

    FOREX_LEVERAGED = "forex_leveraged"
    EXCHANGE_SPAN = "exchange_span"
    FLAT_PERCENT = "flat_percent"


class RollRule(StrEnum):
    """Roll rules for expiring exchange-traded contracts."""

    NONE = "none"
    EXPIRY_CLOSE = "expiry_close"
    NEXT_CONTRACT_ROLL = "next_contract_roll"


class TradingSession(BaseModel):
    """Trading session operating window in UTC."""

    day_of_week: int = Field(ge=0, le=6, description="0=Monday, 6=Sunday")
    open_time: time = Field(description="Session opening time in UTC")
    close_time: time = Field(description="Session closing time in UTC")


class InstrumentSpec(BaseModel):
    """Comprehensive instrument specification as pure data.

    Enforces that zero engine, strategy, or risk code hardcodes instrument facts.
    """

    canonical_symbol: str = Field(
        description="Canonical symbol across platform, e.g. XAUUSD, USDINR"
    )
    broker_symbol: str = Field(description="Broker-specific symbol, e.g. GOLD.m, USDINR26OCTFUT")
    asset_class: AssetClass = Field(default=AssetClass.SPOT_FOREX)

    # Contract & Lot sizes
    contract_size: float = Field(
        gt=0, description="Number of units per standard lot, e.g. 100,000 for FX, 100 for gold"
    )
    lot_min: float = Field(gt=0, description="Minimum allowable order lot size, e.g. 0.01")
    lot_max: float = Field(gt=0, description="Maximum allowable order lot size, e.g. 100.0")
    lot_step: float = Field(gt=0, description="Lot increment step, e.g. 0.01")

    # Tick and Pip measurements
    tick_size: float = Field(gt=0, description="Minimum price movement increment")
    tick_value: float = Field(
        gt=0, description="Value of 1 tick per contract in quote/settlement currency"
    )
    pip_size: float = Field(
        gt=0, description="Pip size reference, e.g. 0.0001 for EURUSD, 0.01 for XAUUSD/USDJPY"
    )

    # Currency and conversion
    quote_currency: str = Field(description="Currency that price is quoted in, e.g. USD, JPY, INR")
    settlement_currency: str = Field(default="USD", description="Currency that P&L settles in")
    conversion_path: list[str] = Field(
        default_factory=list,
        description="Path of pair symbols needed to convert quote/tick value to account currency",
    )

    # Margin and Costs
    margin_model: MarginModel = Field(default=MarginModel.FOREX_LEVERAGED)
    margin_requirement: float = Field(
        gt=0, description="Base initial margin requirement, e.g. 0.01 for 100:1 leverage"
    )

    # Trading Sessions in UTC
    sessions: list[TradingSession] = Field(default_factory=list)

    # Exchange-Traded Specific Fields (FR-INS-1, DECISIONS D9)
    expiry_date: datetime | None = Field(
        default=None, description="Contract expiration datetime in UTC for futures"
    )
    roll_rule: RollRule = Field(default=RollRule.NONE)
    exchange_calendar: str | None = Field(
        default=None, description="Identifier for exchange calendar, e.g. NSE, CME"
    )

    @field_validator("lot_max")
    @classmethod
    def validate_lot_bounds(cls, v: float, info: object) -> float:
        # Pydantic v2 validation
        data = getattr(info, "data", {})
        lot_min = data.get("lot_min")
        if lot_min is not None and v < lot_min:
            raise ValueError(f"lot_max ({v}) cannot be less than lot_min ({lot_min})")
        return v
