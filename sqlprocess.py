from flask import Flask, request, jsonify
import sqlite3
import re
import os

app = Flask(__name__)

# 连接到 SQLite 数据库
def get_db_connection():
    conn = sqlite3.connect('todo.db')
    conn.row_factory = sqlite3.Row  # 使用 Row 工厂来返回字典形式的行
    return conn

# 检查 SQL 语句是否合法
def is_sql_allowed(sql):
    """
    检查 SQL 语句是否合法，仅允许 SELECT、INSERT、UPDATE、DELETE 操作。
    """
    # 转换为小写并去除多余空格
    sql = sql.strip().lower()
    # 检查是否以允许的关键字开头
    if re.match(r'^(select|insert|update|delete)', sql):
        return True
    return False

# 执行 SQL 语句
def execute_sql(sql):
    """
    执行 SQL 语句并返回结果。
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        # 如果是查询操作，返回结果
        if sql.strip().lower().startswith('select'):
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
        else:
            # 如果是增删改操作，返回受影响的行数
            conn.commit()
            result = {"rows_affected": cursor.rowcount}
    except sqlite3.Error as e:
        result = {"error": str(e)}
    finally:
        conn.close()

    return result

# SQL 接口
@app.route('/sql', methods=['POST'])
def sql_endpoint():
    data = request.get_json()
    sql = data.get('sql')

    if not sql:
        return jsonify({"error": "SQL statement is required"}), 400

    # 检查 SQL 语句是否合法
    if not is_sql_allowed(sql):
        return jsonify({"error": "Only SELECT, INSERT, UPDATE, DELETE statements are allowed"}), 400

    # 执行 SQL 语句
    result = execute_sql(sql)
    if "error" in result:
        return jsonify(result), 500
    else:
        return jsonify(result)

# 初始化数据库
def init_db():
    # 检查数据库文件是否存在
    if not os.path.exists('todo.db'):
        print("Database does not exist. Creating new database...")
        conn = sqlite3.connect('todo.db')
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
        print("Database initialized successfully")
    else:
        print("Database already exists. Skipping initialization.")

if __name__ == '__main__':
    init_db()  # 初始化数据库（仅在第一次运行时执行）
    app.run(host='127.0.0.1', port=5001)

'''
测试用例
有效的 SELECT 查询：
curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT * FROM todos"}' http://8.138.178.146:5001/sql

有效的 INSERT 操作：
curl -X POST -H "Content-Type: application/json" -d '{"sql": "INSERT INTO todos (content, created_at) VALUES (\'Test todo\', \'2023-10-27 10:00:00\') "}' http://8.138.178.146:5001/sql

有效的 UPDATE 操作：
curl -X POST -H "Content-Type: application/json" -d '{"sql": "UPDATE todos SET content = \'updated content\' WHERE id = 1"}' http://8.138.178.146:5001/sql

有效的 DELETE 操作：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "DELETE FROM todos WHERE id = 1"}' http://8.138.178.146:5001/sql
无效的 SQL 语句（不允许的关键字）：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "CREATE TABLE test (id INTEGER)"}' http://8.138.178.146:5001/sql
无效的 SQL 语句（语法错误）：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT FROM todos"}' http://8.138.178.146:5001/sql
缺少 SQL 语句：

Bash

curl -X POST -H "Content-Type: application/json" -d '{}' http://8.138.178.146:5001/sql
空的 SQL 语句：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": ""}' http://8.138.178.146:5001/sql
使用 SQL 注入的尝试：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT * FROM todos; DROP TABLE todos;"}' http://8.138.178.146:5001/sql
查询不存在的表：

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT * FROM non_existent_table"}' http://8.138.178.146:5001/sql
查询数据表中的特定字段

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT content, created_at FROM todos"}' http://8.138.178.146:5001/sql
使用where条件语句进行查询

Bash

curl -X POST -H "Content-Type: application/json" -d '{"sql": "SELECT * FROM todos WHERE id = 1"}' http://8.138.178.146:5001/sql

'''