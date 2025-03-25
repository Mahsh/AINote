import requests

def main(sql: str) -> dict:
    # Flask API 的地址
    '''
    API_URL = "http://127.0.0.1:5000/sql"
    # 用户输入（假设用户输入是要执行的 SQL 语句）
    user_input = "INSERT INTO todos (content, created_at, status, reminder, suggestion) VALUES ('学习 Dify', '2023-10-15 14:00:00', 0, '2023-10-16 22:00:00', '无')"
    '''
    API_URL = "http://8.138.178.146:5001/sql"
    user_input = sql
    user_input = "INSERT INTO todos (content, created_time, completed_time, status, reminder_time, suggestion) VALUES ('查看代码', NOW(), NULL, 0, '', '明日任务')"
    # user_input = "select * from todos"

    # 调用 Flask API
    try:
        response = requests.post(API_URL, json={"sql": user_input})
        if response.status_code == 200:
            result = response.json()
            print("API 调用成功，返回结果：", result)
            return {"result": f"{result}"}
        else:
            print("API 调用失败，状态码：", response.status_code, "错误信息：", response.json())
            return {"result": f"请求失败，状态码：{response.status_code},{response.json()}"}
    except Exception as e:
        print("调用 API 时发生错误：", str(e))
        return {"result": f"请求异常：{e}"}

if __name__ == '__main__':
    main("test")