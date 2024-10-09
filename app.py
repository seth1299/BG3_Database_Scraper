from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# Function to query the database based on the selected filters
def query_database(filters):
    query = "SELECT name, enchantment, damage, damage_type, weight, price, special FROM weapons WHERE 1=1"
    params = []

    if filters.get('enchantment'):
        query += " AND enchantment = ?"
        params.append(filters['enchantment'])
    
    if filters.get('damage_type'):
        query += " AND damage_type = ?"
        params.append(filters['damage_type'])
    
    if filters.get('min_weight'):
        query += " AND weight >= ?"
        params.append(filters['min_weight'])
    
    if filters.get('max_weight'):
        query += " AND weight <= ?"
        params.append(filters['max_weight'])
    
    if filters.get('min_price'):
        query += " AND price >= ?"
        params.append(filters['min_price'])
    
    if filters.get('max_price'):
        query += " AND price <= ?"
        params.append(filters['max_price'])

    conn = sqlite3.connect('bg3_weapons.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()

    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/filter', methods=['POST'])
def filter_weapons():
    filters = {
        'enchantment': request.form.get('enchantment'),
        'damage_type': request.form.get('damage_type'),
        'min_weight': request.form.get('min_weight'),
        'max_weight': request.form.get('max_weight'),
        'min_price': request.form.get('min_price'),
        'max_price': request.form.get('max_price')
    }

    results = query_database(filters)
    
    weapons = []
    for result in results:
        weapon = {
            'name': result[0],
            'enchantment': result[1],
            'damage': result[2],
            'damage_type': result[3],
            'weight': result[4],
            'price': result[5],
            'special': result[6]
        }
        weapons.append(weapon)

    return jsonify(weapons)

if __name__ == '__main__':
    app.run(debug=True)
