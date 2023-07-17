import streamlit as st
import time
import pdfplumber
import io
import matplotlib.pyplot as plt
import numpy as np
import fitz

st.set_option("deprecation.showfileUploaderEncoding", False)

st.sidebar.title("AI_OCRアプリ")
st.sidebar.write("添付のPDFの文字やその座標を検出します。")

st.sidebar.write("")

pdf_file = st.sidebar.file_uploader("PDFファイルを選択してください。", type=["pdf"])

def extract_text_and_coordinates(pdf_data):
    # バイト列からPDFを開く
    with pdfplumber.open(io.BytesIO(pdf_data)) as pdf:
        results = []
        for i, page in enumerate(pdf.pages):
            # ページから単語を抽出
            for word in page.extract_words():
                # 単語と座標情報を保存
                result = {
                    'page': i + 1,
                    'text': word['text'],
                    'left_x': word['x0'],
                    'top_y': word['top'],
                    'right_x': word['x1'],
                    'bottom_y': word['bottom'],
                }
                results.append(result)
    return results

text_and_coordinates = []

# PDFファイルがアップロードされたら処理を開始
if pdf_file is not None:
    with st.spinner('Processing...'):
        pdf_data = pdf_file.getvalue()
        text_and_coordinates = extract_text_and_coordinates(pdf_data)
    st.success('Processing done!')

# 結果の表示
if text_and_coordinates:
    st.write('0から',len(text_and_coordinates)-1,'まで')
    number = st.number_input('何個目の文字を表示しますか？',value=0, min_value=0, max_value=len(text_and_coordinates)-1)
    selected_text = text_and_coordinates[number]
    st.write(selected_text)

    # PDFを画像に変換
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    page = doc.load_page(selected_text['page'] - 1) # 0-based index
    pix = page.get_pixmap()
    img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)

    # RGBA to RGB
    img = img[..., :3]

    # 選択されたテキストの座標に矩形を描画
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    rect = plt.Rectangle((selected_text['left_x'], selected_text['top_y']), selected_text['right_x'] - selected_text['left_x'], selected_text['bottom_y'] - selected_text['top_y'], edgecolor='r', facecolor='none')
    ax.add_patch(rect)
    st.pyplot(fig)  # Streamlit 用に変更
