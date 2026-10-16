# jeoksn 세션 인계 문서

> 마지막 갱신: 2026-10-16 (2일차 세션 종료 시점)
> 새 채팅을 시작하면 이 문서부터 읽고 **「7. 다음 세션 첫 작업」**부터 이어간다.
> 세션이 끝날 때마다 이 문서를 갱신하고 `docs(handoff)` 커밋으로 남긴다.

---

## 1. 프로젝트 한눈에 보기

| 항목 | 내용 |
|---|---|
| 이름 | **jeoksn** (적산, 마지막 모음만 뺀 표기) |
| 한 줄 소개 | 원가분석사 기준(정부 원가계산 기준) 원가계산 엔진 |
| 목적 | 원가분석사 시험 과목 도메인 학습 + 자기계발 (취업 후 재미/성장용) |
| 핵심 원칙 | "돌아간다"가 아니라 **"맞다"를 증명**하는 계산기. 교재 정답 = 테스트 기대값 |
| 저장소 | https://github.com/sagming40/jeoksn (branch `main`) |
| 로컬 경로 | `D:\_dev\jeoksn` |

### 로드맵 (5단계, 각 단계는 멈춰도 완성품)

1. **제조원가 엔진** ← 지금 여기 (부품 계산기 완료, 조립기 남음)
2. 공사원가로 확장 (요율을 연도별로 관리)
3. 화면 붙이기
4. 관리회계 분석 탭 (손익분기점 등)
5. 법규 근거 툴팁 (요율 옆에 출처 표시)

- 재무회계 과목은 결이 달라서 **범위에서 제외**함.
- 다른 프로젝트 상태: BidWise 보류, 콕(kkok) 드롭, Mutting Room은 노트북에서 가볍게.

---

## 2. 작업 방식 (프로젝트 지침 요약)

### 학습 방식
- 사용자가 **코드를 직접 타이핑**한다. 코드는 파일이 아니라 **코드 블록**으로 제공한다.
- 함수·로직마다 **일상어 비유 주석**을 넣는다.
- 수정은 "어느 파일 몇 번째 줄을 이렇게"로 안내한다. 유지할 줄은 블록 밖에서 "건드리지 마"라고 말한다.
- 에러가 나면 **원인 먼저**, 해결책은 그다음.
- 사용자가 "직접 만들어줘/고쳐줘"라고 명시할 때만 대신 작업한다.

### 개발 흐름 (TDD)
1. 테스트 먼저 작성 → `pytest` → **빨간불 확인**
2. 코드 작성 → `pytest` → **초록불 확인**
3. 커밋 → 푸시 → 프로젝트 지식 탭 **GitHub Sync** (이 셋이 한 덩어리)

### Git 규칙
- 형식: `type(scope): 한글 메시지` + Description (Summary + Description 필수)
- type: `feat` `fix` `refactor` `docs` `test` `chore` (영문 유지)
- 성격이 다른 작업은 커밋 분리. 기준: **"이것만 따로 되돌리고 싶을 수 있는가?"**
- 각 커밋은 최소 "실행되는 상태" 유지 → 테스트와 그 코드는 **같은 커밋**
- PowerShell: `git commit -m "Summary" -m "Description"` / GitHub Desktop 혼용

---

## 3. 개발 환경

| 항목 | 값 |
|---|---|
| OS / 터미널 | Windows / VS Code PowerShell |
| Python | **3.14.8** (conda 환경 `jeoksn`) |
| conda 위치 | `C:\Users\Windows\miniconda3\envs\jeoksn` |
| 환경 변수 | `PYTHONNOUSERSITE=1` (conda env config vars로 설정) |
| 설치 | `pip install -e ".[dev]"` (editable 설치, 개발 의존성 pytest) |
| pytest | 9.1.1 |
| VS Code 인터프리터 | `jeoksn (3.14.8)` 선택 완료 |

### 새 세션 시작 체크
```powershell
cd D:\_dev\jeoksn
conda activate jeoksn
pytest            # 22 passed 확인
git status        # working tree clean 확인
```

### 주의
- 프로젝트 폴더를 옮기거나 이름을 바꾸면 `pip install -e ".[dev]"` 다시 실행 (editable 설치는 경로를 기억함)
- `base` 환경에는 아무것도 설치하지 않는다

