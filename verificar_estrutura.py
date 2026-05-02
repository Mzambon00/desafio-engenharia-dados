# teste1_processamento.py
import pandas as pd
import glob
import os
import re
from datetime import datetime

def normalizar_cpf(cpf):
    """
    Normaliza CPF: remove caracteres especiais e valida
    Retorna: (cpf_formatado, cpf_limpo, tipo)
    """
    if pd.isna(cpf) or cpf == '':
        return None, None, None
    
    cpf_str = str(cpf).strip()
    
    # Remove tudo que não for número
    cpf_limpo = re.sub(r'\D', '', cpf_str)
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) == 11:
        # Formata CPF: 123.456.789-00
        cpf_formatado = f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf_formatado, cpf_limpo, 'CPF'
    else:
        return None, None, None

def normalizar_status(status):
    """
    Normaliza o status do pedido
    Retorna: status normalizado ou None se inválido
    """
    if pd.isna(status):
        return None
    
    status_str = str(status).strip().lower()
    
    # Mapeamento de status
    if status_str in ['delivered', 'entregue', 'concluído', 'concluido']:
        return 'delivered'
    elif status_str in ['canceled', 'cancelado', 'cancelada']:
        return 'canceled'
    elif status_str in ['in_progress', 'em_andamento', 'em andamento', 'preparando']:
        return 'in_progress'
    else:
        return None

def normalizar_data(data_str):
    """
    Converte data para formato YYYY-MM-DD
    """
    if pd.isna(data_str):
        return None
    
    data_str = str(data_str).strip()
    
    # Tentativas de formatos de data
    formatos = [
        '%Y-%m-%d',      # 2024-01-15
        '%d/%m/%Y',      # 15/01/2024
        '%d-%m-%Y',      # 15-01-2024
        '%d.%m.%Y',      # 15.01.2024
        '%Y%m%d'         # 20240115
    ]
    
    for formato in formatos:
        try:
            data = datetime.strptime(data_str, formato)
            return data.strftime('%Y-%m-%d')
        except:
            continue
    
    return None

def normalizar_moeda(valor):
    """
    Converte formato monetário brasileiro para float
    Exemplos: 
    - "R$ 1.234,56" -> 1234.56
    - "1.234,56" -> 1234.56
    - "1234.56" -> 1234.56
    - "R$ 1,234.56" -> 1234.56 (formato americano)
    """
    if pd.isna(valor):
        return None
    
    valor_str = str(valor).strip()
    
    # Remove R$, espaços e outros caracteres
    valor_str = valor_str.replace('R$', '').replace('$', '').replace(' ', '')
    
    # Detecta formato brasileiro (ponto como separador de milhar, vírgula decimal)
    if ',' in valor_str and '.' in valor_str:
        # Caso: 1.234,56 (brasileiro)
        if valor_str.rfind(',') > valor_str.rfind('.'):
            valor_str = valor_str.replace('.', '').replace(',', '.')
    elif ',' in valor_str and '.' not in valor_str:
        # Caso: 1234,56 (brasileiro)
        valor_str = valor_str.replace(',', '.')
    
    try:
        return float(valor_str)
    except:
        return None

def normalizar_numero(valor):
    """
    Converte string para número inteiro
    """
    if pd.isna(valor):
        return None
    
    try:
        return int(float(str(valor).strip()))
    except:
        return None

