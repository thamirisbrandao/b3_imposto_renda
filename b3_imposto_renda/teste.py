import pandas as pd
from os import listdir
from os.path import isfile, join
import numpy as np

class SpreadsheetIncomeTax():
    def __init__(self):
        self.files = None

    def get_data_b3(self):
        path = '../raw_data'
        self.files = [f for f in listdir(path) if isfile(join(path, f))] 
        list_files = []
        for file in range(0, len(self.files)):
            list_file = pd.read_excel(f'{path}/{self.files[file]}', parse_dates=['Data'])
            list_files.append(list_file)
        list_all_files = pd.concat(list_files)
        list_files_s = list_all_files.sort_values(by=['Produto', 'Data'])
        df_files = pd.DataFrame(list_files_s)
        return df_files

    def files_featuring_eng(self):
        df_files = self.get_data_b3()
        df_files['Data da compra'] = df_files['Data'].where(df_files['Entrada/Saída'] == 'Credito')
        df_files['Data da venda'] = df_files['Data'].where(df_files['Entrada/Saída'] == 'Debito')
        df_files = df_files[['Produto', 'Data da compra', 'Data da venda', 'Quantidade', 'Preço unitário', 'Valor da Operação', 'Movimentação', 'Instituição']]
        df_files['Quantidade'] = df_files['Quantidade'].apply(lambda x: x.replace(',','.'))
        df_files['Quantidade'] = df_files['Quantidade'].astype(float)
        return df_files

    def fixed_income(self):
        df_files = self.files_featuring_eng()
        df_fixedi_b = df_files[df_files['Movimentação'] == 'Compra']
        df_fixedi_s = df_files[df_files['Movimentação'] == 'Venda']
        df_fixedi = pd.concat([df_fixedi_b, df_fixedi_s])
        df_fixedi = df_fixedi[['Produto', 'Data da compra', 'Data da venda', 'Quantidade', 'Preço unitário', 'Valor da Operação', 'Instituição']]
        df_fixedi = df_fixedi.sort_values(by=['Produto']).reset_index()
        return df_fixedi

    def fixed_income_quantity(self):
        df_fixedi = self.fixed_income()
        df_fixedi_buy = df_fixedi[df_fixedi['Data da compra'] > '20000101'].groupby('Produto').agg({'Quantidade':'sum'}).reset_index()
        df_fixedi_sel = df_fixedi[df_fixedi['Data da venda'] > '20000101'].groupby('Produto').agg({'Quantidade':'sum'}).transform(lambda x: x *-1).reset_index()
        quantity = pd.concat([df_fixedi_sel, df_fixedi_buy]).reset_index()
        quantity_prod = quantity.groupby(['Produto']).sum().reset_index()
        quantity_prod.drop(columns='index', inplace=True)
        for line in range(0, len(quantity_prod)):
            if quantity_prod.Quantidade[line] < 0:
                quantity_prod.Quantidade[line] = quantity_prod.Quantidade[line]*-1
            else:
                quantity_prod.Quantidade[line]
        quantity_prod = quantity_prod.rename(columns={'Quantidade': 'Saldo no Tesouro'})
        quantity_prod = pd.DataFrame(quantity_prod)
    #  quantity_prod = quantity_prod.drop(columns='index')
        return quantity_prod

    def fixed_income_prof_loss(self):
        df_fixedi = self.fixed_income()
        df_fixedi_opB = df_fixedi[df_fixedi['Data da compra'] > '20000101'].reset_index()
        df_fixedi_opS = df_fixedi[df_fixedi['Data da venda'] > '20000101'].reset_index()

        df_fixedi_opB['Lucro/Prejuízo'] = 0
        for lineS in range(0, len(df_fixedi_opS)):
            for lineB in range(0, len(df_fixedi_opB)):
                if df_fixedi_opS['Quantidade'][lineS] == df_fixedi_opB['Quantidade'][lineB]:
                    df_fixedi_opB['Lucro/Prejuízo'][lineB] = df_fixedi_opS['Valor da Operação'][lineS] - df_fixedi_opB['Valor da Operação'][lineB]
        prof_loss_prod = df_fixedi_opB[['Produto', 'Lucro/Prejuízo']]
        return prof_loss_prod

    def fixed_income_b3(self):
        prof_loss_prod = self.fixed_income_prof_loss()
        quantity_prod = self.fixed_income_quantity()
        df_fixedi = fixed_income()
        quan_prof_loss = pd.concat([quantity_prod, prof_loss_prod]).reset_index()
        prof_loss = quan_prof_loss.groupby(['Produto']).sum().reset_index()
        prof_loss = prof_loss.drop(columns='index')

        merge_fixo = pd.merge(df_fixedi, prof_loss, how='left', on='Produto')
        merge_fixo.drop(columns=['index', 'Instituição'], inplace = True)
        merge_fixo = merge_fixo.sort_values(['Produto', 'Data da compra', 'Data da venda'])

        merge_fixo['Lucro/Prejuizo'] = ''
        merge_fixo['Saldo Tesouro'] = ''
        for line in range(0, len(merge_fixo)-1):
            if merge_fixo['Produto'].iloc[line] != merge_fixo['Produto'].iloc[line+1]:
                merge_fixo['Lucro/Prejuizo'].iloc[line] = merge_fixo['Lucro/Prejuízo'].iloc[line]
                merge_fixo['Saldo Tesouro'].iloc[line] = merge_fixo['Saldo no Tesouro'].iloc[line]
            else:
                merge_fixo['Lucro/Prejuizo'].iloc[line] = 'nan'
                merge_fixo['Saldo Tesouro'].iloc[line] = 'nan'
        merge_fixo['Lucro/Prejuizo'].iloc[len(merge_fixo)-1] = merge_fixo['Lucro/Prejuízo'].iloc[len(merge_fixo)-1]
        merge_fixo['Saldo Tesouro'].iloc[len(merge_fixo)-1] = merge_fixo['Saldo no Tesouro'].iloc[len(merge_fixo)-1]
        merge_fixo.drop(columns=['Saldo no Tesouro', 'Lucro/Prejuízo'], inplace=True)
        spreadsheet_to_income_tax = merge_fixo.to_excel('../raw_data/files_to_ti/spreadsheet_income_tax4.xlsx', index = False)
        return spreadsheet_to_income_tax

if __name__ == "__main__":
    instan_class = SpreadsheetIncomeTax()
    print('opening data')
    df_files = instan_class.get_data_b3()
    print('Arrange features')
    df_files = instan_class.files_featuring_eng()
    print('Selecting fixed_income')
    df_fixedi = instan_class.fixed_income()
    print('Calculate of quantity')
    quantity_prod = instan_class.fixed_income_quantity()
    print('Calculate profit and loss')
    prof_loss_prod = instan_class.fixed_income_prof_loss()
    print('Creating spreadsheet to income tax')
    spreadsheet_to_income_tax = instan_class.fixed_income_b3()