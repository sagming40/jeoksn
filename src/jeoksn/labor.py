"""
노무비 계산 모음

노무비 = 사람이 일한 값
'퇴직금 적립 비울', '원가로 인정되는 작업 시간', '제품 하나에 든 시간'을 다룬다
"""

from decimal import Decimal

from jeoksn.rounding import to_decimal, truncate

# 원가로 인정되는 '정상 조업' 작업 종류
# set(집합) = 중복 없는 이름표 상자. '이 안에 있는지 없는지'를 빠르게 확인할 때 사용한다
NORMAL_WORK = {"정상작업", "직무교육", "작업준비"}

# 비정상이라 원가에서 차감하는 작업 종류
ABNORMAL_WORK = {"기계고장", "정전대기"}


def retirement_allowance_rate(*, total_labor, eligible_labor) -> Decimal:
    """
    퇴직급여충당금 비율(%)

    퇴직금은 1년에 한 달 치(30일분)이기 때문에 기본 비율은 1/12이다.
    하지만 1년 미만 근무자는 퇴직금 대상이 아니므로
    '대상자 급여가 전체에서 차지하는 비중'만큼만 곱한다
    비유 ─ 아르바이트를 1년을 다 채우지 못하고 그만두게 되면 퇴직금이 없는 것과 같다
    시험 기준: 소수 둘째 자리 절사
    """
    # 대상자 비중 = 1년 이상 근속자 급여 + 전체 노무비
    eligible_share = to_decimal(eligible_labor) / to_decimal(total_labor)

    # 1/12 × 비중 × 100 → %
    rate = eligible_share / 12 * 100
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
