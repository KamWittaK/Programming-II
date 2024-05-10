import datetime
import jwt, os, pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(__file__)
csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))
database_df = pd.read_csv(csv_path)

JWT_KEY = "ec599d45e025437d8206209e3b2e536d"
JWT_ALGO = "HS256"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")
        print(token)

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGO])
        except jwt.ExpiredSignatureError:
            return render_template("token_expired.html"), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route("/auth", methods=['POST'])
def login():
    data = request.get_json()
    user = data.get('username', '').lower()
    user_hash = data.get('hash')

    # Get usernames and passwords from the DataFrame
    usernames = database_df["Username"].str.lower()
    passwords = database_df["Password"]

    for username, password in zip(usernames, passwords):
        if user == username and user_hash == password:
            token = jwt.encode({"user": user, "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=10)}, JWT_KEY)

            # Return the token in the JSON response
            return jsonify({"token": token, "message": "Authentication successful"})

    # If no match is found
    return jsonify({'message': 'Authentication failed. Invalid Username or Hash.'}), 401

@app.route("/")
def home():
    return render_template("landingpage.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/token_expired")
def token_expired():
    return render_template("landingpage.html")

@app.route("/dash")
@token_required
def dash():
    return render_template("dashboard.html")

@app.route('/client/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)