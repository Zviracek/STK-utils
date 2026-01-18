import datetime
from calendar_generator import CalendarGenerator
from reportlab.lib import colors
from calendar_generator import FONT_NAME, FONT_BOLD_NAME
# --- CSJU subclass overrides minimal behavior ---
class CsjuCalendarGenerator(CalendarGenerator):
    def __init__(self, config_file='./csju_config.yaml', data_file='./competitions.yaml'):
        super().__init__(config_file=config_file, data_file=data_file)
        self.collumn_width = 50  # Adjusted column width for CSJU

    def get_title():
        return "Kalendář soutěží ČSJU"

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

    def get_header_style(self):
        style = [
            ('COLBACKGROUNDS', (3, 0), (-3, 0), [colors.aliceblue, colors.aliceblue, colors.mistyrose, colors.mistyrose]),
            ('FONTNAME', (3, 0), (-1, 0), FONT_BOLD_NAME),
            ('FONTNAME', (0, 0), (-1, -1), FONT_NAME),
            ('BACKGROUND', (2, 2), (2, -1), colors.whitesmoke),
            ('BACKGROUND', (15, 0), (15, 1), colors.aliceblue),
            ('BACKGROUND', (16, 0), (16, 1), colors.mistyrose),
            ('SPAN', (0, 0), (2, 1)),
            ('NOSPLIT', (0, 0), (2, 1)),
            ('BOX', (0, 0), (-1, -1), 2, colors.gray),
        ]
        for i in range(3, 21, 2):
            style.append(('LINEBEFORE', (i, 0), (i, -1), 1.5, colors.gray))
        for i in range(3, 16, 2):
            style.append(('SPAN', (i, 0), (i+1, 0)))
        style.append(('SPAN', (15, 0), (15, 1)))
        style.append(('SPAN', (16, 0), (16, 1)))
        style.append(('SPAN', (17, 0), (17, 1)))
        style.append(('LINEBEFORE', (-1, 0), (-1, -1), 1.5, colors.gray))
        style.append(('LINEBELOW', (0, 1), (-1, 1), 1.5, colors.gray))
        #style.append(('BACKGROUND', (0, 0), (2, 0), colors.lightgrey))
        style.append(('FONTNAME', (0, 0), (-1, 0), FONT_BOLD_NAME))
        return style
    # small tweak: CSJU may want different column widths
    def generate_pdf(self, output_file, year, version="v1", date_str=None):
        # reuse base but adjust coll widths factor for CSJU
        super().generate_pdf(output_file, year, version=version, date_str=date_str)