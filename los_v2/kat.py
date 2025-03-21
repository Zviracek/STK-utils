# This script puts all contestants into one file and than separates them into idividual age catagories

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
        df = pd.read_excel(file, index_col=None, header = 0, usecols="B,C,D,E", skiprows=range(9), sheet_name=sheet)
        if df.empty:
            continue
        weightName = 'Váha'    
        # Filter empty lines and 0 weights
        filt = (df[weightName] == '0')
        df = df.drop(df[filt].index)
        filt = (df[weightName] == 'nevyplňovat')
        df = df.drop(df[filt].index)
        df.dropna(subset=[weightName], inplace = True)
        df = df.reset_index(drop = True)
        
        count += len(df.index)
        zav.append(df)

print('All contestants: ' + str(count))  
print('') 
    
# Create data frame from our list and drop empty rows    
frame = pd.concat(zav, axis=0, ignore_index=True)
#frame.dropna(subset=['Příjmení a jméno'], inplace=True)


# Spliting name
#frame[['Prijmeni', 'Jmeno']] = frame['Příjmení, jméno'].str.split(pat = ' ', n = 1, expand=True)
frame[['Příjmení', 'Jméno']] = frame['Příjmení, jméno'].str.split(pat = ' ', n = 1, expand=True)
#frame.rename(columns = {'Ročník':'Vek', 'Váha':'Vah'}, inplace = True)

# Filter out NaN weights and create new table for all contestants without empty weights
# No longer needed, done beforehand
#frame.dropna(subset=['Vah'], inplace=True)
#frame = frame.reset_index(drop = True)
#filt = (frame['Vah'] == 0)
#all = frame.drop(frame[filt].index)
#all = all.reset_index(drop = True)
#filt = (frame['Vah'] == 'nevyplňovat')
#all = frame.drop(frame[filt].index)
#all = all.reset_index(drop = True)

# split catagories into their own files
for kat in kategorie:
    kat_alt = 'M' + kat
        
    filt = (frame['Kategorie'] == kat) | (frame['Kategorie'] == kat_alt)
    df = frame.loc[filt]
    file = './Kategorie/%s.xlsx' %kat
    df.to_excel(file)


# Get all clubs
clubs = frame['Klub']
clubs.drop_duplicates(inplace = True)
clubs = clubs.reset_index(drop = True)

# Print number of contestants in clubs
for club in clubs:
    filt = (frame['Klub'] == club)
    df = frame.loc[filt]
    print(club + ': ' + str(len(df.index)))
print('') 

# Export all contestants to file    
file = './Vsichni.xlsx'
frame.to_excel(file)

print("Age separation done")
print('___________________') 
print('') 