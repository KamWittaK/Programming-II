import datetime
import jwt
from flask import Flask, render_template, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

EXPECTED_USER = 'kameron'
EXPECTED_HASH = 'f8e4b9226f1b9cf140a2ca20f0922c1ae13d12ef24a0a537416adf6c8886a873'

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

    if user == EXPECTED_USER and user_hash == EXPECTED_HASH:
        token = jwt.encode({"user": user, "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=10)}, JWT_KEY)

        # Return the token in the JSON response
        return jsonify({"token": token, "message": "Authentication successful"})
    else:
        return jsonify({'message': 'Authentication failed. Invalid Username or Hash.'}), 401

@app.route("/")
def home():
    return render_template("landingpage.html")

@app.route("/token_expired")
def token_expired():
    return render_template("token_expired.html")

@app.route("/dash")
@token_required
def dash():
    return render_template("dashboard.html")

@app.route('/client/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)