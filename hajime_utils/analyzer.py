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

filename = fd.askopenfilename(title="Vyberte export hajime databáze", filetypes=[("Excel Files", "*.xlsx")])
frame = pd.read_excel(filename, header=None)
frame.columns = ["id", "first", "last", "year of birth", "club", "country", "cat", "age", "weight", "weight_in"]

with open(fd.asksaveasfilename(parent=root, title="Uložit výsledky to txt souboru", defaultextension=".txt", filetypes=[("Text Files", "*.txt")]), "w", encoding="utf8") as f:
    # Competitors
    print('Závodníci:', len(frame.index))
    f.write('Závodníci: ' + str(len(frame.index)))

    frame_non_duplicates = frame.drop_duplicates(subset=['id'])

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
    grouped = (
        frame_non_duplicates
        .assign(
            cat_code=lambda df: df['age'].str.extract(r'(MU\d+|WU\d+|U\d+)')[0],
        )
        .groupby(['cat_code', 'cat'])
        .size()
        .reset_index(name='competitors')
    )

    def medals(n):
        if n == 1:
            return (1, 0, 0)
        elif n == 2:
            return (1, 1, 0)
        elif n < 6:
            return (1, 1, 1)
        else:
            return (1, 1, 2)

    vals = grouped['competitors'].apply(medals)

    grouped[['gold', 'silver', 'bronze']] = pd.DataFrame(
        grouped['competitors'].apply(medals).tolist(),
        index=grouped.index
    )

    print()
    competitors_by_cat = grouped.groupby('cat_code')['competitors'].sum()

    print(competitors_by_cat)
    print('---')

    cat_sum = (
        grouped
        .groupby('cat')[['competitors', 'gold', 'silver', 'bronze']]
        .sum()
    )

    print('Kontrolní součet závodníků:', competitors_by_cat.sum())
    print()
    f.write('\nGrouped:\n')
    f.write(grouped.to_string())
    f.write('\n---\n')

    f.write('\nSummary (by weight):\n')
    f.write(cat_sum.to_string())
    f.write('\n')

    print('Medaile celkem')
    print('Zlatá:', cat_sum['gold'].sum())
    print('Stříbrná:', cat_sum['silver'].sum())
    print('Bronzová:', cat_sum['bronze'].sum())
    print()

    f.write('\nMedaile celkem')
    f.writelines([
        '\nZlatá: ' + str(cat_sum['gold'].sum()),
        '\nStříbrná: ' + str(cat_sum['silver'].sum()),
        '\nBronzová: ' + str(cat_sum['bronze'].sum()),
        '\n'
    ])
    # Fees per club
    print('--Startovné--')
    f.write('\n--Startovné--')
    fee = input("Zadejte výši startovného za jednu osobu v Kč: ").strip().split()[0]
    while not fee.isnumeric():
        fee = input("Zadejte výši startovného za jednu osobu v Kč: ").strip()
    fee = int(fee)
    print()
    f.write('\nZa jednoho závodníka: ' + str(fee) + ' Kč')
    f.write('\nZa kluby')
    test_sum = 0
    for club in clubs:
        filt = (frame_non_duplicates['club'] == club)
        competitors = len(frame_non_duplicates.loc[filt].index)
        print(club, ':', competitors * fee)
        f.write('\n ' + str(club) + ': ' + str(competitors * fee))
        test_sum += competitors * fee
    print('--')
    print('Kontrolní vybraná částka:', test_sum)
    f.write('\nCelková částka: ' + str(test_sum) + ' Kč')