"""
경비 계산 모음

경비 = 재료비 · 노무비가 아닌 나머지 원가 (연구개발비, 운반비, 전력비 등)
'여러 해에 나눠 넣는 연구개발비'와 '트럭 운반비'를 다룬다
"""

import math
from dataclasses import dataclass
from decimal import Decimal

from jeoksn.rounding import to_decimal, truncate

# 내용연수를 신고하지 않았을 때 사용하는 기본 상각 기간 (법인세법)
DEFAULT_RND_LIFE = 5


def rnd_cost_per_unit(*, yearly_costs, annual_output, useful_life=None) -> Decimal:
    """
    제품 1개당 연구개발비

    비유 ─ 노트북 같은 값비싼 물품을 구매할때 할부 결제를 하면
    구매할 때 그 금액이 한꺼번에 빠져나가 첫 회에 모두 결제가 된 것처럼 보이지만
    실질적으로는 할부기간 안에서 매달 일정금액이 나눠서 결제(갚아지는)되는 것처럼

    연구개발비도 어려 해 치를 모아서, 정해진 기간에 나눠 원가에 넣는다

    useful_life=None → '신고 안 함'이라는 뜻. 그때는 기본 5년
    시험 기준: 원 미만 절사
    """
    # 1) 여러 해 비용을 한 바구니에 모은다
    #    sum(... for ...) = 목록을 하나씩 줄자로 바꾸면서 바로 더하기
    total = sum(to_decimal(cost) for cost in yearly_costs)

    # 2) 신고한 기간이 없으면 기본 5년
    #    None은 '0'이 아닌 '빈칸'이다. 아예 적지 않았다는 뜻
    years = DEFAULT_RND_LIFE if useful_life is None else useful_life

    # 3) 1년 몫 ÷ 1년 생산량 = 제품 1개 몫
    per_year = total / to_decimal(years)
    return truncate(per_year / to_decimal(annual_output))


@dataclass(frozen=True)
class Delivery:
    """
    납품지 한 곳의 배송 정보 (배송 전표 한 장)

    지역, 보낼 개수, 트럭 1대 운임(부가세 포함)이 적혀 있다
    """

    region: str
    quantity: int
    fare_per_truck: int


def freight_per_unit(
    *,
    deliveries,
    truck_capacity,
    vat_included=True,
    vat_rate="0.1",
) -> Decimal:
    """
    제품 1개 당 운반비

    지역마다 트럭을 몇 대 부르는지 세고 → 운임을 다 더하고 → 부가세를 차감하고 → 전체 수량으로 나눈다

    원가계산은 항상 부가세를 뺀 금액으로 한다
    즉, 부가세는 마지막 예정가격 단계에서 따로 가산하기 때문에, 중복 가산이 되어버린다
    시험 기준: 원 미만 절사
    """
    total_fare = Decimal(0)
    total_quantity = 0

    for d in deliveries:
        # 1) 트럭 대수 = 개수 ÷ 적재량, 남으면 무조건 한대 더
        #    트럭은 반(0.5) 대만 부를 수 없기 때문에 올림(ceil)
        trucks = math.ceil(d.quantity / truck_capacity)

        # 2) 해당 지역 운임 = 대수 × 1대 운임
        total_fare += trucks * to_decimal(d.fare_per_truck)
        total_quantity += d.quantity

    # 3) 부가세 포함 금액이면 1.1로 나눠서 부가세를 걷어낸다
    if vat_included:
        total_fare = total_fare / (1 + to_decimal(vat_rate))

    # 4) 전체 운임 ÷ 전체 개수 = 1개당 운반비
    return truncate(total_fare / total_quantity)
