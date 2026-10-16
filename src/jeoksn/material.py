"""
재료비 계산 모음

재료비 = 제품을 만드는 데 들어간 재료값
'얼마나 버려지나' 와 '공용 재료비를 어떻게 나누나(간접재료비)'를 다룬다
"""

from decimal import Decimal

from jeoksn.rounding import round_half_up, to_decimal, truncate


def material_surcharge_rate(source_qty, product_qty) -> Decimal:
    """
    재료할증율(%): 소재에서 제품을 만들고 남은 자투리가 제품의 몇 %인가

    비유 ─ 피자 도우 자르기. (⭐ 분모는 소재가 아니라 제품)
    도우를 네모낳게 자르고 남은 가장자리(남는 양)를 '제품' 기준으로 잰다

    면적, 길이, 무게 어떤 값을 넣어도 상관없다. 단위만 서로 동일하면 된다.
    시험 기준: 소수 둘째 자리 절사
    """
    source = to_decimal(source_qty)
    product = to_decimal(product_qty)

    # 버려지는 양 ÷ 제품량 × 100 → %(퍼센트)
    rate = (source - product) / product * 100
    return truncate(rate, 2)


def indirect_material_per_unit(
    *,
    total_direct_material,
    total_labor,
    total_indirect_material,
    reclass_to_direct,
    unit_direct_material,
    unit_labor,
) -> Decimal:
    """
    원가법 간접재료비: 회사 전체 간접재료비를 제품 하나 몫으로 나눠준다.

    여러 메뉴가 같이 쓰는 식용유값(간접재료비)을
    메뉴마다 들어가는 재료비 + 인건비 크기에 비례하여 나눠 갖는 방식
    시험 기준: 원 미만 사사오입
    """
    # 1) 간접재료비 중 '사실 직접재료비인 것'을 차감하여 직접재료비 쪽으로 옮긴다
    #    서랍 정리: 한 쪽에서 꺼낸 후에는 반드시 다른 쪽 서랍에 집어 넣어야 한다
    indirect = to_decimal(total_indirect_material) - to_decimal(reclass_to_direct)
    direct = to_decimal(total_direct_material) + to_decimal(reclass_to_direct)

    # 2) 배부율 = 간접재료비 ÷ (직접재료비 + 노무비)
    #    '덩치 1원 당 식용유 값이 얼마인지'를 구하는 단계
    rate = indirect / (direct + to_decimal(total_labor))

    # 3) 제품 하나의 덩치(재료비 + 노무비) × 배부율 = 이 제품의 몫
    unit_size = to_decimal(unit_direct_material) + to_decimal(unit_labor)
    return round_half_up(unit_size * rate)
