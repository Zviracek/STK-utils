import pandas as pd
import glob
import conf as confc

conf = confc.readConfig()
kategorie = conf['kategorie']['kategorie']
kategorie = kategorie.split(',')

tab_Kluby = glob.glob('./Kluby/*.xlsx')

zav = []
# Put all clubs into one list
count = 0
for file in tab_Kluby:
    xls = pd.ExcelFile(file)
    for sheet in xls.sheet_names:
        df = pd.read_excel(file, index_col=None, header = 0, usecols="B,C,D,E,F,G,H", skiprows=range(4), sheet_name=sheet)
        if df.empty:
            continue
        # Filter empty lines and 0 weights
        df.dropna(subset=['Jméno'], inplace = True)
        df = df.reset_index(drop = True)
        
        count += len(df.index)
        zav.append(df)

print('All contestants: ' + str(count))  
print('') 
frame = pd.concat(zav, axis=0, ignore_index=True)

# Add sex field
frame['Pohlavi'] = frame['Kategorie'].astype(str).str[0]

# Export all boys and girls to individual files
filt = (frame['Pohlavi'] == 'U') | (frame['Pohlavi'] == 'M')
boys = frame.loc[filt]
file = './Kluci.xlsx'
filecsv = './Kluci.csv'
boys = boys.sort_values(by='Příjmení')
boys = boys.sort_values(by='Klub')
boys.to_csv(filecsv)
boys.to_excel(file)

filt = (frame['Pohlavi'] == 'F' ) | (frame['Kategorie'] == 'U10')
girls = frame.loc[filt]
file = './Holky.xlsx'
filecsv = './Holky.csv'
girls = girls.sort_values(by='Příjmení')
girls = girls.sort_values(by='Klub')
girls.to_csv(filecsv)
girls.to_excel(file)
