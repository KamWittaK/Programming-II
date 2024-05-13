import os
import pyotp
import qrcode
import requests
import numpy as np
import pandas as pd
import yfinance as yf
import multiprocessing as mp
from io import BytesIO
from flask_cors import CORS
from flask import Flask, request, jsonify, send_file
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

def fetch_sp500_tickers():
    # Fetch S&P 500 data from Wikipedia
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    sp500_df = table[0]
    tickers = sp500_df['Symbol'].tolist()
    
    # Correcting specific ticker symbols that might not be formatted correctly
    tickers = [ticker.replace('.', '-') for ticker in tickers]
    
    return tickers

def predict_tomorrows_price_multiprocessing(ticker_symbol):
    try:
        # Fetch historical stock data for the past 51 days including the target (tomorrow's price)
        stock_data = yf.download(ticker_symbol, period="51d", interval="1d")
        if stock_data.empty:
            print(f"No data for {ticker_symbol}")
            return None
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

        # Predict tomorrow's price using the last available data
        last_data_point = np.array([stock_data.iloc[-1]['Close'], stock_data.iloc[-1]['MA_10']]).reshape(1, -1)
        predicted_price = model.predict(last_data_point)
        
        # Calculate the percentage change
        current_price = stock_data.iloc[-1]['Close']
        percentage_change = ((predicted_price[0] - current_price) / current_price) * 100

        return {
            "Ticker": ticker_symbol,
            "Current Price": f"{current_price:.2f}",
            "Predicted Price": f"{predicted_price[0]:.2f}",
            "Percentage Change": f"{percentage_change:.2f}"
        }

    except Exception as e:
        print(f"Error processing {ticker_symbol}: {e}")
        return None

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

@app.route("/predict_saved_stocks", methods=["POST"])
def predict_saved_stocks():
    data = request.get_json()

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/stock_predictions.csv"))
    database = pd.read_csv(csv_path)
    
    row_index = database.index[database['Username'] == data['Username']].tolist()


    if row_index:
        tickers_string = database.at[row_index[0], 'Tickers']
        # Split the tickers string into a list, and strip extra quotes if necessary
        tickers = [ticker.strip().replace('"', '') for ticker in tickers_string.split(",")]

        data = {}

        for i in tickers:
            data[i] = predict_tomorrows_price_multiprocessing(i)

        return jsonify({"Tickers": data})
    else:
        return jsonify({"Error": "Username not found"})

@app.route("/predict_all_stocks", methods=["GET"])
def predict():
    tickers = fetch_sp500_tickers()
    results = []
    
    # Define the number of processes to use (adjust as needed)
    num_processes = mp.cpu_count()  # Utilize all available CPU cores
    
    with mp.Pool(processes=num_processes) as pool:
        results = pool.map(predict_tomorrows_price_multiprocessing, tickers)
    
    # Filter out None results
    results = [result for result in results if result is not None]
    
    results_df = pd.DataFrame(results)

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/stock_predictions.csv"))
    results_df.to_csv(csv_path, index=False)
    
    data = pd.read_csv(csv_path)
    top_changes = data.sort_values(by='Percentage Change', ascending=False).head(10)
    
    # Convert DataFrame to dictionary
    top_changes_dict = top_changes.to_dict(orient='records')
    
    print("Top 10 stocks with the highest percentage changes:")
    return jsonify(top_changes_dict)

def test():
    return jsonify([
	{
		"Current Price": 117.31,
		"Percentage Change": 3.49,
		"Predicted Price": 121.41,
		"Ticker": "MRNA"
	},
	{
		"Current Price": 61.92,
		"Percentage Change": 3.22,
		"Predicted Price": 63.91,
		"Ticker": "ETSY"
	},
	{
		"Current Price": 283.44,
		"Percentage Change": 3.16,
		"Predicted Price": 292.41,
		"Ticker": "CPAY"
	},
	{
		"Current Price": 146.32,
		"Percentage Change": 2.98,
		"Predicted Price": 150.68,
		"Ticker": "ABNB"
	},
	{
		"Current Price": 108.35,
		"Percentage Change": 2.76,
		"Predicted Price": 111.34,
		"Ticker": "ENPH"
	},
	{
		"Current Price": 183.4,
		"Percentage Change": 2.3,
		"Predicted Price": 187.62,
		"Ticker": "EPAM"
	},
	{
		"Current Price": 143.0,
		"Percentage Change": 2.24,
		"Predicted Price": 146.2,
		"Ticker": "XYL"
	},
	{
		"Current Price": 97.18,
		"Percentage Change": 2.13,
		"Predicted Price": 99.25,
		"Ticker": "IFF"
	},
	{
		"Current Price": 132.0,
		"Percentage Change": 2.12,
		"Predicted Price": 134.8,
		"Ticker": "EL"
	},
	{
		"Current Price": 163.38,
		"Percentage Change": 2.07,
		"Predicted Price": 166.77,
		"Ticker": "GE"
	}
])

