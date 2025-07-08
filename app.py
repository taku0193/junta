import cv2
import numpy as np
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import mediapipe as mp

# FlaskアプリケーションとSocketIOを初期化
# Initialize Flask app and SocketIO
app = Flask(__name__)
# セキュリティキーは本番環境では複雑なものに変更してください
# Change the secret key to something complex in a production environment
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# MediaPipe Poseを初期化
# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

@app.route('/')
def index():
    """クライアントのページ (index.html) を表示"""
    # Render the client page (index.html)
    return render_template('index.html')

@socketio.on('image')
def handle_image(data_image):
    """クライアントから 'image' イベントで送られてきた画像を処理"""
    # Process the image sent from the client via the 'image' event
    
    # Base64エンコードされた画像データをデコード
    # Decode the Base64 encoded image data
    try:
        # ヘッダー部分（例: 'data:image/jpeg;base64,'）を削除
        # Remove the header part (e.g., 'data:image/jpeg;base64,')
        header, encoded = data_image.split(',', 1)
        sbuf = base64.b64decode(encoded)
        nparr = np.frombuffer(sbuf, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    except (ValueError, TypeError) as e:
        print(f"Error decoding image: {e}")
        return

    if frame is None:
        print("Failed to decode frame")
        return

    # 映像を左右反転させると、ユーザーの動きと画面上の動きが一致して直感的になります
    # Flipping the frame horizontally makes it intuitive, matching the user's movement
    frame = cv2.flip(frame, 1)
    
    # 色空間をBGRからRGBに変換
    # Convert color space from BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    rgb_frame.flags.writeable = False # パフォーマンス向上のため書き込み不可に

    # MediaPipeで姿勢を推定
    # Perform pose estimation with MediaPipe
    results = pose.process(rgb_frame)
    
    rgb_frame.flags.writeable = True # 再び書き込み可能に

    # 検出されたランドマークの座標をクライアントに送信
    # Send the coordinates of detected landmarks to the client
    if results.pose_landmarks:
        landmarks = []
        for landmark in results.pose_landmarks.landmark:
            landmarks.append({
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            })
        # 'pose_data'イベントでランドマークデータを送信
        # Emit landmark data with the 'pose_data' event
        emit('pose_data', {'landmarks': landmarks})

if __name__ == '__main__':
    # サーバーを実行
    # Run the server
    # host='0.0.0.0'は、同じネットワーク内の他のデバイスからのアクセスを許可します
    # host='0.0.0.0' allows access from other devices on the same network
    socketio.run(app, port=5000, debug=True)
