# This script loads exported JSON from Judo Shiai,
# removes duplicates (I prefer to copy competitors when it comes to friendly matches)
# and counts competitors per categories and clubs, as well as number of needed medals

# currently outputs to terminal, consider outputing to file instead
# another consideration, I could extract this from shiai using sql querries (prbly better idea)

# Lot of things are written really badly. 
# I was creating it at hand per parts of what was required at the moment
# and it's sewed together in a way it works. And I cant be bothered rewriting it just now.
# So dont judge me. Or you know what, do.

import pandas as pd
import json
import tkinter as tk
from tkinter import filedialog as fd

root = tk.Tk()
root.withdraw()
root.attributes("-topmost", True)

filename = fd.askopenfilename(title="Vyberte export shiai databáze", filetypes=[("Text Files", "*.txt")])
with open(filename, 'r', encoding="utf8") as f:
    string = f.read()
    
    # Remove 'ISODate(', ')' is it necesarry??
    string = string.replace('ISODate(', '')
    string = string.replace(')', '')

    ff = json.loads(string)
    frame = pd.DataFrame(ff)

with open(fd.asksaveasfilename(parent=root, title="Uložit výsledky to txt souboru", defaultextension=".txt", filetypes=[("Text Files", "*.txt")]), "w", encoding="utf8") as f:
    # Competitors
    print(frame)
    print('Závodníci:', len(frame.index))
    f.write('Závodníci: ' + str(len(frame.index)))

    frame_non_duplicates = frame.drop_duplicates(subset=['id'])
    print('Unikátní závodníci:', len(frame_non_duplicates.index))
    print()
    f.write('\nUnikátní závodníci: ' + str(len(frame_non_duplicates.index)))
    f.write('\n')

    # Clubs
    clubs = frame_non_duplicates['club']
    clubs.drop_duplicates(inplace = True)
    clubs = clubs.reset_index(drop = True)
    print('Kluby:', len(clubs.index))
    print()
    f.write('\nKluby: ' + str(len(clubs.index)))
    f.write('\n')

    print('--Závodníci podle klubů--')
    f.write('\n--Závodníci podle klubů--')
    test_sum = 0
    for club in clubs:
        filt = (frame_non_duplicates['club'] == club)
        competitors = len(frame_non_duplicates.loc[filt].index)
        print(club, ':', competitors)
        f.write('\n' + str(club) + ': ' + str(competitors))
        test_sum += competitors
    print('---')
    print('Kontrolní součet závodníků:', test_sum)
    print()
    f.write('\n')

    # Categories
    print('--Kategorie--')
    f.write('\n--Kategorie--')
    cats = frame_non_duplicates[['category']]
    cats.drop_duplicates(inplace=True)
    cats[['cat', 'weight', 'official']] = cats['category'].str.extract(r'^([A-Z]+\d+)([-+]\d+(?:\,\d+)?)(?:-([A-Z]+))?')
    cats['cat'] = pd.Categorical(cats['cat'], categories=['U8', 'U10', 'MU12', 'WU12', 'MU14', 'WU14', 'MU16', 'WU16', 'MU18', 'WU18'], ordered=True)
    cats['weight'] = cats['weight'].str.replace(',', '.').astype(float).apply(lambda s: (0, -s) if s < 0 else (1, s))
    cats['official'] = cats['official'].fillna('')
    cats = cats.sort_values(by=['cat', 'official', 'weight'])
    cats = cats.reset_index(drop=True)
    cat_stats = pd.DataFrame(0, columns=cats['cat'].drop_duplicates(), index=['sum', 'gold', 'silver', 'bronze'])
    cats = cats['category']

    for cat in cats:
        filt = (frame_non_duplicates['category'] == cat)
        competitors = len(frame_non_duplicates.loc[filt].index)
        if competitors >= 4:
            cnt = 4
        else:
            cnt = competitors
        print(cat, ':', competitors)
        f.write('\n' + str(cat) + ': ' + str(competitors))
        for stat in cat_stats:
            if str(cat).startswith(stat):
                cat_stats.loc['sum', stat] += competitors
                cat_stats.loc['gold', stat] += 1
                if competitors >= 2:
                    cat_stats.loc['silver', stat] += 1
                if 3 <= competitors < 6:
                    cat_stats.loc['bronze', stat] += 1
                if competitors >= 6:
                    cat_stats.loc['bronze', stat] += 2

    print()
    print(cat_stats)
    print('---')
    cat_sum = pd.DataFrame(0, columns=cat_stats.columns, index=cat_stats.index)
    cat_sum.rename(columns=lambda col: col[1:] if str(col[:2]).isalpha() and len(col) > 1 else col, inplace=True)
    cat_sum = cat_sum.loc[:, ~cat_sum.columns.duplicated()]
    for cat in cat_sum:
        for stat in [stat for stat in cat_stats if str(cat) in str(stat)]:
            cat_sum.loc['sum', cat] += cat_stats.loc['sum', stat]
            cat_sum.loc['gold', cat] += cat_stats.loc['gold', stat]
            cat_sum.loc['silver', cat] += cat_stats.loc['silver', stat]
            cat_sum.loc['bronze', cat] += cat_stats.loc['bronze', stat]
    print(cat_sum)
    print('---')
    print('Kontrolní součet závodníků:', cat_stats.loc['sum'].sum())
    print()
    f.writelines(['\n', '\n' + str(cat_stats) + '\n---', '\n' + str(cat_sum), '\n'])

    print('Medaile celkem')
    print('Zlatá:', cat_sum.loc['gold'].sum())
    print('Stříbrná:', cat_sum.loc['silver'].sum())
    print('Bronzová:', cat_sum.loc['bronze'].sum())
    print()
    f.write('\nMedaile celkem')
    f.writelines(['\nZlatá: ' + str(cat_sum.loc['gold'].sum()), '\nStříbrná: ' + str(cat_sum.loc['silver'].sum()), '\nBronzová: ' + str(cat_sum.loc['bronze'].sum()), '\n'])

    # Fees per club
    print('--Startovné--')
    f.write('\n--Startovné--')
    fee = input("Zadejte výši startovného za jednu osobu v Kč: ").strip().split()[0]
    while not fee.isnumeric():
        fee = input("Zadejte výši startovného za jednu osobu v Kč: ").strip()
    fee = int(fee)
    f.write('\nZa jednoho závodníka: ' + str(fee) + ' Kč')
    f.write('\nZa kluby')
    test_sum = 0
    for club in clubs:
        filt = (frame_non_duplicates['club'] == club)
        competitors = len(frame_non_duplicates.loc[filt].index)
        print(club, ':', competitors * fee)
        f.write('\n ' + str(club) + ': ' + str(competitors * fee))
        test_sum += competitors * fee
    print('Kontrolní vybraná částka:', test_sum)
    f.write('\nCelková částka: ' + str(test_sum) + ' Kč')