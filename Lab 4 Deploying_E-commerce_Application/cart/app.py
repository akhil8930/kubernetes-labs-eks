from flask import Flask, jsonify, request
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS on the app

cart = []

@app.route('/cart', methods=['GET', 'POST'])
def handle_cart():
    if request.method == 'POST':
        cart.append(request.json)
    return jsonify(cart)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)