
import streamlit as st
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

st.set_page_config(page_title="서논술형 자동 채점", page_icon="📝", layout="wide")

# ============================================================
# 1. 채점 데이터
# ============================================================

@dataclass
class Criterion:
    required_groups: List[List[str]]
    # 각 group에서 하나 이상의 의미 표현이 충족되어야 함
    forbidden_patterns: List[str]
    # 오개념/반대 방향 표현
    conclusion_groups: List[List[str]]
    # 결론 방향을 판단하기 위한 의미 그룹
    method: str | None = None
    method_patterns: List[str] | None = None
    score: int = 1

def norm(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text

def has_any(text: str, patterns: List[str]) -> bool:
    return any(p in text for p in patterns)

def groups_met(text: str, groups: List[List[str]]) -> bool:
    return all(has_any(text, g) for g in groups)

def contains_forbidden(text: str, patterns: List[str]) -> bool:
    return has_any(text, patterns)

# ------------------------------------------------------------
# 설명 방법 판정
# ------------------------------------------------------------
METHOD_PATTERNS = {
    "정의": [
        "정의", "이란", "말한다", "뜻이다", "의미한다"
    ],
    "예시": [
        "예를 들어", "예로는", "예로", "대표적으로", "사례로", "예를 들면"
    ],
    "인과": [
        "때문에", "이기 때문에", "해서", "하므로", "따라서",
        "그 결과", "결과적으로", "원인", "결과"
    ],
    "분석": [
        "구성", "요소", "부분", "여러 요소", "종합적으로", "나뉘어"
    ],
    "비교와 대조": [
        "반면", "하지만", "그러나", "차이", "공통점",
        "다르", "같", "보다", "에 비해"
    ],
    "분류와 구분": [
        "종류", "분류", "구분", "나뉘", "묶"
    ],
}

def method_present(text: str, method: str) -> bool:
    t = norm(text)

    if method == "비교와 대조":
        # 비교/대조는 표지어 하나만으로 충분하지 않음.
        # 서로 다른 대상을 비교하는 흔적을 요구.
        targets = [
            ("쉬운", "어려운"),
            ("비교적 쉬운", "지나치게 어려운"),
            ("실생활 전기", "정전기"),
            ("실생활에서 사용하는 전기", "정전기"),
            ("인간", "인공지능"),
            ("인간의 예술", "인공지능의 예술"),
            ("인간의 작품", "인공지능"),
        ]
        if any(a in t and b in t for a, b in targets):
            return True
        return any(p in t for p in METHOD_PATTERNS[method]) and (
            "하지만" in t or "반면" in t or "차이" in t or "다르" in t
        )

    if method == "인과":
        return any(p in t for p in METHOD_PATTERNS[method])

    if method == "예시":
        return any(p in t for p in METHOD_PATTERNS[method])

    if method == "정의":
        return any(p in t for p in METHOD_PATTERNS[method])

    if method == "분석":
        return any(p in t for p in METHOD_PATTERNS[method])

    if method == "분류와 구분":
        return any(p in t for p in METHOD_PATTERNS[method])

    return False

def labeled_method(text: str) -> str | None:
    # 학생이 괄호 안에 방법명을 쓴 경우 우선 인식
    for method in METHOD_PATTERNS:
        if method in text:
            return method
    return None

# ============================================================
# 2. 문항별 채점
# ============================================================

SETS = {
    "1세트 · 사회적 촉진/억제": {
        "items": {
            "1-㉠": {
                "answer": "비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제",
                "required": [["쉬운", "난이도가 낮은", "큰 노력을 들일 필요가 없는", "노력이 많이 필요하지 않은"]],
                "forbidden": ["어려운 과제", "지나치게 어려운 과제"],
            },
            "1-㉡": {
                "answer": "충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가짐",
                "required": [["혼자"], ["집중"], ["충분히 연습", "연습하며", "익숙해질 때까지", "차분하게"]],
                "partial_required": [["혼자"], ["집중"]],
                "forbidden": ["다른 사람들과 함께", "친구들과 함께", "공부 모임"],
            },
            "1-㉢": {
                "answer": "사회적 억제",
                "required": [["사회적 억제"]],
                "forbidden": ["사회적 촉진"],
            },
            "2": {
                "answers": [
                    {
                        "label": "예시 + 비교와 대조",
                        "sample": "예를 들어 비교적 쉬운 과제는 커피숍이나 도서관에서 하거나 공부 모임을 만들어 다른 사람들과 함께 하는 것이 효율적일 수 있다. (예시) 반면 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 것이 좋다. (비교와 대조)"
                    },
                    {
                        "label": "비교와 대조 + 인과",
                        "sample": "비교적 쉬운 과제는 다른 사람들과 함께 하는 것이 효율적일 수 있지만, 지나치게 어렵거나 도전이 필요한 과제는 혼자 집중하는 것이 좋다. (비교와 대조) 어려운 과제는 충분히 연습하여 익숙해져야 하므로 차분하게 혼자 집중하는 것이 좋다. (인과)"
                    }
                ],
                "logic": "two_methods_and_content",
            },
            "3": {
                "sample": "시각: 다른 사람 없이 한 학생이 조용한 공간에서 어려운 과제에 집중하는 모습을 보여준다. 효과: 어려운 과제는 혼자 차분하게 집중하는 것이 좋다는 내용을 전달한다. 청각: 배경음악을 거의 사용하지 않고 연필 소리나 책장 넘기는 소리처럼 작은 소리를 들려준다. 효과: 차분하게 혼자 집중하는 환경을 전달한다.",
                "logic": "video_easy_hard",
            }
        }
    },
    "2세트 · 정전기": {
        "items": {
            "1-㉠": {
                "answer": "높은 곳에 고여 있는 물",
                "required": [["고여 있는 물", "고인 물"], ["높은 곳", "높은 곳에"]],
                "forbidden": ["흐르는 물"],
            },
            "1-㉡": {
                "answer": "전하가 이동하지 않고 머물러 있음",
                "required": [["전하"], ["이동하지", "머물러", "정지"]],
                "forbidden": ["전하가 이동함"],
            },
            "1-㉢": {
                "answer": "위험하지 않음",
                "required": [["위험하지", "안전", "위험성이 없다"]],
                "forbidden": ["감전 위험", "위험이 있음", "위험함"],
            },
            "2": {
                "answers": [
                    {
                        "label": "정의 + 비교와 대조",
                        "sample": "정전기는 전하가 이동하지 않고 머물러 있는 전기이다. (정의) 실생활에서 사용하는 전기는 전하가 이동하지만, 정전기는 전하가 이동하지 않고 머물러 있다. (비교와 대조)"
                    },
                    {
                        "label": "정의 + 인과",
                        "sample": "정전기는 전하가 이동하지 않고 머물러 있는 전기이다. (정의) 정전기는 전하가 이동하지 않고 머물러 있기 때문에 위험하지 않다. (인과)"
                    }
                ],
                "logic": "two_methods_and_content",
            },
            "3": {
                "sample": "시각: 높은 곳의 물탱크에 물이 가득 차 있지만 흐르거나 떨어지지 않고 고여 있는 모습을 보여준다. 효과: 정전기는 높은 곳에 고여 있는 물과 같고 전하가 이동하지 않는다는 특징을 전달한다. 청각: 물이 흐르는 소리를 사용하지 않고 조용한 분위기를 만든다. 효과: 전하가 이동하지 않고 머물러 있는 정전기의 특성을 강조한다.",
                "logic": "video_static",
            }
        }
    },
    "3세트 · AI와 예술": {
        "items": {
            "1-㉠": {
                "answer": "로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 하는 것",
                "required": [["로봇"], ["피겨 스케이팅", "피겨"], ["완벽", "실수 없이", "한 번의 실수 없이"]],
                "forbidden": ["인간 선수", "실수를 많이"],
            },
            "1-㉡": {
                "answer": "감정을 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 예술로 보기 어렵다",
                "required": [["감정", "감정을 느끼지 못"], ["독자적인 철학", "철학"], ["이야기"], ["예술로 보기 어렵", "예술이 아니"]],
                "forbidden": ["인간이 아니기 때문에", "가치가 없다", "가치가 전혀 없다"],
            },
            "1-㉢": {
                "answer": "기존 미술계에 큰 변화를 가져오고 예술의 범주를 확장할 수 있다는 점에서 상징적 가치가 있음",
                "required": [["미술계", "미술계에", "미술"], ["변화"], ["예술의 범주", "예술의 범위", "범주를 확장", "범위를 확장"], ["가치", "의미"]],
                "forbidden": ["가치가 없다", "가치가 전혀 없다"],
            },
            "2": {
                "answers": [
                    {
                        "label": "비교와 대조 + 인과",
                        "sample": "인간의 예술에는 작가의 감정과 철학, 삶의 경험 등이 담기지만 인공지능에는 감정이나 독자적인 철학과 이야기가 없다. (비교와 대조) 인공지능은 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 이를 예술로 보기는 어렵다. (인과)"
                    },
                    {
                        "label": "분석 + 인과",
                        "sample": "인간의 작품에는 작가의 감정, 철학, 삶의 경험, 관점, 환경 등의 요소가 종합적으로 담겨 있다. (분석) 인공지능은 감정이나 독자적인 철학과 이야기가 없기 때문에 이를 인간의 예술과 같은 의미의 예술로 보기는 어렵다. (인과)"
                    }
                ],
                "logic": "two_methods_and_content",
            },
            "3": {
                "sample": "시각: 작가가 자신의 삶의 경험과 주변 환경을 바탕으로 작품을 만드는 모습을 보여준다. 효과: 인간의 예술에는 작가의 경험과 관점, 환경 등이 담긴다는 점을 전달한다. 청각: 작가가 작품에 담은 자신의 생각과 감정을 이야기하는 목소리를 들려준다. 효과: 인간의 예술에는 작가의 고유한 감정과 철학이 담긴다는 점을 전달한다.",
                "logic": "video_human_art",
            }
        }
    }
}

def check_short(item: Dict, text: str) -> Tuple[str, str]:
    t = norm(text)
    if contains_forbidden(t, item.get("forbidden", [])):
        return "❌ 오답", "지문의 개념과 반대되는 특성이 포함되어 있습니다."

    if groups_met(t, item.get("required", [])):
        return "✅ 정답", "필수 의미 요소가 모두 확인되었습니다."

    # 부분 정답: 1-㉡처럼 핵심 일부가 맞는 경우
    partial = item.get("partial_required")
    if partial and groups_met(t, partial):
        return "🟡 부분 정답", "핵심 방향은 맞지만 일부 필수 내용이 빠졌습니다."

    return "❌ 오답", "필수 의미 요소가 충분히 확인되지 않았습니다."

def check_explanation(text: str, set_name: str) -> Tuple[str, str]:
    t = norm(text)

    # 반대 방향 오개념
    bad = []
    if set_name.startswith("1세트"):
        bad = ["쉬운 과제는 혼자", "어려운 과제는 함께", "어려운 과제도 다른 사람들과 함께"]
        content_ok = (
            ("쉬운" in t and ("함께" in t or "다른 사람" in t)) or
            ("어려운" in t and ("혼자" in t or "집중" in t))
        )
    elif set_name.startswith("2세트"):
        bad = ["정전기는 전하가 이동한다", "전하가 이동하기 때문에 위험하지 않", "전압이 낮아서 안전"]
        content_ok = (
            ("정전기" in t and ("이동하지" in t or "머물" in t)) and
            ("정의" in t or "비교" in t or "대조" in t or "때문에" in t)
        )
    else:
        bad = ["ai는 감정을 느낀다", "인공지능은 독자적인 철학이 있다", "가치가 전혀 없다"]
        content_ok = (
            ("인공지능" in t or "ai" in t) and
            ("예술로 보기 어렵" in t or "예술이 아니다" in t or "가치" in t)
        )

    if has_any(t, bad):
        return "❌ 오답", "한 개념의 특성을 다른 개념에 적용했거나 지문과 반대되는 결론이 포함되어 있습니다."

    # 설명 방법명 또는 의미 기반 방법 판정
    found = [m for m in METHOD_PATTERNS if method_present(t, m)]
    labeled = [m for m in METHOD_PATTERNS if m in text]

    # 비유는 1쪽 설명 방법에 포함되지 않으므로 방법으로 인정하지 않음
    if len(set(found)) < 2:
        return "🟡 조건 미충족", "서로 다른 설명 방법 2가지가 실제 문장에 드러나는지 확인할 수 없습니다."

    # 세트별 결론 방향
    if set_name.startswith("1세트"):
        conclusion = (
            ("쉬운" in t and ("함께" in t or "다른 사람" in t)) and
            ("어려운" in t and ("혼자" in t or "집중" in t))
        )
    elif set_name.startswith("2세트"):
        conclusion = (
            ("정전기" in t and ("이동하지" in t or "머물" in t)) and
            ("전기" in t and ("이동" in t or "흐르" in t))
        ) or ("정전기" in t and "위험하지" in t)
    else:
        conclusion = (
            ("인공지능" in t or "ai" in t) and
            ("예술로 보기 어렵" in t or "예술이 아니다" in t)
            and ("가치" in t or "변화" in t or "범주" in t)
        )

    if not conclusion:
        return "❌ 오답", "문항에서 요구한 결론 방향이 충분히 드러나지 않습니다."

    # 지문 밖 대표적인 외부 지식
    external = ["저작권", "일자리", "윤리", "편향", "표절"]
    if set_name.startswith("3세트") and has_any(t, external):
        return "🟡 검토 필요", "지문에 없는 외부 내용이 포함되어 있어 지문 활용 조건을 확인해야 합니다."

    return "✅ 정답", f"설명 방법 {', '.join(found[:3])}이 실제 문장에 드러나며 핵심 결론도 확인됩니다."

def check_video(text: str, set_name: str) -> Tuple[str, str]:
    t = norm(text)

    if set_name.startswith("1세트"):
        required = (
            has_any(t, ["어려운 과제", "도전이 필요한 과제"]) and
            has_any(t, ["혼자", "혼자서"]) and
            has_any(t, ["차분", "집중"]) and
            has_any(t, ["효과", "전달", "보여주"])
        )
        forbidden = ["친구들과 함께", "다른 사람들과 함께"]
    elif set_name.startswith("2세트"):
        required = (
            has_any(t, ["고여", "고인", "높은 곳"]) and
            has_any(t, ["이동하지", "머물", "조용"]) and
            has_any(t, ["효과", "전달", "강조"])
        )
        forbidden = ["흐르는 물", "물이 거세게", "폭포수가 콸콸"]
    else:
        required = (
            has_any(t, ["작가", "인간"]) and
            has_any(t, ["감정", "철학", "경험", "관점", "환경"]) and
            has_any(t, ["효과", "전달", "보여주"])
        )
        forbidden = ["인공지능이 감정을 느낀다", "ai가 감정을 느낀다"]

    if has_any(t, forbidden):
        return "❌ 오답", "장면의 대상 또는 특성이 반대로 설정되어 있습니다."
    if required:
        return "✅ 정답", "연출 내용과 지문 근거가 연결되어 있습니다."
    return "🟡 검토 필요", "연출은 다양하게 허용되지만 지문의 핵심 특성과 효과가 충분히 연결되는지 확인해야 합니다."

# ============================================================
# 3. Streamlit UI
# ============================================================

st.title("📝 2회고사 대비 서논술형 자동 채점")
st.caption("1~3세트의 모범답안과 채점 기준을 바탕으로 한 의미 기반 보조 채점 앱")

st.info(
    "⚠️ 이 앱은 완전 자동 확정 채점보다 '1차 자동 판정 + 교사 검토'를 전제로 합니다. "
    "특히 설명 방법과 영상 연출은 표현의 다양성이 크므로 '검토 필요'를 별도로 표시합니다."
)

set_name = st.sidebar.selectbox("세트 선택", list(SETS.keys()))
item_name = st.sidebar.selectbox("문항 선택", list(SETS[set_name]["items"].keys()))
item = SETS[set_name]["items"][item_name]

st.subheader(f"{set_name} · {item_name}")

if "answers" not in st.session_state:
    st.session_state.answers = {}

if item_name.startswith("1-"):
    st.markdown("### 학생 답안")
    answer = st.text_input("답안을 입력하세요", key=f"{set_name}-{item_name}")
    if st.button("채점하기", type="primary"):
        result, reason = check_short(item, answer)
        st.session_state.answers[item_name] = answer
        if result.startswith("✅"):
            st.success(f"{result} — {reason}")
        elif result.startswith("🟡"):
            st.warning(f"{result} — {reason}")
        else:
            st.error(f"{result} — {reason}")

    st.markdown("### 모범 답안")
    st.write(item["answer"])

elif item_name == "2":
    st.markdown("### 학생 답안")
    answer = st.text_area(
        "두 문장을 입력하세요. 설명 방법 명칭을 쓰지 않아도 의미가 드러나면 인정하도록 설계되어 있습니다.",
        height=180,
        key=f"{set_name}-{item_name}"
    )
    if st.button("채점하기", type="primary"):
        result, reason = check_explanation(answer, set_name)
        if result.startswith("✅"):
            st.success(f"{result} — {reason}")
        elif result.startswith("🟡"):
            st.warning(f"{result} — {reason}")
        else:
            st.error(f"{result} — {reason}")

    st.markdown("### 선택 가능한 모범 답안")
    for ans in item["answers"]:
        st.markdown(f"**{ans['label']}**")
        st.write(ans["sample"])

else:
    st.markdown("### 학생 답안")
    answer = st.text_area(
        "시각 요소 / 효과 / 청각 요소 / 효과를 자유롭게 작성하세요.",
        height=240,
        key=f"{set_name}-{item_name}"
    )
    if st.button("채점하기", type="primary"):
        result, reason = check_video(answer, set_name)
        if result.startswith("✅"):
            st.success(f"{result} — {reason}")
        elif result.startswith("🟡"):
            st.warning(f"{result} — {reason}")
        else:
            st.error(f"{result} — {reason}")

    st.markdown("### 모범 답안")
    st.write(item["sample"])

st.divider()
st.caption(
    "채점 원칙: 핵심 의미는 표현이 달라도 인정 · 선택한 설명 방법은 실제 기능이 드러나야 함 · "
    "개념의 특성을 서로 뒤바꾸면 오답 · 요구된 결론 방향이 명확해야 정답."
)
