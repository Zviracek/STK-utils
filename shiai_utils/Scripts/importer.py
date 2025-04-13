# This script takes exports from database of registered and all competitors.
# From the latter, which contains more informations, filters ids from the former.
# It basicaly works only for this specific use case. 
# The .xlsx and .csv files are under gitignore for obvious reasons.

# This script requires modifications almost every time it is used, 
# cause export formats changes a lot for reasons unknown.

import pandas as pd
import tkinter as tk
from tkinter import filedialog as fd

def get_filters():
    use_default_filters = input("Použít defaultní filtry (Věková kat, Váhová kat, Pohlaví, Jméno, Přijímení, Klub, Rok narození, ID člena)?\n-> Y,y / N,n: ").strip()
    if (use_default_filters not in ['Y', 'y', 'N', 'n']):
        get_filters()
    elif (use_default_filters in ['Y', 'y']):
        return ['Věková kategorie', 'Váhová kategorie', 'Pohlaví', 'Jméno', 'Příjmení', 'Klub_x', 'Rok narození', 'ID člena_x']
    else:
        filters = input("Zadejte požadované filtry ve formátu: 'filtr1', 'filtr2', ...: ").split(",")
        i = 0
        while i < len(filters):
            filters[i] = filters[i].strip()
            i+=1
        return filters

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

# Get registered competitors
filename = fd.askopenfilename(title="Vyberte export přihlášených závodníků", filetypes=[("Excel Files", "*.xlsx *.xls")])
registered = pd.read_excel(filename, index_col='UID')
print(registered)

# Get competitors from evidence
filename = fd.askopenfilename(title="Vyberte export všech závodníků", filetypes=[("Excel Files", "*.xlsx *.xls")])
evid = pd.read_excel(filename, index_col='UID')
filtered_cols = get_filters()
print(filtered_cols)

# Create one DF with information according to file with registered competitors
# Split age category column to long name and shortcut
merged_df = pd.merge(evid, registered, how='inner', left_index=True, right_index=True)
filtered_df = merged_df.loc[merged_df.index.isin(registered.index)]
print(filtered_df)
filtered_df[['Garbage', 'Věková kategorie']] = filtered_df['Věková kategorie_y'].str.rsplit(n=1, expand=True)

# Filter information according to filters set by user
# Save DF to file
filtered_df = filtered_df[filtered_cols]
print(filtered_df)
filtered_df.to_csv(fd.asksaveasfilename(parent=root, title="Uložit import závodníků jako CSV", defaultextension=".csv", filetypes=[("CSV files", "*.csv")]))