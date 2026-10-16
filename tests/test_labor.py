from decimal import Decimal

import pytest

from jeoksn.labor import (
    daily_wage,
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


# ── 노임단가: 하루치 품삯 영수증을 뽑아서 시간당으로 나누기 ──

def test_daily_wage_breakdown():
    # 풀이집 계산 9 (용접공)
    # 미끼: 업체 기본급 100,000원, 자격수당, 월 22일 → 입력칸 자체가 없다
    wage = daily_wage(
        market_wage=91_928,        # 시중노임 (기본급에는 이걸 사용한다)
        overtime_hours=2,          # 연장근로 2시간
        bonus_rate=3,              # 상여 연 300% → 3배
        years_of_service="2.5",    # 근속 2년 6개월
    )
    # 영수증 항목 하나하나 확인 (주관식은 과정 점수가 있으니까)
    assert wage.base == Decimal("91928")
    assert wage.overtime == Decimal("34473")
    assert wage.bonus == Decimal("22982")
    assert wage.retirement == Decimal("12448")
    assert wage.total == Decimal("161831")
    # 최종 답: 교재 정답 16,183/Hr
    assert wage.hourly == Decimal("16183")


def test_daily_wage_no_retirement_under_one_year():
    # 근속 1년 미만이면 퇴직급여충당금은 0원
    wage = daily_wage(
        market_wage=91_928,
        overtime_hours=2,
        bonus_rate=3,
        years_of_service="0.5",
    )
    assert wage.retirement == Decimal("0")
    assert wage.total == Decimal("149383")
