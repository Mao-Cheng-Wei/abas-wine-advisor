import os
import base64
import tiktoken
import streamlit as st
from openpyxl import load_workbook
from openai import OpenAI

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.embeddings.fastembed import FastEmbedEmbedding


st.set_page_config(
    page_title="安貝斯風味人格選酒顧問",
    page_icon="🍷",
    layout="centered"
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2.4rem; padding-bottom: 2rem;}
    .ai-main-title {text-align:center;font-size:40px;font-weight:800;color:#2F3140;margin-top:18px;margin-bottom:10px;}
    .ai-subtitle {text-align:center;font-size:16px;color:#7A7A7A;margin-bottom:10px;}
    .ai-divider {height:2px;background:linear-gradient(to right,transparent,#D8C2A1,transparent);margin:10px 0 24px;border-radius:999px;}
    </style>
    """,
    unsafe_allow_html=True,
)

with open("images/ABAS_logo.jpg", "rb") as f:
    logo_base64 = base64.b64encode(f.read()).decode()

st.markdown(
    f"""
    <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
      <img src="data:image/jpeg;base64,{logo_base64}" style="width:82px;height:auto;display:block;">
      <div style="font-size:34px;font-weight:700;line-height:1.15;color:#2F3140;">安貝斯風味人格選酒顧問</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div style="font-size:18px;margin:2px 0 12px;">先不談酒名。用幾個生活與感官問題，找出最接近你的風味個性。</div>',
    unsafe_allow_html=True,
)

questions = [
    {"id":"Q01","title":"社交能量","question":"今晚最想把時間留給哪一種狀態？","options":{
        "A":{"text":"一個人安靜整理思緒","tags":["安靜","內省","慢飲"]},
        "B":{"text":"和一位熟悉的人好好聊天","tags":["親密","柔和","分享"]},
        "C":{"text":"三五好友輕鬆聚會","tags":["活潑","分享","易飲"]},
        "D":{"text":"把氣氛推到最高點","tags":["強烈","慶祝","高能量"]}}},
    {"id":"Q02","title":"生活節奏","question":"你的理想週末比較像哪一幕？","options":{
        "A":{"text":"晨光、書、沒有行程","tags":["清爽","細緻","低刺激"]},
        "B":{"text":"午後茶席與一段長談","tags":["茶香","雅緻","柔順"]},
        "C":{"text":"黃昏市集與街邊小吃","tags":["果香","鮮明","親切"]},
        "D":{"text":"夜晚派對與即興冒險","tags":["濃郁","強烈","高酒感"]}}},
    {"id":"Q03","title":"自然意象","question":"哪一種風景最像你現在的心情？","options":{
        "A":{"text":"竹林與薄霧","tags":["清幽","草本","內斂"]},
        "B":{"text":"金色夕陽與柑橘園","tags":["柑橘","明亮","溫暖"]},
        "C":{"text":"海風、礁石與鹹味空氣","tags":["海風","鹹感","俐落"]},
        "D":{"text":"木屋、火光與乾燥木香","tags":["木質","煙燻","成熟"]}}},
    {"id":"Q04","title":"味覺性格","question":"吃甜點時，你通常偏向？","options":{
        "A":{"text":"幾乎不甜，重視原味","tags":["乾型","穀物","純粹"]},
        "B":{"text":"微甜即可，尾韻乾淨","tags":["低甜","清爽","平衡"]},
        "C":{"text":"酸甜平衡，容易入口","tags":["酸甜","果香","易飲"]},
        "D":{"text":"濃郁甜香，層次越多越好","tags":["甜潤","濃郁","桶陳"]}}},
    {"id":"Q05","title":"口感偏好","question":"你喜歡的飲品口感比較接近？","options":{
        "A":{"text":"清脆俐落，像冰涼氣泡水","tags":["清爽","輕盈","俐落"]},
        "B":{"text":"滑順柔和，沒有壓迫感","tags":["柔順","圓潤","入門"]},
        "C":{"text":"厚實飽滿，入口有存在感","tags":["厚實","醇厚","熟成"]},
        "D":{"text":"強勁集中，能感覺到力量","tags":["高酒感","強勁","原漿"]}}},
    {"id":"Q06","title":"香氣直覺","question":"不看酒名，你最想靠近哪一種香氣？","options":{
        "A":{"text":"梅子、蜜桃與果乾","tags":["梅果","蜜桃","酸甜"]},
        "B":{"text":"柑橘、鳳梨與新鮮果皮","tags":["柑橘","熱帶水果","明亮"]},
        "C":{"text":"茶葉、香草與草本植物","tags":["茶香","草本","清新"]},
        "D":{"text":"烘烤穀物、木桶與太妃糖","tags":["穀香","木桶","焦糖"]}}},
    {"id":"Q07","title":"個性表達","question":"朋友通常怎麼形容你？","options":{
        "A":{"text":"安靜但有自己的深度","tags":["內斂","細緻","熟成"]},
        "B":{"text":"溫和、可靠、容易親近","tags":["柔順","平衡","大眾接受"]},
        "C":{"text":"有趣、有創意、常帶來驚喜","tags":["特色","草本","創新"]},
        "D":{"text":"果斷、有主見、氣場明確","tags":["強烈","高酒感","收藏"]}}},
    {"id":"Q08","title":"冒險程度","question":"面對沒喝過的風味，你會？","options":{
        "A":{"text":"先選經典安全款","tags":["經典","入門","平衡"]},
        "B":{"text":"熟悉中有一點變化最好","tags":["親切","特色","低風險"]},
        "C":{"text":"願意嘗試地方植物或特殊香氣","tags":["創新","在地","草本"]},
        "D":{"text":"越少見、越有挑戰越想試","tags":["限量","高酒感","實驗性"]}}},
    {"id":"Q09","title":"飲用情境","question":"你希望這瓶酒主要出現在？","options":{
        "A":{"text":"獨處慢飲，讓自己沉澱","tags":["慢飲","深度","熟成"]},
        "B":{"text":"餐桌上搭配料理","tags":["搭餐","平衡","乾淨"]},
        "C":{"text":"朋友聚會或調酒時刻","tags":["調酒","活潑","分享"]},
        "D":{"text":"重要節日或值得收藏的時刻","tags":["贈禮","收藏","尊榮"]}}},
    {"id":"Q10","title":"酒精感接受度","question":"你期待酒精帶來多少存在感？","options":{
        "A":{"text":"越低越好，以果香為主","tags":["低酒精","果香","易飲"]},
        "B":{"text":"有感但柔和，不想太刺激","tags":["中低酒感","柔順","平衡"]},
        "C":{"text":"明顯、有溫度，但仍要有層次","tags":["中高酒感","醇厚","熟成"]},
        "D":{"text":"喜歡強勁、集中、帶衝擊力","tags":["高酒感","原漿","強勁"]}}},
]


def get_alcohol_level(alcohol_text):
    if alcohol_text is None:
        return "待確認"
    text = str(alcohol_text).replace("%", "").replace("vol", "").strip()
    try:
        value = float(text)
        if value < 20:
            return "低"
        if value < 50:
            return "中高"
        return "高"
    except Exception:
        return "待確認"


def split_tags(tag_text):
    if tag_text is None:
        return []
    text = str(tag_text).strip()
    if text in ["", "待補", "待確認", "None"]:
        return []
    for mark in ["；", ";", ",", "，"]:
        text = text.replace(mark, "、")
    return [t.strip() for t in text.split("、") if t.strip()]


@st.cache_data
def load_products_from_excel():
    wb = load_workbook("data/安貝斯產品知識庫_維護主檔_補標籤.xlsx", data_only=True)
    ws = wb["知識庫產品主檔"]
    headers = [c.value for c in ws[1]]
    hm = {h: i for i, h in enumerate(headers) if h}
    out = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row[hm["產品編號"]]:
            continue
        if str(row[hm["產品類型"]]).strip() != "酒類":
            continue
        current = row[hm["是否現行商品"]]
        status = row[hm["商品狀態"]]
        alcohol = row[hm["酒精度"]]
        out.append({
            "id": row[hm["產品編號"]],
            "name": row[hm["產品名稱"]],
            "tags": split_tags(row[hm["風味標籤"]]),
            "alcohol_level": get_alcohol_level(alcohol),
            "status": status,
            "recommendable": str(current).strip() == "是" and str(status).strip() == "販售中",
            "url": row[hm["來源網址"]],
            "price": row[hm["價格"]],
            "alcohol": alcohol,
        })
    return out


products = load_products_from_excel()


@st.cache_resource(show_spinner="第一次啟動：正在載入中文 Embedding 模型與建立 RAG 索引...")
def build_rag_index():
    Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-zh-v1.5")
    Settings.tokenizer = tiktoken.get_encoding("cl100k_base").encode
    docs = SimpleDirectoryReader(
        input_dir="data",
        recursive=True,
        required_exts=[".md", ".txt"],
    ).load_data()
    return VectorStoreIndex.from_documents(docs)


def get_openrouter_client():
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("尚未設定 OPENROUTER_API_KEY。")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=key,
        default_headers={
            "HTTP-Referer": "https://streamlit.app",
            "X-Title": "ABAS Wine Personality Advisor",
        },
    )


if "step" not in st.session_state:
    st.session_state.step = 0
if "scores" not in st.session_state:
    st.session_state.scores = {}
if "finished" not in st.session_state:
    st.session_state.finished = False


if not st.session_state.finished:
    step = st.session_state.step
    q = questions[step]
    st.progress((step + 1) / len(questions))
    st.caption(f"第 {step + 1} / {len(questions)} 題")
    st.subheader(f"{q['id']}｜{q['title']}")
    st.write(q["question"])
    answer = st.radio(
        "請選擇：",
        list(q["options"].keys()),
        format_func=lambda x: f"{x}. {q['options'][x]['text']}",
        key=f"q_{step}",
    )

    if st.button("下一題", use_container_width=True):
        for tag in q["options"][answer]["tags"]:
            st.session_state.scores[tag] = st.session_state.scores.get(tag, 0) + 3
        if step + 1 >= len(questions):
            st.session_state.finished = True
        else:
            st.session_state.step += 1
        st.rerun()

else:
    st.success("測驗完成")
    user_scores = st.session_state.scores

    if "低酒精" in user_scores or "中低酒感" in user_scores:
        ual = "低"
    elif "中高酒感" in user_scores:
        ual = "中高"
    elif "高酒感" in user_scores:
        ual = "高"
    else:
        ual = None

    results = []
    for p in products:
        if not p["recommendable"]:
            continue
        if ual == "低" and p["alcohol_level"] in ["中高", "高"]:
            continue
        if ual == "中高" and p["alcohol_level"] == "高":
            continue

        score = 0
        matched = []
        for tag in p["tags"]:
            if tag in user_scores:
                score += 3
                matched.append(tag)
        if p["alcohol_level"] == ual:
            score += 4
        if p["status"] == "販售中":
            score += 2
        results.append({**p, "score": score, "matched_tags": matched})

    results.sort(key=lambda x: x["score"], reverse=True)
    top3 = results[:3]

    st.markdown('<div style="font-size:30px;font-weight:700;margin-top:20px;">你的風味人格</div>', unsafe_allow_html=True)
    top_tags = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:8]
    chips = "".join(
        f'<span style="display:inline-block;background:#F7F0E4;color:#7A5520;padding:7px 14px;border-radius:20px;margin:4px;font-size:16px;">{tag}</span>'
        for tag, _ in top_tags
    )
    st.markdown(chips, unsafe_allow_html=True)

    st.markdown('<div style="font-size:30px;font-weight:700;margin-top:18px;margin-bottom:18px;">你的推薦酒款</div>', unsafe_allow_html=True)
    labels = ["最像你的酒", "另一種可能", "想挑戰的酒"]

    for i, p in enumerate(top3):
        st.markdown(
            f"""
            <div style="border:1px solid #E8E2D8;border-radius:16px;padding:22px;margin-bottom:12px;background:#FFFDF9;">
              <div style="font-size:16px;color:#A9782A;font-weight:700;">{labels[i]}</div>
              <div style="font-size:25px;font-weight:700;margin:8px 0 14px;">{p['name']}</div>
              <div style="font-size:16px;line-height:1.8;">
                配對分數：{p['score']}<br>
                酒精感：{p['alcohol_level']}<br>
                酒精度：{p['alcohol'] if p['alcohol'] else '待確認'}<br>
                價格：{'NT$' + str(p['price']) if p['price'] else '待確認'}<br>
                命中標籤：{'、'.join(p['matched_tags']) if p['matched_tags'] else '目前無直接命中'}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if p["url"]:
            st.link_button("查看官方產品", p["url"], use_container_width=True)
        st.divider()

    if top3:
        try:
            index = build_rag_index()
            retriever = index.as_retriever(similarity_top_k=4)
            rq = f"""
使用者風味標籤：{user_scores}
推薦酒款：{[p['name'] for p in top3]}
請找相關安貝斯產品特色與推薦規則。
"""
            nodes = retriever.retrieve(rq)
            rag_context = "\n\n".join(n.get_content() for n in nodes)

            rec = ""
            for i, p in enumerate(top3, 1):
                rec += f"\n第{i}名｜{p['name']}｜分數{p['score']}｜酒精感{p['alcohol_level']}｜命中標籤：{'、'.join(p['matched_tags'])}"

            prompt = f"""你是安貝斯風味人格選酒顧問。排名已由 Python 決定，不得修改。
【RAG知識】
{rag_context}

【使用者標籤】
{user_scores}

【推薦結果】
{rec}

請以繁體中文輸出：
【你的風味人格輪廓】80～120字，2～3句。
【最像你的酒】直接寫產品名，2～3句。
【另一種可能】若有第2名才輸出，2～3句。
【想挑戰的酒】只有第3名存在才輸出，2～3句。
不得新增酒款、年份、原料或未提供資訊；推薦理由只可使用RAG知識、命中標籤與使用者標籤。"""

            client = get_openrouter_client()
            with st.spinner("安貝斯 AI 顧問正在雲端分析..."):
                resp = client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2,
                    timeout=120,
                )

            ai_text = resp.choices[0].message.content
            st.markdown(
                '<div class="ai-main-title">安貝斯 AI 顧問解讀</div>'
                '<div class="ai-subtitle">根據你的風味人格與安貝斯 RAG 知識庫，整理出推薦說明</div>'
                '<div class="ai-divider"></div>',
                unsafe_allow_html=True,
            )
            st.markdown(ai_text)

        except Exception as e:
            st.warning("目前無法完成雲端 AI / RAG 分析。")
            st.caption(f"錯誤資訊：{e}")

    if st.button("重新測驗", use_container_width=True):
        st.session_state.step = 0
        st.session_state.scores = {}
        st.session_state.finished = False
        st.rerun()