---

## 4. 저장소 구조와 설정

```
jeoksn/
├── README.md
├── pyproject.toml          # requires-python >=3.12, dependencies=[], dev=[pytest]
├── .gitignore              # .venv/ .vscode/ __pycache__/ *egg-info/ .pytest_cache/
├── .gitattributes          # LF 통일, .bat/.cmd/.ps1은 CRLF, 이미지/PDF/xlsx binary
├── docs/
│   └── HANDOFF.md          # 이 문서
├── src/jeoksn/
│   ├── __init__.py
│   ├── rounding.py
│   ├── material.py
│   ├── labor.py
│   ├── expense.py
│   ├── overhead.py
│   └── data/rates.json
└── tests/
    ├── test_rounding.py
    ├── test_material.py
    ├── test_labor.py
    ├── test_expense.py
    └── test_overhead.py
```

- `pyproject.toml`의 `[tool.setuptools.package-data] jeoksn = ["data/*.json"]` → 이게 있어야 rates.json이 패키지에 포함됨
- `src` 레이아웃: 테스트가 "설치된 패키지"를 검사하도록 하기 위함

---

## 5. 지금까지 만든 것 (1단계 부품 계산기 — 완료)

**테스트 22개 전부 통과.** 자료의 풀이집 계산 문제 11개를 모두 코드로 옮김.

### 공통 설계 원칙
- 돈·비율 계산은 전부 **`Decimal`**. float 입력은 `to_decimal()`이 `str()`을 거쳐 변환
- 끝자리 처리는 **함수마다 명시** (절사 / 사사오입 / 올림). 파이썬 `round()`는 은행가 반올림이라 사용 금지
- 인자가 여러 개인 함수는 `*`로 **키워드 전용** (순서 실수 방지)
- 모르는 값(미분류 작업 종류, 미등록 업종)은 조용히 넘기지 않고 **`ValueError`**
- 규정·해마다 바뀌는 숫자는 `rates.json`, 수학·정의는 코드 상수
- 결과가 여러 항목이면 **dataclass 영수증**으로 반환 (`DailyWage`)

### 모듈별 API

#### `rounding.py`
| 함수 | 설명 |
|---|---|
| `to_decimal(value)` | 어떤 숫자든 Decimal로 (str 경유) |
| `_unit(places)` | 자릿수 → 눈금 (0→1, 2→0.01) |
| `truncate(value, places=0)` | 절사 (ROUND_DOWN) |
| `round_half_up(value, places=0)` | 사사오입 (ROUND_HALF_UP) |

#### `material.py`
| 함수 | 끝자리 | 풀이집 |
|---|---|---|
| `material_surcharge_rate(source_qty, product_qty)` → % | 둘째 자리 절사 | 계산 1 (2.05%), 계산 2 (5%) |
| `indirect_material_per_unit(*, total_direct_material, total_labor, total_indirect_material, reclass_to_direct, unit_direct_material, unit_labor)` | 원 미만 사사오입 | 계산 3 (7,251원) |

- 할증율 분모는 **제품량**. 면적·길이·무게 공용
- 원가법: 간접재료비에서 뺀 금액은 **직접재료비에 더한다**

#### `labor.py`
| 함수/클래스 | 끝자리 | 풀이집 |
|---|---|---|
| `NORMAL_WORK`, `ABNORMAL_WORK` (set) | — | — |
| `retirement_allowance_rate(*, total_labor, eligible_labor)` → % | 둘째 자리 절사 | 계산 5 (6.87%) |
| `normal_labor_hours(hours: dict)` | — | 계산 6 (21,900Hr) |
| `labor_hours_per_unit(*, total_hours, completed, beginning_wip, beginning_progress, ending_wip, ending_progress)` | 둘째 자리 절사 ⚠️ | 계산 10 (10.95Hr) |
| `DailyWage(base, overtime, bonus, retirement, work_hours)` + `.total`, `.hourly` | hourly 원 미만 절사 | — |
| `daily_wage(*, market_wage, overtime_hours, bonus_rate, years_of_service, regular_hours=8, overtime_premium="1.5")` | 각 항목 원 미만 절사 ⚠️ | 계산 9 (16,183원/Hr) |

