import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="postgres",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

# Önceki çalıştırmalardan / diğer projelerden kalan tabloları temizle
cur.execute("DROP TABLE IF EXISTS customers, products, orders CASCADE;")

cur.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    signup_date DATE
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    price NUMERIC(10,2),
    category VARCHAR(50)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(customer_id),
    product_id INT REFERENCES products(product_id),
    order_date DATE,
    quantity INT,
    status VARCHAR(20)
);
""")

cur.execute("""
INSERT INTO customers (full_name, email, signup_date) VALUES
('Ahmet Yılmaz', 'ahmet@example.com', '2022-01-15'),
('Ayşe Demir', 'ayse@example.com', '2022-05-22'),
('Mehmet Kaya', 'mehmet@example.com', '2022-07-30'),
('Fatma Şahin', 'fatma@example.com', '2022-09-18');
""")

cur.execute("""
INSERT INTO products (product_name, price, category) VALUES
('Laptop', 15000.00, 'Electronics'),
('Smartphone', 8000.00, 'Electronics'),
('Coffee Machine', 1200.00, 'Home Appliances'),
('Book - SQL Basics', 150.00, 'Books');
""")

cur.execute("""
INSERT INTO orders (customer_id, product_id, order_date, quantity, status) VALUES
(1, 1, '2023-02-10', 1, 'completed'),
(2, 2, '2023-03-12', 2, 'completed'),
(3, 4, '2023-04-05', 1, 'cancelled'),
(4, 3, '2023-05-20', 1, 'completed');
""")

conn.commit()
cur.close()
conn.close()
