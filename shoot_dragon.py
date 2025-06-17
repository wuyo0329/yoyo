import streamlit as st
import random
import matplotlib.pyplot as plt

# Safe rerun wrapper in case experimental_rerun triggers a Rerun
# Catch BaseException to swallow the Streamlit rerun exception

def rerun():
    try:
        st.experimental_rerun()
    except BaseException:
        pass

# 帳號密碼設定
auths = {"yoyo": "a123", "lccnet": "22235089"}
# 撲克牌數字映射 (不考慮花色)
ranks = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13}

# 初始化 Session State
def init_session():
    s = st.session_state
    defaults = {
        "logged_in": False,
        "user": None,
        "money": 0,
        "pot": 1000,
        "win": 0,
        "lose": 0,
        "giveup": 0,
        "game_started": False,
        "current_round": 0,
        "total_rounds": 0
    }
    for key, val in defaults.items():
        if key not in s:
            s[key] = val
init_session()

st.title("🎯 射龍門 - Streamlit 版")

# 登入流程
if not st.session_state.logged_in:
    st.subheader("請先登入")
    account = st.text_input("帳號", key="login_account")
    password = st.text_input("密碼", type="password", key="login_password")
    if st.button("登入"):
        if account in auths and auths[account] == password:
            st.session_state.logged_in = True
            st.session_state.user = account
            st.session_state.money = 1000
            st.session_state.pot = 1000
            st.session_state.win = 0
            st.session_state.lose = 0
            st.session_state.giveup = 0
            rerun()
        else:
            st.error("帳號或密碼錯誤，請再試一次。")
    st.stop()

# 已登入後顯示側邊欄狀態
st.sidebar.markdown(f"### 玩家: {st.session_state.user}")
st.sidebar.write(f"籌碼: {st.session_state.money}")
st.sidebar.write(f"底池: {st.session_state.pot}")

# 登出按鈕
if st.sidebar.button("登出"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    rerun()

# 遊戲設置
st.header("射龍門遊戲設置")
if not st.session_state.game_started:
    total = st.number_input("請輸入遊玩場次：", min_value=1, step=1, value=8)
    if st.button("開始遊戲"):
        st.session_state.money = 1000
        st.session_state.pot = 1000
        st.session_state.win = 0
        st.session_state.lose = 0
        st.session_state.giveup = 0
        st.session_state.game_started = True
        st.session_state.total_rounds = total
        st.session_state.current_round = 1
        rerun()
    st.stop()

# 逐局互動
cr = st.session_state.current_round
tr = st.session_state.total_rounds
if cr <= tr:
    st.subheader(f"第 {cr} 局 (共 {tr} 局)")
    if f"door1_{cr}" not in st.session_state:
        st.session_state[f"door1_{cr}"] = random.choice(list(ranks.keys()))
        st.session_state[f"door2_{cr}"] = random.choice(list(ranks.keys()))
    door1 = st.session_state[f"door1_{cr}"]
    door2 = st.session_state[f"door2_{cr}"]
    st.write(f"柱子: {door1} 與 {door2}")
    if door1 == door2:
        choice = st.radio("兩張一樣，選擇：", ["往上(1)", "往下(2)", "棄牌(n)"], key=f"choice_{cr}")
        if choice == "棄牌(n)":
            if st.button("確認棄牌", key=f"submit_{cr}"):
                st.session_state.money -= 100
                st.session_state.pot += 100
                st.session_state.giveup += 1
                st.warning("棄牌，-100 籌碼。")
                st.session_state.current_round += 1
                rerun()
        else:
            bet = st.number_input("下注金額：", min_value=100, max_value=st.session_state.money, key=f"bet_{cr}")
            if st.button("確認下注", key=f"submit_{cr}"):
                hand = random.choice(list(ranks.keys()))
                st.write(f"抽牌: {hand}")
                d = ranks[door1]; h = ranks[hand]
                if hand == door1:
                    st.session_state.money -= bet*3
                    st.session_state.pot += bet*3
                    st.session_state.lose += 1
                    st.error("撞柱！賠三倍。")
                elif (choice.startswith("往上") and h > d) or (choice.startswith("往下") and h < d):
                    st.session_state.money += bet
                    st.session_state.pot -= bet
                    st.session_state.win += 1
                    st.success("命中！贏得下注額。")
                else:
                    st.session_state.money -= bet
                    st.session_state.pot += bet
                    st.session_state.lose += 1
                    st.warning("未命中，失去下注額。")
                st.session_state.current_round += 1
                rerun()
    else:
        play = st.radio("是否玩牌？", ["是", "否"], key=f"play_{cr}")
        if play == "否":
            if st.button("跳過本局", key=f"submit_{cr}"):
                st.session_state.money -= 100
                st.session_state.pot += 100
                st.session_state.giveup += 1
                st.warning("跳過，-100 籌碼。")
                st.session_state.current_round += 1
                rerun()
        else:
            bet = st.number_input("下注金額：", min_value=100, max_value=st.session_state.money, key=f"betdiff_{cr}")
            if st.button("確認下注", key=f"submit_{cr}"):
                hand = random.choice(list(ranks.keys()))
                st.write(f"抽牌: {hand}")
                d1, d2 = ranks[door1], ranks[door2]; h = ranks[hand]
                if hand == door1 or hand == door2:
                    st.session_state.money -= bet*2
                    st.session_state.pot += bet*2
                    st.session_state.lose += 1
                    st.error("撞柱！賠兩倍。")
                elif min(d1, d2) < h < max(d1, d2):
                    st.session_state.money += bet
                    st.session_state.pot -= bet
                    st.session_state.win += 1
                    st.success("射中！贏得下注額。")
                else:
                    st.session_state.money -= bet
                    st.session_state.pot += bet
                    st.session_state.lose += 1
                    st.warning("射歪，失去下注額。")
                st.session_state.current_round += 1
                rerun()
else:
    st.subheader("🎯 遊戲結束 - 結果統計 🎯")
    total = st.session_state.win + st.session_state.lose + st.session_state.giveup
    if total > 0:
        rates = [st.session_state.win/total, st.session_state.lose/total, st.session_state.giveup/total]
        labels = ["贏","輸","放棄"]
        plt.rcParams["font.family"] = ["Microsoft JhengHei"]
        fig, ax = plt.subplots()
        ax.pie(rates, labels=labels, autopct="%1.1f%%", colors=["#FF9999","#99FF99","gray"], textprops={"fontsize":14})
        ax.set_title("遊戲結算", fontsize=20)
        st.pyplot(fig)
    if st.button("重新開始新遊戲"):
        for key in ["game_started","current_round","total_rounds","win","lose","giveup"]:
            st.session_state[key] = False if key == "game_started" else 0
        rerun()
