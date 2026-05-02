# generate_test3_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os
import re

# Criar diretórios
os.makedirs('data/sales', exist_ok=True)

print("📊 Gerando dados do Teste 3 - Estoque...")

# Gerar dados de produtos
products_data = {
    'product_sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005', 'SKU006', 'SKU007', 'SKU008'],
    'product_name': [
        'Notebook Gamer', 'Mouse Wireless', 'Teclado Mecânico', 'Monitor 24"', 
        'Headset RGB', 'SSD 1TB', 'Webcam HD', 'Cadeira Gamer'
    ],
    'category': ['Eletrônicos', 'Periféricos', 'Periféricos', 'Monitores', 'Áudio', 'Armazenamento', 'Periféricos', 'Móveis'],
    'stock_initial': [50, 200, 150, 75, 100, 300, 80, 45],
    'min_stock_level': [10, 50, 30, 15, 20, 100, 20, 10],
    'reorder_point': [20, 80, 50, 25, 35, 150, 35, 18]
}
products_df = pd.DataFrame(products_data)
products_df.to_excel('data/products.xlsx', index=False)
print("  ✓ products.xlsx criado")

# Função para converter string de preço para número
def parse_price(price_str):
    if isinstance(price_str, (int, float)):
        return float(price_str)
    # Remove "R$" e espaços
    price_str = str(price_str).replace('R$', '').strip()
    # Troca vírgula por ponto
    price_str = price_str.replace('.', '').replace(',', '.')
    try:
        return float(price_str)
    except:
        return 100.00  # valor padrão se falhar

# Gerar vendas
skus = ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005', 'SKU006', 'SKU007', 'SKU008']
cnpjs = ['12345678000199', '98765432000188', 'invalid', '11122233000177', '55566677000144']
zipcodes = ['12345678', '87654321', 'invalid', '11111111', '22222222']

sales_data = []
for i in range(1, 151):  # 150 vendas
    # Gerar preço base (numérico)
    base_price = round(random.uniform(50, 3000), 2)
    
    # Preço unitário em diferentes formatos
    if i % 6 == 0:
        unit_price = f"R$ {base_price:.2f}".replace('.', ',')
    else:
        unit_price = base_price
    
    # Desconto variado - USANDO O base_price para calcular
    if i % 8 == 0:
        discount_percent = random.uniform(0, 30)  # até 30% de desconto
        discount_value = (base_price * discount_percent) / 100
        discount = f"{discount_percent:.2f}%"
    else:
        discount_value = random.uniform(0, base_price - 10) if base_price > 10 else 0
        discount = discount_value
    
    sales_data.append({
        'sale_id': i,
        'product_sku': random.choice(skus),
        'store_cnpj': random.choice(cnpjs),
        'sale_date': (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%d/%m/%Y'),
        'quantity_sold': random.randint(-5, 20),  # Pode gerar quantidade negativa
        'unit_price': unit_price,
        'discount': discount,
        'customer_zipcode': random.choice(zipcodes)
    })

# Salvar em lotes com encodings diferentes
df_sales = pd.DataFrame(sales_data)
df_sales[:75].to_csv('data/sales/sales_0001.csv', index=False, encoding='utf-8')
df_sales[75:].to_csv('data/sales/sales_0002.csv', index=False, encoding='latin1', sep='|')  # Separador pipe
print(f"  ✓ sales_0001.csv criado (75 vendas, UTF-8)")
print(f"  ✓ sales_0002.csv criado (75 vendas, Latin1, separador '|')")

print("✅ Dados do Teste 3 gerados com sucesso!\n")