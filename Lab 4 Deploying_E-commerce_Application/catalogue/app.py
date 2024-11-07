from flask import Flask, jsonify
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS on the app

@app.route('/products')
def products():
    return jsonify([
        {'id': 1, 'name': 'Product 1', 'price': 10.99},
        {'id': 2, 'name': 'Product 2', 'price': 12.99}
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)