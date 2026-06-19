import random
import time
import streamlit as st

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="🌸 단비 내리는 날 💧",
    page_icon="🌱",
    layout="centered",
)

# 2. 봄날의 단비 파스텔 CSS 스타일
st.html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poor+Story&display=swap');

    .stApp {
        background: linear-gradient(135deg, #FFF5F5 0%, #E8F5E9 100%);
        font-family: 'Poor Story', cursive;
    }
    .main-title {
        color: #77A605;
        text-align: center;
        font-size: 3rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(255, 255, 255, 0.6);
        margin-bottom: 5px;
    }
    .sub-title {
        text-align: center;
        color: #FF8E9E;
        font-size: 1.2rem;
        margin-bottom: 25px;
    }
    /* 게임 화면 보드 */
    .game-board {
        background-color: rgba(255, 255, 255, 0.7);
        border: 2px dashed #B5FFFC;
        border-radius: 20px;
        height: 350px;
        position: relative;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.03);
    }
    /* 떨어지는 단어 스타일 */
    .word-drop {
        position: absolute;
        background-color: #FFFFFF;
        padding: 6px 14px;
        border-radius: 15px;
        border: 2px solid #FFDEE9;
        font-size: 1.15rem;
        font-weight: bold;
        color: #444;
        box-shadow: 0px 3px 6px rgba(0,0,0,0.05);
    }
    /* 점수판 스타일 */
    .status-container {
        display: flex;
        justify-content: space-around;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 10px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #E8F5E9;
    }
    .status-item {
        font-size: 1.2rem;
        font-weight: bold;
        color: #555;
    }
    </style>
    """
)

# 예쁜 봄날 관련 단어 소스 리스트
WORD_POOL = [
    "벚꽃", "민들레", "개나리", "봄바람", "새싹", "나비", "햇살", "비눗방울", 
    "피크닉", "무지개", "도시락", "라일락", "푸른하늘", "꿀벌", "따스함", "초록잎",
    "솜사탕", "종이비행기", "과수원", "자전거", "도토리", "소나기", "은방울꽃"
]

# 3. 게임 내부 상태 세션 초기화
if "game_active" not in st.session_state:
    st.session_state["game_active"] = False
if "score" not in st.session_state:
    st.session_state["score"] = 0
if "life" not in st.session_state:
    st.session_state["life"] = 5
if "words" not in st.session_state:
    st.session_state["words"] = []  
if "last_spawn_time" not in st.session_state:
    st.session_state["last_spawn_time"] = time.time()

# 4. 타이틀 구성
st.html("<div class='main-title'>💧 단비 내리는 날 🌸</div>")
st.html("<div class='sub-title'>하늘에서 내려오는 예쁜 단어들을 입력해 대지를 촉촉하게 적셔주세요! 🌱</div>")

# 5. 게임 컨트롤 버튼들
col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("🌱 게임 시작하기", use_container_width=True):
        st.session_state["game_active"] = True
        st.session_state["score"] = 0
        st.session_state["life"] = 5
        st.session_state["words"] = []
        st.session_state["last_spawn_time"] = time.time()
        st.rerun()

with col_btn2:
    if st.button("🛑 게임 멈추기", use_container_width=True):
        st.session_state["game_active"] = False
        st.rerun()

# 6. 상단 스탯 표시창
st.html(f"""
<div class='status-container'>
    <div class='status-item'>💯 점수: <span style='color:#FF8E9E;'>{st.session_state['score']} 점</span></div>
    <div class='status-item'>❤️ 남은 대지의 수분: <span style='color:#77A605;'>{"💧" * st.session_state['life'] if st.session_state['life'] > 0 else "🧱 메마름"}</span></div>
</div>
""")

# 7. 게임 메인 로직
if st.session_state["game_active"]:
    
    # 💥 타자 입력 처리 포커스
    with st.form(key="typer_form", clear_on_submit=True):
        user_input = st.text_input("✍ Honor Word", placeholder="여기에 입력하세요", label_visibility="collapsed")
        st.html("<div style='display:none;'>")
        submit_word = st.form_submit_button("⌨️ 정답 확인")
        st.html("</div>")

        # 🛠️ [해결 1] 사용자가 아무것도 치지 않고 엔터했거나 실시간 루프로 재생성된 빈 입력값("")은 검사 자체를 패스!
        if user_input and user_input.strip() != "":
            input_clean = user_input.strip()
            matched_index = -1
            max_top = -1
            
            # 🛠️ [해결 2] 화면에 떠 있는 동일 단어 중 가장 아래에 있는(Y좌표 'top'이 가장 큰) 단어 하나의 위치를 검색합니다.
            for i, w in enumerate(st.session_state["words"]):
                if w["text"] == input_clean:
                    if w["top"] > max_top:
                        max_top = w["top"]
                        matched_index = i
            
            # 매칭된 단어가 있다면 리스트에서 '딱 하나만' 골라 제거
            if matched_index != -1:
                st.session_state["words"].pop(matched_index)
                st.session_state["score"] += 10
                st.toast("🌱 단비가 내려 땅이 촉촉해집니다!", icon="💧")
            else:
                # 정말로 오타를 냈을 때만 토스트 팝업 활성화
                st.toast("❌ 오타가 났어요! 다시 집중해 봐요!", icon="⚠️")

    # [단어 하강 연산]
    current_time = time.time()
    alive_words = []
    for w in st.session_state["words"]:
        if w["top"] >= 310:  
            st.session_state["life"] -= 1
        else:
            w["top"] += 20  
            alive_words.append(w)
            
    st.session_state["words"] = alive_words

    # 게임 오버 체크
    if st.session_state["life"] <= 0:
        st.session_state["game_active"] = False
        st.error("😭 가뭄이 찾아왔어요! 대지가 메말라 게임이 종료되었습니다. 다시 도전해 보세요! 🧱")
        st.session_state["words"] = []
        st.rerun()

    # [신규 단어 스폰] 중복 단어 낙하도 게임의 재미 요소이므로 pool 내 무작위 생성 허용
    if current_time - st.session_state["last_spawn_time"] > 2.0 and len(st.session_state["words"]) < 4:
        new_word = {
            "text": random.choice(WORD_POOL),
            "top": 10,                 
            "left": random.randint(15, 75) 
        }
        st.session_state["words"].append(new_word)
        st.session_state["last_spawn_time"] = current_time

    # 8. 실시간 게임 화면 그리기
    words_html = ""
    for w in st.session_state["words"]:
        words_html += f"<div class='word-drop' style='top: {w['top']}px; left: {w['left']}%;'>{w['text']}</div>"

    st.html(f"<div class='game-board'>{words_html}</div>")

    # 0.5초마다 루프 재생성
    time.sleep(0.5)
    st.rerun()

else:
    # 게임 시작 전 대기 화면
    st.html(
        """
        <div class='game-board' style='display:flex; justify-content:center; align-items:center; flex-direction:column; color:#888;'>
            <div style='font-size:1.5rem; margin-bottom:10px;'>🌱 준비가 되셨나요?</div>
            <div style='font-size:1rem;'>[게임 시작하기] 버튼을 누르면 단비 단어들이 내려옵니다!</div>
        </div>
        """
    )
