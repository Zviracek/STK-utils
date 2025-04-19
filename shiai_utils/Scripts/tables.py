import json
import pandas as pd
import pymupdf as pm
import tkinter as tk
from tkinter import filedialog as fd
import os

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
print(frame)

# Find mistakes in club names (too long names are sometimes cut) and replace them with correct name (if present in the data)
clubs = frame['club'].drop_duplicates()
for club in clubs:
    for club2 in clubs:
        if club in club2 and club != club2:
            frame.loc[frame['club'] == club, 'club'] = club2

clubs = pd.DataFrame({club: [[]] for club in frame['club'].drop_duplicates()})

filename = fd.askopenfilename(title="Vyberte export tabulek", filetypes=[("PDF Files", "*.pdf")])
with pm.open(filename) as pdf:
    # Find every weight category for each club
    # Save category table page number from original pdf file
    for i, page in enumerate(pdf):
        text_lines = page.get_text()
        for club in clubs.columns:
            if club in text_lines:
                clubs.at[0, club].append(i)
    print(clubs.T)

    # Copy all pages of each category related to the club one after another
    # The tables for each club are sorted according to the original table export
    # At the top of each page add the name of the club for which the table is for
    file = pm.open()
    for club in clubs:
        for page in clubs.at[0, club]:
            file.insert_pdf(pdf, from_page=page, to_page=page)
            new_page = file[-1]

            fontname="roboto"
            script_dir = os.path.dirname(os.path.abspath(__file__))
            fontfile=os.path.join(script_dir, "fonts/Roboto/Roboto-Regular.ttf")
            new_page.insert_font(fontname=fontname, fontfile=fontfile)
            
            fontsize = 25
            left_margin = 10

            page_width = new_page.rect.width
            text_width = pm.Font(fontfile=fontfile).text_length(club, fontsize=fontsize)
            if text_width < page_width - 2 * left_margin:
                x = (page_width - text_width) / 2
            else:
                x = left_margin

            new_page.insert_text(
                pm.Point(x, 30),
                club,
                fontname=fontname,
                fontsize=fontsize,
                color=(0,0,0),
                overlay=True)
    file.save(fd.asksaveasfilename(parent=root, title="Uložit klubové tabulky jako PDF", defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")]))
    file.close()