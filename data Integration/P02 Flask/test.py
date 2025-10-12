from flask import Flask, render_template
from data_loader import load_data

app = Flask(__name__)


@app.route('/')
def index():
    """主页路由，显示书籍表格"""
    books = load_data('book.txt')
    return render_template('index.html', books=books)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)