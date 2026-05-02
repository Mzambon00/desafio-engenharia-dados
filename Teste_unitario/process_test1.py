# process_test1.py
import pandas as pd
import glob
import os
import re
from datetime import datetime

def normalize_currency(value):
    """Converte formato monetário para float"""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        value = value.replace('R$', '').strip()
        value = value.replace('.', '').replace(',', '.')
        try:
            return float(value)
        except:
            return None
    return None

def validate_cpf(cpf):
    """Valida e normaliza CPF"""
    cpf = str(cpf).strip()
    digits = re.sub(r'\D', '', cpf)
    
    if len(digits) == 11:
        formatted = f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
        return formatted, digits, 'CPF'
    return None, None, None

def process_date(date_str):
    """Converte data para YYYY-MM-DD"""
    try:
        date_str = str(date_str).strip()
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except:
                continue
        return None
    except:
        return None

def normalize_status(status):
    """Normaliza o status do pedido"""
    status_map = {
        'delivered': 'delivered',
        'DELIVERED': 'delivered',
        'Delivered': 'delivered',
        'canceled': 'canceled',
        'CANCELED': 'canceled',
        'in_progress': 'in_progress',
        'IN_PROGRESS': 'in_progress'
    }
    status_str = str(status).strip()
    return status_map.get(status_str, None)

# Criar diretório de saída
os.makedirs('out', exist_ok=True)

# Carregar dados dos restaurantes
print("📚 Carregando dados dos restaurantes...")
try:
    restaurants_df = pd.read_excel('data/restaurants.xlsx')
    # Converter vírgula para ponto nas colunas numéricas
    restaurants_df['commission_rate'] = restaurants_df['commission_rate'].astype(str).str.replace(',', '.').astype(float)
    restaurants_df['min_order_amount'] = restaurants_df['min_order_amount'].astype(float)
    print(restaurants_df[['restaurant_id', 'name', 'commission_rate', 'min_order_amount']])
    print()
except FileNotFoundError:
    print("❌ Arquivo data/restaurants.xlsx não encontrado!")
    print("   Execute primeiro o script generate_data_test1.py")
    exit(1)

# Listar arquivos de pedidos
order_files = glob.glob('data/orders/orders_*.csv')

if not order_files:
    print("❌ Nenhum arquivo de pedidos encontrado em data/orders/")
    print("   Execute primeiro o script generate_data_test1.py")
    exit(1)

clean_rows = []
invalid_rows = []

for file in order_files:
    print(f"🔄 Processando {file}...")
    
    # Ler CSV com diferentes separadores e encodings
    try:
        df = pd.read_csv(file, encoding='utf-8')
        print(f"  ✓ Lido com UTF-8, {len(df)} registros")
    except:
        try:
            df = pd.read_csv(file, encoding='latin1')
            print(f"  ✓ Lido com Latin1, {len(df)} registros")
        except:
            df = pd.read_csv(file, encoding='latin1', sep=';')
            print(f"  ✓ Lido com Latin1 e separador ';', {len(df)} registros")
    
    for idx, row in df.iterrows():
        invalid_reasons = []
        
        # Extrair dados originais
        original_row = row.to_dict()
        
        # 1. Validar status
        status = normalize_status(row.get('status'))
        if not status:
            invalid_reasons.append('invalid_status')
        elif status != 'delivered':
            invalid_reasons.append('not_delivered')
        
        # 2. Validar CPF
        cpf_formatted, cpf_clean, doc_type = validate_cpf(row.get('deliveryman_cpf'))
        if not cpf_formatted:
            invalid_reasons.append('invalid_document')
        
        # 3. Validar data
        order_date = process_date(row.get('order_date'))
        if not order_date:
            invalid_reasons.append('invalid_date')
        
        # 4. Validar números
        try:
            total_amount = normalize_currency(row.get('total_amount'))
            delivery_fee = normalize_currency(row.get('delivery_fee'))
            items_quantity = int(row.get('items_quantity')) if pd.notna(row.get('items_quantity')) else None
            preparation_time = int(row.get('preparation_time_min')) if pd.notna(row.get('preparation_time_min')) else None
            delivery_time = int(row.get('delivery_time_min')) if pd.notna(row.get('delivery_time_min')) else None
            
            if total_amount is None or total_amount <= 0:
                invalid_reasons.append('invalid_amount')
            if delivery_fee is None or delivery_fee < 0:
                invalid_reasons.append('invalid_fee')
            if items_quantity is None or items_quantity <= 0:
                invalid_reasons.append('invalid_quantity')
            if preparation_time is None or preparation_time <= 0:
                invalid_reasons.append('invalid_preparation_time')
            if delivery_time is None or delivery_time <= 0:
                invalid_reasons.append('invalid_delivery_time')
        except Exception as e:
            invalid_reasons.append(f'invalid_number')
        
        # Se houver qualquer invalidação, salvar em invalid_rows
        if invalid_reasons:
            original_row['invalid_reason'] = ', '.join(invalid_reasons)
            original_row['source_file'] = os.path.basename(file)
            invalid_rows.append(original_row)
            continue
        
        # 5. Buscar informações do restaurante
        restaurant_info = restaurants_df[restaurants_df['restaurant_id'] == row.get('restaurant_id')]
        if restaurant_info.empty:
            invalid_reasons.append('restaurant_not_found')
            original_row['invalid_reason'] = ', '.join(invalid_reasons)
            original_row['source_file'] = os.path.basename(file)
            invalid_rows.append(original_row)
            continue
        
        commission_rate = restaurant_info['commission_rate'].values[0]
        min_order_amount = restaurant_info['min_order_amount'].values[0]
        
        # 6. Calcular comissão (só para delivered e se atingir valor mínimo)
        if status == 'delivered' and total_amount >= min_order_amount:
            commission = total_amount * commission_rate
        else:
            commission = 0
        
        # 7. Calcular tempo total de entrega
        total_delivery_time = preparation_time + delivery_time
        
        # 8. Salvar registro limpo
        clean_rows.append({
            'order_id': row.get('order_id'),
            'restaurant_id': row.get('restaurant_id'),
            'restaurant_name': restaurant_info['name'].values[0],
            'deliveryman_cpf': cpf_formatted,
            'document_clean': cpf_clean,
            'document_type': doc_type,
            'order_date': order_date,
            'status': status,
            'items_quantity': items_quantity,
            'total_amount': total_amount,
            'delivery_fee': delivery_fee,
            'preparation_time_min': preparation_time,
            'delivery_time_min': delivery_time,
            'commission_rate': commission_rate,
            'min_order_amount': min_order_amount,
            'commission': commission,
            'total_delivery_time': total_delivery_time,
            'is_valid_order': (status == 'delivered'),
            'source_file': os.path.basename(file)
        })

print(f"\n📊 Resumo:")
print(f"  ✅ Pedidos válidos (delivered): {len([c for c in clean_rows if c['is_valid_order']])}")
print(f"  ⚠️  Pedidos inválidos: {len(invalid_rows)}")

# Salvar resultados
if clean_rows:
    clean_df = pd.DataFrame(clean_rows)
    clean_df.to_csv('out/clean_orders.csv', index=False)
    print(f"\n💾 clean_orders.csv salvo com {len(clean_rows)} registros")

if invalid_rows:
    invalid_df = pd.DataFrame(invalid_rows)
    invalid_df.to_csv('out/invalid_rows.csv', index=False)
    print(f"💾 invalid_rows.csv salvo com {len(invalid_rows)} registros")

print("\n✅ Processamento do Teste 1 concluído!")