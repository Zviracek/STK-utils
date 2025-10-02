import datetime
from datetime import timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import Table, SimpleDocTemplate, Spacer, Paragraph
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
# FONT_BOLD_NAME = 'DejaVuSansBold'

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


def parse_config(file='./config.yaml'):
    with open(file, 'r', encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)
        # print(loaded_data)
        month_dict = loaded_data['config']['month_dict']
        cat_to_col_dict = loaded_data['config']['cat_to_col_dict']
        origin_dict = {
            key: tuple(value) for key, value in loaded_data['config']['origin_dict'].items()
        }
    return month_dict, cat_to_col_dict, origin_dict


[month_dict, cat_to_col_dict, origin_dict] = parse_config()

def parse_data(file='./competitions.yaml'):
    with open(file, 'r', encoding="utf-8") as f:
        loaded_data = yaml.safe_load(f)

        competitions = []
        for category in loaded_data['competitions']:
            competitions = competitions + [tuple(item) for item in loaded_data['competitions'][category]]

        return competitions


test_comps = parse_data()


class RotatedText(Flowable):
    """
    A Flowable for rotated text inside a table cell.
    """

    def __init__(self, text, angle=0):
        super().__init__()
        self.text = text
        self.angle = angle

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        # Move to the center of the cell
        canvas.translate(0, 0)
        # Rotate text
        canvas.rotate(self.angle)
        # Draw centered text
        canvas.setFont(FONT_BOLD_NAME, FONT_SIZE)
        canvas.drawCentredString(0, -2, self.text)
        canvas.restoreState()


def generate_weekend_dates(start_year, end_date_str):
    weekend_dates = []
    # Start with the first day of the year
    start_date = datetime.date(start_year, 1, 1)

    # Parse the end date string without the year (e.g., "12-15")
    end_date = datetime.datetime.strptime(f"{start_year}-{end_date_str}", "%Y-%m-%d").date()

    # Ensure the end date is within the specified year
    if end_date.year != start_year:
        raise ValueError("End date must be within the specified start year.")

    # Find the first Saturday of the year
    first_saturday = start_date + datetime.timedelta(days=(5 - start_date.weekday()) % 7)

    # Iterate through the year, adding Saturdays and Sundays
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


def generate_header(year):
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

def generate_header_csju(year):
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
    return_list.append(f'Mladší Dorostenci MU16\nStarší žáci MU14\n{year-15} až {year-14}\n{year-13} až {year-12}')
    return_list.append(f'Mladší Dorostenky MU16\nStarší žačky MU14\n{year-15} až {year-14}\n{year-13} až {year-12}')
    return_list.append('VT, školení')
    return return_list

def genereate_subheader_csju():
    return_list = ['', '', '']
    for i in range(6):
        return_list.append('CSJU')
        return_list.append('IJF/EJU')
    return_list.append('')
    return_list.append('')
    return_list.append('')
    return return_list

def generate_pdf():
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'NotoSans'
    #header = generate_header(2025)
    header = generate_header_csju(2025)
    weekends = generate_weekend_dates(2025, "12-15")
    weekends.insert(0, header)
    
    # pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    # pdfmetrics.registerFont(TTFont('DejaVuSansBold', 'DejaVuSans-Bold.ttf'))
    style = [
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('SIZE', (0, 0), (-1, -1), FONT_SIZE),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 2, colors.gray),
        ('BOX', (0, 0), (-1, 0), 2, colors.gray),
        ('BOX', (0, 0), (2, -1), 2, colors.gray),
        ('TOPPADDING', (0, 0), (-1, 0), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('COLBACKGROUNDS', (3, 0), (-3, 0), [colors.aliceblue, colors.mistyrose]),
        ('FONTNAME', (3, 0), (-1, 0), FONT_BOLD_NAME),
        ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
        ('BACKGROUND', (2, 1), (2, -1), colors.whitesmoke),
        ('LEADING', (0, 0), (-1, -1), 7),
    ]

    subheader = genereate_subheader_csju()
    weekends.insert(1, subheader)
    #print(weekends)
    data = weekends
    comp_dict = preprocess_events_with_cats(test_comps)
    data = insert_competitions(comp_dict, data)

    

    weekends = data
    start_index = 0
    end_index = 0
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

    #ss
    set_header_style_csju(header, style)

    coll_widths = [15, 15, 15]
    for i in range(len(weekends)-3):
        coll_widths.append(72*0.75)

    row_heights = [20]
    for i in range(len(weekends)-1):
        row_heights.append(18.5)

    wrapped_data = [
        [cell if isinstance(cell, str) else cell for cell in row] for row in weekends
    ]

    table = Table(
        wrapped_data,
        style=style,
        colWidths=coll_widths,
        rowHeights=row_heights,
        repeatRows=1
    )

    doc = SimpleDocTemplate("output.pdf", title='Kalendář KSJu PK 2025', pagesize=landscape(A4), topMargin=36, bottomMargin=36)
    # doc.build([table])


