from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M5-decline-distress-contingent-survival-contract.md"


def _contract_text() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_m5_financing_path_is_explicit_and_recomputable() -> None:
    text = _contract_text()

    assert "`status_quo_forecast`, `financing_path`, `closure`" in text
    for field in (
        "`opening_face_debt`",
        "`debt_issuances`",
        "`debt_repayments`",
        "`closing_face_debt`",
        "`market_value_debt`",
        "`market_value_equity`",
        "`cash_interest_tax_benefits`",
        "`after_tax_costs_of_debt`",
        "`costs_of_capital`",
    ):
        assert field in text

    assert "closing_face_debt[t]" in text
    assert "debt_to_capital_ratio[t]" in text
    assert "status_quo_forecast.discount_rates[t]" in text


def test_m5_interest_tax_benefit_is_floored_at_zero() -> None:
    text = _contract_text()

    assert "taxable_operating_income_available[t]\n= max(0, operating_income[t])" in text
    assert (
        "min(cash_interest[t], taxable_operating_income_available[t]) * tax_rate[t]" in text
    )
    assert "a loss therefore produces no negative tax benefit" in text


def test_m5_orderly_liquidation_is_a_separate_alternative() -> None:
    text = _contract_text()
    terminal_section = text.split("### Terminal or closure state", 1)[1].split("## Schema contract", 1)[0]

    assert "A full `orderly_liquidation` is a separate conditional alternative" in terminal_section
    assert "never a `closure.mode`" in terminal_section
    assert "- `orderly_liquidation`:" not in terminal_section
    assert "cannot also appear as `closure.mode`" in text
