from flask import Flask,request,render_template
import urllib
import json
import os

app = Flask(__name__)
@app.route('/')
def index():
    return render_template("form.html")

@app.route('/<name>')
def hello(name):
    return "Hello, " + name + "!!!"

@app.route('/aml', methods=['GET','POST'])
def aml():
    data = {
        "Inputs": {
            "input1":
            [
                {
                    "Pregnancies": 6,
                    "Glucose": request.values['p5'],
                    "BloodPressure": request.values['p4'],
                    "SkinThickness": 35,
                    "Insulin": request.values['p6'],
                    "BMI": request.values['p3'],
                    "DiabetesPedigreeFunction": 0.627,
                    "Age": request.values['p1'],
                    "Outcome": 1
                },
            ],
        },
        "GlobalParameters": {
        }
    }

    body = str.encode(json.dumps(data))

    url = 'http://2285a820-842e-4f76-9be0-2506bcb9c71b.eastasia.azurecontainer.io/score'

    api_key = 'ijeNHrFOhkoR5F90LgD1Scfdh1ewSCKx'
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer " + api_key
    }

    req = urllib.request.Request(url, body, headers)

    htmlstr="<html><body>"

    try:
        response = urllib.request.urlopen(req)

        result = json.loads(response.read())
        htmlstr=htmlstr+"依據您輸入的參數，經過決策模型比對，診斷糖尿病的結果為"
        if str(result['Results']['WebServiceOutput0'][0]['Scored Labels']) == "1.0":
            htmlstr += " 陽性"
        else:
            htmlstr += " 陰性"

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(json.loads(error.read().decode("utf8", 'ignore')))

        htmlstr=htmlstr+"</body></html>"
    return htmlstr

if __name__=="__main__":
    app.run()