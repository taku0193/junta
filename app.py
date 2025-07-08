from flask import Flask, render_template

# Flaskアプリケーションを初期化
app = Flask(__name__)

@app.route('/')
def index():
    """クライアントのページ (index.html) を表示するだけ"""
    return render_template('index.html')

if __name__ == '__main__':
    # シンプルなHTTPサーバーとして実行
    app.run(host='0.0.0.0', port=5000, debug=True)
