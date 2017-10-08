import re
from subprocess import PIPE, Popen

from .utils import count_pdf_pages, get_line_value, get_content_value
from .summary import make_summary
from .headings import get_font_styles, font_attr

class Diario():
    def __init__(self, PDF_filepath):
        self.PDF = PDF_filepath
        self.encoding = 'Latin1'
        self._pages = None
        self.HEADER_SIZE = 2500

    def __str__(self):
        return 'Diario({})'.format(self.PDF)

    def __repr__(self):
        return 'Diario({})'.format(self.PDF)

    @property
    def page_count(self):
        return count_pdf_pages(self.PDF)

    @property
    def pages(self):
        if self._pages is None:
            self._pages = self.parse_pages()

        return self._pages

    @property
    def summary(self):
        page1 = self.pages[0]
        return make_summary(page1)

    @property
    def fontstyles(self):
        page1 = self.pages[0]
        return get_font_styles(page1)

    def parse_pages(self):
        xml = self.toxml(self.PDF, self.encoding)
        pages = self.get_pages_from_xml(xml)
        pages = [self.remove_page_header(i) for i in pages]
        return pages

    def toxml(self, filepath, encoding, decode=True):
        PDFTOXML = ['pdftohtml', '-xml', '-i', '-stdout', '-enc', encoding,
                    filepath]
        p = Popen(PDFTOXML, stdout=PIPE, stderr=PIPE)
        xml_content, err = p.communicate()

        if decode is True:
            return xml_content.decode(encoding)
        else:
            return xml_content

    def get_pages_from_xml(self, xml):
        delimiter = '</page>'
        pages = [p + delimiter for p in xml.split('</page>')][:-1]
        return pages

    def remove_page_header(self, page):
        header, body = page[:self.HEADER_SIZE], page[self.HEADER_SIZE:]

        PATTERNS = [
            '\n*(<text.*?>)(Ano)\s.*?(o-).*?ISSN.*?ICP-Brasil\.</text>\n*',
            #'\n*<text.*?>N.*?(ICP-Brasil)\.</text>\n*<text.*?>.*?\d{1,3}</text>\n*',
            '<text.*?>(1|3)</text>',
            '<text.*?>(Este documento).*?PÁGINA</text>\n*',
            '<text.*?><i>\d.*?(ICP-Brasil)\.</text>\n*'
            ]

        PATTERN = '|'.join(p for p in PATTERNS)

        clean_header = re.sub(PATTERN, '', header, flags=re.DOTALL)
        return clean_header + body

    def remove_footer(self, page):
        #DOC_ASSINADO = '\n*<text.*?>(Documento)\s(assinado).*?(ICP-Brasil)\.</text>\n*'
        PATTERN = '\n*<text.*?>Este documento.*?\d{17}*.*?ICP-Brasil\.</text>\n*'
        page = re.sub(PATTERN, '', page, flags=re.DOTALL)
        return page

    def find_headers(self, heading):
        headers = []
        for page_number, page in enumerate(self.pages):
            assert len(page.splitlines()) > 0
            lines = [l for l in page.splitlines() if l.strip()]
            last_number = None
            for line_number, line in enumerate(lines):
                font = font_attr(line, 'font')
                if font == self.fontstyles[heading]:
                    if 'Sumário' in line or 'fontspec' in line:
                        continue
                    line_value = get_line_value(line)
                    if headers:
                        if line_number - 1 == last:
                            headers[-1][-1] = headers[-1][-1] + ' ' + line_value
                            last = line_number
                        else:
                            headers.append([page_number, line_number, line_value])
                            last = line_number
                    else:
                        headers.append([page_number, line_number, line_value])
                        last = line_number
        return sorted(headers, key=lambda x: x[0])

    def section_limits(self, section_name):
        headers = self.find_headers('h1')
        start_page, start_line, n = list(filter(lambda x: x[-1] == section_name, headers))[0]
        end_index = headers.index([start_page, start_line, n]) + 1
        end_page, end_line, n = headers[end_index]
        return start_page, start_line, end_page, end_line

    def section_contents(self, section_name):
        start_page, start_line, end_page, end_line = self.section_limits(section_name)
        section_contents = ''
        for index, n in enumerate(range(start_page, end_page + 1)):
            if index == start_page:
                content = '\n'.join(self.pages[n].splitlines()[start_line + 1:])
                section_contents += content
            elif index == end_page:
                content = '\n'.join(self.pages[n].splitlines()[:end_line])
                section_contents += content
            else:
                content = self.pages[n]
                section_contents += content

        lines = section_contents.splitlines()


        return '\n'.join([get_content_value(i) for i in lines])






'''
d = Diario(f'/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS2.pdf')
d.pages[0].splitlines()[45]
d.find_headers('h1')'''
