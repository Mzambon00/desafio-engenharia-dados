# teste3_processamento.py
import pandas as pd
import glob
import os
import re
from datetime import datetime

def validar_cnpj(cnpj):
    """
    Normaliza CNPJ: remove caracteres especiais e valida
    Retorna: (cnpj_formatado, cnpj_limpo, tipo)
    """
    if pd.isna(cnpj) or cnpj == '':
        return None, None, None
    
    cnpj_str = str(cnpj).strip()
    cnpj_limpo = re.sub(r'\D', '', cnpj_str)
    
    if len(cnpj_limpo) == 14:
        cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj_formatado, cnpj_limpo, 'CNPJ'
    else:
        return None, None, None

def validar_cep(cep):
    """
    Normaliza CEP: remove caracteres especiais
    """
    if pd.isna(cep) or cep == '':
        return None
    
    cep_str = str(cep).strip()
    cep_limpo = re.sub(r'\D', '', cep_str)
    
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    else:
        return None

def normalizar_data(data_str):
    """Converte data para formato YYYY-MM-DD"""
    if pd.isna(data_str):
        return None
    
    data_str = str(data_str).strip()
    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
    
    for formato in formatos:
        try:
            data = datetime.strptime(data_str, formato)
            return data.strftime('%Y-%m-%d')
        except:
            continue
    return None

def normalizar_moeda(valor):
    """Converte formato monetário para float"""
    if pd.isna(valor):
        return None
    
    if isinstance(valor, (int, float)):
        return float(valor)
    
    valor_str = str(valor).strip()
    valor_str = valor_str.replace('R$', '').replace('$', '').replace(' ', '')
    
    # Remover % se for desconto percentual
    if valor_str.endswith('%'):
        return None  # Vai ser tratado separadamente
    
    if ',' in valor_str and '.' in valor_str:
        if valor_str.rfind(',') > valor_str.rfind('.'):
            valor_str = valor_str.replace('.', '').replace(',', '.')
    elif ',' in valor_str and '.' not in valor_str:
        valor_str = valor_str.replace(',', '.')
    
    try:
        return float(valor_str)
    except:
        return None

