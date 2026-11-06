import streamlit as st
from openai import OpenAI
from duckduckgo_search import DDGS

# ================= 1. 页面设置与深度美化 =================
st.set_page_config(page_title="诗娅 - 我的情感 AI", page_icon="💖", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp { background: linear-gradient(135deg, #fdfbfb 0%, #ebedee 100%); }
    h1 { text-align: center; background: -webkit-linear-gradient(45deg, #ff758c, #ff7eb3); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800; padding-bottom: 20px; }
    .stChatMessage { border-radius: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); padding: 10px 15px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("💖 诗娅 - 我的情感专属 AI")
st.caption("基于 DeepSeek 打造，手机电脑均可访问")

# ================= 2. 配置 API =================
# ⚠️ 把下面的 API_KEY 换成你自己的真实密钥
API_KEY = "sk-5539d658ecb54ae9ba299fc3d02686ba"
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

# ================= 4. 网页交互 =================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "你好呀！我是诗娅，今天过得怎么样？"}]

for msg in st.session_state.messages:
    avatar_img = "avatar.png" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_img):
        st.markdown(msg["content"])

if user_input := st.chat_input("在这里输入你想说的话..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    search_keywords = ["今天", "最新", "新闻", "天气", "现在", "实时"]
    need_search = any(keyword in user_input for keyword in search_keywords)
    search_context = ""
    if need_search:
        with st.spinner("正在为你联网搜索..."):
            search_context = search_web(user_input)

    user_prompt = user_input
    if search_context:
        user_prompt = f"用户问题：{user_input}\n\n【实时搜索资料】：\n{search_context}\n\n请结合资料回答。"

    with st.chat_message("assistant", avatar="avatar.png"):
        with st.spinner("唔…… 我想想该怎么跟你说……"):
            try:
                api_messages = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.messages:
                    api_messages.append(m)
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