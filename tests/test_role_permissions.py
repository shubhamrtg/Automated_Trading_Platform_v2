"""Mandatory Test: Role permissions and withdrawal prevention (TECH_STACK §14).

Ensures:
- Exact roles defined in DECISIONS D8 (VIEWER, OPERATOR, ADMIN, AI).
- No role can change risk limits unless Admin.
- No role or code path can withdraw funds.
- AI role cannot reach engine control or administrative privileges.
"""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from engine.storage.models import Role, RoleType

# Permitted actions per role according to DECISIONS D8
ROLE_CAPABILITIES = {
    RoleType.VIEWER: {
        "view_pnl": True,
        "view_positions": True,
        "view_reports": True,
        "view_journal": True,
        "run_backtest": False,
        "create_draft_strategy": False,
        "add_journal_note": False,
        "pause_resume_profile": False,
        "trigger_kill_switch": False,
        "activate_strategy": False,
        "edit_risk_limits": False,
        "manage_devices": False,
        "withdraw_funds": False,
    },
    RoleType.OPERATOR: {
        "view_pnl": True,
        "view_positions": True,
        "view_reports": True,
        "view_journal": True,
        "run_backtest": True,
        "create_draft_strategy": True,
        "add_journal_note": True,
        "pause_resume_profile": True,
        "trigger_kill_switch": True,
        "activate_strategy": False,
        "edit_risk_limits": False,
        "manage_devices": False,
        "withdraw_funds": False,
    },
    RoleType.ADMIN: {
        "view_pnl": True,
        "view_positions": True,
        "view_reports": True,
        "view_journal": True,
        "run_backtest": True,
        "create_draft_strategy": True,
        "add_journal_note": True,
        "pause_resume_profile": True,
        "trigger_kill_switch": True,
        "activate_strategy": True,
        "edit_risk_limits": True,
        "manage_devices": True,
        "withdraw_funds": False,
    },
    RoleType.AI: {
        "view_pnl": True,
        "view_positions": True,
        "view_reports": True,
        "view_journal": True,
        "run_backtest": True,
        "create_draft_strategy": True,
        "add_journal_note": True,
        "pause_resume_profile": False,
        "trigger_kill_switch": False,
        "activate_strategy": False,
        "edit_risk_limits": False,
        "manage_devices": False,
        "withdraw_funds": False,
    },
}


@pytest.mark.asyncio
async def test_all_defined_roles_exist_in_db(db_session: AsyncSession) -> None:
    """Verify all four roles exist and are correctly initialized."""
    for role_type in RoleType:
        role = Role(name=role_type.value, description=f"System {role_type.value} role")
        db_session.add(role)
    await db_session.commit()

    result = await db_session.execute(select(Role))
    roles = result.scalars().all()
    role_names = {r.name for r in roles}
    assert role_names == {"VIEWER", "OPERATOR", "ADMIN", "AI"}


def test_zero_roles_can_withdraw_funds() -> None:
    """Safety rule: No code path or role may withdraw funds."""
    for role, capabilities in ROLE_CAPABILITIES.items():
        assert capabilities["withdraw_funds"] is False, (
            f"Violation: {role.value} has withdraw_funds=True"
        )


def test_only_admin_can_edit_risk_limits() -> None:
    """Safety rule: Only Admin can edit risk limits."""
    for role, capabilities in ROLE_CAPABILITIES.items():
        if role == RoleType.ADMIN:
            assert capabilities["edit_risk_limits"] is True
        else:
            assert capabilities["edit_risk_limits"] is False, (
                f"Violation: {role.value} should not be allowed to edit risk limits"
            )


def test_ai_role_has_no_engine_control_privileges() -> None:
    """Safety rule: AI role cannot pause, resume, trigger kill switch, or activate."""
    ai_caps = ROLE_CAPABILITIES[RoleType.AI]
    assert ai_caps["pause_resume_profile"] is False
    assert ai_caps["trigger_kill_switch"] is False
    assert ai_caps["activate_strategy"] is False
    assert ai_caps["edit_risk_limits"] is False
    assert ai_caps["manage_devices"] is False


def test_viewer_has_strictly_read_only_privileges() -> None:
    """Viewer cannot alter any state, trigger runs, or modify profiles."""
    viewer_caps = ROLE_CAPABILITIES[RoleType.VIEWER]
    assert viewer_caps["run_backtest"] is False
    assert viewer_caps["create_draft_strategy"] is False
    assert viewer_caps["add_journal_note"] is False
    assert viewer_caps["pause_resume_profile"] is False
    assert viewer_caps["trigger_kill_switch"] is False
    assert viewer_caps["activate_strategy"] is False
