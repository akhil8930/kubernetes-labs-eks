from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT'),
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )

@app.route('/cart', methods=['GET', 'POST'])
def handle_cart():
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if request.method == 'POST':
            item = request.json
            product_id = item.get('id')  # Assuming the product object has an 'id' field
            quantity = item.get('quantity', 10.99)

            if not product_id:
                return jsonify([{'error': 'Missing required product ID'}]), 400

            cur.execute('INSERT INTO cart (product_id, quantity) VALUES (%s, %s)', (product_id, quantity))
            conn.commit()
            
            cur.execute('SELECT product_id AS name, quantity AS price FROM cart')  # Adjust these fields as necessary
            items = cur.fetchall()
            return jsonify(items), 201

        elif request.method == 'GET':
            cur.execute('SELECT product_id AS name, quantity AS price FROM cart')
            items = cur.fetchall()
            return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)