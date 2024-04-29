from flask import Flask, render_template, request, jsonify, url_for, redirect
import sqlite3
import urllib.parse
import json

app = Flask(__name__)

conn = sqlite3.connect('slqlite3.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS items
             (id INTEGER PRIMARY KEY, name TEXT, price FLOAT)''')
c.execute('''CREATE TABLE IF NOT EXISTS orders
             (id INTEGER PRIMARY KEY, whole_order TEXT, total FLOAT)''')


def parse_order(query):
    try:
        decoded_query = urllib.parse.unquote(query)
        order = json.loads(decoded_query)
        return order
    except Exception as e:
        print(f"Error parsing order: {e}")
        return {}


def generate_statistics():
    c.execute("SELECT * FROM orders")
    orders = c.fetchall()

    total_orders = len(orders)
    total_items_sold = 0
    total_amount_made = 0
    item_counts = {}

    # Loop through each order
    for order in orders:
        # Convert the string representation of whole_order to a dictionary
        whole_order = eval(order[1])

        # Loop through each item in the order
        for item in whole_order.values():
            total_items_sold += item['quantity']
            item_name = item['item_name']
            # Increment the count for this item
            item_counts[item_name] = item_counts.get(
                item_name, 0) + item['quantity']

        total_amount_made += order[2]

    print(total_amount_made)

    return {
        'total_orders': total_orders,
        'total_items_sold': total_items_sold,
        'total_amount_made': total_amount_made,
        'item_counts': item_counts
    }


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        c.execute("INSERT INTO items (name, price) VALUES (?, ?)", (name, price))
        conn.commit()
        return "Item added successfully!"
    return render_template('add.html')


@app.route('/', methods=['GET', 'POST'])
def make_order():
    if request.method == 'POST':
        # Handle order submission
        order = {}  # Initialize order dictionary
        for key, value in request.form.items():
            if key.startswith('item'):
                item_id = key[4:]  # Extract item ID from the key
                # Corresponding quantity key
                quantity_key = f'quantity{item_id}'
                # Get quantity or default to 0
                quantity = int(request.form.get(quantity_key, 0))
                order[item_id] = {'quantity': quantity, 'item_name': value}

        total_price = float(request.form.get(
            'totalPrice', 0))  # Extract total price

        # Process the order (e.g., save to database)
        # Example:
        for item_id, item_data in order.items():
            item_name = item_data['item_name']
            quantity = item_data['quantity']
            # Process each item in the order (e.g., save to database)

        # Optionally, you can send a response back to the client
        return redirect(url_for('order_confirmation', total_price=total_price, **order))
    c.execute("SELECT * FROM items")
    items = c.fetchall()
    return render_template('make_order.html', items=items)


@app.route('/order_confirmation', methods=['GET', 'POST'])
def order_confirmation():
    total_price = request.args.get('total_price')
    orders = {}

    # Iterate through the request arguments to extract order information
    for key, value in request.args.items():
        if key.isdigit():
            order_info = eval(value)
            quantity = order_info['quantity']
            item_name = order_info['item_name']
            orders[int(key)] = {'quantity': quantity, 'item_name': item_name}
    print(orders)

    if request.method == 'POST':
        whole_order = json.dumps(orders)
        choice = request.form['choice']
        if choice == 'option1':
            print(whole_order)
            c.execute("INSERT INTO orders (whole_order, total) VALUES (?, ?)",
                      (whole_order, total_price))
            conn.commit()
            return redirect('/')
        elif choice == 'option2':
            return redirect('/')

    return render_template('order_confirmation.html', total_price=total_price, orders=orders)


@app.route('/stats')
def statistics():
    stats = generate_statistics()
    return jsonify(stats)
    return render_template('statistics.html')


if __name__ == '__main__':
    app.run(debug=True)
