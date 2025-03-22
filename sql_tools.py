from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 确保 JSON 响应支持中文

# 连接 SQLite 数据库
def get_db_connection():
    conn = sqlite3.connect('todos.db')
    conn.row_factory = sqlite3.Row # 使用 Row 工厂来返回字典形式的行
    return conn

# 获取当前时间
def get_current_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 创建表
@app.route('/create_table', methods=['POST'])
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    # 创建 todos 表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS todos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL,
        completed_at TEXT,
        status INTEGER NOT NULL DEFAULT 0,
        reminder TEXT,
        suggestion TEXT,
        expected_completion_time TEXT
    )
    ''')
    conn.commit()
    conn.close()
    return jsonify({'status': 'success', 'message': 'Table created'})

# 创建事项
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    content = data.get('content')
    reminder = data.get('reminder')
    suggestion = data.get('suggestion')
    expected_completion_time = data.get('expected_completion_time')

    if not content:
        return jsonify({'error': 'Content is required'}), 400

    created_at = get_current_time()
    status = 0  # 默认状态为 0（未开始）

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO todos (content, created_at, status, reminder, suggestion, expected_completion_time)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (content, created_at, status, reminder, suggestion, expected_completion_time))
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': todo_id, 'message': 'Todo created successfully'}), 201

# 获取所有事项
@app.route('/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos')
    todos = cursor.fetchall()
    conn.close()

    # 将结果转换为字典列表
    todos_list = [dict(todo) for todo in todos]
    return jsonify(todos_list)

# 获取单个事项
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    conn.close()

    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    return jsonify(dict(todo))

# 更新某一行某一列的元素
@app.route('/todos/<int:todo_id>/<column>', methods=['PATCH'])
def update_todo_column(todo_id, column):
    data = request.get_json()
    new_value = data.get('value')

    # 检查列名是否合法
    allowed_columns = ['content', 'status', 'reminder', 'suggestion', 'expected_completion_time']
    if column not in allowed_columns:
        return jsonify({'error': 'Invalid column name'}), 400

    # 检查状态是否为整数且在 0-100 之间
    if column == 'status':
        try:
            new_value = int(new_value)
            if new_value < 0 or new_value > 100:
                return jsonify({'error': 'Status must be between 0 and 100'}), 400
        except ValueError:
            return jsonify({'error': 'Status must be an integer'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查事项是否存在
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    if todo is None:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404

    # 更新指定列
    if column == 'status' and new_value == 100:
        # 如果状态更新为 100，则设置完成时间
        completed_at = get_current_time()
        cursor.execute(f'UPDATE todos SET {column} = ?, completed_at = ? WHERE id = ?', (new_value, completed_at, todo_id))
    else:
        cursor.execute(f'UPDATE todos SET {column} = ? WHERE id = ?', (new_value, todo_id))

    conn.commit()
    conn.close()

    return jsonify({'message': f'Column {column} updated successfully'})

# 删除事项
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查事项是否存在
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    if todo is None:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404

    # 删除事项
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Todo deleted successfully'})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)