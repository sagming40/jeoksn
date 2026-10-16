"""
끝자리 처리 규칙 모음

원가계산은 문제마다 "소수 둘째 자리 절사", "원 미만 사사오입"과 같이
끝자리 처리방법이 정해져 있다. 그 규칙을 한 곳에 모아둔다.
비유: 공구함의 '끝손질 칸'
"""

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal


def to_decimal(value) -> Decimal:
    """
    어떤 숫자가 들어와도 Decimal(줄자)로 변환한다

    float를 바로 Decimal(0.1)로 바꾸면 눈대중 오차까지 그대로 복사 되어버린다
    따라서, str()로 한 번 '옮겨 적은 후' 그 글자를 보고 다시 옮겨적는다. (Decimal)
    """
    return Decimal(str(value))


def _unit(places: int) -> Decimal:
    """
    자릿수를 '자르는 눈금'으로 바꾼다
    places=0 → 1 (원 단위), places=2 → 0.01 (소수 둘째 자리)
    줄자에서 어느 눈금에 맞춰 자를지 고르는 것
    """
    return Decimal(10) ** -places


def truncate(value, places: int = 0) -> Decimal:
    """
    절사: 정한 눈금 아래는 반올림 없이 그냥 자른다
    비유 ─ 빵을 자로 재서 칼로 싹둑. 부스러기는 그냥 버린다
    """
    return to_decimal(value).quantize(_unit(places), rounding=ROUND_DOWN)


def round_half_up(value, places: int = 0) -> Decimal:
    """
    사사오입: 5 ↑ 올림, 4 ↓ 버림 ─ 학교에서 배운 반올림 그대로다
    """
    return to_decimal(value).quantize(_unit(places), rounding=ROUND_HALF_UP)
