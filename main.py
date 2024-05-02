import numpy as np
import yfinance as yf
from flask_cors import CORS
from flask import Flask, request, jsonify
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

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

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    Ticker = data.get("Ticker_Symbol")

    # Ticker symbol of the stock (e.g., Apple Inc. is 'AAPL')
    # Ticker = "AAPL"

    # Fetch historical stock data for the past 51 days including the target (tomorrow's price)
    stock_data = yf.download(Ticker, period="51d", interval="1d")
    stock_data1 = yf.download(Ticker, period="1d", interval="1d")

    stock_prices = stock_data1['Close'].values


    # Calculate moving average (MA) for the past 10 days
    stock_data['MA_10'] = stock_data['Close'].rolling(window=10).mean()

    # Drop rows with missing values
    stock_data.dropna(inplace=True)

    # Feature engineering: Use 'Close' prices and 'MA_10' as features
    X = stock_data[['Close', 'MA_10']].values[:-1]  # Remove the last row to match with shifted y
    y = stock_data['Close'].shift(-1).dropna().values  # Shift y by -1 day

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train the linear regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Make predictions on the testing set
    predictions = model.predict(X_test)

    # Predict tomorrow's price using the last available data
    last_data_point = np.array([stock_data.iloc[-1]['Close'], stock_data.iloc[-1]['MA_10']]).reshape(1, -1)
    predicted_price = model.predict(last_data_point)

    response = {}

    response["Starting"] = (f"Starting price: {stock_prices[0]:.2f}")
    response["Predicted"] = (f"Predicted price: {predicted_price[0]:.2f}")

    response = jsonify(result=response)  # Create JSON response
    response.headers.add('Access-Control-Allow-Origin', '*')  # Allow requests from any origin

    return response

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
