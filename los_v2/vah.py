# This script manages sparatin of weight categories for all age categories
# For U8 and U10 applies special rules for dynamic weights

import pandas as pd
import glob
import os
import conf as config

conf = config.readConfig()
tab_Kategorie = glob.glob('./Kategorie/*.xlsx')

for kat in tab_Kategorie:
    df = pd.read_excel(kat, index_col=0, header = 0)
    # df.reset_index(inplace=True)
    
    # Throw out empty weights
    filt = (df['Váha'] == 0)
    df = df.drop(df[filt].index)
    df.dropna(subset=['Váha'], inplace=True)
    kat_name = os.path.splitext(os.path.basename(kat))[0]
    df = df.sort_values('Váha', ascending=True)
    df.reset_index(inplace= True, drop= True)

    # Create forlder for saving organized individual weight categories if not already present 
    dir = os.path.join(os.getcwd(), 'Vahy', kat_name)
    if not (os.path.exists(dir) or os.path.isdir(dir)):
        os.mkdir(dir)   
    
    # for U8 and U10 categories we use different algorithm cause we do not have fixed weights
    if kat_name == 'U8' or kat_name == 'U10':
        df['Vah'] = df['Váha'].astype(float)
        df.sort_values('Váha', inplace = True)
        df = df.reset_index(drop=True)
        i = 0
        for x in range(0, len(df.index)):
            vah = float(df.at[x, 'Váha'])
        while i < len(df.index):
            vah = float(df.at[i, 'Váha'])
            
            count = 0
            for j in range(1, 3):
                if i + j >= len(df.index):
                    continue
                #if df.at[i + j, 'Vah'] <= df.at[i, 'Vah'] * 1.1:
                count += 1
             
            #minIndex = df.at[i, 'index']     
            maxWeight = df.at[i + count, 'Váha']   
            #maxIndex = df.at[i + count, 'index']
            list = []
            for y in range(i, i + count + 1):
                list.append(y)
                
            de = df[df.index.isin(list)]
            #de.reset_index(inplace=True)
            
            #filt = (df['index'] >=  minIndex)&(df['index'] <=  maxIndex)
            file = str(maxWeight) + '.xlsx'
            #de = df[filt]
            dir = os.path.join(os.getcwd(), 'Vahy', kat_name, file)
            de.to_excel(dir)
            i += count + 1
        continue 

    #continue
    # load weights for fixed categories from config
    try:
        vahy = conf['vahy'][kat_name]
        vahy = vahy.split(',')
    except KeyError:
        vahy = []
        continue

    # limit makes tolerance when inscribing contestants by exact weight
    limit = float(conf['vahy']['limit'])
    for i in range(0, len(vahy) + 1):
        if(i == 0):
            vah = vahy[i]
            filt = (df['Váha'] <= float(vah)+limit)
            file = vah + '.xlsx'
        elif(i<len(vahy)):
            vah = vahy[i]
            filt = (df['Váha'] <= float(vah)+limit) & (df['Váha'] > float(vahy[i-1])+limit)
            file = vah + '.xlsx'
        else:
            vah = vahy[i-1]
            filt = (df['Váha'] > float(vah)+limit)
            file = '+' + vah + '.xlsx'
            
        de = df[filt]
        de.reset_index(drop=True, inplace=True)
        dir = os.path.join(os.getcwd(), 'Vahy', kat_name, file)
        de.to_excel(dir)

print("Weight separation done")
print('______________________') 
print('') 