- 노임단가: 기본급은 **시중노임**. 업체 기본급·자격수당·월 근무일수는 입력칸 자체가 없음 (미끼 차단)
- 퇴직급여충당금은 근속 1년 이상만

#### `expense.py`
| 함수/클래스 | 끝자리 | 풀이집 |
|---|---|---|
| `DEFAULT_RND_LIFE = 5` | — | — |
| `rnd_cost_per_unit(*, yearly_costs, annual_output, useful_life=None)` | 원 미만 절사 | 계산 7 (666원/EA) |
| `Delivery(region, quantity, fare_per_truck)` | — | — |
| `freight_per_unit(*, deliveries, truck_capacity, vat_included=True, vat_rate="0.1")` | 원 미만 절사 | 계산 11 (553원) |

- 내용연수 무신고(`None`) → 5년
- 트럭 대수는 `math.ceil` 올림, 운임은 부가세 제외 후 계산

#### `overhead.py`
| 함수 | 끝자리 | 풀이집 |
|---|---|---|
| `_load_rates()` (`@cache`, `importlib.resources`, `parse_float=Decimal`) | — | — |
| `general_admin_cap(industry)` | — | — |
| `general_admin_rate(*, cost_of_sales, sga_total, excluded: dict, industry)` → % | 둘째 자리 절사 후 `min(실제, 상한)` | 계산 4 (5.85%) |
| `defense_indirect_expense(*, direct_labor, indirect_labor, rate)` | 원 미만 절사 | 계산 8 (1,800,000원) |

- 일반관리비율 분모는 **매출원가** (매출액 아님)
- 방산 간접경비 기준은 **노무비 전체(직접+간접)**

#### `data/rates.json` 구조
```json
{
  "general_admin_cap": {
    "source": "예정가격 작성기준 별표3",
    "checked": "2026-10-16",
    "rates": { "나무제품": 9, "제1차금속제품": 6, "조립금속제품": 7, "수입물품": 8 }
  }
}
```

### 경계 테스트 (풀이집 외에 일부러 추가한 것)
- 은행가 반올림 함정 (`round_half_up("2.5") == 3`)
- float 오차 유입 (`truncate(0.1 + 0.2, 2) == 0.30`)
- 미분류 작업 종류 → ValueError
- 근속 1년 미만 → 퇴직급여 0원
- 트럭 올림 (201개 / 200개 적재 → 2대)
- 일반관리비 상한 적용 (6.05% → 6%, drill 오답노트 예시)
- 미등록 업종 → ValueError

---

## 6. 미해결 · 확인 필요 사항

### 확인 안 된 가정 (교재로 검증 필요)
- ⚠️ `labor_hours_per_unit` 끝자리: 풀이집에 규칙 없음. 둘째 자리 절사로 가정 (10.952는 절사/반올림 모두 10.95)
- ⚠️ `daily_wage` 제수당·상여금 끝자리: 예제 숫자가 딱 떨어져서 검증 불가. 원 미만 절사로 가정 (퇴직급여 절사만 풀이집으로 확인됨)
- ⚠️ `rates.json`에 업종 4개만 있음. 나머지는 **사용자가 별표3 보고 직접 채우기로 함** (기억에 의존한 규정 숫자 입력 금지)

### 남은 작업 (작은 것)
- [ ] `refactor(labor)`: `/ 12` 두 곳을 `MONTHS_PER_YEAR = 12` 상수로 교체
- [ ] `chore(rates)`: 별표3 나머지 업종 상한 추가 (데이터만 바뀌니 따로 커밋)
- [ ] README에 1단계 진행 상황 반영 (선택)

### 설계 결정 대기
- **입력 비율 vs 출력 비율 표기가 섞여 있음**
  - 입력: 소수 (`progress="0.5"`, `bonus_rate=3`, `rate="0.3"`)
  - 출력: 퍼센트 숫자 (`2.05` = 2.05%, `6.87`, `5.85`)
  - 조립기에서 일반관리비율(% 출력)을 곱셈에 쓸 때 `/100`이 필요해짐 → 조립기 설계 시 통일 규칙을 정할 것

