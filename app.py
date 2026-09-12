
import streamlit as st
import re

st.set_page_config(
    page_title="서논술형 답안 연습",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# 데이터
# ============================================================

COMMON_CONCEPTS = {
    "정의": "대상의 뜻이나 개념을 밝히는 방법",
    "예시": "구체적인 예를 들어 대상을 설명하는 방법",
    "인과": "원인과 결과를 연결하여 설명하는 방법",
    "분석": "대상을 여러 요소나 부분으로 나누어 설명하는 방법",
    "비교·대조": "둘 이상의 대상의 공통점이나 차이점을 드러내는 방법",
    "분류·구분": "기준에 따라 대상을 종류별로 묶거나 나누는 방법",
}

SETS = {
    "1세트 · 사회적 촉진과 억제": {
        "summary": [
            "🟢 쉬운 과제 → 다른 사람들과 함께하면 효율적일 수 있음",
            "🔵 어려운 과제 → 충분히 연습한 뒤 혼자 차분하게 집중",
            "🧠 쉬운 과제와 관련 → 사회적 촉진",
            "🧠 어려운 과제와 관련 → 사회적 억제",
        ],
        "items": {
            "1번 · 표 완성": {
                "type": "short",
                "questions": [
                    ("㉠", "비교적 쉬운 취미 생활이나 큰 노력을 들일 필요가 없는 과제",
                     [["쉬운", "난이도가 낮은", "큰 노력을 들일 필요가 없는", "노력이 많이 필요하지 않은"]],
                     ["어려운 과제", "지나치게 어려운 과제"]),
                    ("㉡", "충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 시간을 가짐",
                     [["혼자"], ["집중"], ["충분히 연습", "연습하며", "익숙해질 때까지", "차분하게"]],
                     ["다른 사람들과 함께", "친구들과 함께", "공부 모임"]),
                    ("㉢", "사회적 억제", [["사회적 억제"]], ["사회적 촉진"]),
                ],
                "hint": "표에서 ‘쉬운 과제’와 ‘어려운 과제’에 대응하는 방법과 심리 현상을 찾아보세요.",
            },
            "2번 · 설명문 작성": {
                "type": "explanation",
                "hint": "쉬운 과제와 어려운 과제의 학습 방법이 어떻게 다른지 생각해 보세요.",
                "methods": ["예시", "비교·대조", "인과"],
                "frames": {
                    "예시": "예를 들어, ＿＿＿＿은/는 ＿＿＿＿하다.",
                    "비교·대조": "＿＿＿＿은/는 ＿＿＿＿하지만, ＿＿＿＿은/는 ＿＿＿＿하다.",
                    "인과": "＿＿＿＿은/는 ＿＿＿＿하기 때문에 ＿＿＿＿하다.",
                },
                "samples": [
                    ("예시 + 비교·대조",
                     "예를 들어 비교적 쉬운 과제는 커피숍이나 도서관에서 하거나 공부 모임을 만들어 다른 사람들과 함께 하는 것이 효율적일 수 있다. (예시) 반면 지나치게 어렵거나 도전이 필요한 과제는 충분히 연습하며 익숙해질 때까지 차분하게 혼자 집중하는 것이 좋다. (비교와 대조)"),
                    ("비교·대조 + 인과",
                     "비교적 쉬운 과제는 다른 사람들과 함께 하는 것이 효율적일 수 있지만, 지나치게 어렵거나 도전이 필요한 과제는 혼자 집중하는 것이 좋다. (비교와 대조) 어려운 과제는 충분히 연습하여 익숙해져야 하므로 차분하게 혼자 집중하는 것이 좋다. (인과)")
                ],
            },
            "3번 · 영상 기획": {
                "type": "video",
                "hint": "장면 2는 ‘어렵고 도전적인 과제’를 할 때 필요한 환경을 보여줘야 해요.",
                "visual_options": [
                    "혼자 공부하는 학생을 보여준다.",
                    "조용한 공간에서 한 학생이 어려운 과제에 집중하는 모습을 보여준다.",
                    "다른 사람의 방해 없이 과제에 집중하는 모습을 보여준다.",
                ],
                "audio_options": [
                    "배경음악을 거의 사용하지 않는다.",
                    "연필 소리나 책장 넘기는 소리처럼 작은 소리를 들려준다.",
                    "조용한 분위기를 만든다.",
                ],
                "sample": "시각: 조용한 공간에서 한 학생이 다른 사람 없이 어려운 과제에 집중하는 모습을 보여준다. 효과: 어려운 과제는 혼자 차분하게 집중하는 것이 좋다는 내용을 전달한다. 청각: 배경음악을 거의 사용하지 않고 작은 소리를 들려준다. 효과: 차분하게 혼자 집중하는 환경을 전달한다.",
            },
        },
    },
    "2세트 · 정전기": {
        "summary": [
            "💧 실생활 전기 → 흐르는 물 → 전하가 이동함 → 위험이 있음",
            "💧 정전기 → 높은 곳에 고여 있는 물 → 전하가 이동하지 않고 머물러 있음 → 위험하지 않음",
            "⚠️ 정전기는 전압이 매우 높지만 위험하지 않음",
        ],
        "items": {
            "1번 · 표 완성": {
                "type": "short",
                "questions": [
                    ("㉠", "높은 곳에 고여 있는 물", [["고여 있는 물", "고인 물"], ["높은 곳", "높은 곳에"]], ["흐르는 물"]),
                    ("㉡", "전하가 이동하지 않고 머물러 있음", [["전하"], ["이동하지", "머물러", "정지"]], ["전하가 이동함"]),
                    ("㉢", "위험하지 않음", [["위험하지", "안전", "위험성이 없다"]], ["감전 위험", "위험이 있음", "위험함"]),
                ],
                "hint": "실생활 전기와 정전기를 ‘물’과 ‘전하’의 상태로 짝지어 보세요.",
            },
            "2번 · 설명문 작성": {
                "type": "explanation",
                "hint": "정전기가 무엇인지 먼저 설명한 뒤, 실생활 전기와 어떻게 다른지 또는 왜 위험하지 않은지 이어서 설명해 보세요.",
                "methods": ["정의", "비교·대조", "인과"],
                "frames": {
                    "정의": "＿＿＿＿이란 ＿＿＿＿을/를 말한다.",
                    "비교·대조": "실생활에서 사용하는 전기는 ＿＿＿＿하지만, 정전기는 ＿＿＿＿하다.",
                    "인과": "정전기는 ＿＿＿＿하기 때문에 ＿＿＿＿하다.",
                },
                "samples": [
                    ("정의 + 비교·대조",
                     "정전기는 전하가 이동하지 않고 머물러 있는 전기이다. (정의) 실생활에서 사용하는 전기는 전하가 이동하지만, 정전기는 전하가 이동하지 않고 머물러 있다. (비교와 대조)"),
                    ("정의 + 인과",
                     "정전기는 전하가 이동하지 않고 머물러 있는 전기이다. (정의) 정전기는 전하가 이동하지 않고 머물러 있기 때문에 위험하지 않다. (인과)")
                ],
                "note": "※ ‘비유’는 지문에 사용되지만 1쪽의 설명 방법 목록에는 없으므로 설명 방법 선택지에서는 제외합니다.",
            },
            "3번 · 영상 기획": {
                "type": "video",
                "hint": "장면 2에서는 ‘높은 곳에 고여 있는 물’처럼 움직이지 않는 정전기의 특징을 보여줘야 해요.",
                "visual_options": [
                    "높은 곳의 물탱크에 물이 가득 차 있지만 흐르지 않고 고여 있는 모습을 보여준다.",
                    "물이 높은 곳에 고여 움직이지 않는 모습을 보여준다.",
                    "물이 떨어지지 않고 그대로 머물러 있는 모습을 보여준다.",
                ],
                "audio_options": [
                    "물이 흐르는 소리를 사용하지 않고 조용하게 만든다.",
                    "아주 작은 물소리만 들려주어 흐르는 물과 대비한다.",
                    "거의 소리가 들리지 않는 분위기를 만든다.",
                ],
                "sample": "시각: 높은 곳의 물탱크에 물이 가득 차 있지만 흐르거나 떨어지지 않고 고여 있는 모습을 보여준다. 효과: 정전기는 높은 곳에 고여 있는 물과 같고 전하가 이동하지 않는다는 특징을 전달한다. 청각: 물이 흐르는 소리를 사용하지 않고 조용한 분위기를 만든다. 효과: 전하가 이동하지 않고 머물러 있는 정전기의 특성을 강조한다.",
            },
        },
    },
    "3세트 · AI와 예술": {
        "summary": [
            "🎨 인간의 예술 → 감정·철학·삶의 경험·관점·환경이 담김 → 예술로 볼 수 있음",
            "🤖 AI 그림 → 감정·독자적인 철학·이야기가 없음 → 인간의 예술과 같은 의미의 예술로 보기 어려움",
            "⭐ 하지만 AI 그림도 미술계 변화와 예술 범주 확장이라는 상징적 가치가 있음",
        ],
        "items": {
            "1번 · 표 완성": {
                "type": "short",
                "questions": [
                    ("㉠", "로봇이 한 번의 실수 없이 완벽하게 피겨 스케이팅을 하는 것",
                     [["로봇"], ["피겨 스케이팅", "피겨"], ["완벽", "실수 없이", "한 번의 실수 없이"]], ["인간 선수"]),
                    ("㉡", "감정을 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 예술로 보기 어렵다",
                     [["감정", "감정을 느끼지 못"], ["독자적인 철학", "철학"], ["이야기"], ["예술로 보기 어렵", "예술이 아니"]],
                     ["인간이 아니기 때문에", "가치가 없다", "가치가 전혀 없다"]),
                    ("㉢", "기존 미술계에 큰 변화를 가져오고 예술의 범주를 확장할 수 있다는 점에서 상징적 가치가 있음",
                     [["미술계", "미술"], ["변화"], ["예술의 범주", "예술의 범위", "범주를 확장", "범위를 확장"], ["가치", "의미"]],
                     ["가치가 없다", "가치가 전혀 없다"]),
                ],
                "hint": "AI 그림은 ‘예술로 보기 어려움’과 ‘가치가 없음’을 같은 뜻으로 보면 안 돼요.",
            },
            "2번 · 설명문 작성": {
                "type": "explanation",
                "hint": "인간의 예술과 AI 그림의 차이를 설명한 뒤, AI 그림을 어떻게 볼 수 있는지 이어서 생각해 보세요.",
                "methods": ["비교·대조", "인과", "분석"],
                "frames": {
                    "비교·대조": "인간의 예술에는 ＿＿＿＿이/가 담기지만, 인공지능에는 ＿＿＿＿이/가 없다.",
                    "인과": "인공지능은 ＿＿＿＿이/가 없기 때문에 ＿＿＿＿로 보기 어렵다.",
                    "분석": "인간의 작품에는 ＿＿＿＿, ＿＿＿＿, ＿＿＿＿ 등의 요소가 담겨 있다.",
                },
                "samples": [
                    ("비교·대조 + 인과",
                     "인간의 예술에는 작가의 감정과 철학, 삶의 경험 등이 담기지만 인공지능에는 감정이나 독자적인 철학과 이야기가 없다. (비교와 대조) 인공지능은 감정을 느끼지 못하고 독자적인 철학이나 이야기가 없기 때문에 이를 예술로 보기는 어렵다. (인과)"),
                    ("분석 + 인과",
                     "인간의 작품에는 작가의 감정, 철학, 삶의 경험, 관점, 환경 등의 요소가 종합적으로 담겨 있다. (분석) 인공지능은 감정이나 독자적인 철학과 이야기가 없기 때문에 이를 인간의 예술과 같은 의미의 예술로 보기는 어렵다. (인과)")
                ],
            },
            "3번 · 영상 기획": {
                "type": "video",
                "hint": "장면 2에서는 ‘인간의 예술에 작가의 감정과 경험 등이 담긴다’는 특징이 드러나야 해요.",
                "visual_options": [
                    "작가가 자신의 삶의 경험을 떠올리며 작품을 만드는 모습을 보여준다.",
                    "작가가 주변 환경을 관찰하고 그것을 작품에 담는 모습을 보여준다.",
                    "작가의 작업 과정과 완성된 작품을 함께 보여준다.",
                ],
                "audio_options": [
                    "작가가 작품에 담은 자신의 생각과 감정을 이야기한다.",
                    "작가가 작품을 만들게 된 경험이나 생각을 들려준다.",
                    "작품에 대한 작가의 철학을 담은 내레이션을 들려준다.",
                ],
                "sample": "시각: 작가가 자신의 삶의 경험과 주변 환경을 바탕으로 작품을 만드는 모습을 보여준다. 효과: 인간의 예술에는 작가의 경험과 관점, 환경 등이 담긴다는 점을 전달한다. 청각: 작가가 작품에 담은 자신의 생각과 감정을 이야기하는 목소리를 들려준다. 효과: 인간의 예술에는 작가의 고유한 감정과 철학이 담긴다는 점을 전달한다.",
            },
        },
    },
}

# ============================================================
# 유틸리티 / 채점
# ============================================================

def norm(text):
    return re.sub(r"\s+", " ", text.lower().strip())

def any_in(text, patterns):
    return any(p.lower() in text for p in patterns)

def all_groups(text, groups):
    return all(any_in(text, group) for group in groups)

def method_works(text, method):
    t = norm(text)
    if method == "정의":
        return any_in(t, ["이란", "말한다", "뜻이다", "의미한다"])
    if method == "예시":
        return any_in(t, ["예를 들어", "예로는", "예로", "대표적으로", "사례"])
    if method == "인과":
        return any_in(t, ["때문에", "이기 때문에", "하므로", "따라서", "그 결과", "결과적으로"])
    if method == "분석":
        return any_in(t, ["요소", "부분", "구성", "종합적으로", "여러"])
    if method == "비교·대조":
        pairs = [
            ("쉬운", "어려운"),
            ("실생활 전기", "정전기"),
            ("실생활에서 사용하는 전기", "정전기"),
            ("인간의 예술", "인공지능"),
            ("인간의 작품", "인공지능"),
        ]
        pair_ok = any(a in t and b in t for a, b in pairs)
        marker_ok = any_in(t, ["반면", "하지만", "그러나", "차이", "다르", "공통점"])
        return pair_ok and marker_ok
    if method == "분류·구분":
        return any_in(t, ["종류", "분류", "구분", "나뉘", "묶"])
    return False

def explain_concept(method):
    return COMMON_CONCEPTS.get(method, "")

def check_short(item, answer):
    t = norm(answer)
    if not t:
        return "⚪ 미입력", "답안을 입력해 주세요."
    for q, model, required, forbidden in item["questions"]:
        # 해당 함수는 전체 문항에서 사용하지 않고 아래에서 직접 처리
        pass
    return "🟡 검토 필요", "표 답안은 문항별 의미를 확인해야 합니다."

def check_short_question(model, required, forbidden, answer):
    t = norm(answer)
    if not t:
        return "⚪ 미입력", "답안을 입력해 주세요."
    if any_in(t, forbidden):
        return "❌ 오답", "개념의 방향이 반대로 나타났습니다."
    if all_groups(t, required):
        return "✅ 정답", "핵심 의미가 모두 확인되었습니다."
    # 일부 핵심만 맞는 경우
    matched = sum(1 for g in required if any_in(t, g))
    if matched >= max(1, len(required)-1):
        return "🟡 부분 정답", "핵심 방향은 맞지만 일부 내용이 빠졌습니다."
    return "❌ 오답", "필수 의미 요소가 충분히 드러나지 않습니다."

def check_explanation(set_name, answer, selected_methods):
    t = norm(answer)
    if not t:
        return "⚪ 미입력", "답안을 입력해 주세요.", []

    # 반대 방향/오개념
    bad = []
    if set_name.startswith("1세트"):
        bad = ["쉬운 과제는 혼자", "어려운 과제는 함께", "어려운 과제도 다른 사람들과 함께"]
        content_ok = ("쉬운" in t and ("함께" in t or "다른 사람" in t)) and \
                     ("어려운" in t and ("혼자" in t or "집중" in t))
    elif set_name.startswith("2세트"):
        bad = ["정전기는 전하가 이동한다", "전압이 낮아서 안전"]
        content_ok = ("정전기" in t and ("이동하지" in t or "머물" in t)) and \
                     (("전기" in t and "이동" in t) or "위험하지" in t)
    else:
        bad = ["ai는 감정을 느낀다", "인공지능은 감정을 느낀다", "가치가 전혀 없다"]
        content_ok = ("인공지능" in t or "ai" in t) and \
                     ("예술로 보기 어렵" in t or "예술이 아니다" in t or "가치" in t)

    if any_in(t, bad):
        return "❌ 오답", "한 개념의 특성을 다른 개념에 적용했거나 지문과 반대되는 내용이 있습니다.", []

    if len(selected_methods) != 2 or selected_methods[0] == selected_methods[1]:
        return "🟡 조건 미충족", "서로 다른 설명 방법을 2가지 선택해야 합니다.", []

    failed_methods = [m for m in selected_methods if not method_works(t, m)]
    if failed_methods:
        return "🟡 조건 미충족", f"선택한 방법 중 실제 문장에 드러나지 않은 방법: {', '.join(failed_methods)}", failed_methods

    if not content_ok:
        return "❌ 오답", "지문에서 요구한 핵심 내용 또는 결론 방향이 충분히 드러나지 않습니다.", []

    if set_name.startswith("3세트") and any_in(t, ["저작권", "일자리", "윤리", "편향", "표절"]):
        return "🟡 검토 필요", "지문에 없는 외부 내용이 포함되어 있습니다. 조건 위반 여부를 확인하세요.", []

    return "✅ 정답", "선택한 설명 방법이 실제 문장에 드러나고 핵심 결론도 확인됩니다.", []

def check_video(set_name, visual, visual_effect, audio, audio_effect):
    all_text = norm(" ".join([visual, visual_effect, audio, audio_effect]))
    if not all_text:
        return "⚪ 미입력", "연출 내용을 입력해 주세요."

    if set_name.startswith("1세트"):
        if any_in(all_text, ["친구들과 함께", "다른 사람들과 함께"]) and \
           any_in(all_text, ["어려운 과제", "도전이 필요한 과제"]):
            return "❌ 오답", "어려운 과제의 환경을 반대로 설정했습니다."
        ok = all_in = (
            any_in(all_text, ["어려운 과제", "도전이 필요한 과제"]) and
            any_in(all_text, ["혼자", "혼자서"]) and
            any_in(all_text, ["차분", "집중"]) and
            any_in(all_text, ["효과", "전달", "보여"])
        )
    elif set_name.startswith("2세트"):
        if any_in(all_text, ["흐르는 물", "폭포수가 콸콸", "물이 거세게"]):
            return "❌ 오답", "정전기의 특성과 반대되는 ‘흐름’이 중심으로 표현되었습니다."
        ok = (
            any_in(all_text, ["고여", "고인", "높은 곳"]) and
            any_in(all_text, ["이동하지", "머물", "조용"]) and
            any_in(all_text, ["효과", "전달", "강조"])
        )
    else:
        if any_in(all_text, ["인공지능이 감정을 느낀다", "ai가 감정을 느낀다"]):
            return "❌ 오답", "인간 예술의 특성과 반대되는 내용입니다."
        ok = (
            any_in(all_text, ["작가", "인간"]) and
            any_in(all_text, ["감정", "철학", "경험", "관점", "환경"]) and
            any_in(all_text, ["효과", "전달", "보여"])
        )

    if ok:
        return "✅ 정답", "연출과 효과가 지문의 핵심 내용에 연결되어 있습니다."
    return "🟡 검토 필요", "연출은 자유롭게 표현할 수 있지만 지문의 핵심 특성과 효과가 연결되는지 확인해 주세요."

# ============================================================
# 사이드바
# ============================================================

st.sidebar.title("📚 개념 길잡이")
st.sidebar.caption("필요한 개념을 먼저 확인하고 답안을 작성해 보세요.")

st.sidebar.markdown("### 설명 방법")
for name, desc in COMMON_CONCEPTS.items():
    st.sidebar.markdown(f"**{name}**  \n{desc}")

st.sidebar.divider()

set_name = st.sidebar.selectbox("연습할 세트", list(SETS.keys()))
item_names = list(SETS[set_name]["items"].keys())
item_name = st.sidebar.selectbox("문항", item_names)

st.sidebar.divider()
st.sidebar.markdown("### 🧠 이 세트의 핵심")
for line in SETS[set_name]["summary"]:
    st.sidebar.markdown(line)

item = SETS[set_name]["items"][item_name]

# ============================================================
# 본문
# ============================================================

st.title("📝 서논술형 답안 연습")
st.caption("중학교 1학년을 위한 단계별 연습 · 생각하기 → 쓰기 → 채점하기")

st.markdown(f"## {set_name}")
st.markdown(f"### {item_name}")

# 현재 문항 힌트
with st.container(border=True):
    st.markdown("### 💡 먼저 생각해 봐요")
    st.write(item["hint"])

# ------------------------------------------------------------
# 1번
# ------------------------------------------------------------
if item["type"] == "short":
    st.markdown("### ✏️ 답안을 입력해 보세요")

    for idx, (label, model, required, forbidden) in enumerate(item["questions"]):
        answer = st.text_input(
            f"{label}에 들어갈 내용",
            key=f"{set_name}-{item_name}-{label}"
        )

        if st.button(f"{label} 채점", key=f"check-{set_name}-{label}"):
            result, reason = check_short_question(model, required, forbidden, answer)
            if result.startswith("✅"):
                st.success(f"{result}  {reason}")
            elif result.startswith("🟡"):
                st.warning(f"{result}  {reason}")
            elif result.startswith("⚪"):
                st.info(f"{result}  {reason}")
            else:
                st.error(f"{result}  {reason}")

    with st.expander("📖 모범 답안 보기"):
        for label, model, _, _ in item["questions"]:
            st.markdown(f"**{label}**: {model}")

# ------------------------------------------------------------
# 2번
# ------------------------------------------------------------
elif item["type"] == "explanation":
    st.markdown("### 1️⃣ 설명 방법을 먼저 골라요")
    st.caption("서로 다른 방법 2가지를 골라야 해요.")

    selected = st.multiselect(
        "사용할 설명 방법",
        item["methods"],
        max_selections=2,
        key=f"methods-{set_name}-{item_name}"
    )

    if selected:
        cols = st.columns(len(selected))
        for col, method in zip(cols, selected):
            with col:
                st.markdown(f"**{method}**")
                st.info(explain_concept(method))
                st.code(item["frames"].get(method, ""), language=None)

    st.markdown("### 2️⃣ 문장으로 만들어 봐요")
    answer = st.text_area(
        "답안",
        height=180,
        placeholder="두 문장을 작성해 보세요. 설명 방법의 이름을 쓰지 않아도 실제 문장에 방법이 드러나면 인정합니다.",
        key=f"answer-{set_name}-{item_name}"
    )

    if st.button("📝 내 답안 채점하기", type="primary"):
        result, reason, failed = check_explanation(set_name, answer, selected)
        if result.startswith("✅"):
            st.success(f"{result}  {reason}")
        elif result.startswith("🟡"):
            st.warning(f"{result}  {reason}")
        elif result.startswith("⚪"):
            st.info(f"{result}  {reason}")
        else:
            st.error(f"{result}  {reason}")

        if failed:
            st.markdown("#### 🔎 다시 생각해 볼 부분")
            for m in failed:
                st.write(f"• **{m}**: {explain_concept(m)}")

    if item.get("note"):
        st.caption(item["note"])

    with st.expander("📖 가능한 모범 답안 모두 보기"):
        for label, sample in item["samples"]:
            st.markdown(f"**{label}**")
            st.write(sample)

# ------------------------------------------------------------
# 3번
# ------------------------------------------------------------
elif item["type"] == "video":
    st.markdown("### 1️⃣ 무엇을 보여줄까요? 👀")
    visual_choice = st.radio(
        "시각 요소",
        item["visual_options"] + ["직접 입력하기"],
        key=f"visual-choice-{set_name}"
    )
    if visual_choice == "직접 입력하기":
        visual = st.text_area("시각 요소 직접 입력", height=90, key=f"visual-{set_name}")
    else:
        visual = visual_choice

    visual_effect = st.text_input(
        "💡 이 화면은 어떤 내용을 전달하나요?",
        placeholder="지문의 어떤 내용을 보여주는지 써 보세요.",
        key=f"visual-effect-{set_name}"
    )

    st.markdown("### 2️⃣ 어떤 소리를 넣을까요? 🔊")
    audio_choice = st.radio(
        "청각 요소",
        item["audio_options"] + ["직접 입력하기"],
        key=f"audio-choice-{set_name}"
    )
    if audio_choice == "직접 입력하기":
        audio = st.text_area("청각 요소 직접 입력", height=90, key=f"audio-{set_name}")
    else:
        audio = audio_choice

    audio_effect = st.text_input(
        "💡 이 소리는 어떤 내용을 전달하나요?",
        placeholder="지문의 어떤 내용을 들려주는지 써 보세요.",
        key=f"audio-effect-{set_name}"
    )

    if st.button("🎬 영상 기획안 채점하기", type="primary"):
        result, reason = check_video(set_name, visual, visual_effect, audio, audio_effect)
        if result.startswith("✅"):
            st.success(f"{result}  {reason}")
        elif result.startswith("🟡"):
            st.warning(f"{result}  {reason}")
        else:
            st.error(f"{result}  {reason}")

    with st.expander("📖 모범 답안 보기"):
        st.write(item["sample"])

# ============================================================
# 하단 안내
# ============================================================

st.divider()
st.caption(
    "채점 원칙: 표현이 달라도 의미가 같으면 인정 · 선택한 설명 방법은 실제 기능이 드러나야 함 · "
    "개념을 서로 뒤바꾸면 오답 · 요구된 결론 방향이 명확해야 함."
)
