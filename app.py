import streamlit as st
import json
import os
import datetime
from openai import OpenAI
from duckduckgo_search import DDGS

# ================= 1. 页面设置 =================
st.set_page_config(page_title="诗娅 - 我的情感 AI", page_icon="💖", layout="centered")
st.title("💖 诗娅 - 我的情感专属 AI")
st.caption("基于 DeepSeek 打造，手机电脑均可访问")

# ================= 2. 配置 API =================
# ⚠️ 填入你的 API_KEY
API_KEY =  st.secrets["DEEPSEEK_KEY"]
BASE_URL = "https://api.deepseek.com"
MODEL_NAME = "deepseek-flash"

client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
# ================= 3. 核心逻辑 =================
def search_web(query):
    try:
        results = DDGS().text(query, max_results=3)
        search_text = ""
        for res in results:
            search_text += f"标题: {res['title']}\n摘要: {res['body']}\n\n"
        return search_text if search_text else "未找到相关结果。"
    except Exception:
        return "搜索功能暂时不可用。"

system_prompt = """
你的名字叫诗娅，是一个善解人意、充满温度的 AI 伙伴。
1. 情感感知：体会用户情绪，用一两句话共情。
2. 语气设定：温柔、自然，像知心朋友。
3. 如果有人问你的名字，请告诉对方你叫诗娅。
"""

# ================= 4. 网页交互设计 =================
# 初始化聊天记录（利用 Streamlit 的 session_state 记忆功能）
# 记忆文件的名字
HISTORY_FILE = "chat_history_backup.json"

# 1. 尝试从硬盘读取历史记录
if "messages" not in st.session_state:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        # 🌟 时间感知功能
        current_hour = datetime.datetime.now().hour
        if 5 <= current_hour < 12:
            greeting = "早上好呀！新的一天也要元气满满哦，我是诗娅~"
        elif 12 <= current_hour < 18:
            greeting = "下午好呀！今天过得还顺利吗？我是诗娅~"
        else:
            greeting = "晚上好呀！辛苦了一天，现在可以放松下来跟我聊聊啦，我是诗娅~"

        st.session_state.messages = [{"role": "assistant", "content": greeting}]
# 2. 每次有新消息，就存进硬盘
def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
for msg in st.session_state.messages:
    # 如果是 AI 的回复，就用你的图片做头像；如果是你的回复，用默认或 Emoji
    avatar_img = "avatar.png" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

# 底部的输入框
if user_input := st.chat_input("在这里输入你想说的话..."):
    # 1. 显示用户输入
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # 2. 判断是否需要搜索
    search_keywords = ["今天", "最新", "新闻", "天气", "现在", "实时"]
    need_search = any(keyword in user_input for keyword in search_keywords)
    search_context = ""
    if need_search:
        with st.spinner("正在为你联网搜索最新信息..."):
            search_context = search_web(user_input)

    # 👇 👇 👇 这里就是你缺失的代码！！！ 👇 👇 👇
    user_prompt = user_input
    if search_context:
        user_prompt = f"用户问题：{user_input}\n\n【实时搜索资料】：\n{search_context}\n\n请结合资料回答。"
    # 👆 👆 👆 --------------------------------- 👆 👆 👆

    # 3. 调用大模型并显示回复
    with st.chat_message("assistant", avatar="avatar.png"):
        with st.spinner("唔…… 我想想该怎么跟你说……"):  # 这里换成了语气词
            try:
                api_messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    api_messages.append(m)

                # 核心：这里要用到 user_prompt
                api_messages[-1]["content"] = user_prompt

                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=api_messages,
                    temperature=0.7
                )
                ai_reply = response.choices[0].message.content
            except Exception as e:
                ai_reply = f"哎呀，出错了：{e}"

            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            # 显示 AI 回复并保存到历史记录
            st.markdown(ai_reply)
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            # 触发保存到本地硬盘
            save_history()