def processar_teste1():
    """
    Função principal de processamento do Teste 1
    """
    print("="*60)
    print("TESTE 1: Processamento de Pedidos de Restaurante")
    print("="*60)
    
    # Criar diretório de saída
    os.makedirs('out', exist_ok=True)
    
    # Passo 1: Carregar dados dos restaurantes
    print("\n📚 Passo 1: Carregando dados dos restaurantes...")
    try:
        restaurants_df = pd.read_excel('data/restaurants.xlsx')
        # Garantir que as colunas numéricas estão corretas
        restaurants_df['commission_rate'] = restaurants_df['commission_rate'].astype(str).str.replace(',', '.').astype(float)
        restaurants_df['min_order_amount'] = restaurants_df['min_order_amount'].astype(float)
        print(f"   ✓ Carregados {len(restaurants_df)} restaurantes")
        print(restaurants_df[['restaurant_id', 'name', 'commission_rate', 'min_order_amount']].to_string(index=False))
    except FileNotFoundError:
        print("   ❌ Arquivo 'data/restaurants.xlsx' não encontrado!")
        print("   Execute o script de geração de dados primeiro.")
        return
    except Exception as e:
        print(f"   ❌ Erro ao carregar restaurantes: {e}")
        return
    
    # Passo 2: Listar arquivos de pedidos
    print("\n📁 Passo 2: Procurando arquivos de pedidos...")
    order_files = glob.glob('data/orders/orders_*.csv')
    
    if not order_files:
        print("   ❌ Nenhum arquivo de pedido encontrado em 'data/orders/'")
        return
    
    print(f"   ✓ Encontrados {len(order_files)} arquivo(s)")
    
    # Estruturas para armazenar resultados
    registros_validos = []
    registros_invalidos = []
    
    # Passo 3: Processar cada arquivo
    for arquivo in order_files:
        print(f"\n🔄 Processando: {os.path.basename(arquivo)}")
        
        # Tentar ler com diferentes codificações e separadores
        df = None
        tentativas = [
            (pd.read_csv, {'encoding': 'utf-8', 'sep': ','}),
            (pd.read_csv, {'encoding': 'latin1', 'sep': ','}),
            (pd.read_csv, {'encoding': 'utf-8', 'sep': ';'}),
            (pd.read_csv, {'encoding': 'latin1', 'sep': ';'}),
        ]
        
        for leitor, kwargs in tentativas:
            try:
                df = leitor(arquivo, **kwargs)
                print(f"   ✓ Lido com {kwargs.get('encoding')}, separador '{kwargs.get('sep')}'")
                break
            except:
                continue
        
        if df is None:
            print(f"   ❌ Não foi possível ler o arquivo {arquivo}")
            continue
        
        print(f"   ✓ Total de registros: {len(df)}")
        
        # Processar cada linha
        for idx, row in df.iterrows():
            razoes_invalidacao = []
            
            # Criar cópia dos dados originais
            dados_originais = row.to_dict()
            
            # 1. Validar e normalizar CPF (coluna C=deliveryman_cpf)
            try:
                # Tentar diferentes nomes de coluna
                cpf_valor = None
                for col in ['deliveryman_cpf', 'cpf', 'deliveryman_cpf']:
                    if col in row:
                        cpf_valor = row[col]
                        break
                
                if cpf_valor is None:
                    razoes_invalidacao.append('coluna_cpf_nao_encontrada')
                else:
                    cpf_formatado, cpf_limpo, tipo_doc = normalizar_cpf(cpf_valor)
                    if not cpf_formatado:
                        razoes_invalidacao.append('cpf_invalido')
            except Exception as e:
                razoes_invalidacao.append(f'erro_cpf: {str(e)}')
            
            # 2. Validar status (coluna E)
            try:
                status_valor = None
                for col in ['status', 'order_status']:
                    if col in row:
                        status_valor = row[col]
                        break
                
                if status_valor is None:
                    razoes_invalidacao.append('coluna_status_nao_encontrada')
                else:
                    status = normalizar_status(status_valor)
                    if not status:
                        razoes_invalidacao.append('status_invalido')
            except Exception as e:
                razoes_invalidacao.append(f'erro_status: {str(e)}')
            
            # 3. Validar data do pedido
            try:
                data_valor = None
                for col in ['order_date', 'date', 'data_pedido']:
                    if col in row:
                        data_valor = row[col]
                        break
                
                if data_valor is None:
                    razoes_invalidacao.append('coluna_data_nao_encontrada')
                else:
                    data_normalizada = normalizar_data(data_valor)
                    if not data_normalizada:
                        razoes_invalidacao.append('data_invalida')
            except Exception as e:
                razoes_invalidacao.append(f'erro_data: {str(e)}')
            
            # 4. Validar números e valores monetários
            try:
                # Total amount (valor monetário)
                total_amount = None
                for col in ['total_amount', 'total', 'valor_total']:
                    if col in row:
                        total_amount = normalizar_moeda(row[col])
                        break
                
                if total_amount is None:
                    razoes_invalidacao.append('total_amount_invalido')
                elif total_amount <= 0:
                    razoes_invalidacao.append('total_amount_negativo')
                
                # Delivery fee (taxa de entrega)
                delivery_fee = None
                for col in ['delivery_fee', 'taxa_entrega', 'frete']:
                    if col in row:
                        delivery_fee = normalizar_moeda(row[col])
                        break
                
                if delivery_fee is None:
                    delivery_fee = 0  # Se não tiver, assume 0
                elif delivery_fee < 0:
                    razoes_invalidacao.append('delivery_fee_negativo')
                
                # Quantidade de itens
                items_quantity = None
                for col in ['items_quantity', 'quantity', 'qtd_itens']:
                    if col in row:
                        items_quantity = normalizar_numero(row[col])
                        break
                
                if items_quantity is None:
                    razoes_invalidacao.append('items_quantity_invalido')
                elif items_quantity <= 0:
                    razoes_invalidacao.append('items_quantity_negativo')
                
                # Tempo de preparo
                preparation_time = None
                for col in ['preparation_time_min', 'prep_time', 'tempo_preparo']:
                    if col in row:
                        preparation_time = normalizar_numero(row[col])
                        break
                
                if preparation_time is None:
                    razoes_invalidacao.append('preparation_time_invalido')
                elif preparation_time <= 0:
                    razoes_invalidacao.append('preparation_time_negativo')
                
                # Tempo de entrega
                delivery_time = None
                for col in ['delivery_time_min', 'delivery_time', 'tempo_entrega']:
                    if col in row:
                        delivery_time = normalizar_numero(row[col])
                        break
                
                if delivery_time is None:
                    razoes_invalidacao.append('delivery_time_invalido')
                elif delivery_time <= 0:
                    razoes_invalidacao.append('delivery_time_negativo')
                
                # ID do restaurante
                restaurant_id = None
                for col in ['restaurant_id', 'id_restaurante']:
                    if col in row:
                        restaurant_id = normalizar_numero(row[col])
                        break
                
                if restaurant_id is None:
                    razoes_invalidacao.append('restaurant_id_invalido')
                    
            except Exception as e:
                razoes_invalidacao.append(f'erro_numeros: {str(e)}')
            
            # Se houver qualquer invalidação, salvar como inválido
            if razoes_invalidacao:
                dados_originais['invalid_reason'] = '; '.join(razoes_invalidacao)
                dados_originais['source_file'] = os.path.basename(arquivo)
                registros_invalidos.append(dados_originais)
                continue
            
            # 5. Buscar informações do restaurante
            restaurante = restaurants_df[restaurants_df['restaurant_id'] == restaurant_id]
            if restaurante.empty:
                dados_originais['invalid_reason'] = 'restaurant_not_found'
                dados_originais['source_file'] = os.path.basename(arquivo)
                registros_invalidos.append(dados_originais)
                continue
            
            # 6. Calcular comissão (apenas se delivered e valor mínimo)
            commission_rate = restaurante['commission_rate'].values[0]
            min_order_amount = restaurante['min_order_amount'].values[0]
            
            if status == 'delivered' and total_amount >= min_order_amount:
                commission = total_amount * commission_rate
            else:
                commission = 0
            
            # 7. Calcular tempo total
            total_delivery_time = preparation_time + delivery_time
            
            # 8. Salvar registro válido
            registros_validos.append({
                'order_id': row.get('order_id', idx),
                'restaurant_id': restaurant_id,
                'restaurant_name': restaurante['name'].values[0],
                'deliveryman_cpf': cpf_formatado,
                'document_clean': cpf_limpo,
                'document_type': tipo_doc,
                'order_date': data_normalizada,
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
                'source_file': os.path.basename(arquivo)
            })
    
    # Passo 4: Salvar resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS")
    print("="*60)
    
    # Salvar registros válidos
    if registros_validos:
        df_validos = pd.DataFrame(registros_validos)
        df_validos.to_csv('out/clean_orders.csv', index=False)
        print(f"✅ clean_orders.csv: {len(registros_validos)} registros válidos")
        
        # Estatísticas
        entregues = len([r for r in registros_validos if r['status'] == 'delivered'])
        print(f"   - Pedidos entregues: {entregues}")
        print(f"   - Pedidos cancelados/andamento: {len(registros_validos) - entregues}")
        
        # Total de comissões
        total_comissao = sum([r['commission'] for r in registros_validos if r['status'] == 'delivered'])
        print(f"   - Total de comissões: R$ {total_comissao:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
    else:
        print("⚠️ Nenhum registro válido encontrado!")
    
    # Salvar registros inválidos
    if registros_invalidos:
        df_invalidos = pd.DataFrame(registros_invalidos)
        df_invalidos.to_csv('out/invalid_rows.csv', index=False)
        print(f"\n⚠️ invalid_rows.csv: {len(registros_invalidos)} registros inválidos")
        
        # Mostrar principais motivos de invalidação
        razoes = []
        for r in registros_invalidos:
            if 'invalid_reason' in r:
                razoes.extend(r['invalid_reason'].split('; '))
        
        if razoes:
            from collections import Counter
            principais = Counter(razoes).most_common(5)
            print("\n   Principais motivos de invalidação:")
            for razao, qtd in principais:
                print(f"   - {razao}: {qtd} ocorrências")
    else:
        print("✅ Nenhum registro inválido encontrado!")
    
    # Passo 5: Gerar relatório de performance
    if registros_validos:
        print("\n📈 Gerando relatório de performance dos restaurantes...")
        
        # Filtrar apenas entregues
        entregues_df = pd.DataFrame([r for r in registros_validos if r['is_valid_order']])
        
        if not entregues_df.empty:
            # Agrupar por restaurante
            performance = entregues_df.groupby(['restaurant_id', 'restaurant_name']).agg({
                'order_id': 'count',
                'total_amount': 'sum',
                'commission': 'sum',
                'total_delivery_time': 'mean'
            }).reset_index()
            
            performance.columns = ['restaurant_id', 'restaurant_name', 'total_orders', 'total_revenue', 'total_commission', 'avg_delivery_time']
            
            # Formatar valores para exibição
            performance['total_revenue_fmt'] = performance['total_revenue'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
            performance['total_commission_fmt'] = performance['total_commission'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
            performance['avg_delivery_time_fmt'] = performance['avg_delivery_time'].apply(lambda x: f"{x:.0f} min")
            
            # Salvar Excel
            with pd.ExcelWriter('out/restaurant_performance.xlsx', engine='openpyxl') as writer:
                performance.to_excel(writer, sheet_name='Performance', index=False)
            
            print("✅ restaurant_performance.xlsx gerado!")
            print("\n   Performance dos restaurantes:")
            print(performance[['restaurant_name', 'total_orders', 'total_revenue_fmt', 'total_commission_fmt', 'avg_delivery_time_fmt']].to_string(index=False))
        else:
            print("⚠️ Nenhum pedido entregue para gerar performance!")
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO DO TESTE 1 CONCLUÍDO!")
    print("="*60)

# Executar o processamento
if __name__ == "__main__":
    processar_teste1()