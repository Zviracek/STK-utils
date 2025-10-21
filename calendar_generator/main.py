import datetime
from datetime import timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Table, SimpleDocTemplate, Spacer, Paragraph, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus.flowables import Flowable
from reportlab.graphics.shapes import Drawing, Rect, String, Group, Line
from collections import defaultdict
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import reportlab.rl_config
import yaml
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

reportlab.rl_config.warnOnMissingFontGlyphs = 0

pdfmetrics.registerFont(TTFont('EncodeSansCondensed', 'EncodeSansCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('EncodeSansCondensedBold', 'EncodeSansCondensed-Bold.ttf'))
pdfmetrics.registerFont(TTFont('RobotoCondensed', 'RobotoCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('RobotoCondensedBold', 'RobotoCondensed-Bold.ttf'))
pdfmetrics.registerFont(TTFont('HelveticaNarrow', 'helvn.ttf'))
pdfmetrics.registerFont(TTFont('HelveticaNarrowBold', 'helvn_b.ttf'))
pdfmetrics.registerFont(TTFont('IBM', 'IBMPlexSansCondensed-Regular.ttf'))
pdfmetrics.registerFont(TTFont('IBMBold', 'IBMPlexSansCondensed-Bold.ttf'))

FONT_NAME = 'RobotoCondensed'
FONT_BOLD_NAME = 'RobotoCondensedBold'
FONT_SIZE = 6

default_style = [
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ('SIZE', (0, 0), (-1, -1), FONT_SIZE),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('LEADING', (0, 0), (-1, -1), 7),
    ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
]

default_par_style = ParagraphStyle(
    'default_style',
    fontName=FONT_NAME,
    fontSize=FONT_SIZE,
    textColor='black',
    alignment=TA_CENTER,
    leading=6
)

# --- small helpers reused by classes ---
class RotatedText(Flowable):
    def __init__(self, text, angle=0):
        super().__init__()
        self.text = text
        self.angle = angle
    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.rotate(self.angle)
        canvas.setFont(FONT_BOLD_NAME, FONT_SIZE)
        canvas.drawCentredString(0, -2, self.text)
        canvas.restoreState()

def create_legend_entry(color, label, square_size=10, font_size=10, text_color="#000000"):
    d = Drawing(square_size * 4, square_size)
    y_offset = (square_size - font_size) / 2 + 1
    d.add(Rect(0, 0, square_size, square_size, fillColor=color, strokeColor=colors.black, strokeWidth=0.25))
    d.add(String(square_size + 5, y_offset, label, fontName=FONT_NAME, fontSize=font_size, fillColor=text_color))
    return d

def create_horizontal_legend(entries, items_per_row=6):
    legend = Drawing(0, 0)
    x_position = -50
    y_position = 0
    for idx, entry in enumerate(entries):
        if len(entry) == 3:
            color, label, text_color = entry
        else:
            color, label = entry
            text_color = "#000000"
        legend_entry = create_legend_entry(color, label, square_size=8, font_size=8, text_color=text_color)
        entry_group = Group(legend_entry)
        entry_group.translate(x_position, y_position)
        legend.add(entry_group)
        legend_length = pdfmetrics.stringWidth(label, FONT_NAME, 8)
        x_position += 10 + 20 + legend_length
        if (idx + 1) % items_per_row == 0:
            x_position = -50
            y_position -= 16
    return legend

# --- config parsing (shared) ---
def parse_config(file='./config.yaml'):
    with open(file, 'r', encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)
    cfg = loaded_data.get('config', {})
    month_dict = cfg.get('month_dict', {})
    cat_to_col_dict = cfg.get('cat_to_col_dict', {})
    origin_raw = cfg.get('origin_dict', {})
    # unify origin entries to (bg, label, text_color)
    def tuple_with_text_color(value):
        if len(value) == 2:
            return (value[0], value[1], "#000000")
        return tuple(value)
    origin_dict = {k: tuple_with_text_color(v) for k, v in origin_raw.items()}
    notes = cfg.get('notes', [])  # expect list of dicts: {lines: n, color: "#...", text: ..." }
    return month_dict, cat_to_col_dict, origin_dict, notes

def parse_data(file='./competitions.yaml'):
    with open(file, 'r', encoding="utf-8") as f:
        loaded = yaml.safe_load(f)
    competitions = []
    for category in loaded.get('competitions', {}):
        competitions += [tuple(item) for item in loaded['competitions'][category]]
    return competitions

# --- Base class ---
class CalendarGenerator:
    def __init__(self, config_file='./config.yaml', data_file='./competitions.yaml'):
        self.config_file = config_file
        self.data_file = data_file
        self.month_dict = {}
        self.cat_to_col_dict = {}
        self.origin_dict = {}
        self.notes = []
        self.events = []
        self.load_config()
        self.load_data()

    def load_config(self):
        self.month_dict, self.cat_to_col_dict, self.origin_dict, self.notes = parse_config(self.config_file)

    def load_data(self):
        try:
            self.events = parse_data(self.data_file)
        except FileNotFoundError:
            self.events = []

    # headers - subclasses may override
    def get_header(self, year):
        # Datum, datum, datum, Muzi, Zeny, MU21, WU21, MU18, WU18, MU16, WU16, MU14, WU14, MU12, WU12, U8 U10, VT SE Skoleni
        return_list = ['Datum', '', '']
        return_list.append(f'Muži\n{year-21} a starší')
        return_list.append(f'Ženy\n{year-21} a starší')
        return_list.append(f'Junioři MU21\n{year-20} až {year-18}')
        return_list.append(f'Juniorky WU21\n{year-20} až {year-18}')
        return_list.append(f'Dorostenci MU18\n{year-17} až {year-16}')
        return_list.append(f'Dorostenky WU18\n{year-17} až {year-16}')
        return_list.append(f'Dorostenci MU16\n{year-15} až {year-14}')
        return_list.append(f'Dorostenky MU16\n{year-15} až {year-14}')
        return_list.append(f'Žáci MU14\n{year-13} až {year-12}')
        return_list.append(f'Žáci MU14\n{year-13} až {year-12}')
        return_list.append(f'Žáci MU12\n{year-11} až {year-10}')
        return_list.append(f'Žáci MU12\n{year-11} až {year-10}')
        return_list.append(f'U10, U8\n{year-9} a mladší')
        return_list.append('VT, školení')
        return return_list

    def get_subheader(self, year):
        return None

    # weekend generator (same as before)
    def generate_weekend_dates(self, start_year, end_date_str):
        weekend_dates = []
        start_date = datetime.date(start_year, 1, 1)
        end_date = datetime.datetime.strptime(f"{start_year}-{end_date_str}", "%Y-%m-%d").date()
        first_saturday = start_date + datetime.timedelta(days=(5 - start_date.weekday()) % 7)
        current_date = first_saturday
        last_month = 0
        while current_date <= end_date:
            saturday = current_date
            sunday = current_date + datetime.timedelta(days=1)
            month = ''
            if saturday.month != last_month:
                month = saturday.month
                last_month = month
            row = [month, saturday.day, sunday.day]
            for i in range(17-3):
                row.append(None)
            weekend_dates.append(row)
            current_date += datetime.timedelta(weeks=1)
        return weekend_dates

    def preprocess_events_with_cats(self, events):
        grouped = defaultdict(lambda: defaultdict(list))
        for rec in events:
            # expected tuple formats: previous versions had multiple variants
            # try to normalize: (date, name, cats, loc, source?, tags?)
            if len(rec) == 5:
                date, name, cats, loc, tags = rec
                source = loc  # older format confusion: keep loc as source for csju logic fallback
            elif len(rec) == 6:
                date, name, cats, loc, source, tags = rec
            else:
                # fallback: ignore
                continue
            comp_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            weekend = self.get_weekend(comp_date)
            for cat in cats:
                grouped[cat][weekend].append((name, loc, tags, cats, source))
        return grouped

    def get_weekend(self, date):
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        start_of_week = date - timedelta(days=date.weekday())
        saturday = start_of_week + timedelta(days=5)
        sunday = start_of_week + timedelta(days=6)
        return saturday, sunday

    # Default mapping: column key is category only
    def keys_for_event(self, event):
        # event is (name, loc, tags, cats, source)
        _, loc, tags, cats, source = event
        keys = []
        for c in cats:
            keys.append(c)
        return keys

    # insert events in a given row by grouping into columns
    def insert_competitions_day(self, comps, data, row_index):
        col_to_comps = defaultdict(list)
        for comp in comps:
            for key in self.keys_for_event(comp):
                col_index = self.cat_to_col_dict.get(key)
                if col_index is not None:
                    col_to_comps[col_index].append(comp)
        for col_index, comps_in_col in col_to_comps.items():
            datas = []
            style = []
            style += default_style
            for i, comp in enumerate(comps_in_col):
                name = comp[0]
                origin = comp[1]
                tags = comp[2]
                cats = comp[3]
                par_style = default_par_style.clone('par_style')
                if len(comps_in_col) > 1:
                    par_style.fontSize -= 1
                bg_color, _, text_color = self.origin_dict.get(origin, (colors.white, '', "#000000"))
                if '?' in (tags or ''):
                    style.append(('BACKGROUND', (0, i), (0, i), bg_color))
                elif 'ost' in (cats or []):
                    style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#ffffff')))
                    par_style.fontSize -= 2
                else:
                    style.append(('BACKGROUND', (0, i), (0, i), bg_color))
                par_style.textColor = text_color
                if 'MU14' in (cats or []) or 'WU14' in (cats or []):
                    if 'Body' in (tags or ''):
                        if col_index == self.cat_to_col_dict.get('MU14') or col_index == self.cat_to_col_dict.get('WU14'):
                            par_style.fontName = FONT_BOLD_NAME
                par = Paragraph(name.encode('UTF-8'), par_style)
                datas.append([par])
            data[row_index][col_index] = Table(
                datas,
                style=style,
                rowHeights=[18.5/len(comps_in_col) for _ in comps_in_col],
                colWidths=[72*0.75]
            )
        return data

    # main insertion pass (two-pass)
    def collect_competition_inserts(self, comp_dict, data):
        inserts = []
        for cat, weekends in comp_dict.items():
            for weekend, events in weekends.items():
                row_index = -1
                start_index = 0
                for i in range(start_index, len(data)):
                    if data[i][0] == weekend[0].month:
                        for j in range(i, i+6):
                            if data[j][1] == weekend[0].day:
                                row_index = j
                                break
                if row_index == -1:
                    raise ValueError(f"No date for competiton found: {cat}, {weekend[1]}")
                inserts.append((row_index, cat, events))
        return inserts

    def apply_competition_inserts(self, inserts, data):
        for row_index, cat, events in inserts:
            # default: insert whole day's events using standard column logic
            data = self.insert_competitions_day(events, data, row_index)
        return data

    # header/footer callbacks
    def header_canvas(self, canvas, doc, version, date_str):
        canvas.saveState()
        canvas.setFont(FONT_NAME, 8)
        canvas.drawString(30, doc.pagesize[1] - 18, f"Verze: {version}")
        canvas.drawRightString(doc.pagesize[0] - 30, doc.pagesize[1] - 18, date_str)
        canvas.restoreState()

    def footer_canvas(self, canvas, doc):
        # default - draw notes lines if configured (draw on all pages in base class)
        canvas.saveState()
        y = 14
        x = 20
        for note in self.notes:
            text = note.get('text', '')
            color = note.get('color', '#000000')
            canvas.setFillColor(colors.HexColor(color))
            canvas.setFont(FONT_NAME, 7)
            canvas.drawString(x, y, text)
            y += 10
        canvas.restoreState()

    # top-level generator
    def generate_pdf(self, output_file, year, version="v1", date_str=None):
        if date_str is None:
            date_str = datetime.datetime.now().strftime('%d.%m.%Y')
        month_dict, cat_to_col_dict, origin_dict, test_comps = get_config_and_data(style_mode)
        header = self.get_header(year)
        subheader = self.get_subheader(year)
        weekends = self.generate_weekend_dates(year, "12-15")
        weekends.insert(0, header)
        if subheader:
            weekends.insert(1, subheader)
        data = weekends
        comp_dict = self.preprocess_events_with_cats(self.events)
        inserts = self.collect_competition_inserts(comp_dict, data)
        data = self.apply_competition_inserts(inserts, data)
        # build table
        style = self.get_style()
        for i in range(len(weekends)):
            if isinstance(weekends[i][0], int):
                weekends[i][0] = RotatedText(month_dict.get(weekends[i][0]).encode('UTF-8'), 90)
                end_index = i-1
                if end_index != -1 and end_index != 0:
                    style.append(('NOSPLIT', (0, start_index), (-1, end_index)))
                    style.append(('LINEBELOW', (0, end_index), (-1, end_index), 1, colors.black))
                    style.append(('SPAN', (0, start_index), (0, end_index)))
                start_index = i
        style.append(('NOSPLIT', (0, start_index), (-1, -1)))
        style.append(('SPAN', (0, start_index), (0, -1)))
        # header style handled by subclass if needed
        if subheader:
            repeat_rows = 2
        else:
            repeat_rows = 1
        coll_widths = [15, 15, 15] + [72*0.75 for _ in range(len(data)-3)]
        row_heights = [20] + [18.5 for _ in range(len(data)-1)]
        wrapped_data = [[cell if isinstance(cell, str) else cell for cell in row] for row in data]
        table = Table(wrapped_data, style=style, colWidths=coll_widths, rowHeights=row_heights, repeatRows=repeat_rows)
        doc = SimpleDocTemplate(output_file, title=f'Kalendář {year}', pagesize=landscape(A4), topMargin=36, bottomMargin=16)
        legend_items = [v for v in self.origin_dict.values()]
        legend = create_horizontal_legend(legend_items)
        elements = [table, Spacer(1, 20), legend]
        # build with header/footer callbacks
        def on_first(canvas, doc):
            self.header_canvas(canvas, doc, version, date_str)
        def on_later(canvas, doc):
            self.header_canvas(canvas, doc, version, date_str)
            self.footer_canvas(canvas, doc)
        doc.build(elements, onFirstPage=on_first, onLaterPages=on_later)
    
    def get_style(self):
        style = [
            ('BOX', (0, 0), (-1, -1), 2, colors.gray),
            ('TOPPADDING', (0, 0), (-1, 0), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ('LEADING', (0, 0), (-1, -1), 7),
        ]
        style.extend(default_style)
        style.extend(self.get_header_style())
        style.extend(self.get_subheader_style() or [])
        return style

    def get_header_style(self):
        style = [
            ('COLBACKGROUNDS', (3, 0), (-3, 0), [colors.aliceblue, colors.mistyrose]),
            ('FONTNAME', (3, 0), (-1, 0), FONT_BOLD_NAME),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('BACKGROUND', (2, 1), (2, -1), colors.whitesmoke),
        ]
        style.append(('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey))
        style.append(('FONTNAME', (0, 0), (-1, 0), FONT_BOLD_NAME))
        return style

    def get_subheader_style(self):
        return None

# --- CSJU subclass overrides minimal behavior ---
class CsjuCalendarGenerator(CalendarGenerator):
    def get_header(self, year):
        # Datum, datum, datum, Muzi, Zeny, MU21, WU21, MU18, WU18, MU16, WU16, MU14, WU14, MU12, WU12, U8 U10, VT SE Skoleni
        return_list = ['Datum', '', '']
        return_list.append(f'Muži\n{year-21} a starší')
        return_list.append('')
        return_list.append(f'Ženy\n{year-21} a starší')
        return_list.append('')
        return_list.append(f'Junioři MU21\n{year-20} až {year-18}')
        return_list.append('')
        return_list.append(f'Juniorky WU21\n{year-20} až {year-18}')
        return_list.append('')
        return_list.append(f'Dorostenci MU18\n{year-17} až {year-16}')
        return_list.append('')
        return_list.append(f'Dorostenky WU18\n{year-17} až {year-16}')
        return_list.append('')
        return_list.append(f'Mladší Dorostenci\nMU16\nStarší žáci MU14\n{year-15} až {year-14}\n{year-13} až {year-12}')
        return_list.append(f'Mladší Dorostenky\nWU16\nStarší žačky WU14\n{year-15} až {year-14}\n{year-13} až {year-12}')
        return_list.append('VT, školení')
        return return_list

    def get_subheader(self, year):
        return_list = ['', '', '']
        for i in range(6):
            return_list.append('CSJU')
            return_list.append('IJF/EJU')
        return_list.append('')
        return_list.append('')
        return_list.append('')
        return return_list

    # keys: prefer combined cat-source except for U14/U16/ost
    def keys_for_event(self, event):
        _, loc, tags, cats, source = event
        keys = []
        for c in cats:
            if "U14" in c or "U16" in c or "ost" in c:
                keys.append(c)
            else:
                keys.append(f"{c}-{source}")
        return keys
    # small tweak: CSJU may want different column widths
    def generate_pdf(self, output_file, year, version="v1", date_str=None):
        # reuse base but adjust coll widths factor for CSJU
        super().generate_pdf(output_file, year, version=version, date_str=date_str)

# --- GUI wiring: instantiate proper class ---
def get_generator_for_mode(mode, competitions_file):
    if mode == 'csju':
        gen = CsjuCalendarGenerator(config_file='./config_csju.yaml', data_file=competitions_file)
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
    ttk.Combobox(frm, textvariable=style_mode_var, values=["csju", "standard"], width=10, state="readonly").grid(column=1, row=0, sticky="ew")
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
