from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)  # Initialize Flask application
CORS(app)  # Allow Cross-Origin Resource Sharing (CORS) for the app

# Define default budget percentages for different expenses
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
    # Get expense data from the request
    data = request.get_json()
    Expenses = data.get("Expenses")
    Monthly_Income_After_Tax = data.get("Monthly_Income_After_Tax")
    Left_Over = Monthly_Income_After_Tax

    # Calculate budgeted expenses based on income and predefined percentages
    Budget_Expenses = {key: Monthly_Income_After_Tax * (value / 100) for key, value in Budget.items()}
    result = {}

    # Compare actual expenses with budgeted expenses and provide feedback
    for key, value in Expenses.items():
        if key in Budget_Expenses:
            if int(value) == Budget_Expenses[key]:
                result[key] = f"You are very close to going over Budget (yellow)"
            elif int(value) > Budget_Expenses[key]:
                result[key] = f"You should cutback by ${int(value) - Budget_Expenses[key]} (red)"
                Left_Over -= int(value)
            elif int(value) < Budget_Expenses[key]:
                result[key] = f"You are well under budget (green)"
                Left_Over -= int(value)
            else:
                Left_Over -= int(value)

    # Calculate and add remaining amount after expenses for investing
    result["Left Over"] = f"You have {Left_Over} left for investing"
    
    response = jsonify(result=result)  # Create JSON response
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin
    
    return response

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
