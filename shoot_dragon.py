import streamlit as st
import random
import matplotlib.pyplot as plt

# 帳號密碼設定
auths = {"yoyo": "a123", "lccnet": "22235089"}

# 撲克牌數字映射 (不考慮花色)
ranks = {"A":1, "2":2, "3":3, "4":4, "5":5, "6":6, "7":7, "8":8, "9":9, "10":10, "J":11, "Q":12, "K":13}

# 初始化 Session State
def init_session():
    session = st.session_state
    if "logged_in" not in session:
        session.logged_in = False
    if "user" not in session:
        session.user = None
    if "money" not in session:
        session.money = 0
    if "pot" not in session:
        session.pot = 1000
    if "win" not in session:
        session.win = 0
    if "lose" not in session:
        session.lose = 0
    if "giveup" not in session:
        session.giveup = 0

init_session()

st.title("🎯 射龍門 - Streamlit 版")

# 登入區塊
if not st.session_state.logged_in:
    st.subheader("請先登入")
    account = st.text_input("帳號", key="login_account")
    password = st.text_input("密碼", type="password", key="login_password")
    if st.button("登入"):
        if account in auths and password == auths[account]:
            st.success(f"歡迎回來: {account}")
            st.session_state.logged_in = True
            st.session_state.user = account
            st.session_state.money = 1000
            st.session_state.pot = 1000
            st.session_state.win = 0
            st.session_state.lose = 0
            st.session_state.giveup = 0
            st.experimental_rerun()
        else:
            st.error("帳號或密碼錯誤")
    st.stop()

# 已登入後
st.sidebar.markdown(f"### 玩家: {st.session_state.user}")
st.sidebar.write(f"籌碼: {st.session_state.money}")
st.sidebar.write(f"底池: {st.session_state.pot}")

# 選單功能
action = st.sidebar.selectbox("選擇動作", ["開始遊戲", "我的籌碼", "重置遊戲"])

if action == "我的籌碼":
    st.write(f"目前籌碼: {st.session_state.money}")
    if st.button("儲值 1000 籌碼"):
        st.session_state.money += 1000
        st.success(f"儲值成功，籌碼: {st.session_state.money}")

elif action == "開始遊戲":
    rounds = st.number_input("輸入遊玩場次", min_value=1, step=1, value=8)
    if st.button("開始射龍門"):
        for i in range(1, rounds+1):
            st.subheader(f"第 {i} 局")
            door1 = random.choice(list(ranks.keys()))
            door2 = random.choice(list(ranks.keys()))
            st.write(f"柱子: {door1} 與 {door2}")

            if door1 == door2:
                choice = st.radio("兩張一樣，選擇: 往上(1) / 往下(2) / 棄牌(n)", ["1","2","n"], key=f"same_{i}")
                if choice == "n":
                    st.session_state.money -= 100
                    st.session_state.pot += 100
                    st.session_state.giveup += 1
                    st.warning("棄牌，損失 100 籌碼。")
                    continue
                bet = st.number_input("下注金額", min_value=100, max_value=st.session_state.money, key=f"bet_{i}")
                hand = random.choice(list(ranks.keys()))
                st.write(f"開牌: {hand}")
                d = ranks[door1]; h = ranks[hand]
                if hand == door1:
                    st.session_state.money -= bet*3
                    st.session_state.pot += bet*3
                    st.session_state.lose += 1
                    st.error("撞柱，賠三倍")
                elif choice == "1" and h > d or choice == "2" and h < d:
                    st.session_state.money += bet
                    st.session_state.pot -= bet
                    st.session_state.win += 1
                    st.success("命中，贏得下注額")
                else:
                    st.session_state.money -= bet
                    st.session_state.pot += bet
                    st.session_state.lose += 1
                    st.warning("未命中，失去下注額")

            else:
                play = st.radio("是否玩牌?", ["是","否"], key=f"play_{i}")
                if play == "否":
                    st.session_state.money -= 100
                    st.session_state.pot += 100
                    st.session_state.giveup += 1
                    st.warning("跳過，損失 100 籌碼。")
                    continue
                bet = st.number_input("下注金額", min_value=100, max_value=st.session_state.money, key=f"betdiff_{i}")
                hand = random.choice(list(ranks.keys()))
                st.write(f"開牌: {hand}")
                d1 = ranks[door1]; d2 = ranks[door2]; h = ranks[hand]
                if hand in (door1, door2):
                    st.session_state.money -= bet*2
                    st.session_state.pot += bet*2
                    st.session_state.lose += 1
                    st.error("撞柱，賠兩倍")
                elif min(d1,d2) < h < max(d1,d2):
                    st.session_state.money += bet
                    st.session_state.pot -= bet
                    st.session_state.win += 1
                    st.success("射中，贏得下注額")
                else:
                    st.session_state.money -= bet
                    st.session_state.pot += bet
                    st.session_state.lose += 1
                    st.warning("射歪，失去下注額")

        # 畫結果統計圖
        total = st.session_state.win + st.session_state.lose + st.session_state.giveup
        if total > 0:
            rates = [st.session_state.win/total, st.session_state.lose/total, st.session_state.giveup/total]
            labels = ["贏","輸","放棄"]
            plt.rcParams["font.family"] = ["Microsoft JhengHei"]
            fig, ax = plt.subplots()
            ax.pie(rates, labels=labels, autopct="%1.1f%%", colors=["#FF9999","#99FF99","gray"], textprops={"fontsize":14})
            ax.set_title("遊戲結算", fontsize=20)
            st.pyplot(fig)

elif action == "重置遊戲":
    for k in ["money","pot","win","lose","giveup"]:
        st.session_state[k] = 0 if k != "pot" else 1000
    st.success("遊戲已重置")
    st.experimental_rerun()
