from decimal import Decimal

from jeoksn.expense import Delivery, freight_per_unit, rnd_cost_per_unit


# ── 연구개발비: 몇 년 치를 모아서 여러 해에 나눠 원가에 넣기 ──

def test_rnd_cost_default_five_years():
    # 풀이집 계산 7 → 666원/EA
    # 내용연수 무신고 → 법인세법에 따라 5년으로 나눈다
    result = rnd_cost_per_unit(
        yearly_costs=[110_000_000, 60_000_000, 85_000_000, 78_000_000],
        annual_output=100_000,
    )
    assert result == Decimal("666")


def test_rnd_cost_declared_life():
    # 내용연수를 3년으로 신고했다면 3년으로 나눈다
    result = rnd_cost_per_unit(
        yearly_costs=[110_000_000, 60_000_000, 85_000_000, 78_000_000],
        annual_output=100_000,
        useful_life=3,
    )
    assert result == Decimal("1110")


# ── 운반비: 트럭을 몇대 부르는지 세고, 부가세를 차감한 후 수량으로 나누기 ──

def test_freight_per_unit_split_regions():
    # 풀이집 계산 11 → 553원
    # 함정: 부가세를 차감하지 않으면 608원 (객관식 보기에 실제로 있던 오답)
    deliveries = [
        Delivery(region="갑", quantity=600, fare_per_truck=150_000),
        Delivery(region="을", quantity=400, fare_per_truck=100_000),
        Delivery(region="병", quantity=200, fare_per_truck=80_000),
    ]
    result = freight_per_unit(deliveries=deliveries, truck_capacity=200)
    assert result == Decimal("553")


def test_freight_rounds_up_trucks():
    # 201개를 200개짜리 트럭으로 옮기면 1.005대가 아니라 2대를 불러야 한다
    deliveries = [Delivery(region="갑", quantity=201, fare_per_truck=110_000)]
    result = freight_per_unit(deliveries=deliveries, truck_capacity=200)
    # 2대 × 110,000 = 220,000 → 부가세 차감 후 200,000 → ÷ 201개 = 995.02 → 995
    assert result == Decimal("995")
