from decimal import Decimal

from jeoksn.material import indirect_material_per_unit, material_surcharge_rate


# ── 재료할증률: 자르고 남은 자투리가 몇 %인가 ──

def test_surcharge_rate_plate():
    # 풀이집 계산 1 (철판)
    # 두께·비중이 같으니 면적만 비교해도 된다 (같은 반죽이면 넓이만 보면 됨)
    source = 914 * 1829   # 소재 철판 면적
    product = 910 * 1800  # 제품 면적
    assert material_surcharge_rate(source, product) == Decimal("2.05")


def test_surcharge_rate_pipe():
    # 풀이집 계산 2 (파이프): 5.04m 소재에서 2.4m 제품이 2개 나온다
    # 함정: 제품 1개(2.4m)로 나누면 110%라는 엉뚱한 답이 나옴
    product_total = Decimal("2.4") * 2
    assert material_surcharge_rate("5.04", product_total) == Decimal("5")


# ── 원가법 간접재료비: 공용 비용을 덩치 비례로 나눠 갖기 ──

def test_indirect_material_cost_method():
    # 풀이집 계산 3 → 교재 정답 7,251원
    result = indirect_material_per_unit(
        total_direct_material=200_000_000,
        total_labor=100_000_000,
        total_indirect_material=50_000_000,
        reclass_to_direct=10_500_000,
        unit_direct_material=36_000,
        unit_labor=21_000,
    )
    assert result == Decimal("7251")
