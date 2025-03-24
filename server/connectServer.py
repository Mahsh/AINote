# connect to server
from flask import Flask, jsonify, request, abort
import sqlite3

app = Flask(__name__)


# 连接到SQLite数据库
def get_db_connection():
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row  # 返回字典形式的结果
    return conn


# 初始化数据库（创建表和插入示例数据）
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    # 插入示例数据
    cursor.execute("INSERT OR IGNORE INTO users (name, age) VALUES ('Alice', 30)")
    cursor.execute("INSERT OR IGNORE INTO users (name, age) VALUES ('Bob', 25)")
    conn.commit()
    conn.close()


# 获取所有用户
@app.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return jsonify([dict(user) for user in users])


# 获取单个用户
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user is None:
        abort(404, description="User not found")
    return jsonify(dict(user))


# 添加新用户
@app.route('/users', methods=['POST'])
def add_user():
    if not request.json or not 'name' in request.json or not 'age' in request.json:
        abort(400, description="Invalid request: name and age are required")

    name = request.json['name']
    age = request.json['age']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': user_id, 'name': name, 'age': age}), 201


# 更新用户信息
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    if not request.json:
        abort(400, description="Invalid request: JSON body is required")

    name = request.json.get('name')
    age = request.json.get('age')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查用户是否存在
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        abort(404, description="User not found")

    # 更新用户信息
    if name:
        cursor.execute('UPDATE users SET name = ? WHERE id = ?', (name, user_id))
    if age:
        cursor.execute('UPDATE users SET age = ? WHERE id = ?', (age, user_id))
    conn.commit()
    conn.close()

    return jsonify({'id': user_id, 'name': name, 'age': age})


# 删除用户
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查用户是否存在
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    if user is None:
        conn.close()
        abort(404, description="User not found")

    # 删除用户
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return jsonify({'result': True})


# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': str(error)}), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error)}), 400


# 启动应用
if __name__ == '__main__':
    init_db()  # 初始化数据库
    app.run(host='0.0.0.0', port=5000)