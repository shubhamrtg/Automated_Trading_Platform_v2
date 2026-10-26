"""Market data models and data feed interfaces."""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from engine.core.interfaces.instrument import InstrumentSpec


class Timeframe(StrEnum):
    """Standard trading timeframes."""

    M1 = "M1"
    M5 = "M5"
    M15 = "M15"
    M30 = "M30"
    H1 = "H1"
    H4 = "H4"
    D1 = "D1"


class Bar(BaseModel):
    """Single completed OHLCV bar with spread data."""

    timestamp_utc: datetime = Field(description="Bar open timestamp strictly in UTC")
    open: float = Field(gt=0)
    high: float = Field(gt=0)
    low: float = Field(gt=0)
    close: float = Field(gt=0)
    volume: float = Field(ge=0, default=0.0)
    spread: float = Field(
        ge=0, default=0.0, description="Average or closing spread in instrument points"
    )


class MarketDataFeed(ABC):
    """Abstract interface for historical and live market data ingestion."""

    @abstractmethod
    async def get_historical_bars(
        self,
        symbol: str,
        timeframe: Timeframe,
        start_utc: datetime,
        end_utc: datetime,
    ) -> list[Bar]:
        """Fetch historical bars within the given UTC datetime range."""
        ...

    @abstractmethod
    async def get_latest_completed_bar(self, symbol: str, timeframe: Timeframe) -> Bar:
        """Fetch the most recently completed bar for a symbol and timeframe."""
        ...

    @abstractmethod
    def is_market_open(self, spec: InstrumentSpec, at_time_utc: datetime) -> bool:
        """Check if trading is currently open according to the instrument's sessions."""
        ...
