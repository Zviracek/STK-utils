# This script takes exports from database of registered and all competitors.
# From the latter, which contains more informations, filters ids from the former.
# It basicaly works only for this specific use case. 
# The .xlsx and .csv files are under gitignore for obvious reasons.

# This script requires modifications almost every time it is used, 
# cause export formats changes a lot for reasons unknown. 

import pandas as pd

registered = pd.read_excel("Export_Susice.xlsx", index_col='UID')
evid = pd.read_excel('Evidence_Susice.xlsx', index_col='UID')
print(registered )
filtered_cols = ['Věková kategorie', 'Váhová kategorie', 'Pohlaví', 'Jméno', 'Příjmení', 'Klub_x', 'Rok narození', 'ID člena_x']

merged_df = pd.merge(evid, registered, how='inner', left_index=True, right_index=True)
filtered_df = merged_df.loc[merged_df.index.isin(registered.index)]
print(filtered_df)
filtered_df[['Garbage', 'Věková kategorie']] = filtered_df['Věková kategorie_y'].str.rsplit(n=1, expand=True)

filtered_df = filtered_df[filtered_cols]
print(filtered_df)
filtered_df.to_csv('output_Susic_test.csv')