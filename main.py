import logging
import os

import openpyxl
import pandas as pd
from openpyxl.worksheet.table import TableStyleInfo, Table
from openpyxl.worksheet.worksheet import Worksheet
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings

from financial.spiders.fca import FcaSpider

logger = logging.getLogger(__name__)


def prettify_excel_file(excel_file: str):
    workbook = openpyxl.load_workbook(excel_file)
    set_table_style(workbook.active, 'active_table')
    auto_fit_columns(workbook.active)
    workbook.save(excel_file)
    workbook.close()


def auto_fit_columns(worksheet: Worksheet):
    for column_cells in worksheet.columns:
        max_length = max(len(str(cell.value)) for cell in column_cells)
        min_length = len(column_cells[0].value) + 5
        worksheet.column_dimensions[column_cells[0].column_letter].width = max(min_length, max_length)


def set_table_style(worksheet: Worksheet, table_name: str, table_style: str = 'TableStyleLight16'):
    table_style = TableStyleInfo(name=table_style,
                                 showFirstColumn=False,
                                 showLastColumn=False,
                                 showRowStripes=True,
                                 showColumnStripes=False)
    worksheet.freeze_panes = 'A2'
    table = Table(displayName=table_name, ref=worksheet.dimensions)
    table.tableStyleInfo = table_style
    worksheet.add_table(table)


def main():
    keywords = {
        'https://register.fca.org.uk/s/search?q=pension&type=Companies&sortby=status': '420',
        'https://register.fca.org.uk/s/search?q=health&type=Companies&sortby=status': '780',
        'https://register.fca.org.uk/s/search?q=credit&type=Companies&sortby=status': '920',
        'https://register.fca.org.uk/s/search?q=IFA&type=Companies&sortby=status': '440',
        'https://register.fca.org.uk/s/search?q=advisor&type=Companies&sortby=status': '840',
        'https://register.fca.org.uk/s/search?q=broker&type=Companies&sortby=status': '1520',
        'https://register.fca.org.uk/s/search?q=will&type=Companies&sortby=status': '860',
        'https://register.fca.org.uk/s/search?q=funeral&type=Companies&sortby=status': '1160',
    }

    configure_logging()
    settings = get_project_settings()

    if settings.get('HTTP_PROXY'):
        os.environ.setdefault('HTTP_PROXY', settings.get('HTTP_PROXY'))
        os.environ.setdefault('HTTPS_PROXY', settings.get('HTTP_PROXY'))

    process = CrawlerProcess(settings, install_root_handler=False)
    process.crawl(FcaSpider, keywords_list=keywords, max_pages=5)
    process.start(install_signal_handlers=True)

    df = pd.read_csv('data.csv')

    for keyword in df['keyword'].unique():
        filtered_records = df[df['keyword'] == keyword]
        filtered_records.to_csv(f'{keyword}.csv', index=False)

if __name__ == '__main__':
    main()
