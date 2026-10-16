from decimal import Decimal

from jeoksn.rounding import round_half_up, truncate


# ── 절사: 남는 부분을 칼로 잘라버리기 ──

def test_truncate_two_places():
    # 풀이집 계산 1 (철판 재료 할증률): 2.0577% → 둘째 자리 절사 → 2.05%
    assert truncate("2.0577", 2) == Decimal("2.05")


def test_truncate_won():
    # 원 미만 절사: 0.9원이 남아도 미련 없이 버린다
    assert truncate("7251.9") == Decimal("7251")


# ── 사사오입: 5 이상이면 올리고, 4 이하면 버리기 ──

def test_round_half_up_won():
    # 풀이집 계산 3 (간접재료비): 7,251.2원 → 7,251원
    assert round_half_up("7251.2") == Decimal("7251")
    assert round_half_up("7251.5") == Decimal("7252")


def test_round_half_up_is_not_bankers_rounding():
    # 함정: Python 기본 round(2.5)는 3이 아닌 2가 나온다
    # 원가계산은 사사오입이 적용되므로 무조건 3이 나와야만 통과시킨다
    assert round_half_up("2.5") == Decimal("3")


def test_float_input_does_not_leak_error():
    # 0.1 + 0.2 = 0.30000000000000004 (float의 눈대중 오차)
    # 이 값이 들어와도 절사 결과는 깨끗한 0.30이어야 한다
    assert truncate(0.1 + 0.2, 2) == Decimal("0.30")
