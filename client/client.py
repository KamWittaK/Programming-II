import datetime, pyotp, qrcode
import jwt, os, pandas as pd
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

current_dir = os.path.dirname(__file__)
csv_path = os.path.abspath(os.path.join(current_dir, "../server/data/database.csv"))

JWT_KEY = "ec599d45e025437d8206209e3b2e536d"
JWT_ALGO = "HS256"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")

        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, JWT_KEY, algorithms=[JWT_ALGO])
        except jwt.ExpiredSignatureError:
            return render_template("login.html"), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401

        return f(*args, **kwargs)

    return decorated

@app.route("/auth", methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').lower()
    password_hash = data.get('hash')
    user_otp = data.get('twofa')  # This is the 2FA code the user submits

    print(f"Username: {username}")
    database_df = pd.read_csv(csv_path)

    # Get user data from the DataFrame or your database system
    user_data = database_df.loc[database_df["Username"].str.lower() == username]

    if user_data.empty:
        print("empty")

    if not user_data.empty:
        user_secret_key = user_data.iloc[0]['SecretKey']  # Assume the secret key is stored in the database
        user_password = user_data.iloc[0]['Password']
        print(f"Expected Hash: {password_hash}")
        print(f"Given Hash: {user_password}")
        print(f"Given: 2FA {user_otp}")

        if password_hash == user_password:
            print("Step 1")
            # Verify TOTP
            totp = pyotp.TOTP(user_secret_key)
            print(user_secret_key)
            print(totp.verify(user_otp))
            if totp.verify(user_otp):
                # Generate JWT token
                token = jwt.encode({"user": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, JWT_KEY, algorithm="HS256")
                return jsonify({"token": token, "message": "Authentication successful"})
            else:
                return jsonify({"message": "Invalid 2FA code."}), 403
        else:
            return jsonify({"message": "Invalid username or password."}), 401
    else:
        return jsonify({"message": "User not found."}), 404
    
@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/token_expired")
def token_expired():
    return render_template("login.html")

@app.route("/STrack")
@token_required
def STrack():
    return render_template("STrack.html")

@app.route("/CTrack")
@token_required
def Ctrack():
    return render_template("CTrack.html")

@app.route("/CTrack_Portfolio")
@token_required
def CTrack_Portfolio():
    return render_template("CTrack_Portfolio.html")

@app.route('/client/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)