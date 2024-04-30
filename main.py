from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

Budget = {
    "Rent": 30,
    "Utilities": 10,
    "Subscriptions": 5,
    "Groceries": 10,
    "Car Payment": 15,
    "Debt": 10,
    "Savings": 15,
    "Custom": 5
}

@app.route("/budget", methods=["POST"])
def budget():
    data = request.get_json()
    Expenses = data.get("Expenses")
    Monthly_Income_After_Tax = data.get("Monthly_Income_After_Tax")
    Left_Over = Monthly_Income_After_Tax

    Budget_Expenses = {key: Monthly_Income_After_Tax * (value / 100) for key, value in Budget.items()}

    result = ""
    for key, value in Expenses.items():
        if key in Budget_Expenses:
            if int(value) > Budget_Expenses[key]:
                result += f"You should cutback on {key} by ${int(value) - Budget_Expenses[key]}\n"
                Left_Over -= int(value)
            elif int(value) < Budget_Expenses[key]:
                Left_Over -= int(value)
            else:
                Left_Over -= int(value)

    result += f"You have {Left_Over} left for investing\n"
    
    response = jsonify(result=result)
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    
    return response

if __name__ == '__main__':
    app.run(debug=True)
