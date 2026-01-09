from flask import Flask, request, render_template
import urllib.request
import json
import os

app = Flask(__name__)

# 首頁：顯示表單頁面
@app.route('/')
def index():
    return render_template("form.html")

# 測試路徑
@app.route('/hello/<name>')
def hello(name):
    return "Hello, " + name + "!!!"

# 處理預測邏輯
@app.route('/aml', methods=['GET', 'POST'])
def aml():
    # 1. 接收前端傳來的資料 (與 form.html 的 name 屬性對應)
    try:
        p1 = request.values.get('p1', 0) # Age
        p3 = request.values.get('p3', 0) # BMI
        p4 = request.values.get('p4', 0) # BloodPressure
        p5 = request.values.get('p5', 0) # Glucose
        p6 = request.values.get('p6', 0) # Insulin
    except KeyError:
        return "表單資料讀取失敗，請確認所有欄位皆已填寫。"

    # 2. 組裝成 Azure ML 端點所需的 JSON 格式
    data = {
        "Inputs": {
            "input1": [
                {
                    "Pregnancies": 6,
                    "Glucose": p5,
                    "BloodPressure": p4,
                    "SkinThickness": 35,
                    "Insulin": p6,
                    "BMI": p3,
                    "DiabetesPedigreeFunction": 0.627,
                    "Age": p1,
                    "Outcome": 1
                },
            ],
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    # 3. 設定 Azure ML 端點資訊
    url = 'http://2285a820-842e-4f76-9be0-2506bcb9c71b.eastasia.azurecontainer.io/score'
    api_key = 'ijeNHrFOhkoR5F90LgD1Scfdh1ewSCKx'
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + api_key
    }

    req = urllib.request.Request(url, body, headers)

    # 4. 呼叫端點並處理回傳結果
    # 初始化 HTML 字串與結果容器
    response_content = ""
    result_text = ""
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        
        # 根據回傳結構抓取 Scored Labels
        # 這裡假設回傳格式為：result['Results']['WebServiceOutput0'][0]['Scored Labels']
        scored_label = str(result['Results']['WebServiceOutput0'][0]['Scored Labels'])
        
        if scored_label == "1.0":
            result_text = "<h3 style='color:red;'>診斷結果：陽性 (高風險)</h3>"
        else:
            result_text = "<h3 style='color:green;'>診斷結果：陰性 (低風險)</h3>"
            
    except urllib.error.HTTPError as error:
        result_text = f"<h3 style='color:gray;'>預測失敗，錯誤代碼: {error.code}</h3>"
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))
    except Exception as e:
        result_text = f"<h3 style='color:gray;'>發生系統錯誤: {str(e)}</h3>"

    # 5. 回傳簡單的結果頁面
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>預測結果</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container py-5 text-center">
        <div class="card shadow p-4">
            <h2>依據您輸入的參數，經過決策模型比對：</h2>
            <hr>
            {result_text}
            <div class="mt-4">
                <a href="/" class="btn btn-primary">返回重新輸入</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

if __name__ == "__main__":
    # 在本機測試時開啟 debug，部署到 Azure 後通常由 gunicorn 啟動
    app.run(host='0.0.0.0', port=5000)