import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np

def get_data_b3():
    path = '../raw_data'
    files = [f for f in listdir(path) if isfile(join(path, f))] 
    list_files = []
    for file in range(0, len(files)):
        list_file = pd.read_excel(f'{path}/{files[file]}', parse_dates=['Data'])
        list_files.append(list_file)
    list_all_files = pd.concat(list_files)
    list_files_s = list_all_files.sort_values(by=['Produto', 'Data'])
    df_files = pd.DataFrame(list_files_s)
    return df_files

def files_featuring_eng():
    df_files = get_data_b3()
    df_files['Data da compra'] = df_files['Data'].where(df_files['Entrada/Saída'] == 'Credito')
    df_files['Data da venda'] = df_files['Data'].where(df_files['Entrada/Saída'] == 'Debito')
    df_files = df_files[['Produto', 'Data da compra', 'Data da venda', 'Quantidade', 'Preço unitário', 'Valor da Operação', 'Movimentação', 'Instituição']]
    df_files['Quantidade'] = df_files['Quantidade'].apply(lambda x: x.replace(',','.'))
    df_files['Quantidade'] = df_files['Quantidade'].astype(float)
    return df_files

def variable_income():
    df_files = files_featuring_eng()
    df_stock = df_files[df_files['Movimentação'] == 'Transferência - Liquidação']
    df_stock = df_stock[['Produto', 'Data da compra', 'Data da venda', 'Quantidade', 'Preço unitário', 'Valor da Operação']]
    df_stock = df_stock.sort_values(by=['Produto', 'Data da compra', 'Data da venda']).reset_index()
    df_stock['Produto'] = df_stock['Produto'].apply(lambda x: x.split('-')[0].strip())
    return df_stock

def variable_income_quantity():
    df_stock = variable_income()
    df_stock_buy = df_stock[df_stock['Data da compra'] > '20000101'].groupby('Produto').agg({'Quantidade':'sum'}).reset_index()
    df_stock_sel = df_stock[df_stock['Data da venda'] > '20000101'].groupby('Produto').agg({'Quantidade':'sum'}).transform(lambda x: x *-1).reset_index()
    quantidades_stock = pd.concat([df_stock_sel, df_stock_buy]).reset_index()
    quantidades_prod_stock = quantidades_stock.groupby(['Produto']).sum().reset_index()
    quantidades_prod_stock = pd.DataFrame(quantidades_prod_stock)
    quantidades_prod_stock = quantidades_prod_stock.drop(columns='index')
    quantidades_prod_stock = quantidades_prod_stock.rename(columns={'Quantidade': 'Saldo de ações'})
    return quantidades_prod_stock

