import pandas as pd

df_18 = pd.read_excel("Output/Bol.com_2022-08-18.xlsx")
df_19 = pd.read_excel("Output/Bol.com_2022-08-19.xlsx")
df_22 = pd.read_excel("Output/Bol.com_2022-08-22.xlsx")

test = pd.merge(df_18, df_22[['id', 'stock']], on='id').drop_duplicates(subset='id')

test['delta'] = test['stock_x'] - test['stock_y']
test['delta_value'] = test['delta'].astype('float') * test['price'].str.replace('.-', '').astype('float')
test.sort_values(by='delta_value', ascending=False, inplace=True)



test.delta.isnull().groupby(test['cat_link']).sum().sort_values()

test_1 = df_22.iloc[df_22.duplicated(subset='id').values].sort_values(by='id')

test_1.sort_values(by='id', inplace=True)

test_1.iloc[0].id

test_1[test_1['id'] == 1001004002372629]

len(df_22)

test_1 = test[test['cat3'] == 'Tijdschriften']

cat3_sales = test[test['delta'] > 0].groupby(['cat_link']).sum().sort_values(by='delta_value', ascending=False)
cat3_sales['avg_price'] = cat3_sales['delta_value'] / cat3_sales['delta']

cat_analysis = test[test['cat3'] == 'Bijverwarming']

test_1 = test[test['cat3'] == 'Deurbellen']
cat_analysis

(test.groupby('cat3').max().position < 20) & (test.groupby('cat3').max().position > 2)

test_1 = test[test['cat3'] == 'Accessoires']

{cat:val for (cat, val) in dict(((test.groupby('cat3').max().position < 20) & (test.groupby('cat3').max().position > 2)).items() if val == True}