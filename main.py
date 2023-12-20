import streamlit as st
from PIL import Image, ImageEnhance, ImageChops
from io import BytesIO
import os

# Streamlitアプリのタイトルを設定
st.title('複数画像アップロードとスライドバーによる切り替えデモ')

# 複数の画像をアップロードするためのウィジェットを作成
uploaded_files = st.file_uploader("画像を選択してください", type=['jpg', 'png'], accept_multiple_files=True)

# アップロードされた画像がある場合にのみ処理を実行
if uploaded_files:
    # スライドバーを作成
    # スライドバーの値は選択された画像のインデックスに対応
    image_index = st.slider('画像を選択', 0, len(uploaded_files) - 1)

    # 選択された画像を表示
    selected_image = uploaded_files[image_index]
    bytes_data = selected_image.getvalue()
    image = Image.open(BytesIO(bytes_data))

    # 前の画像（n-1枚目）を取得
    if image_index > 0:
        previous_image = uploaded_files[image_index - 1]
        bytes_data_previous = previous_image.getvalue()
        previous_image = Image.open(BytesIO(bytes_data_previous))

        # 透過率を50%に設定
        previous_image = previous_image.convert("RGBA")
        alpha = 128  # 50%透過率 (0から255の範囲で指定)
        previous_image.putalpha(alpha)

        # 画像を合成
        combined_image = Image.alpha_composite(image.convert("RGBA"), previous_image)
        
        # ファイル名を取得して表示
        previous_image_name = os.path.basename(uploaded_files[image_index - 1].name)
        selected_image_name = os.path.basename(selected_image.name)
        st.image(combined_image, caption=f'合成された画像 (前の画像: {previous_image_name}, 今の画像: {selected_image_name})', use_column_width=True)

        # 画像の差分を生成
        diff_image = ImageChops.difference(image.convert("RGB"), previous_image.convert("RGB"))
        
        # 差分画像を表示
        st.image(diff_image, caption=f'画像の差分 (前の画像: {previous_image_name}, 今の画像: {selected_image_name})', use_column_width=True)
    else:
        st.warning("前の画像がありません。")
