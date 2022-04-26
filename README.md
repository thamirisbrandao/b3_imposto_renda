# Data analysis
- Document here the project: b3_imposto_renda
- Description: Using B3 informations to create a sheat healpful to declarate income tax :)
- Data Source: https://www.investidor.b3.com.br/ 
-              Follow this steps: Extrato --> Movimentação --> Filtrar: Download all investments per year in an excel planilha
-              Features from B3: Entrada/Saída Data Movimentação Produto Instituição Quantidade Preço unitário Valor da Operação
- Data Location: Put all data in raw_data (directory: /home/thamirisbrandao/code/thamirisbrandao/b3_imposto_renda/raw_data), it is a private information. Is important put just excel spreadsheed to do analysis.
- Type of analysis: Using python to create an excel spreasheet

# Startup the project

pip install git+ssh://git@github.com/thamirisbrandao/b3_imposto_renda

- Go to follow directory:
/home/thamirisbrandao/code/thamirisbrandao/b3_imposto_renda/b3_imposto_renda

- Execute the 2 scripts:
ipython fixed_income.py 
ipython variable_income.py

- Go find the spreadsheed in /home/thamirisbrandao/code/thamirisbrandao/b3_imposto_renda/raw_data/files_to_ti directory

# Notes from developer

I used these codes for 2 real cases, however B3 didn't give all the informations about investments in my hole life. There are some investments that I checked on my personal spreadsheet. Althout B3 is uncomplete, these codes were really usefull to create a investment spreadsheet.
