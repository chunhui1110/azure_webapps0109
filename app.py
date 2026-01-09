from flask import Flask, request, render_template
import urllib.request
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("form.html")

@app.route('/aml', methods=['POST'])
def aml():
    # 1. 接收前端 4 項特徵資料
    age = request.values.get('p1')
    debt_ratio = request.values.get('p2')
    income = request.values.get('p3')
    past_due = request.values.get('p4')

    # 2. 組裝成 AML 端點所需的 JSON 格式 (對應你的模型欄位名稱)
    data = {
        "Inputs": {
            "input1": [
                {
                    "Age": age,
                    "DebtRatio": debt_ratio,
                    "MonthlyIncome": income,
                    "NumberOfTime30-59DaysPastDueNotWorse": past_due,
                    "SeriousDlqin2yrs": 0  # 預設預測目標
                },
            ],
        },
        "GlobalParameters": {}
    }

    body = str.encode(json.dumps(data))

    # 3. Azure ML 端點配置 (請替換為你的實際端點資訊)
    url = 'http://2285a820-842e-4f76-9be0-2506bcb9c71b.eastasia.azurecontainer.io/score'
    api_key = 'ijeNHrFOhkoR5F90LgD1Scfdh1ewSCKx'
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        
        # 4. 解析預測結果與機率
        # 假設 AML 回傳包含 'Scored Labels' 與 'Scored Probabilities'
        prediction = result['Results']['WebServiceOutput0'][0]
        label = str(prediction['Scored Labels'])
        # 取得違約機率並轉為百分比
        prob = float(prediction['Scored Probabilities'])
        
        risk_class = "高風險" if label == "1" else "低風險"
        risk_color = "danger" if label == "1" else "success"
        prob_display = f"{prob * 100:.2f}%"

        result_html = f"""
        <div class="card p-4 text-center shadow">
            <h2 class="text-{risk_color}">預測結果：{risk_class}</h2>
            <hr>
            <h4>預測違約機率：<span class="badge bg-secondary">{prob_display}</span></h4>
            <div class="mt-4"><a href="/" class="btn btn-outline-primary">重新評估</a></div>
        </div>
        """
    except Exception as e:
        result_html = f"<div class='alert alert-danger'>呼叫端點失敗：{str(e)}</div>"

    # 回傳結果頁面佈局
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <title>評估結果</title>
    </head>
    <body class="container py-5">{result_html}</body>
    </html>
    """

if __name__ == "__main__":
    app.run()