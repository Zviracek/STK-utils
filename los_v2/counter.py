import pandas as pd
import glob
import conf as config

conf = config.readConfig()
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

print('All contestants with null weight: ' + str(count))  
print('') 
frame = pd.concat(zav, axis=0, ignore_index=True)

# Get all clubs
clubs = frame['Klub']
clubs.drop_duplicates(inplace = True)
clubs = clubs.reset_index(drop = True)

# Print number of contestants in clubs
for club in clubs:
    filt = (frame['Klub'] == club)
    df = frame.loc[filt]
    print(str(club) + ': ' + str(len(df.index)))
print('') 

filt = (frame['Váha'] != 0)
frame = frame.loc[filt]

frame.dropna(subset=['Váha'], inplace = True)
frame = frame.reset_index(drop = True)

print('') 
print('') 

print('All contestants without null weight: ' + str(len(frame.index)))  
print('') 

clubs = frame['Klub']
clubs.drop_duplicates(inplace = True)
clubs = clubs.reset_index(drop = True)

# Print number of contestants in clubs
for club in clubs:
    filt = (frame['Klub'] == club)
    df = frame.loc[filt]
    print(str(club) + ': ' + str(len(df.index)))
print('') 