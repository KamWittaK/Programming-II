from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

Budget = {
    "Rent": 30,
    "Utilities": 10,
    "Subscription": 5,
    "Groceries": 15,
    "Car Payment": 15,
    "Debt": 10,
    "Savings": 15
}

@app.route("/budget", methods=["POST"])
def budget():
    data = request.get_json()
    Expensises = data.get("Expensises")
    Monthly_Income_After_Tax = data.get("Monthly_Income_After_Tax")
    Left_Over = 0

    Budget_Expensises = {key: Monthly_Income_After_Tax * (value / 100) for key, value in Budget.items()}

    result = ""
    for key, value in Expensises.items():
        if int(value) == Budget_Expensises[key]:
            result += f"You are within your budget for {key}\n"
        elif int(value) > Budget_Expensises[key]:
            result += f"You should cutback on {key} by {int(value) - Budget_Expensises[key]}\n"
        elif int(value) < Budget_Expensises[key]:
            result += f"You have {Budget_Expensises[key] - int(value)} left over from {key}\n"
    
    result += f"You have {Left_Over} left for investing\n"
    return jsonify(result=result)

if __name__ == '__main__':
    app.run(debug=True)