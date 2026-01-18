import datetime
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import reportlab.rl_config
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from calendar_generator import CalendarGenerator
from csju_calendar_generator import CsjuCalendarGenerator
from jcpl_calendar_generator import JcplCalendarGenerator

reportlab.rl_config.warnOnMissingFontGlyphs = 0

pdfmetrics.registerFont(TTFont('EncodeSansCondensed', 'EncodeSansCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('EncodeSansCondensedBold', 'EncodeSansCondensed-Bold.ttf'))
pdfmetrics.registerFont(TTFont('RobotoCondensed', 'RobotoCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('RobotoCondensedBold', 'RobotoCondensed-Bold.ttf'))
pdfmetrics.registerFont(TTFont('HelveticaNarrow', 'helvn.ttf'))
pdfmetrics.registerFont(TTFont('HelveticaNarrowBold', 'helvn_b.ttf'))
pdfmetrics.registerFont(TTFont('IBM', 'IBMPlexSansCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('IBMBold', 'IBMPlexSansCondensed-Bold.ttf'))


# --- GUI wiring: instantiate proper class ---
def get_generator_for_mode(mode, competitions_file):
    if mode == 'csju':
        gen = CsjuCalendarGenerator(config_file='./config_csju.yaml', data_file=competitions_file)
    elif mode == 'JCPL':
        gen = JcplCalendarGenerator(config_file='./config_jcpl.yaml', data_file=competitions_file)
    else:
        gen = CalendarGenerator(config_file='./config.yaml', data_file=competitions_file)
    return gen

# ...existing GUI code adjusted to call new classes...
def run_gui():
    def select_competitions_file():
        file_path = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")])
        if file_path:
            competitions_file_var.set(file_path)
    def select_output_file():
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        return file_path
    root = tk.Tk()
    root.title("Judo Calendar Generator")
    frm = ttk.Frame(root, padding=10); frm.grid()
    ttk.Label(frm, text="Mode:").grid(column=0, row=0, sticky="w")
    style_mode_var = tk.StringVar(value="csju")
    ttk.Combobox(frm, textvariable=style_mode_var, values=["csju", "ksju PK", "JCPL"], width=10, state="readonly").grid(column=1, row=0, sticky="ew")
    ttk.Label(frm, text="Competitions YAML:").grid(column=0, row=1, sticky="w")
    competitions_file_var = tk.StringVar(value="./competitions.yaml")
    ttk.Entry(frm, textvariable=competitions_file_var, width=40).grid(column=1, row=1, sticky="ew")
    ttk.Button(frm, text="Browse...", command=select_competitions_file).grid(column=2, row=1, sticky="ew")
    ttk.Label(frm, text="Version:").grid(column=0, row=2, sticky="w")
    version_var = tk.StringVar(value="v1"); ttk.Entry(frm, textvariable=version_var, width=10).grid(column=1, row=2, sticky="ew")
    ttk.Label(frm, text="Year:").grid(column=0, row=3, sticky="w")
    year_var = tk.StringVar(value=str(datetime.datetime.now().year)); ttk.Entry(frm, textvariable=year_var, width=10).grid(column=1, row=3, sticky="ew")
    ttk.Label(frm, text="Date:").grid(column=0, row=4, sticky="w")
    date_var = tk.StringVar(value=datetime.datetime.now().strftime('%d.%m.%Y')); ttk.Entry(frm, textvariable=date_var, width=15).grid(column=1, row=4, sticky="ew")
    def on_generate():
        mode = style_mode_var.get()
        comp_file = competitions_file_var.get()
        version = version_var.get()
        year = int(year_var.get())
        date_str = date_var.get()
        output = select_output_file()
        if not output:
            return
        gen = get_generator_for_mode(mode, comp_file)
        gen.generate_pdf(output, year, version=version, date_str=date_str)
    ttk.Button(frm, text="Generate PDF", command=on_generate).grid(column=0, row=5, columnspan=3, pady=10)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