---

## 7. 다음 세션 첫 작업: 조립기 (원가계산서)

### 목표
부품 계산기들의 결과를 모아 **원가계산서 한 장**으로 쌓는 모듈 (예: `statement.py` + `test_statement.py`).

```
재료비 + 노무비 + 경비          = 제조원가
제조원가 × 일반관리비율         = 일반관리비
이윤 대상액 × 이윤율            = 이윤
제조원가 + 일반관리비 + 이윤    = 총원가
```

### 핵심 함정: 이윤 대상액
자료(3강 2교시 문제풀이 PDF) 해설 기준:
- "이윤은 영업이익을 말하며 **제조원가 중 노무비, 경비와 일반관리비의 합계액**에 이윤율을 곱한다"
- "제조원가에서 **재료비, 외주가공비, 기술료 등을 제외**하고 일반관리비를 합산한 금액"
- 수입품: 일반관리비율 8%, 이윤율 10% (국가계약법 시행규칙 제8조)
- 업종별 이윤율 상한은 **교재로 확인 후** rates.json에 추가 (기억으로 넣지 말 것)

### 시작 순서 제안
1. 테스트용 **종합 문제(원가계산서 전체)**를 자료에서 찾기
   - 풀이집 11문제는 전부 비목 단위라 종합 문제가 없음
   - 후보: `03_manufacturing-cost/3강_2교시_제조원가+문제풀이(전체).pdf` (재료대금 5,350,000원 등이 나오는 문제 근처)
2. 비율 표기 통일 규칙 결정 (6장 참고)
3. 원가계산서 dataclass 설계 (`DailyWage`처럼 항목별 영수증 + `@property` 합계)
4. 이윤 대상액에서 재료비·외주가공비·기술료가 빠지는지 검증하는 테스트를 반드시 포함

---

## 8. 자료 위치와 취급 규칙

- 회사 제공 원가분석사 자료: `G:\내 드라이브\_private\Kcost_23th` (`D:\Kcost_23th`에도 있음)
  - `03_manufacturing-cost/` 제조원가 강의자료·문제풀이 PDF
  - `04_construction-cost/` 공사원가 (2단계용)
  - `05_cost-regulations/` 제도·법규 (5단계용)
  - `99_summary/제조원가 주관식 풀이집.html` ← 계산 1~11 정답 출처 (KCOST 교재 대조)
  - `99_summary/kcost_drill.py`, `오답노트.csv` ← 기존 연습 프로그램 (참고용)
- 🚫 **자료 원본은 절대 저장소에 넣지 않는다.** 테스트에는 문제 숫자와 정답만 옮긴다.

---

## 9. 커밋 히스토리 (2026-10-15 ~ 10-16)

```
chore(git):      git 추적 규칙 설정
chore(setup):    패키지 구조 및 pyproject 설정
docs(readme):    프로젝트 소개 작성
feat(rounding):  절사·사사오입 함수 추가
docs(rounding):  테스트 주석 오타 수정
feat(material):  재료할증율·원가법 간접재료비 계산 추가
feat(labor):     퇴직급여충당금 비율·정상 노무공수·단위당 공수 계산 추가
feat(labor):     노임단가 계산 추가
feat(expense):   연구개발비·운반비 단위당 계산 추가
feat(overhead):  일반관리비율·방산 간접경비 계산 추가
```

---

## 10. 지금까지 배운 개념 (설명 중복 방지용)

Decimal과 float 오차 / 절사·사사오입·올림 / 은행가 반올림 / TDD / `*` 키워드 전용 인자 / set과 집합 빼기 / `raise ValueError`와 `pytest.raises` / dataclass(`frozen=True`) / `@property` / 기본값 인자 / `None`과 `is None` / generator 표현식과 `sum()` / `math.ceil` / JSON과 `parse_float` / `@cache` / `importlib.resources.files` / src 레이아웃 / editable 설치 / conda 환경 / pyproject vs requirements vs environment.yml / `.gitattributes` 줄바꿈 / 매직 넘버

→ 이미 배운 개념은 짧게 복습만 하고, 새 개념에 비유 설명을 집중한다.
