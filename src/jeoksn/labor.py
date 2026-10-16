"""
노무비 계산 모음

노무비 = 사람이 일한 값
'퇴직금 적립 비율', '원가로 인정되는 작업 시간', '제품 하나에 든 시간'을 다룬다
"""

from dataclasses import dataclass
from decimal import Decimal

from jeoksn.rounding import to_decimal, truncate

# 원가로 인정되는 '정상 조업' 작업 종류
# set(집합) = 중복 없는 이름표 상자. '이 안에 있는지 없는지'를 빠르게 확인할 때 사용한다
NORMAL_WORK = {"정상작업", "직무교육", "작업준비"}

# 비정상이라 원가에서 차감하는 작업 종류
ABNORMAL_WORK = {"기계고장", "정전대기"}

# 1년 = 12개월
# 퇴직금(1년 근무 시 1개월 치)과 상여금(1년 치를 개월로 쪼갬) 두 금액 모두 이 상수를 사용한다
# 비유 ─ 달력에 원래 찍혀있는 숫자. 규정이 해마다 바뀌는 값이 아니기 때문에 rates.json이 아닌 코드 상수로 둔다
MONTHS_PER_YEAR = 12


def retirement_allowance_rate(*, total_labor, eligible_labor) -> Decimal:
    """
    퇴직급여충당금 비율(%)

    퇴직금은 1년에 한 달 치(30일분)이기 때문에 기본 비율은 1/12이다.
    하지만 1년 미만 근무자는 퇴직금 대상이 아니므로
    '대상자 급여가 전체에서 차지하는 비중'만큼만 곱한다
    비유 ─ 아르바이트를 1년을 다 채우지 못하고 그만두게 되면 퇴직금이 없는 것과 같다
    시험 기준: 소수 둘째 자리 절사
    """
    # 대상자 비중 = 1년 이상 근속자 급여 ÷ 전체 노무비
    eligible_share = to_decimal(eligible_labor) / to_decimal(total_labor)

    # 1/12 × 비중 × 100 → %
    rate = eligible_share / MONTHS_PER_YEAR * 100
    return truncate(rate, 2)


def normal_labor_hours(hours: dict) -> Decimal:
    """
    정상 노무공수: 정상 조업에 속하는 시간만 골라서 더한다

    장바구니에서 '회사가 돈 내주는 물건'만 골라 계산대에 올리는 것
    기계고장 · 정전대기는 회사 사정이라 원가에 넣지 않는다
    """
    # 1) 처음 보는 작업 종류가 섞여 있는지 검사
    #    set(hours) = 딕셔너리의 이름표(키)만 뽑은 상자
    #    알고 있는 이름표를 전부 제외하고도 남는 것이 있으면 = 모르는 종류
    unknown = set(hours) - NORMAL_WORK - ABNORMAL_WORK
    if unknown:
        # 모르는 걸 조용히 빼버리면 틀린 답이 '정답처럼' 나와버린다
        # 따라서, 멈추고 크게 알린다
        raise ValueError(f"분류되지 않은 작업 종류: {sorted(unknown)}")

    # 2) 정상 작업만 하나씩 꺼내서 더하기
    total = Decimal(0)
    for kind, hr in hours.items():
        if kind in NORMAL_WORK:
            total += to_decimal(hr)
    return total


def labor_hours_per_unit(
    *,
    total_hours,
    completed,
    beginning_wip,
    beginning_progress,
    ending_wip,
    ending_progress,
) -> Decimal:
    """
    재공품을 반영한 제품 1개당 노무공수(Hr)

    반쯤 만든 물건 2개 = 완성품 1개 만큼 일한 것
    이번 기간에 '실제로 일한 양'을 완성품 개수로 환산하여 시간을 나눈다
    - 기말재공품: 이번 기간에 손댄 만큼 가산
    - 기초재공품: 지난 기간에 이미 해둔 만큼 차감
    완성도는 0.5처럼 소수로 넣는다 (50% → 0.5)
    시험 기준: 소수 둘째 자리 절사
    """
    # 완성품 환산량 = 완성품 + 기말 몫 - 기초 몫
    equivalent = (
        to_decimal(completed)
        + to_decimal(ending_wip) * to_decimal(ending_progress)
        - to_decimal(beginning_wip) * to_decimal(beginning_progress)
    )
    return truncate(to_decimal(total_hours) / equivalent, 2)


@dataclass(frozen=True)
class DailyWage:
    """
    하루치 품삯 영수증

    항목별로 찍혀있어서 '어떻게 이 금액이 나왔는지' 한눈에 보인다
    frozen=True = 영수증은 한 번 뽑으면 고칠 수 없다 (위조 방지)
    """

    base: Decimal         # 기본급 (시중노임)
    overtime: Decimal     # 제수당 (연장근로수당)
    bonus: Decimal        # 상여금 (하루치로 나눈 몫)
    retirement: Decimal   # 퇴직급여충당금
    work_hours: Decimal   # 하루 총 작업시간 (정상 + 연장)

    @property
    def total(self) -> Decimal:
        """1일 합계: 영수증 맨 아래 '합계'줄"""
        return self.base + self.overtime + self.bonus + self.retirement

    @property
    def hourly(self) -> Decimal:
        """시간당 노임단가: 하루 합계를 일한 시간으로 나눈다. 원 미만 절사"""
        return truncate(self.total / self.work_hours)


def daily_wage(
    *,
    market_wage,
    overtime_hours,
    bonus_rate,
    years_of_service,
    regular_hours=8,
    overtime_premium="1.5",
) -> DailyWage:
    """
    노임단가 영수증을 출력한다

    기본급은 업체가 실제로 주는 돈이 아니라 '시중노임'을 사용한다
    ─ 정부는 시장 평균 단가만 인정한다. 업체가 더 지불하더라도 그건 업체의 사정이다.
    자격수당 등은 시중노임 안에 이미 포함되어 있어서 따로 받지 않는다
    시험 기준: 각 항목 원 미만 절사
    """
    base = to_decimal(market_wage)

    # 1) 제수당: 연장근로는 시급의 1.5배 ─ 시급 = 일당 ÷ 정상근무 8시간
    hourly_base = base / to_decimal(regular_hours)
    overtime = truncate(
        hourly_base * to_decimal(overtime_hours) * to_decimal(overtime_premium)
    )

    # 2) 상여금: 연 300%를 12달로 나눠서 하루 단가에 얹는다
    #    1년에 3번 지급되는 보너스를 매달 조금씩 미리 적립하는 느낌
    bonus = truncate(base * to_decimal(bonus_rate) / MONTHS_PER_YEAR)

    # 3) 퇴직급여충당금: 1년 이상 근속자만, (기본급 + 제수당 + 상여) ÷ 12
    #    1년 근무 시 1달 치 퇴직금 → 그래서 1/12씩 적립해둔다
    if to_decimal(years_of_service) >= 1:
        retirement = truncate((base + overtime + bonus) / MONTHS_PER_YEAR)
    else:
        retirement = Decimal(0)

    # 4) 영수증 발행
    work_hours = to_decimal(regular_hours) + to_decimal(overtime_hours)
    return DailyWage(
        base=base,
        overtime=overtime,
        bonus=bonus,
        retirement=retirement,
        work_hours=work_hours,
    )
