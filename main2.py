import streamlit as st  # Streamlitライブラリをインポート
from PIL import Image  # PILライブラリからImageをインポート
import numpy as np  # Numpyライブラリをインポート
import cv2  # OpenCVライブラリをインポート
from io import BytesIO  # BytesIOをインポート

# アップロードされたファイルをOpenCV形式に変換する関数
def load_image(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.read()  # ファイルのバイトデータを読み込む
        pil_image = Image.open(BytesIO(bytes_data))  # PILイメージとして開く
        cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)  # OpenCVの形式に変換
        return cv_image
    return None

# Streamlit UIの設定
st.title("画像比較ツール")  # タイトルの設定

# 複数ファイルアップローダーウィジェット
uploaded_files = st.file_uploader("Upload images:", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

# アップロードされた画像を読み込み、保存
loaded_images = [load_image(file) for file in uploaded_files if file is not None]

# 画像インデックス選択用のスライダー
if len(loaded_images) > 1:
    selected_index = st.slider("Select Image Index for Comparison", 1, len(loaded_images)) - 1

    # 有効な選択がある場合の処理
    if selected_index < len(loaded_images) and selected_index > 0:
        image1 = cv2.cvtColor(loaded_images[selected_index - 1], cv2.COLOR_BGR2RGB)
        image2 = cv2.cvtColor(loaded_images[selected_index], cv2.COLOR_BGR2RGB)

        akaze = cv2.AKAZE_create()  # AKAZEオブジェクトを作成
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)  # 画像をグレースケールに変換
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        # AKAZEを使用してキーポイントとディスクリプタを見つける
        kp1, des1 = akaze.detectAndCompute(gray1, None)
        kp2, des2 = akaze.detectAndCompute(gray2, None)

        # マッチャーの初期化
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # ディスクリプタをマッチング
        matches = bf.match(des1, des2)

        # マッチの距離順にソート
        matches = sorted(matches, key=lambda x: x.distance)

        # 良いマッチの位置を抽出
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = kp1[match.queryIdx].pt
            points2[i, :] = kp2[match.trainIdx].pt

        # ホモグラフィを見つける
        h, mask = cv2.findHomography(points2, points1, cv2.RANSAC)

        # ホモグラフィを使用して画像を変形
        height, width, channels = image1.shape
        aligned_image2 = cv2.warpPerspective(image2, h, (width, height))

        # 画像を50%の透明度で重ね合わせ
        blended_image = cv2.addWeighted(image1, 0.5, aligned_image2, 0.5, 0)
        # 比較した画像を表示
        col1, col2 = st.columns(2)
        with col1:
            st.image(image1, caption="Previous Image", use_column_width=True)
        with col2:
            st.image(image2, caption="Selected Image", use_column_width=True)
        # 比較結果またはブレンドした画像を表示
        st.image(blended_image, caption="Comparison Result", use_column_width=True)
