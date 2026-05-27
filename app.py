import streamlit as st
import random

# --- 페이지 설정 ---
st.set_page_config(page_title="도둑과 경찰 게임", page_icon="💰", layout="centered")

# --- 게임 상 수 및 설정 ---
SIZE = 10

# --- 세션 상태(Session State) 초기화 ---
# Streamlit은 버튼을 누를 때마다 코드가 재실행되므로, 상태를 세션에 저장해야 합니다.
if 'char_x' not in st.session_state:
    st.session_state.char_x = 0
    st.session_state.char_y = 0
    st.session_state.police_x = SIZE - 1
    st.session_state.police_y = SIZE - 1
    st.session_state.score = 0
    st.session_state.has_shield = False
    st.session_state.game_over = False
    
    # 돈(💰) 위치 초기화 (3개)
    st.session_state.money_list = []
    while len(st.session_state.money_list) < 3:
        pos = [random.randint(0, SIZE-1), random.randint(0, SIZE-1)]
        if pos != [0, 0] and pos not in st.session_state.money_list:
            st.session_state.money_list.append(pos)
            
    # 방패(🛡️) 위치 초기화 (1개)
    st.session_state.shield_pos = [random.randint(1, SIZE-2), random.randint(1, SIZE-2)]

# --- 게임 리셋 함수 ---
def reset_game():
    st.session_state.char_x = 0
    st.session_state.char_y = 0
    st.session_state.police_x = SIZE - 1
    st.session_state.police_y = SIZE - 1
    st.session_state.score = 0
    st.session_state.has_shield = False
    st.session_state.game_over = False
    st.session_state.money_list = []
    while len(st.session_state.money_list) < 3:
        pos = [random.randint(0, SIZE-1), random.randint(0, SIZE-1)]
        if pos != [0, 0] and pos not in st.session_state.money_list:
            st.session_state.money_list.append(pos)
    st.session_state.shield_pos = [random.randint(1, SIZE-2), random.randint(1, SIZE-2)]

# --- 경찰 이동 로직 (지능형 랜덤 AI) ---
def move_police():
    if st.session_state.game_over:
        return

    decision = random.random()
    px, py = st.session_state.police_x, st.session_state.police_y
    cx, cy = st.session_state.char_x, st.session_state.char_y

    if decision < 0.7:  # 70% 확률로 추격 모드 (상하좌우 직각 이동)
        dx = abs(px - cx)
        dy = abs(py - cy)
        
        if dx > dy:
            px += 1 if px < cx else -1
        elif dy != 0:
            py += 1 if py < cy else -1
    else:  # 30% 확률로 수색(랜덤) 모드
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        r_dir = random.choice(directions)
        px = max(0, min(SIZE - 1, px + r_dir[0]))
        py = max(0, min(SIZE - 1, py + r_dir[1]))

    st.session_state.police_x, st.session_state.police_y = px, py

    # 체포 체크
    if px == cx and py == cy:
        if st.session_state.has_shield:
            st.session_state.has_shield = False
            st.session_state.police_x, st.session_state.police_y = SIZE - 1, SIZE - 1
            st.toast("🛡️ 방어막으로 경찰의 체포를 한 번 막았습니다! 경찰이 텔레포트합니다.")
        else:
            st.session_state.game_over = True

# --- 충돌 체크 (아이템 먹기) ---
def check_collision():
    cx, cy = st.session_state.char_x, st.session_state.char_y
    
    # 돈 수집
    if [cx, cy] in st.session_state.money_list:
        st.session_state.money_list.remove([cx, cy])
        st.session_state.score += 100
        # 새로운 돈 생성
        while True:
            new_pos = [random.randint(0, SIZE-1), random.randint(0, SIZE-1)]
            if new_pos != [cx, cy] and new_pos != [st.session_state.police_x, st.session_state.police_y] and new_pos not in st.session_state.money_list:
                st.session_state.money_list.append(new_pos)
                break
                
    # 방패 수집
    if [cx, cy] == st.session_state.shield_pos:
        st.session_state.has_shield = True
        st.session_state.shield_pos = [-1, -1]
        st.toast("🛡️ 방어막 아이템을 획득했습니다!")

# --- 이동 버튼 클릭 핸들러 ---
def handle_move(direction):
    if st.session_state.game_over:
        return
        
    if direction == "up": st.session_state.char_y = max(0, st.session_state.char_y - 1)
    elif direction == "down": st.session_state.char_y = min(SIZE - 1, st.session_state.char_y + 1)
    elif direction == "left": st.session_state.char_x = max(0, st.session_state.char_x - 1)
    elif direction == "right": st.session_state.char_x = min(SIZE - 1, st.session_state.char_x + 1)
    
    check_collision()
    move_police()

# --- 웹 UI 그리기 ---
st.title("🏃‍♂️ 경찰을 피해 돈을 모으세요!")
st.write("🛡️ 방패를 먹으면 체포를 한 번 버티고 경찰을 구석으로 보냅니다. (경찰 AI: 70% 추격, 30% 랜덤)")

# 점수 및 상태 표시
shield_status = "🛡️ 방어막 활성" if st.session_state.has_shield else "❌ 방어막 없음"
col_score1, col_score2 = st.columns(2)
col_score1.metric("💰 현재 점수", f"{st.session_state.score} 점")
col_score2.metric("🛡️ 상태", shield_status)

st.markdown("---")

# 게임 맵 그리기 (텍스트 블록)
map_text = ""
for y in range(SIZE):
    row = ""
    for x in range(SIZE):
        if x == st.session_state.char_x and y == st.session_state.char_y:
            row += "👤 "
        elif x == st.session_state.police_x and y == st.session_state.police_y:
            row += "👮 "
        elif [x, y] in st.session_state.money_list:
            row += "💰 "
        elif [x, y] == st.session_state.shield_pos:
            row += "🛡️ "
        else:
            row += "▫️ "
    map_text += row + "\n"

# 맵 출력 (고정폭 서체로 깨짐 방지)
st.code(map_text, language="")

# --- 게임 오버 및 컨트롤러 배치 ---
if st.session_state.game_over:
    st.error(f"🚨 경찰의 심리전에 당해 체포되었습니다! 최종 점수: {st.session_state.score}점")
    if st.button("다시 도전하기", on_click=reset_game):
        st.rerun()
else:
    # 키패드 형태의 버튼 배치 (3x3 레이아웃 몰아주기)
    st.write("🕹️ **컨트롤러**")
    c1, c2, c3 = st.columns([1, 1, 1])
    
    with c2:
        st.button("위 (W)", on_click=handle_move, args=("up",), use_container_width=True)
    
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.button("왼쪽 (A)", on_click=handle_move, args=("left",), use_container_width=True)
    with c2:
        # 가운데 빈 공간 조절용 버튼 혹은 리셋 버튼
        st.button("🔄 리셋", on_click=reset_game, use_container_width=True)
    with c3:
        st.button("오른쪽 (D)", on_click=handle_move, args=("right",), use_container_width=True)
        
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.button("아래 (S)", on_click=handle_move, args=("down",), use_container_width=True)
