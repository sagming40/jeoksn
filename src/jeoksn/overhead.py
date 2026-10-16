"""
일반관리비 · 방산 간접비 계산 모음

일반관리비 = 회사를 굴리는 데(운영) 드는 비용 (사무실, 관리 인력 등)
정부는 이 중 '만드는 데 필요한 것'만 인정하고, 업종마다 상한선을 둔다
업종별 상한은 코드가 아니라 data/rates.json(요율표)에서 읽어온다
"""

import json
from decimal import Decimal
from functools import cache
from importlib.resources import files

from jeoksn.rounding import to_decimal, truncate


@cache
def _load_rates() -> dict:
    """
    요율표(rates.json)를 읽어온다

    @cache = 도서관에서 책 한 권을 빌려온 후 집 책장에 꽂는다
    처음 한 번만 파일을 열고, 그 다음부터는 책장(메모리)에서 바로 꺼내 쓴다

    parse_float=Decimal = JSON 안의 소수(7.5 같은 수치)를 float가 아닌
    처음부터 줄자(Decimal)로 읽으라는 뜻. 눈대중 오차가 들어올 틈을 막는다
    """
    # files("jeoksn") = 설치된 jeoksn 패키지 폴더를 '주소'로 찾아준다
    # 지금 터미널이 어디에 서 있든 상관없이 항상 동일한 폴더를 찾는다
    text = files("jeoksn").joinpath("data", "rates.json").read_text(encoding="utf-8")
    return json.loads(text, parse_float=Decimal)


def general_admin_cap(industry: str) -> Decimal:
    """
    업종별 일반관리비 상한 비율(%) 요율표에서 찾아온다
    표에 없는 업종이면 멈춘다. (없는 걸 0%나 대충 값으로 채우면 위험)
    """
    caps = _load_rates()["general_admin_cap"]["rates"]
    if industry not in caps:
        raise ValueError(f"상한 비율이 등록되지 않은 업종: {industry}")
    return to_decimal(caps[industry])


def general_admin_rate(*, cost_of_sales, sga_total, excluded, industry) -> Decimal:
    """
    예정가격에 적용할 일반관리비율(%)

    1) 판관비 합계에서 '파는 데 쓴 돈'(광고, 접대, 판매수수료 등)을 걷어낸다
       정부는 '물건 만드는 회사를 굴리는 비용'만 대신 내준다
    2) 남은 금액 ÷ 매출원가 → 실제 비율
    3) 실제 비율과 업종 상한 중 '더 낮은 쪽'을 쓴다
       비유 ─ 속도 제한도로: 내 차가 아무리 빨라도 제한속도까지만 인정

    excluded = 걷어낼 항목 {이름: 금액}. 이름표를 붙여두면 나중에 뭘 했는지 보인다
    시험 기준: 소수 둘째 자리 절사
    """
    # 1) 인정 일반관리비 = 합계 - 걷어낼 항목들
    removed = sum(to_decimal(amount) for amount in excluded.values())
    allowed = to_decimal(sga_total) - removed

    # 2) 실제 비율 (분모는 매출액이 아니라 매출원가!)
    actual = truncate(allowed / to_decimal(cost_of_sales) * 100, 2)

    # 3) 상한과 비교해서 낮은 쪽
    return min(actual, general_admin_cap(industry))


def defense_indirect_expense(*, direct_labor, indirect_labor, rate) -> Decimal:
    """
    방산물자 간접경비

    방산 간접비는 항목마다 '무엇에 곱하는지'가 다르다
    간접경비는 노무비 전체(직접 + 간접)가 기준이다
    (간접재료비 · 간접노무비는 직접노무비만 기준이라 헷갈리기가 쉽다)
    rate는 0.3처럼 소수로 넣는다 (30% → 0.3)
    시험 기준: 원 미만 절사
    """
    base = to_decimal(direct_labor) + to_decimal(indirect_labor)
    return truncate(base * to_decimal(rate))