# Create legend entries
    legend_items = []
    for key in origin_dict.keys():
        legend_items.append(origin_dict.get(key))

# Build the document
    legend = create_horizontal_legend(legend_items)

# Build the document
    elements = [table, Spacer(1, 20), legend]  # Add the table, space, and legend
    # print(weekends)
    doc.build(elements)

def set_header_style(header, style):
    for i in range(3, len(header)):
        if i % 2 == 1 or i == len(header) - 1:
            style.append(('LINEBEFORE', (i, 0), (i, -1), 0.75, colors.black))
    style.append(('COLBACKGROUNDS', (3, 0), (-3, 0), [colors.aliceblue, colors.mistyrose]))
    style.append(('SPAN', (0, 0), (2, 0)))

def set_header_style_csju(header, style):
    for i in range(3, len(header)):
        if i % 2 == 1 or i == len(header) - 1:
            style.append(('LINEBEFORE', (i, 0), (i, -1), 0.75, colors.black))
    for i in range(3, len(header)):
        if i % 2 == 1 and i < len(header) - 3:
            style.append(('SPAN', (i, 0), (i+1, 0)))
    style.append(('COLBACKGROUNDS', (3, 0), (-2, 0), [colors.aliceblue, colors.aliceblue, colors.mistyrose, colors.mistyrose]))
    style.append(('SPAN', (0, 0), (2, 1)))


def create_legend_entry(color, label, square_size=10, font_size=10):
    d = Drawing(square_size * 4, square_size)  # Adjust drawing size to fit the legend item
    y_offset = (square_size - font_size) / 2 + 1  # Center text vertically relative to the square

    d.add(Rect(0, 0, square_size, square_size, fillColor=color, strokeColor=colors.black, strokeWidth=0.25))
    # d.add(Rect(0, 0, square_size, square_size, fillColor=color, strokeColor=colors.black))
    d.add(String(square_size + 5, y_offset, label, fontName=FONT_NAME, fontSize=font_size, fillColor=colors.black))
    return d


def create_horizontal_legend(entries):
    legend = Drawing(0, 0)  # Create a base drawing for the legend
    x_position = -50          # Start position for placing entries

    for color, label in entries:
        # Add each legend entry at the calculated position
        entry = create_legend_entry(color, label, square_size=8, font_size=8)
        entry_group = Group(entry)
        entry_group.translate(x_position, 0)  # Shift the entry horizontally
        legend.add(entry_group)
        # Update the position for the next entry
        legend_length = pdfmetrics.stringWidth(label, FONT_NAME, 8)
        # x_position += 10 + 10 + len(label)*3.5  # Add spacing between entries
        x_position += 10 + 20 + legend_length  # Add spacing between entries

    return legend

def insert_competitions_day_csju(comps, data, col_index, row_index):
    datas = []
    style = []
    style += default_style
    for i in range(len(comps)):
        comp = comps[i]

        origin = comp[1]
        tags = comp[2]
        name = comp[0]
        cats = comp[3]
        par_style = default_par_style.clone('par_style')
        if len(comps) > 1:
            par_style.fontSize -= 1
        # datas.append([name.encode('UTF-8')])
        if '?' in tags:
            # datas.append([create_hatching_with_text(72*0.75, 18.5/len(comps), name, line_color=origin_dict.get(origin)[0])])
            style.append(('BACKGROUND', (0, i), (0, i), origin_dict.get(origin)[0]))
        elif 'ost' in cats:
            style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#ffffff')))
            par_style.fontSize -= 2
        else:
            style.append(('BACKGROUND', (0, i), (0, i), origin_dict.get(origin)[0]))

        if 'MU14' in cats or 'WU14' in cats:
            if 'Body' in tags:
                if col_index == cat_to_col_dict.get('MU14') or col_index == cat_to_col_dict.get('WU14'):
                    par_style.fontName = FONT_BOLD_NAME
                    # par = Paragraph(str('<u>') + name + str('</u>'), par_style)
                    # style.append(('FONTNAME', (0, i), (0, i), FONT_BOLD_NAME))
                    # style.append(('UNDERLINE', (0, i), (0, i), 1))

        par = Paragraph(name.encode('UTF-8'), par_style)
        datas.append([par])
    data[row_index][col_index] = Table(
        datas,
        style=style,
        rowHeights=[18.5/len(comps) for c in comps],
        colWidths=[72*0.75]
    )
    return data
    