@app.route("/save_expenses", methods=["POST"])
def save_expenses():
    data = request.get_json()
    username = data.get('Username')
    expenses = data.get('Expenses')

    if not username:
        return jsonify({"Status": "Not Successful", "Reason": "No username provided"})

    if not expenses:
        return jsonify({"Status": "Not Successful", "Reason": "No expenses provided"})

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))
    database = pd.read_csv(csv_path)

    # Check if the username exists in the database
    row_index = database.index[database['Username'] == username].tolist()

    if row_index:
        # Update expenses for the existing user
        for key, value in expenses.items():
            database.at[row_index[0], key] = value
    else:
        return jsonify({"Status": "Error", "Message": "Username not Found"})

    # Save the updated database to CSV
    database.to_csv(csv_path, index=False)

    return jsonify({"Status": "Success", "Message": "Expenses saved successfully"})

@app.route("/signupapi", methods=["POST"])
def signup():
    data = request.get_json()
    current_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))
    database = pd.read_csv(csv_path)

    if 'Username' not in data:
        return jsonify({"Status": "Not Successful", "Reason": "No username provided"}), 400

    if data['Username'] in database['Username'].values:
        return jsonify({"Status": "Not Successful", "Reason": "Username already exists"}), 400
    
    # Generate a random secret key for the new user
    secret_key = pyotp.random_base32()

    # Save the secret key with the user's other data
    data['SecretKey'] = secret_key  # Add secret key to the data to be saved

    # Create a TOTP object
    totp = pyotp.TOTP(secret_key)
    qr_url = totp.provisioning_uri(name=data['Username'], issuer_name='CTrack')

    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    # Save the image to a bytes buffer
    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)

    # Update the database with new data
    new_data = pd.DataFrame([data])
    database = pd.concat([database, new_data], ignore_index=True)
    database.to_csv(csv_path, index=False)

    # Return the QR code image directly
    return send_file(img_bytes, mimetype='image/png', as_attachment=False)

@app.route("/get_expenses", methods=["POST"])
def get_expenses():
    data = request.get_json()
    username = data.get('Username')

    if not username:
        return jsonify({"Status": "Not Successful", "Reason": "No username provided"})

    current_dir = os.path.dirname(__file__)
    csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))
    database = pd.read_csv(csv_path)

    # Check if the username exists in the database
    row_index = database.index[database['Username'] == username].tolist()

    if not row_index:  # Check if the list is empty
        return jsonify({"Status": "Not Successful", "Reason": "Username not found"})

    user_data = database.loc[row_index[0]]  # Assuming usernames are unique, we use the first match

    send = {}

    # Add Monthly_Income_After_Tax as a separate object
    send["Monthly_Income_After_Tax"] = user_data.get("Income", 0)

    # Add Expenses
    expenses = ["Rent", "Utilities", "Subscriptions", "Groceries", "Car Payment", "Debt", "Savings", "Custom"]
    user_expenses = {}

    for expense in expenses:
        expense_value = user_data.get(expense, 0)
        if not pd.isna(expense_value):
            user_expenses[expense] = expense_value
        else:
            user_expenses[expense] = 0  # Assign 0 or any other default value if NaN
    
    send["Expenses"] = user_expenses

    return jsonify({"Status": "Successful", "Data": send})


if __name__ == '__main__':
    app.run(debug=True, port=4444)  # Run the Flask app in debug mode