"""Tests for core interfaces and data contracts."""

from datetime import UTC, datetime, time

import pytest
from pydantic import BaseModel, ValidationError

from engine.core.interfaces.data import Bar, MarketDataFeed, Timeframe
from engine.core.interfaces.execution import ExecutionBroker
from engine.core.interfaces.instrument import (
    AssetClass,
    InstrumentSpec,
    MarginModel,
    RollRule,
    TradingSession,
)
from engine.core.interfaces.strategy import (
    Signal,
    SignalDirection,
    Strategy,
    StrategyContext,
)


def test_strategy_abc_cannot_be_instantiated() -> None:
    """Strategy is an ABC and requires concrete implementation."""
    with pytest.raises(TypeError):
        Strategy()  # type: ignore[abstract]


def test_concrete_strategy_subclass() -> None:
    """A valid deterministic strategy subclass implements on_bar and warmup."""

    class DummyParams(BaseModel):
        period: int = 14

    class ConcreteStrategy(Strategy):
        name = "test_strat"
        version = "1.0.0"
        parameters = DummyParams()

        def on_bar(self, context: StrategyContext) -> list[Signal]:
            if not context.bars:
                return []
            last_bar = context.bars[-1]
            return [
                Signal(
                    timestamp_utc=last_bar.timestamp_utc,
                    strategy_name=self.name,
                    strategy_version=self.version,
                    symbol=context.symbol,
                    direction=SignalDirection.BUY,
                )
            ]

        def get_warmup_bars(self) -> int:
            return 14

    strat = ConcreteStrategy()
    assert strat.name == "test_strat"
    assert strat.get_warmup_bars() == 14

    bar = Bar(
        timestamp_utc=datetime.now(UTC),
        open=1.1000,
        high=1.1050,
        low=1.0980,
        close=1.1020,
        volume=500.0,
        spread=1.2,
    )
    ctx = StrategyContext(
        symbol="EURUSD",
        timeframe=Timeframe.H1.value,
        bars=[bar],
        current_position_size=0.0,
        account_equity=10000.0,
    )

    signals = strat.on_bar(ctx)
    assert len(signals) == 1
    assert signals[0].direction == SignalDirection.BUY
    assert signals[0].symbol == "EURUSD"


def test_instrument_spec_spot_forex() -> None:
    """Verify InstrumentSpec creation for spot forex."""
    spec = InstrumentSpec(
        canonical_symbol="EURUSD",
        broker_symbol="EURUSD.m",
        asset_class=AssetClass.SPOT_FOREX,
        contract_size=100000.0,
        lot_min=0.01,
        lot_max=100.0,
        lot_step=0.01,
        tick_size=0.00001,
        tick_value=1.0,
        pip_size=0.0001,
        quote_currency="USD",
        settlement_currency="USD",
        margin_model=MarginModel.FOREX_LEVERAGED,
        margin_requirement=0.01,
        sessions=[
            TradingSession(
                day_of_week=0,
                open_time=time(0, 0),
                close_time=time(23, 59),
            )
        ],
    )
    assert spec.canonical_symbol == "EURUSD"
    assert spec.asset_class == AssetClass.SPOT_FOREX
    assert spec.expiry_date is None
    assert spec.roll_rule == RollRule.NONE


def test_instrument_spec_exchange_traded_contract() -> None:
    """Verify InstrumentSpec creation for exchange-traded contracts with expiry and roll rules."""
    expiry = datetime(2026, 11, 26, 17, 0, tzinfo=UTC)
    spec = InstrumentSpec(
        canonical_symbol="USDINR",
        broker_symbol="USDINR26NOV",
        asset_class=AssetClass.EXCHANGE_DERIVATIVE,
        contract_size=1000.0,
        lot_min=1.0,
        lot_max=500.0,
        lot_step=1.0,
        tick_size=0.0025,
        tick_value=2.5,
        pip_size=0.01,
        quote_currency="INR",
        settlement_currency="INR",
        conversion_path=["USDINR"],
        margin_model=MarginModel.EXCHANGE_SPAN,
        margin_requirement=0.03,
        expiry_date=expiry,
        roll_rule=RollRule.NEXT_CONTRACT_ROLL,
        exchange_calendar="NSE",
    )
    assert spec.asset_class == AssetClass.EXCHANGE_DERIVATIVE
    assert spec.expiry_date == expiry
    assert spec.roll_rule == RollRule.NEXT_CONTRACT_ROLL
    assert spec.exchange_calendar == "NSE"


def test_instrument_spec_lot_bounds_validation() -> None:
    """Verify lot_max cannot be less than lot_min."""
    with pytest.raises(ValidationError) as exc_info:
        InstrumentSpec(
            canonical_symbol="XAUUSD",
            broker_symbol="GOLD",
            contract_size=100.0,
            lot_min=1.0,
            lot_max=0.5,  # Invalid: max < min
            lot_step=0.1,
            tick_size=0.01,
            tick_value=1.0,
            pip_size=0.01,
            quote_currency="USD",
            margin_requirement=0.01,
        )
    assert "lot_max" in str(exc_info.value)


def test_interfaces_abc_contracts() -> None:
    """Verify MarketDataFeed and ExecutionBroker are ABCs."""
    with pytest.raises(TypeError):
        MarketDataFeed()  # type: ignore[abstract]

    with pytest.raises(TypeError):
        ExecutionBroker()  # type: ignore[abstract]
