from decimal import Decimal

import pytest

from jeoksn.labor import (
    labor_hours_per_unit,
    normal_labor_hours,
    retirement_allowance_rate,
)


# ── 퇴직급여충당금: 1년을 다 채우지 못한 사람의 몫은 빼고 적립 ──

def test_retirement_allowance_rate():
    # 풀이집 계산 5 → 6.87%
    rate = retirement_allowance_rate(
        total_labor=406_845_000,
        eligible_labor=335_818_250,   # 1년 이상 근속자 급여
    )
    assert rate == Decimal("6.87")


# ── 정상 노무공수: 정상 조업 시간만 골라 담기 ──

def test_normal_labor_hours():
    # 풀이집 계산 6 → 21,900Hr (기계고장 · 정전대기는 빠져야 함)
    hours = {
        "정상작업": 20_000,
        "직무교육": 400,
        "작업준비": 1_500,
        "기계고장": 700,
        "정전대기": 1_000,
    }
    assert normal_labor_hours(hours) == Decimal("21900")


def test_normal_labor_hours_rejects_unknown_kind():
    # 처음 보는 작업 종류가 들어오면 조용히 넘어가지 않고 알려야 한다
    hours = {"정상작업": 100, "회식": 3}
    with pytest.raises(ValueError):
        normal_labor_hours(hours)


# ── 재공품 반영 단위당 공수: 반쯤 만든 물건도 일한 만큼 쳐주기 ──

def test_labor_hours_per_unit_with_wip():
    # 풀이집 계산 10 → 10.95Hr
    result = labor_hours_per_unit(
        total_hours=11_500,
        completed=1_000,
        beginning_wip=100,
        beginning_progress="0.5",   # 기초재공품 완성도 50%
        ending_wip=200,
        ending_progress="0.5",      # 기말재공품 완성도 50%
    )
    assert result == Decimal("10.95")
