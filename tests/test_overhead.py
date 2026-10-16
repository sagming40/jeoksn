from decimal import Decimal

import pytest

from jeoksn.overhead import defense_indirect_expense, general_admin_rate


# ── 일반관리비율: 판매비는 걷어내고, 업종 상한을 넘으면 상한으로 ──

def test_general_admin_rate_under_cap():
    # 풀이집 계산 4 (조립금속, 공장상차도 인도) → 5.85%
    # 공장상차도 = 회사가 배달 하는게 아님 → 운반비도 차감
    rate = general_admin_rate(
        cost_of_sales=10_118_000,   # 매출원가 (천원)
        sga_total=812_000,          # 일반관리비 및 판매비 합계
        excluded={
            "운반비": 54_000,
            "광고선전비": 21_000,
            "판매수수료": 65_000,
            "접대비": 31_000,
            "대손상각비": 49_000,
        },
        industry="조립금속제품",
    )
    # 함정: 매출액으로 나누면 4.96%가 나온다 → 분모는 '매출원가'
    assert rate == Decimal("5.85")


def test_general_admin_rate_capped():
    # 계산 결과(6.05%)가 제1차 금속 상한(6%)을 넘으면 → 상한 6%를 사용한다
    rate = general_admin_rate(
        cost_of_sales=8_500_000,
        sga_total=713_000,
        excluded={
            "운반비": 48_000,
            "광고선전비": 18_000,
            "판매수수료": 56_000,
            "접대비": 37_000,
            "대손상각비": 39_000,
        },
        industry="제1차금속제품",
    )
    assert rate == Decimal("6")


def test_general_admin_rate_unknown_industry():
    # 요율표에 없는 업종이면 조용히 넘어가지 않고 멈춘다
    with pytest.raises(ValueError):
        general_admin_rate(
            cost_of_sales=1_000,
            sga_total=100,
            excluded={},
            industry="외계기술제품",
        )


# ── 방산 간접경비: 기준이 '노무비 전체' 라는 게 함정 ──

def test_defense_indirect_expense():
    # 풀이집 계산 8 (주)우람 → 1,800,000원
    # 함정: 직접노무비만 곱하면 1,200,000원
    result = defense_indirect_expense(
        direct_labor=4_000_000,
        indirect_labor=2_000_000,
        rate="0.3",
    )
    assert result == Decimal("1800000")
