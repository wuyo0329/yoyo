# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 23:05:11 2025

@author: s1230
"""

import streamlit as st
import random
import matplotlib.pyplot as plt

# 遊戲統計資料
win = 0
lose = 0
giveup = 0
money = 1000
pot = 1000

# 撲克牌數字映射
ranks = {"A":1,"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"10":10,"J":11,"Q":12,"K":13}

st.title("🎯 射龍門 - Streamlit 版")

# 初始化 Session State
if "money" not in st.session_state:
    st.session_state.money = 1000
    st.session_state.pot = 1000
    st.session_state.win = 0
    st.session_state.lose = 0
    st.session_state.giveup = 0

st.sidebar.markdown("### 玩家狀態")
st.sidebar.write(f"籌碼: {st.session_state.money}")
st.sidebar.write(f"底池: {st.session_state.pot}")

# 選擇場次
rounds = st.number_input("請輸入此次遊玩的場次 (建議: 8/16/32):", min_value=1, max_value=100, step=1)
start = st.button("🎮 開始遊戲")

if start:
    for i in range(rounds):
        st.subheader(f"第 {i+1} 局")

        door1 = random.choice(list(ranks.keys()))
        door2 = random.choice(list(ranks.keys()))
        st.write(f"柱子是: {door1} 和 {door2}")

        # 判斷兩張是否一樣
        if door1 == door2:
            same = st.radio(f"兩張一樣! 選擇: 往上(1) / 往下(2) / 棄牌(n)", ("1", "2", "n"), key=f"same_{i}")
            if same == "n":
                st.session_state.money -= 100
                st.session_state.pot += 100
                st.session_state.giveup += 1
                st.warning("你選擇棄牌。")
                continue

            bet = st.number_input("請輸入下注金額:", min_value=100, max_value=st.session_state.money, key=f"bet_{i}")
            handcard = random.choice(list(ranks.keys()))
            st.write(f"抽牌為: {handcard}")

            door1size = ranks[door1]
            handsize = ranks[handcard]

            # 撞柱
            if handcard == door1:
                st.session_state.money -= bet * 3
                st.session_state.pot += bet * 3
                st.session_state.lose += 1
                st.error("撞柱！損失三倍。")
            elif same == "1" and handsize > door1size:
                st.session_state.money += bet
                st.session_state.pot -= bet
                st.session_state.win += 1
                st.success("往上命中！")
            elif same == "2" and handsize < door1size:
                st.session_state.money += bet
                st.session_state.pot -= bet
                st.session_state.win += 1
                st.success("往下命中！")
            else:
                st.session_state.money -= bet
                st.session_state.pot += bet
                st.session_state.lose += 1
                st.warning("沒射中。")

        else:
            play = st.radio("是否玩牌?", ("是", "否"), key=f"play_{i}")
            if play == "否":
                st.session_state.money -= 100
                st.session_state.pot += 100
                st.session_state.giveup += 1
                st.warning("你選擇跳過。")
                continue
            bet = st.number_input("請輸入下注金額:", min_value=100, max_value=st.session_state.money, key=f"betdiff_{i}")
            handcard = random.choice(list(ranks.keys()))
            st.write(f"抽牌為: {handcard}")
            h = ranks[handcard]
            d1 = ranks[door1]
            d2 = ranks[door2]

            if handcard == door1 or handcard == door2:
                st.session_state.money -= bet * 2
                st.session_state.pot += bet * 2
                st.session_state.lose += 1
                st.error("撞柱！損失兩倍。")
            elif min(d1, d2) < h < max(d1, d2):
                st.session_state.money += bet
                st.session_state.pot -= bet
                st.session_state.win += 1
                st.success("射中！")
            else:
                st.session_state.money -= bet
                st.session_state.pot += bet
                st.session_state.lose += 1
                st.warning("射歪了。")

    # 如果底池為 0
    if st.session_state.pot <= 0:
        st.session_state.pot = 1000
        st.info("底池補滿至 1000")

    # 顯示統計圖表
    st.subheader("🎯 結果統計")
    total = st.session_state.win + st.session_state.lose + st.session_state.giveup
    if total > 0:
        rates = [st.session_state.win / total, st.session_state.lose / total, st.session_state.giveup / total]
        labels = ["贏", "輸", "放棄"]
        plt.rcParams["font.family"] = ["Microsoft JhengHei"]
        fig, ax = plt.subplots()
        ax.pie(rates, labels=labels, autopct="%1.1f%%", colors=["#FF9999", "#99FF99", "gray"], textprops={"fontsize": 14})
        ax.set_title("遊戲結算", fontsize=20)
        st.pyplot(fig)

st.button("🔄 重置遊戲", on_click=lambda: st.session_state.clear())