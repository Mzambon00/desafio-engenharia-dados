# 🚀 Desafio Engenharia de Dados

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Pandas](https://img.shields.io/badge/pandas-2.0+-blue.svg)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Pipeline ETL** robusto em Python para consolidação, limpeza e validação de dados de transações comerciais (restaurantes, marketing e estoque). Inclui normalização de documentos (CPF/CNPJ), conversão de moeda brasileira, deduplicação e geração de relatórios gerenciais em CSV e Excel.

## 📋 Descrição dos Testes

### Teste 1: Processamento de Pedidos de Restaurante 🍕

**Objetivo:** Consolidar pedidos de delivery, calcular comissões e avaliar performance de entregadores e restaurantes.

**Regras de Negócio:**
- **Status:** Normalizar `delivered`, `canceled`, `in_progress` → apenas pedidos `delivered` são considerados válidos
- **CPF:** Validar formato de 11 dígitos, normalizar para `123.456.789-00`
- **Valores:** Converter formatos monetários (ex: `R$ 1.234,56` → `1234.56`)
- **Comissão:** Calcular se `total_amount >= min_order_amount`
  - Fórmula: `commission = total_amount * commission_rate`

**Métricas Geradas:**
- `commission`: Valor da comissão calculada
- `total_delivery_time`: Soma de `preparation_time_min + delivery_time_min`

**Arquivos de Entrada:**
- `data/orders/orders_*.csv` - Transações de pedidos
- `data/restaurants.xlsx` - Cadastro de restaurantes com taxas de comissão

**Arquivos de Saída:**
- `out/clean_orders.csv` - Pedidos validados e enriquecidos
- `out/invalid_rows.csv` - Registros rejeitados com motivo
- `out/restaurant_performance.xlsx` - Relatório de performance por restaurante

---

### Teste 2: Análise de Campanhas de Marketing 📈

**Objetivo:** Processar leads de campanhas digitais, calcular ROI e identificar canais lucrativos.

**Regras de Negócio:**
- **Email:** Validar formato (regex: `usuario@dominio.com`)
- **Datas:** Converter para formato `YYYY-MM-DD`
- **ROI:** Calcular retorno sobre investimento
  - Fórmula: `roi = (conversion_value - total_cost) / total_cost`
- **Lucratividade:** Lead é lucrativo se `roi > 0.2` (20%)

**Métricas Geradas:**
- `total_cost`: `clicks * cost_per_click`
- `roi`: Retorno sobre o investimento (percentual)
- `is_profitable`: Boolean indicando se ROI > 20%

**Arquivos de Entrada:**
- `data/leads/leads_*.csv` - Dados de leads por campanha
- `data/campaigns.xlsx` - Metadados das campanhas

**Arquivos de Saída:**
- `out/clean_leads.csv` - Leads validados com métricas calculadas
- `out/invalid_rows.csv` - Registros rejeitados com motivo
- `out/campaign_roi.xlsx` - Relatório de ROI por canal de marketing

---

### Teste 3: Controle de Estoque e Vendas 📦

**Objetivo:** Reconciliar vendas com estoque, identificar produtos com baixo giro e níveis críticos.

**Regras de Negócio:**
- **CNPJ:** Validar formato de 14 dígitos, normalizar para `12.345.678/0001-00`
- **CEP:** Validar formato de 8 dígitos, normalizar para `12345-678`
- **Quantidade:** `quantity_sold > 0`
- **Desconto:** Não pode ser maior que `unit_price`

**Métricas Geradas:**
- `total_sale`: `quantity_sold * (unit_price - discount)`
- `running_stock`: Estoque acumulado após cada venda
- `stock_status`: Classificação do nível de estoque
  - `Critical`: Estoque < nível mínimo
  - `Low`: Estoque < ponto de reabastecimento
  - `OK`: Estoque adequado
- `turnover_days`: Dias de giro de estoque

**Arquivos de Entrada:**
- `data/sales/sales_*.csv` - Registros de vendas
- `data/products.xlsx` - Cadastro de produtos com níveis de estoque

**Arquivos de Saída:**
- `out/clean_sales.csv` - Vendas validadas com estoque corrente
- `out/invalid_rows.csv` - Registros rejeitados com motivo
- `out/inventory_report.xlsx` - Relatório de inventário por produto

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+** - Linguagem principal
- **Pandas** - Manipulação e análise de dados
- **OpenPyXL** - Leitura/escrita de arquivos Excel
- **Regex (re)** - Validação de padrões (CPF, CNPJ, email, CEP)

## 📁 Estrutura do Projeto
desafio-engenharia-dados/
├── data/ # Dados de entrada (ignorado pelo Git)
│ ├── orders/ # CSVs de pedidos (Teste 1)
│ ├── leads/ # CSVs de leads (Teste 2)
│ ├── sales/ # CSVs de vendas (Teste 3)
│ ├── restaurants.xlsx # Tabela auxiliar Teste 1
│ ├── campaigns.xlsx # Tabela auxiliar Teste 2
│ └── products.xlsx # Tabela auxiliar Teste 3
├── out/ # Resultados processados (ignorado)
│ ├── clean_.csv # Dados limpos e validados
│ ├── invalid_rows.csv # Registros com erros
│ └── .xlsx # Relatórios gerenciais
├── generate_data_test.py # Scripts para gerar dados de exemplo
├── teste_processamento.py # Pipelines de processamento
├── requirements.txt # Dependências do projeto
└── README.md # Documentação


## 🚀 Como Executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Gerar dados de exemplo (opcional)
python generate_data_test1.py
python generate_data_test2.py
python generate_data_test3.py

# 3. Executar pipelines
python teste1_processamento.py  # Processa pedidos de restaurante
python teste2_processamento.py  # Processa leads de marketing
python teste3_processamento.py  # Processa vendas e estoque
