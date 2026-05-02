# generate_test2_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Criar diretórios
os.makedirs('data/leads', exist_ok=True)

# Gerar dados de campanhas
campaigns_data = {
    'campaign_code': ['CAMP001', 'CAMP002', 'CAMP003', 'CAMP004', 'CAMP005'],
    'campaign_name': ['Black Friday', 'Dia dos Namorados', 'Summer Sale', 'Winter Collection', 'Back to School'],
    'target_audience': ['Todos', 'Casais', 'Jovens', 'Adultos', 'Estudantes'],
    'expected_conversion_rate': [0.15, 0.12, 0.18, 0.10, 0.20]
}
campaigns_df = pd.DataFrame(campaigns_data)
campaigns_df.to_excel('data/campaigns.xlsx', index=False)

# Gerar leads
channels = ['instagram', 'facebook', 'google_ads', 'email', 'linkedin']
campaigns = ['CAMP001', 'CAMP002', 'CAMP003', 'CAMP004', 'CAMP005']

leads_data = []
emails = [
    'joao@email.com', 'maria@teste', 'invalid-email', 'pedro@gmail.com', 
    'ana@empresa.com.br', 'carlos@', '@dominio.com', 'lucia@provedor.com'
]

for i in range(1, 101):  # 100 leads
    # Criar alguns dados inválidos propositalmente
    if i % 7 == 0:
        conversion_date = '2023-13-01'  # Data inválida
    elif i % 9 == 0:
        conversion_date = '31/02/2023'  # Data inválida
    else:
        conversion_date = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime('%Y-%m-%d')
    
    # Gerar custo por clique em formatos variados
    if i % 5 == 0:
        cost_per_click = f"R$ {random.uniform(0.5, 5):.2f}".replace('.', ',')
    else:
        cost_per_click = round(random.uniform(0.5, 5), 2)
    
    leads_data.append({
        'lead_id': i,
        'campaign_code': random.choice(campaigns),
        'client_email': random.choice(emails),
        'conversion_date': conversion_date,
        'channel': random.choice(channels),
        'clicks': random.randint(0, 1000),
        'cost_per_click': cost_per_click,
        'conversion_value': round(random.uniform(50, 5000), 2),
        'days_to_close': random.randint(1, 30)
    })

# Salvar em lotes
df_leads = pd.DataFrame(leads_data)
df_leads[:50].to_csv('data/leads/leads_0001.csv', index=False)
df_leads[50:].to_csv('data/leads/leads_0002.csv', index=False, sep=';')  # Separador diferente

print("✅ Dados do Teste 2 gerados!")