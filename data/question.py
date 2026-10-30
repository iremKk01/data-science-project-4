import psycopg2

## Bu değeri localinde çalışırken kendi passwordün yap. Ama kodu pushlarken 'postgres' olarak bırak.
password = 'postgres'

def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="postgres",
        user="postgres",
        password=1234
    )

def create_view_completed_orders():
    with connect_db() as conn:
        with conn.cursor() as cur:
                        cur.execute("""
                CREATE OR REPLACE VIEW completed_orders AS
                SELECT *
                FROM orders
                WHERE status = 'completed';
            """)
    conn.commit()

def create_view_electronics_products():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE OR REPLACE VIEW electronics_products AS
                SELECT *
                FROM products
                WHERE category = 'Electronics';
            """)
        conn.commit()

def total_spending_per_customer():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""WITH customer_spending AS (
    SELECT c.customer_id, c.full_name,
           COALESCE(SUM(p.price * o.quantity), 0) AS total_spending
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    LEFT JOIN products p ON p.product_id = o.product_id
    GROUP BY c.customer_id, c.full_name
)
SELECT full_name, total_spending
FROM customer_spending
ORDER BY full_name;""")
            return cur.fetchall()

def order_details_with_total():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                WITH order_totals AS (
                    SELECT
                        o.order_id,
                        c.full_name,
                        p.product_name,
                        p.price * o.quantity AS total_price
                    FROM orders o
                    JOIN customers c ON c.customer_id = o.customer_id
                    JOIN products p ON p.product_id = o.product_id
                )
                SELECT order_id, full_name, product_name, total_price
                FROM order_totals
                ORDER BY order_id;
            """)
            return cur.fetchall()

def get_customer_who_bought_most_expensive_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.full_name
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        JOIN products p ON p.product_id = o.product_id
        WHERE p.price = (SELECT MAX(price) FROM products);
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 2. Sipariş durumlarına göre açıklama
def get_order_status_descriptions():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            order_id,
            status,
            CASE status
                WHEN 'completed' THEN 'Tamamlandı'
                WHEN 'cancelled' THEN 'İptal Edildi'
                ELSE status
            END AS status_description
        FROM orders
        ORDER BY order_id;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 3. Ortalama fiyatın üstündeki ürünler
def get_products_above_average_price():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT product_name, price
        FROM products
        WHERE price > (SELECT AVG(price) FROM products)
        ORDER BY price DESC;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 4. Müşteri kategorileri
def get_customer_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            c.full_name,
            CASE
                WHEN COUNT(o.order_id) > 5 THEN 'Sadık Müşteri'
                WHEN COUNT(o.order_id) BETWEEN 2 AND 5 THEN 'Orta Seviye'
                ELSE 'Yeni Müşteri'
            END AS customer_category
        FROM customers c
        LEFT JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.full_name
        ORDER BY c.full_name;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 5. Son 30 gün içinde sipariş veren müşteriler
def get_recent_customers():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.full_name
        FROM customers c
        JOIN orders o ON o.customer_id = c.customer_id
        GROUP BY c.customer_id, c.full_name
        HAVING MAX(o.order_date) >= CURRENT_DATE - INTERVAL '30 days'
        ORDER BY c.full_name;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 6. En çok sipariş verilen ürün
def get_most_ordered_product():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.product_name, COUNT(o.order_id) AS total_orders
        FROM products p
        JOIN orders o ON o.product_id = p.product_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_orders DESC, p.product_name
        LIMIT 1;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result

# 7. Ürün fiyatlarına göre etiketleme
def get_product_price_categories():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            product_name,
            price,
            CASE
                WHEN price > 1000 THEN 'Pahalı'
                WHEN price >= 500 THEN 'Orta'
                ELSE 'Ucuz'
            END AS price_category
        FROM products
        ORDER BY product_name;
    """)
    result = cur.fetchall()
    cur.close()
    conn.close()
    return result