def processar_teste3():
    """
    Função principal de processamento do Teste 3 - Estoque
    """
    print("="*60)
    print("TESTE 3: Controle de Estoque e Vendas")
    print("="*60)
    
    # Criar diretório de saída
    os.makedirs('out', exist_ok=True)
    
    # Passo 1: Carregar dados dos produtos
    print("\n📚 Passo 1: Carregando dados dos produtos...")
    try:
        products_df = pd.read_excel('data/products.xlsx')
        print(f"   ✓ Carregados {len(products_df)} produtos")
        print(products_df[['product_sku', 'product_name', 'stock_initial']].to_string(index=False))
    except FileNotFoundError:
        print("   ❌ Arquivo 'data/products.xlsx' não encontrado!")
        return
    except Exception as e:
        print(f"   ❌ Erro ao carregar produtos: {e}")
        return
    
    # Passo 2: Listar arquivos de vendas
    print("\n📁 Passo 2: Procurando arquivos de vendas...")
    sales_files = glob.glob('data/sales/sales_*.csv')
    
    if not sales_files:
        print("   ❌ Nenhum arquivo de venda encontrado em 'data/sales/'")
        return
    
    print(f"   ✓ Encontrados {len(sales_files)} arquivo(s)")
    
    # Estruturas para resultados
    registros_validos = []
    registros_invalidos = []
    
    # Dicionário para controle de estoque
    estoque_atual = {row['product_sku']: row['stock_initial'] for idx, row in products_df.iterrows()}
    
    # Passo 3: Processar cada arquivo
    for arquivo in sales_files:
        print(f"\n🔄 Processando: {os.path.basename(arquivo)}")
        
        # Tentar diferentes formas de leitura
        df = None
        for sep in [',', ';', '|']:
            try:
                df = pd.read_csv(arquivo, encoding='utf-8', sep=sep)
                print(f"   ✓ Lido com separador '{sep}' (UTF-8)")
                break
            except:
                try:
                    df = pd.read_csv(arquivo, encoding='latin1', sep=sep)
                    print(f"   ✓ Lido com separador '{sep}' (Latin1)")
                    break
                except:
                    continue
        
        if df is None:
            print(f"   ❌ Não foi possível ler o arquivo")
            continue
        
        print(f"   ✓ Total de registros: {len(df)}")
        
        # Processar cada venda
        for idx, row in df.iterrows():
            razoes_invalidacao = []
            
            # Validar CNPJ da loja
            cnpj_formatado, cnpj_limpo, tipo_doc = validar_cnpj(row.get('store_cnpj'))
            if not cnpj_formatado:
                razoes_invalidacao.append('cnpj_invalido')
            
            # Validar CEP
            cep_normalizado = validar_cep(row.get('customer_zipcode'))
            if not cep_normalizado:
                razoes_invalidacao.append('cep_invalido')
            
            # Validar data
            data_venda = normalizar_data(row.get('sale_date'))
            if not data_venda:
                razoes_invalidacao.append('data_invalida')
            
            # Validar números
            try:
                quantity_sold = int(row.get('quantity_sold')) if pd.notna(row.get('quantity_sold')) else 0
                if quantity_sold <= 0:
                    razoes_invalidacao.append('quantidade_invalida')
                
                # Tratar preço unitário
                unit_price_raw = row.get('unit_price')
                unit_price = normalizar_moeda(unit_price_raw)
                if unit_price is None or unit_price < 0:
                    razoes_invalidacao.append('preco_invalido')
                
                # Tratar desconto
                discount_raw = row.get('discount')
                discount = 0
                if pd.notna(discount_raw):
                    if isinstance(discount_raw, str) and '%' in discount_raw:
                        # Desconto percentual
                        percent = float(discount_raw.replace('%', '').strip())
                        discount = unit_price * (percent / 100) if unit_price else 0
                    else:
                        discount = normalizar_moeda(discount_raw) or 0
                
                if discount > unit_price:
                    razoes_invalidacao.append('desconto_maior_que_preco')
                    
            except Exception as e:
                razoes_invalidacao.append('erro_numerico')
            
            # Validar produto
            product_sku = row.get('product_sku')
            if product_sku not in estoque_atual:
                razoes_invalidacao.append('produto_nao_encontrado')
            
            # Se inválido, salvar
            if razoes_invalidacao:
                dados_originais = row.to_dict()
                dados_originais['invalid_reason'] = '; '.join(razoes_invalidacao)
                dados_originais['source_file'] = os.path.basename(arquivo)
                registros_invalidos.append(dados_originais)
                continue
            
            # Calcular total da venda
            total_sale = quantity_sold * (unit_price - discount)
            
            # Atualizar estoque
            if product_sku in estoque_atual:
                estoque_atual[product_sku] -= quantity_sold
                running_stock = estoque_atual[product_sku]
            else:
                running_stock = None
            
            # Buscar informações do produto
            produto_info = products_df[products_df['product_sku'] == product_sku]
            if not produto_info.empty:
                min_stock = produto_info['min_stock_level'].values[0]
                reorder_point = produto_info['reorder_point'].values[0]
                product_name = produto_info['product_name'].values[0]
            else:
                min_stock = None
                reorder_point = None
                product_name = 'Unknown'
            
            # Salvar registro válido
            registros_validos.append({
                'sale_id': row.get('sale_id'),
                'product_sku': product_sku,
                'product_name': product_name,
                'store_cnpj': cnpj_formatado,
                'document_clean': cnpj_limpo,
                'document_type': tipo_doc,
                'sale_date': data_venda,
                'quantity_sold': quantity_sold,
                'unit_price': unit_price,
                'discount': discount,
                'customer_zipcode': cep_normalizado,
                'total_sale': total_sale,
                'running_stock': running_stock,
                'min_stock_level': min_stock,
                'reorder_point': reorder_point,
                'source_file': os.path.basename(arquivo)
            })
    
    # Passo 4: Salvar resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS")
    print("="*60)
    
    # Salvar registros válidos
    if registros_validos:
        df_validos = pd.DataFrame(registros_validos)
        df_validos.to_csv('out/clean_sales.csv', index=False)
        print(f"✅ clean_sales.csv: {len(registros_validos)} vendas válidas")
        
        # Estatísticas
        total_vendas = sum([v['total_sale'] for v in registros_validos])
        total_quantidade = sum([v['quantity_sold'] for v in registros_validos])
        
        print(f"\n📈 Estatísticas gerais:")
        print(f"   - Total de vendas: R$ {total_vendas:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        print(f"   - Quantidade total vendida: {total_quantidade} unidades")
    else:
        print("⚠️ Nenhum registro válido encontrado!")
    
    # Salvar inválidos
    if registros_invalidos:
        df_invalidos = pd.DataFrame(registros_invalidos)
        df_invalidos.to_csv('out/invalid_rows.csv', index=False)
        print(f"\n⚠️ invalid_rows.csv: {len(registros_invalidos)} registros inválidos")
        
        # Mostrar principais motivos
        razoes = []
        for r in registros_invalidos:
            if 'invalid_reason' in r:
                razoes.extend(r['invalid_reason'].split('; '))
        
        if razoes:
            from collections import Counter
            principais = Counter(razoes).most_common(3)
            print("\n   Principais motivos:")
            for razao, qtd in principais:
                print(f"   - {razao}: {qtd} ocorrências")
    
    # Gerar relatório de inventário
    if registros_validos:
        print("\n📈 Gerando relatório de inventário...")
        
        df_validos = pd.DataFrame(registros_validos)
        
        # Agrupar por produto
        inventario = df_validos.groupby(['product_sku', 'product_name']).agg({
            'quantity_sold': 'sum',
            'total_sale': 'sum',
            'running_stock': 'last',  # Último estoque registrado
            'min_stock_level': 'first',
            'reorder_point': 'first'
        }).reset_index()
        
        # Definir status do estoque
        def get_stock_status(row):
            if pd.isna(row['running_stock']):
                return "Unknown"
            elif row['running_stock'] < row['min_stock_level']:
                return "Critical"
            elif row['running_stock'] < row['reorder_point']:
                return "Low"
            else:
                return "OK"
        
        def get_turnover_days(row):
            if row['quantity_sold'] > 0:
                # Calcular giro de estoque (assumindo 30 dias no período)
                initial_stock = row['running_stock'] + row['quantity_sold']
                return (initial_stock / row['quantity_sold']) * 30
            else:
                return None
        
        inventario['stock_status'] = inventario.apply(get_stock_status, axis=1)
        inventario['turnover_days'] = inventario.apply(get_turnover_days, axis=1)
        
        # Formatar
        inventario['total_revenue_fmt'] = inventario['total_sale'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        inventario['turnover_days_fmt'] = inventario['turnover_days'].apply(lambda x: f"{x:.0f} dias" if x else "No sales")
        inventario['running_stock'] = inventario['running_stock'].fillna(0).astype(int)
        
        # Salvar Excel
        with pd.ExcelWriter('out/inventory_report.xlsx', engine='openpyxl') as writer:
            inventario.to_excel(writer, sheet_name='Inventory Report', index=False)
        
        print("✅ inventory_report.xlsx gerado!")
        print("\n   Status do estoque:")
        print(inventario[['product_name', 'quantity_sold', 'total_revenue_fmt', 'running_stock', 'stock_status', 'turnover_days_fmt']].to_string(index=False))
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO DO TESTE 3 CONCLUÍDO!")
    print("="*60)

if __name__ == "__main__":
    processar_teste3()