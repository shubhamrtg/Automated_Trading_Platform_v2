"""Strategy interface, deterministic execution contracts, and signal models."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from engine.core.interfaces.data import Bar


class SignalDirection(StrEnum):
    """Trading signal direction."""

    BUY = "BUY"
    SELL = "SELL"
    FLAT = "FLAT"


class Signal(BaseModel):
    """Signal produced on bar close by a deterministic strategy."""

    timestamp_utc: datetime = Field(
        description="Timestamp of the bar close that produced this signal"
    )
    strategy_name: str
    strategy_version: str
    symbol: str
    direction: SignalDirection
    stop_loss_price: float | None = None
    take_profit_price: float | None = None
    tag: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class StrategyContext(BaseModel):
    """Execution context provided to on_bar. Read-only historical data; zero broker access."""

    symbol: str
    timeframe: str
    bars: list[Bar] = Field(
        description="Completed historical bars in UTC, oldest first. Last element is bar N close."
    )
    current_position_size: float = Field(
        default=0.0, description="Current open lots: >0 for Long, <0 for Short, 0 for Flat"
    )
    account_equity: float = Field(gt=0, description="Current account equity for context")


class Strategy(ABC):
    """Abstract Base Class for all strategy plugins.

    Strategies MUST be deterministic: identical completed bars produce identical signals.
    Strategies NEVER import broker, execution, or risk code.
    """

    name: str
    version: str
    parameters: BaseModel

    @abstractmethod
    def on_bar(self, context: StrategyContext) -> list[Signal]:
        """Process completed bar N and return any generated signals.

        Signals are evaluated at bar close and filled at the next bar's open.
        """
        ...

    @abstractmethod
    def get_warmup_bars(self) -> int:
        """Return the minimum number of completed bars required before generating signals."""
        ...