def vari_quant_prof_loss():
    df_stock = variable_income()
    df_stock_opB = df_stock[df_stock['Data da compra'] > '20000101'].sort_values(['Produto', 'Data da compra']).reset_index()
    df_stock_opS = df_stock[df_stock['Data da venda'] > '20000101'].sort_values(['Produto', 'Data da venda']).reset_index()
    data_buy = []
    data_sell = []
    for lineB in range(0, len(df_stock_opB)):
        for lineS in range(0, len(df_stock_opS)):
            if df_stock_opS.Produto[lineS] == df_stock_opB.Produto[lineB] and df_stock_opS['Data da venda'][lineS] >= df_stock_opB['Data da compra'][lineB]:
                buy = df_stock_opB['Valor da Operação'][lineB]
                sell = df_stock_opS['Valor da Operação'][lineS]
                prod = df_stock_opB['Produto'][lineB]
                datb = df_stock_opB['Data da compra'][lineB]
                dats = df_stock_opS['Data da venda'][lineS]
                data_buy.append([datb, prod, buy])
                data_sell.append([dats, prod, sell])
            if df_stock_opS.Produto[lineS] == df_stock_opB.Produto[lineB] and df_stock_opS['Data da venda'][lineS] <= df_stock_opB['Data da compra'][lineB]:
                sell2 = df_stock_opS['Valor da Operação'][lineS]
                prod2 = df_stock_opB['Produto'][lineB]
                dats2 = df_stock_opS['Data da venda'][lineS]
                data_sell.append([dats2, prod2, sell2])
    buy_stock = pd.DataFrame(data_buy, columns=['Data da compra', 'Produto', 'Compra'])           
    sell_stock = pd.DataFrame(data_sell, columns=['Data da venda', 'Produto', 'Venda']) 
    sell_stock = sell_stock.drop_duplicates()
    df_stock_buy = buy_stock.groupby('Produto').sum().reset_index()
    sell_stock = sell_stock.drop(columns=['Data da venda'])
    lucpre_stock = pd.concat([sell_stock, df_stock_buy]).reset_index()
    df_stock_opB_q = df_stock_opB[['Produto', 'Quantidade']]
    df_stock_opB_v = df_stock_opB[['Produto', 'Valor da Operação']]
    df_stock_opS_q = df_stock_opS[['Produto', 'Quantidade']]
    df_stock_opS_v = df_stock_opS[['Produto', 'Valor da Operação']]
    sumQ_stock_opB = df_stock_opB_q.groupby('Produto').sum().reset_index()
    sumV_stock_opB = df_stock_opB_v.groupby('Produto').sum().reset_index()
    sumQ_stock_opS = df_stock_opS_q.groupby('Produto').sum().reset_index()
    sumV_stock_opS = df_stock_opS_v.groupby('Produto').sum().reset_index()
    df_stock_opB = pd.merge(sumQ_stock_opB, sumV_stock_opB, how='left', on='Produto')
    df_stock_opS = pd.merge(sumQ_stock_opS, sumV_stock_opS, how='left', on='Produto')
    calcu = []
    for lineB in range(0, len(df_stock_opB)):
        for lineS in range(0, len(df_stock_opS)):
            if df_stock_opS.Produto[lineS] == df_stock_opB.Produto[lineB]:
                prod = df_stock_opB.Produto[lineB]
                cal = df_stock_opS['Valor da Operação'][lineS]-((df_stock_opB['Valor da Operação'][lineB]/df_stock_opB.Quantidade[lineB])*df_stock_opS.Quantidade[lineS])
                calcu.append([prod, cal])
    calcula = pd.DataFrame(calcu, columns=['Produto', 'Lucro/Prejuízo']) 
    return calcula

def variable_income_b3():
    quantidades_prod_stock = variable_income_quantity()
    calcula = vari_quant_prof_loss()
    df_stock = variable_income()
    stock_i = pd.merge(quantidades_prod_stock, calcula, how='left', on='Produto')
    merge_stock = pd.merge(df_stock, stock_i, how='left', on='Produto')
    merge_stock.drop(columns='index', inplace = True)
    merge_stock = merge_stock.sort_values(['Produto', 'Data da compra', 'Data da venda'])
    merge_stock['Lucro/Prejuizo'] = ''
    merge_stock['Saldo das ações'] = ''
    for line in range(0, len(merge_stock)-1):
        if merge_stock['Produto'].iloc[line] != merge_stock['Produto'].iloc[line+1]:
            merge_stock['Lucro/Prejuizo'].iloc[line] = merge_stock['Lucro/Prejuízo'].iloc[line]
            merge_stock['Saldo das ações'].iloc[line] = merge_stock['Saldo de ações'].iloc[line]
        else:
            merge_stock['Lucro/Prejuizo'].iloc[line] = 'nan'
            merge_stock['Saldo das ações'].iloc[line] = 'nan'
    merge_stock['Lucro/Prejuizo'].iloc[len(merge_stock)-1] = merge_stock['Lucro/Prejuízo'].iloc[len(merge_stock)-1]
    merge_stock['Saldo das ações'].iloc[len(merge_stock)-1] = merge_stock['Saldo de ações'].iloc[len(merge_stock)-1]
    merge_stock.drop(columns=['Saldo de ações', 'Lucro/Prejuízo'], inplace=True)
    spreadsheet_to_stock_income_tax = merge_stock.to_excel('../raw_data/files_to_ti/spreadsheet_stock_income_tax.xlsx', index = False)
    return spreadsheet_to_stock_income_tax

planilha = variable_income_b3()
# if __name__ = "__main__":
#     planilha = variable_income_b3()