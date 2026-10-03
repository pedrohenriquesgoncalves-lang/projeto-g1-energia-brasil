# ⚡ Consumo de Energia no Brasil (2015–2024)

Projeto da **Avaliação G1** da disciplina *Linguagem de Programação — Análise e Visualização de Dados com Python*.

## Problema
Como o consumo de energia elétrica se distribui entre regiões, estados e setores, como evolui ao longo do tempo e quais variáveis se relacionam com ele?

## Base de dados
`dados/simulacao_consumo_energia_brasil.csv`: 4.440 registros mensais (2015–2024), 14 colunas, sem nulos. Base **simulada**: consumo (MWh), demanda de pico, temperatura, tarifa, população, eficiência energética, emissão de CO₂ e nível de demanda, por região, UF e setor.

## Tecnologias
Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, SQLAlchemy, SQLite e GitHub.

## Funcionalidades
**Intermediárias:** filtros múltiplos (região, setor, nível de demanda e período), KPIs dinâmicos, análise temporal, dashboard organizado em seções (abas) e visualizações comparativas.

**Avançadas:** persistência em banco (SQLAlchemy + SQLite), correlação estatística (Pearson) e séries temporais avançadas (média móvel de 12 meses e variação anual).

## Estrutura
```
projeto-g1/
├── app.py                # dashboard Streamlit
├── requirements.txt
├── README.md
├── index.html            # página do projeto (GitHub Pages)
├── css/style.css
├── dados/                # base CSV
├── database/             # banco SQLite (energia.db)
├── notebooks/            # analise_consumo_energia.ipynb
└── imagens/              # gráficos exportados do notebook
```

## Como executar
```bash
pip install -r requirements.txt
streamlit run app.py
```
O notebook pode ser aberto no Jupyter ou no Google Colab (envie o CSV para a pasta de arquivos do Colab).

## Principais resultados
- Consumo total de ≈ 165,7 milhões de MWh, distribuído de forma equilibrada entre os setores.
- Sudeste concentra ≈ 36% do consumo por ter mais registros; o consumo médio por registro é semelhante entre regiões.
- Queda de ≈ 9,5% em 2020, recuperação em 2021 e pico em 2022.
- Sem correlação linear relevante entre o consumo e as demais variáveis (base simulada).

## Links
- Repositório: https://github.com/pedrohenriquesgoncalves-lang/projeto-g1-energia-brasil
- Página do projeto: https://pedrohenriquesgoncalves-lang.github.io/projeto-g1-energia-brasil/
- Dashboard: LINK_DO_STREAMLIT

**Autor:** Pedro Henrique
