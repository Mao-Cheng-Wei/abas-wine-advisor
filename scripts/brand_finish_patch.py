from pathlib import Path

app_path = Path('app.py')
req_path = Path('requirements.txt')
text = app_path.read_text(encoding='utf-8')

# Imports for official product image discovery.
if 'import re\n' not in text:
    text = text.replace('import os\nimport json\n', 'import os\nimport json\nimport re\nimport html\nimport requests\n')

# Use the official LINE short link published by ABAS.
text = text.replace('DEFAULT_LINE_URL = "https://line.me/R/ti/p/@abas"', 'DEFAULT_LINE_URL = "https://lin.ee/Hw3jvZI"')

old_func = '''def find_product_image(product_id):\n    if not PRODUCT_IMAGE_DIR.exists():\n        return None\n    for ext in ("jpg", "jpeg", "png", "webp"):\n        p = PRODUCT_IMAGE_DIR / f"{product_id}.{ext}"\n        if p.exists():\n            return str(p)\n    return None\n'''
new_func = '''@st.cache_data(ttl=86400, show_spinner=False)\ndef get_official_product_image(product_url):\n    if not product_url or "dagc.com.tw" not in str(product_url):\n        return None\n    try:\n        r = requests.get(\n            str(product_url),\n            timeout=8,\n            headers={"User-Agent": "Mozilla/5.0 ABAS-Wine-Advisor/1.0"},\n        )\n        r.raise_for_status()\n        page = r.text\n        patterns = [\n            r'<meta[^>]+property=["\\\']og:image["\\\'][^>]+content=["\\\']([^"\\\']+)',\n            r'<meta[^>]+content=["\\\']([^"\\\']+)["\\\'][^>]+property=["\\\']og:image["\\\']',\n        ]\n        for pattern in patterns:\n            m = re.search(pattern, page, flags=re.I)\n            if m:\n                return html.unescape(m.group(1))\n    except Exception:\n        return None\n    return None\n\n\ndef find_product_image(product_id, product_url=None):\n    if PRODUCT_IMAGE_DIR.exists():\n        for ext in ("jpg", "jpeg", "png", "webp"):\n            p = PRODUCT_IMAGE_DIR / f"{product_id}.{ext}"\n            if p.exists():\n                return str(p)\n    return get_official_product_image(product_url)\n'''
if old_func in text:
    text = text.replace(old_func, new_func)

text = text.replace('image_path = find_product_image(p["id"])', 'image_path = find_product_image(p["id"], p.get("url"))')

# Refine top-of-page brand framing without crowding the questionnaire.
brand_line = 'st.markdown(\'<div class="brand-line"></div>\', unsafe_allow_html=True)\n'
brand_detail = '''st.markdown('<div class="brand-line"></div>', unsafe_allow_html=True)\nst.caption("台中大安風土｜純糧固態發酵蒸餾｜30年釀酒傳承")\n'''
if brand_line in text and '30年釀酒傳承' not in text:
    text = text.replace(brand_line, brand_detail, 1)

# Add a compact brand block near the bottom, before the sharing section.
marker = '    st.markdown(\'<div class="section-title">分享我的風味結果</div>\', unsafe_allow_html=True)\n'
brand_block = '''    st.markdown('<div class="section-title">關於安貝斯</div>', unsafe_allow_html=True)\n    with st.container(border=True):\n        st.markdown("**在地的人・在地的酒**")\n        st.write(\n            "安貝斯扎根台中大安，承接地方古法釀酒智慧，持續以純糧固態發酵蒸餾與現代食品科學，\n"\n            "釀出能代表大安海風、土地與時間的在地酒。品牌也持續與地方小農合作，讓台灣農產成為風味的一部分。"\n        )\n        b1, b2, b3 = st.columns(3)\n        with b1:\n            st.link_button("品牌故事", "https://www.dagc.com.tw/brandstory", use_container_width=True)\n        with b2:\n            st.link_button("釀酒工藝", "https://www.dagc.com.tw/craft", use_container_width=True)\n        with b3:\n            st.link_button("品嚐安貝斯", "https://www.dagc.com.tw/products", use_container_width=True)\n\n    st.markdown('<div class="section-title">分享我的風味結果</div>', unsafe_allow_html=True)\n'''
if marker in text and '關於安貝斯' not in text:
    text = text.replace(marker, brand_block, 1)

# Clarify fallback image copy if the official page has no detectable image.
text = text.replace('st.caption("商品圖片待補")', 'st.caption("官方商品圖載入中／待補")')

app_path.write_text(text, encoding='utf-8')

req = req_path.read_text(encoding='utf-8')
if 'requests>=' not in req:
    if not req.endswith('\n'):
        req += '\n'
    req += 'requests>=2.32\n'
req_path.write_text(req, encoding='utf-8')
