# 安貝斯風味人格選酒顧問｜雲端部署包

## 使用技術
- Streamlit Community Cloud：免費 Web Hosting
- OpenRouter：雲端 LLM（預設 `openrouter/free`）
- FastEmbed：`BAAI/bge-small-zh-v1.5` 中文 Embedding，於雲端 Web 容器執行
- LlamaIndex：RAG
- Excel：產品主檔
- Python 規則引擎：硬性篩選與 Top 3 排名

## 本機驗證
1. `python -m pip install -r requirements.txt`
2. 將 `.streamlit/secrets.toml.example` 複製為 `.streamlit/secrets.toml`
3. 填入 OpenRouter API Key
4. `python -m streamlit run app.py`

## Streamlit Community Cloud
1. 把整個專案上傳 GitHub。
2. 到 Streamlit Community Cloud 建立 App。
3. Main file path 選 `app.py`。
4. Secrets 加入：`OPENROUTER_API_KEY="你的金鑰"`
5. Deploy。

## 正式營運建議
`openrouter/free` 適合 Demo / 低流量驗證。安貝斯正式公開營運後，建議改為固定模型並設定預算上限，避免免費路由模型變動造成語氣與品質不一致。
