"""Core engine interfaces decoupling strategies, market data, execution, and instruments."""

from engine.core.interfaces.data import Bar, MarketDataFeed, Timeframe
from engine.core.interfaces.execution import (
    AccountState,
    ExecutionBroker,
    OrderRequest,
    OrderResult,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
    ReconciliationReport,
)
from engine.core.interfaces.instrument import (
    AssetClass,
    InstrumentSpec,
    MarginModel,
    RollRule,
    TradingSession,
)
from engine.core.interfaces.strategy import Signal, SignalDirection, Strategy, StrategyContext

__all__ = [
    "AccountState",
    "AssetClass",
    "Bar",
    "ExecutionBroker",
    "InstrumentSpec",
    "MarginModel",
    "MarketDataFeed",
    "OrderRequest",
    "OrderResult",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Position",
    "ReconciliationReport",
    "RollRule",
    "Signal",
    "SignalDirection",
    "Strategy",
    "StrategyContext",
    "Timeframe",
    "TradingSession",
]
