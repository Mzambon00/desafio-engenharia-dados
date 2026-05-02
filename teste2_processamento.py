# teste2_processamento.py
import pandas as pd
import glob
import os
import re
from datetime import datetime
from collections import Counter

def validar_email(email):
    """
    Valida formato de email
    Retorna: (email_normalizado, is_valid)
    """
    if pd.isna(email):
        return None, False
    
    email_str = str(email).strip().lower()
    
    # Regex básico para validar email
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(padrao, email_str):
        return email_str, True
    else:
        return email_str, False

def normalizar_data(data_str):
    """Converte data para formato YYYY-MM-DD"""
    if pd.isna(data_str):
        return None
    
    data_str = str(data_str).strip()
    formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
    
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
    
    valor_str = str(valor).strip()
    valor_str = valor_str.replace('R$', '').replace('$', '').replace(' ', '')
    
    if ',' in valor_str and '.' in valor_str:
        if valor_str.rfind(',') > valor_str.rfind('.'):
            valor_str = valor_str.replace('.', '').replace(',', '.')
    elif ',' in valor_str and '.' not in valor_str:
        valor_str = valor_str.replace(',', '.')
    
    try:
        return float(valor_str)
    except:
        return None

def processar_teste2():
    """
    Função principal de processamento do Teste 2 - Marketing
    """
    print("="*60)
    print("TESTE 2: Análise de Campanhas de Marketing")
    print("="*60)
    
    # Criar diretório de saída
    os.makedirs('out', exist_ok=True)
    
    # Passo 1: Carregar dados das campanhas
    print("\n📚 Passo 1: Carregando dados das campanhas...")
    try:
        campaigns_df = pd.read_excel('data/campaigns.xlsx')
        print(f"   ✓ Carregadas {len(campaigns_df)} campanhas")
        print(campaigns_df[['campaign_code', 'campaign_name', 'expected_conversion_rate']].to_string(index=False))
    except FileNotFoundError:
        print("   ❌ Arquivo 'data/campaigns.xlsx' não encontrado!")
        return
    except Exception as e:
        print(f"   ❌ Erro ao carregar campanhas: {e}")
        return
    
    # Passo 2: Listar arquivos de leads
    print("\n📁 Passo 2: Procurando arquivos de leads...")
    lead_files = glob.glob('data/leads/leads_*.csv')
    
    if not lead_files:
        print("   ❌ Nenhum arquivo de lead encontrado em 'data/leads/'")
        return
    
    print(f"   ✓ Encontrados {len(lead_files)} arquivo(s)")
    
    # Estruturas para resultados
    registros_validos = []
    registros_invalidos = []
    
    # Passo 3: Processar cada arquivo
    for arquivo in lead_files:
        print(f"\n🔄 Processando: {os.path.basename(arquivo)}")
        
        # Tentar diferentes formas de leitura
        df = None
        for sep in [',', ';', '|']:
            try:
                df = pd.read_csv(arquivo, encoding='utf-8', sep=sep)
                print(f"   ✓ Lido com separador '{sep}'")
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
        
        # Processar cada lead
        for idx, row in df.iterrows():
            razoes_invalidacao = []
            
            # Validar email
            email = row.get('client_email')
            email_normalizado, email_valido = validar_email(email)
            if not email_valido:
                razoes_invalidacao.append('email_invalido')
            
            # Validar data de conversão
            data_conversao = normalizar_data(row.get('conversion_date'))
            if not data_conversao:
                razoes_invalidacao.append('data_invalida')
            
            # Validar números
            try:
                clicks = int(row.get('clicks')) if pd.notna(row.get('clicks')) else 0
                if clicks < 0:
                    razoes_invalidacao.append('clicks_negativo')
                
                cost_per_click = normalizar_moeda(row.get('cost_per_click'))
                if cost_per_click is None or cost_per_click < 0:
                    razoes_invalidacao.append('cost_per_click_invalido')
                
                conversion_value = normalizar_moeda(row.get('conversion_value'))
                if conversion_value is None or conversion_value < 0:
                    razoes_invalidacao.append('conversion_value_invalido')
                
                days_to_close = int(row.get('days_to_close')) if pd.notna(row.get('days_to_close')) else 0
                if days_to_close < 0:
                    razoes_invalidacao.append('days_to_close_invalido')
                    
            except Exception as e:
                razoes_invalidacao.append('erro_numerico')
            
            # Se inválido, salvar
            if razoes_invalidacao:
                dados_originais = row.to_dict()
                dados_originais['invalid_reason'] = '; '.join(razoes_invalidacao)
                dados_originais['source_file'] = os.path.basename(arquivo)
                registros_invalidos.append(dados_originais)
                continue
            
            # Calcular métricas
            total_cost = clicks * cost_per_click if cost_per_click else 0
            roi = (conversion_value - total_cost) / total_cost if total_cost > 0 else 0
            is_profitable = roi > 0.2
            
            # Buscar informações da campanha
            campaign_info = campaigns_df[campaigns_df['campaign_code'] == row.get('campaign_code')]
            campaign_name = campaign_info['campaign_name'].values[0] if not campaign_info.empty else 'Unknown'
            expected_rate = campaign_info['expected_conversion_rate'].values[0] if not campaign_info.empty else 0
            
            # Salvar registro válido
            registros_validos.append({
                'lead_id': row.get('lead_id'),
                'campaign_code': row.get('campaign_code'),
                'campaign_name': campaign_name,
                'client_email': email_normalizado,
                'conversion_date': data_conversao,
                'channel': row.get('channel'),
                'clicks': clicks,
                'cost_per_click': cost_per_click,
                'conversion_value': conversion_value,
                'days_to_close': days_to_close,
                'total_cost': total_cost,
                'roi': roi,
                'is_profitable': is_profitable,
                'expected_conversion_rate': expected_rate,
                'source_file': os.path.basename(arquivo)
            })
    
    # Passo 4: Salvar resultados
    print("\n" + "="*60)
    print("📊 RESULTADOS")
    print("="*60)
    
    # Salvar registros válidos
    if registros_validos:
        df_validos = pd.DataFrame(registros_validos)
        df_validos.to_csv('out/clean_leads.csv', index=False)
        print(f"✅ clean_leads.csv: {len(registros_validos)} leads válidos")
        
        # Estatísticas
        leads_profitable = len([l for l in registros_validos if l['is_profitable']])
        total_investimento = sum([l['total_cost'] for l in registros_validos])
        total_receita = sum([l['conversion_value'] for l in registros_validos])
        
        print(f"\n📈 Estatísticas gerais:")
        print(f"   - Leads com ROI > 20%: {leads_profitable}")
        print(f"   - Investimento total: R$ {total_investimento:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        print(f"   - Receita total: R$ {total_receita:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        print(f"   - ROI médio: {(sum([l['roi'] for l in registros_validos])/len(registros_validos)*100):.1f}%")
    
    # Salvar inválidos
    if registros_invalidos:
        df_invalidos = pd.DataFrame(registros_invalidos)
        df_invalidos.to_csv('out/invalid_rows.csv', index=False)
        print(f"\n⚠️ invalid_rows.csv: {len(registros_invalidos)} registros inválidos")
    
    # Gerar relatório ROI por canal
    if registros_validos:
        print("\n📈 Gerando relatório ROI por canal...")
        
        df_validos = pd.DataFrame(registros_validos)
        
        # Agrupar por canal
        roi_canal = df_validos.groupby('channel').agg({
            'lead_id': 'count',
            'conversion_value': 'sum',
            'total_cost': 'sum',
            'roi': 'mean',
            'is_profitable': 'sum'
        }).reset_index()
        
        roi_canal.columns = ['channel', 'total_conversions', 'total_revenue', 'total_investment', 'average_roi', 'profitable_campaigns']
        
        # Formatar
        roi_canal['total_revenue_fmt'] = roi_canal['total_revenue'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        roi_canal['total_investment_fmt'] = roi_canal['total_investment'].apply(lambda x: f"R$ {x:,.2f}".replace(',', 'v').replace('.', ',').replace('v', '.'))
        roi_canal['average_roi_fmt'] = roi_canal['average_roi'].apply(lambda x: f"{x*100:.1f}%")
        
        # Salvar Excel
        with pd.ExcelWriter('out/campaign_roi.xlsx', engine='openpyxl') as writer:
            roi_canal.to_excel(writer, sheet_name='ROI por Canal', index=False)
        
        print("✅ campaign_roi.xlsx gerado!")
        print("\n   ROI por canal:")
        print(roi_canal[['channel', 'total_conversions', 'total_revenue_fmt', 'total_investment_fmt', 'average_roi_fmt', 'profitable_campaigns']].to_string(index=False))
    
    print("\n" + "="*60)
    print("✅ PROCESSAMENTO DO TESTE 2 CONCLUÍDO!")
    print("="*60)

if __name__ == "__main__":
    processar_teste2()