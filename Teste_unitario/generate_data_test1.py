# generate_data_test1.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Criar diretórios
os.makedirs('data/orders', exist_ok=True)
os.makedirs('data', exist_ok=True)

print("📊 Gerando dados do Teste 1 - Restaurante...")

# Gerar dados de restaurantes
restaurants_data = {
    'restaurant_id': [1, 2, 3, 4, 5],
    'name': ['Pizzaria Napoli', 'Sushi House', 'Burger King', 'Massa Fina', 'Veggie Delight'],
    'commission_rate': [0.15, 0.20, 0.12, 0.18, 0.10],
    'min_order_amount': [30.00, 50.00, 20.00, 40.00, 25.00]
}
restaurants_df = pd.DataFrame(restaurants_data)
restaurants_df.to_excel('data/restaurants.xlsx', index=False)
print(f"  ✓ restaurants.xlsx criado com {len(restaurants_df)} restaurantes")

# Gerar pedidos
status_options = ['delivered', 'canceled', 'in_progress']
cpfs = ['12345678901', '98765432100', '11122233344', '55566677788', '99988877766']
restaurant_ids = [1, 2, 3, 4, 5]

orders_data = []
for i in range(1, 51):  # 50 pedidos
    # Alternar entre formatos diferentes
    if i % 3 == 0:
        total_amount = f"R$ {random.uniform(15, 200):.2f}".replace('.', ',')
    else:
        total_amount = round(random.uniform(15, 200), 2)
    
    if i % 4 == 0:
        delivery_fee = f"{random.uniform(5, 15):.2f}"
    else:
        delivery_fee = round(random.uniform(5, 15), 2)
    
    orders_data.append({
        'order_id': i,
        'restaurant_id': random.choice(restaurant_ids),
        'deliveryman_cpf': random.choice(cpfs),
        'order_date': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%d/%m/%Y'),
        'status': random.choice(status_options),
        'items_quantity': random.randint(1, 10),
        'total_amount': total_amount,
        'delivery_fee': delivery_fee,
        'preparation_time_min': random.randint(5, 45),
        'delivery_time_min': random.randint(10, 60)
    })

# Salvar em lotes
df_orders = pd.DataFrame(orders_data)
df_orders[:25].to_csv('data/orders/orders_0001.csv', index=False)
df_orders[25:].to_csv('data/orders/orders_0002.csv', index=False)
print(f"  ✓ orders_0001.csv criado (25 pedidos)")
print(f"  ✓ orders_0002.csv criado (25 pedidos)")

print("✅ Dados do Teste 1 gerados com sucesso!\n")