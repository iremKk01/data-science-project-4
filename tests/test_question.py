import datetime
from decimal import Decimal
import sys
import os
import requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from data.question import (
    create_view_completed_orders,
    create_view_electronics_products,
    total_spending_per_customer,
    order_details_with_total,
    get_customer_who_bought_most_expensive_product,
    get_order_status_descriptions,
    get_products_above_average_price,
    get_customer_categories,
    get_recent_customers,
    get_most_ordered_product,
    get_product_price_categories,
)


# ─────────────────────────────────────────────
# Kaizu ID'n — Profile → Settings → User ID
# Skorunun Kaizu'ya gitmesi için 0 yerine kendi ID'ni yaz.
# ─────────────────────────────────────────────
USER_ID = 0  # ← BURAYI DEĞİŞTİR


def run_common_test(expected_data, tested_func):
    result = tested_func()
    assert result == expected_data


# Q1: VIEW completed_orders
def test_create_view_completed_orders():
    result = create_view_completed_orders()
    assert result is None


# Q2: VIEW electronics_products
def test_create_view_electronics_products():
    result = create_view_electronics_products()
    assert result is None


# Q3: Her müşterinin toplam harcaması (full_name, total_spending)
def test_total_spending_per_customer():
    result = total_spending_per_customer()
    assert isinstance(result, list)
    assert len(result) == 4
    # Sıralama belirtilmemiş, set olarak kontrol
    spending = {r[0]: r[1] for r in result}
    assert spending['Ahmet Yılmaz'] == Decimal('15000.00')
    assert spending['Ayşe Demir'] == Decimal('16000.00')
    assert spending['Mehmet Kaya'] == Decimal('150.00')
    assert spending['Fatma Şahin'] == Decimal('1200.00')


# Q4: Sipariş detayları (order_id, full_name, product_name, total_price)
def test_order_details_with_total():
    result = order_details_with_total()
    assert isinstance(result, list)
    assert len(result) == 4
    totals = {r[0]: r[3] for r in result}
    assert totals[1] == Decimal('15000.00')
    assert totals[2] == Decimal('16000.00')
    assert totals[3] == Decimal('150.00')
    assert totals[4] == Decimal('1200.00')


# Q5: En pahalı ürünü alan kişi (Laptop → Ahmet Yılmaz)
def test_get_customer_who_bought_most_expensive_product():
    expected = [('Ahmet Yılmaz',)]
    run_common_test(expected, get_customer_who_bought_most_expensive_product)


# Q6: Status Türkçe açıklama (order_id, status, status_description)
def test_get_order_status_descriptions():
    expected = [
        (1, 'completed', 'Tamamlandı'),
        (2, 'completed', 'Tamamlandı'),
        (3, 'cancelled', 'İptal Edildi'),
        (4, 'completed', 'Tamamlandı'),
    ]
    run_common_test(expected, get_order_status_descriptions)


# Q7: Ortalama fiyatın (6087.50) üzerindeki ürünler (product_name, price)
def test_get_products_above_average_price():
    expected = [
        ('Laptop', Decimal('15000.00')),
        ('Smartphone', Decimal('8000.00')),
    ]
    run_common_test(expected, get_products_above_average_price)


# Q8: Müşteri kategorileri (her müşterinin 1 siparişi var → hepsi Yeni Müşteri)
def test_get_customer_categories():
    result = get_customer_categories()
    assert isinstance(result, list)
    assert len(result) == 4
    categories = {r[0]: r[1] for r in result}
    assert all(v == 'Yeni Müşteri' for v in categories.values())


# Q9: Son 30 gün içinde sipariş veren müşteriler
def test_get_recent_customers():
    result = get_recent_customers()
    assert isinstance(result, list)
    # Seed data 2023'ten, güncel tarih çok ileride → boş dönmeli
    # Ama öğrenci doğru sorguyu yazarsa boş döner


# Q10: En çok sipariş verilen ürün
def test_get_most_ordered_product():
    result = get_most_ordered_product()
    assert isinstance(result, list)
    assert len(result) >= 1
    assert isinstance(result[0][0], str)


# Q11: Fiyat etiketleme (product_name, price, price_category)
def test_get_product_price_categories():
    result = get_product_price_categories()
    cats = {r[0]: r[2] for r in result}
    assert cats['Laptop'] == 'Pahalı'
    assert cats['Smartphone'] == 'Pahalı'
    assert cats['Coffee Machine'] == 'Pahalı'
    assert cats['Book - SQL Basics'] == 'Ucuz'


def send_post_request(url: str, data: dict, headers: dict = None):
    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err} - Status Code: {response.status_code}")
    except Exception as err:
        print(f"Other error occurred: {err}")


class ResultCollector:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            if report.passed:
                self.passed += 1
            elif report.failed:
                self.failed += 1


def run_tests():
    collector = ResultCollector()
    pytest.main(["tests"], plugins=[collector])
    total = collector.passed + collector.failed
    print(f"\nToplam Başarılı: {collector.passed}")
    print(f"Toplam Başarısız: {collector.failed}")

    if total == 0:
        print("Hiç test çalıştırılmadı.")
        return

    user_score = round((collector.passed / total) * 100, 2)
    print(f"Skor: {user_score}")

    if USER_ID == 0:
        print("\n⚠️  USER_ID=0 — tests/test_question.py dosyasının başına kendi Kaizu ID'ni yazmadın, skor gönderilmeyecek.")
        return

    url = "https://kaizu-api-8cd10af40cb3.herokuapp.com/projectLog"
    payload = {
        "user_id": 751,
        "project_id": 4,
        "user_score": user_score,
        "is_auto": False
    }
    headers = {"Content-Type": "application/json"}
    send_post_request(url, payload, headers)


if __name__ == "__main__":
    run_tests()