def insert_competitions_day(comps, data, col_index, row_index):
    datas = []
    style = []
    style += default_style
    for i in range(len(comps)):
        comp = comps[i]

        origin = comp[1]
        tags = comp[2]
        name = comp[0]
        cats = comp[3]
        par_style = default_par_style.clone('par_style')
        if len(comps) > 1:
            par_style.fontSize -= 1
        # datas.append([name.encode('UTF-8')])
        if '?' in tags:
            # datas.append([create_hatching_with_text(72*0.75, 18.5/len(comps), name, line_color=origin_dict.get(origin)[0])])
            style.append(('BACKGROUND', (0, i), (0, i), origin_dict.get(origin)[0]))
        elif 'ost' in cats:
            style.append(('BACKGROUND', (0, i), (0, i), colors.HexColor('#ffffff')))
            par_style.fontSize -= 2
        else:
            style.append(('BACKGROUND', (0, i), (0, i), origin_dict.get(origin)[0]))

        if 'MU14' in cats or 'WU14' in cats:
            if 'Body' in tags:
                if col_index == cat_to_col_dict.get('MU14') or col_index == cat_to_col_dict.get('WU14'):
                    par_style.fontName = FONT_BOLD_NAME
                    # par = Paragraph(str('<u>') + name + str('</u>'), par_style)
                    # style.append(('FONTNAME', (0, i), (0, i), FONT_BOLD_NAME))
                    # style.append(('UNDERLINE', (0, i), (0, i), 1))

        par = Paragraph(name.encode('UTF-8'), par_style)
        datas.append([par])
    data[row_index][col_index] = Table(
        datas,
        style=style,
        rowHeights=[18.5/len(comps) for c in comps],
        colWidths=[72*0.75]
    )
    return data

def insert_competitions(comp_dict, data):
    style = []
    for cat, weekends in comp_dict.items():
        col_index = cat_to_col_dict.get(cat)
        for weekend, events in weekends.items():
            # print(weekend)
            if len(events) > 2:
                print(f"More than 2 duplicate values not yet implemented, unexpected behaviour: {cat}, {weekend[1]}")
            row_index = -1
            # true if CSJU
            start_index = 0
            if True:
                start_index = 2
            for i in range(start_index, len(data)):
                #print(data[i][0])
                if data[i][0] == weekend[0].month:
                    for j in range(i, i+6):
                        if data[j][1] == weekend[0].day:
                            # uz konecne mame weekend
                            row_index = j
                            break
            if row_index == -1:
                raise ValueError(f"No date for competiton found: {cat}, {weekend[1]}")
            else:
                data = insert_competitions_day(events, data, col_index, row_index)

    return data


def parse_datetime(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d")


def get_weekend(date):
    """
    Given a date, return a tuple of weekend days (Saturday and Sunday) for the week the date belongs to.

    Parameters:
    - date (datetime or str): The input date, either as a datetime object or a string in 'YYYY-MM-DD' format.

    Returns:
    - tuple: A tuple of two datetime.date objects representing the Saturday and Sunday of the week.
    """
    if isinstance(date, str):
        date = datetime.strptime(date, "%Y-%m-%d").date()

    # Find the start of the week (Monday)
    start_of_week = date - timedelta(days=date.weekday())

    # Calculate Saturday and Sunday
    saturday = start_of_week + timedelta(days=5)
    sunday = start_of_week + timedelta(days=6)

    return saturday, sunday

def get_weekend_old(date):
    saturday = date - timedelta(days=date.weekday() + 2)  # Adjust to Saturday
    sunday = saturday + timedelta(days=1)
    return (saturday.date(), sunday.date())


def preprocess_events_with_cats(events):
    grouped_by_cats = defaultdict(lambda: defaultdict(list))

    for date, name, cats, loc, tags in events:
        comp_date = parse_datetime(date)
        weekend = get_weekend(comp_date)
        for cat in cats:  # Handle multi-tag events
            grouped_by_cats[cat][weekend].append((name, loc, tags, cats))

    return grouped_by_cats

def create_hatching_with_text(width, height, text, spacing=5, line_color=colors.grey, font_size=12):
    d = Drawing(width, height)

    # Draw the hatching pattern
    for x in range(0, int(width) + int(height), spacing):
        d.add(Line(x, 0, x - height, height, strokeColor=line_color, strokeWidth=0.5))
    for x in range(0, int(width) + int(height), spacing):
        d.add(Line(x - width, 0, x, height, strokeColor=line_color, strokeWidth=0.5))

    # Add the text on top, centered
    text_element = String(
        width / 2, height / 2,
        text,
        textAnchor="middle",
        fontSize=font_size,
        fillColor=colors.black
    )
    d.add(text_element)

    return d

generate_pdf()
