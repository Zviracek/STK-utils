# This scripts take export from database of all competitors and filter out specific IDs.
# Main use case is to filter aditional unregistered competitors, but since our regulations
# requires us to have everyone under registered, its basicaly faster for me to make the changes
# directly over the database. So this script is rarely used.

# This script requires modifications almost every time it is used, 
# cause export formats changes a lot for reasons unknown. 

import pandas as pd
import numpy as np

evid = pd.read_excel('Evidence_09.xlsx', index_col='UID')
ids = []

filtered_cols = ['Věková kategorie', 'Váhová kategorie', 'Pohlaví', 'Jméno', 'Příjmení', 'Klub', 'Rok narození', 'ID člena']

filtered_df = evid.loc[evid['ID člena'].isin(ids)]
filtered_df[['Garbage', 'Věková kategorie']] = filtered_df['Věková kategorie'].str.rsplit(n=1, expand=True)
filtered_df['Váhová kategorie'] = np.nan
filtered_df = filtered_df[filtered_cols]
print(filtered_df)
filtered_df.to_csv('additional_domazlice.csv')