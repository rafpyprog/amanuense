import re
from subprocess import PIPE, Popen

from .utils import count_pdf_pages, get_line_value
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
        for page in self.pages:
            assert len(page.splitlines()) > 0
            lines = [l for l in page.splitlines() if l.strip().startswith('<text')]
            for n, line in enumerate(lines):
                font = font_attr(line, 'font')
                if font == self.fontstyles[heading]:
                    line_value = get_line_value(line)
                    if line_value == 'Sumário':
                        continue
                    if headers:
                        if n - 1 == last:
                            headers[-1][1] = headers[-1][1] + ' ' + line_value
                        else:
                            headers.append([n, line_value])
                    else:
                        headers.append([n, line_value])
                    last = n
        return sorted(headers, key=lambda x: x[0])




'''
def serialize_pages(n):
    import json
    d = Diario(f'/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS{n}.pdf')
    j = json.dumps(d.pages)
    with open(f'dou{n}.pages', 'w') as f:
        f.write(j)


serialize_pages(2)


d = Diario(f'/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS2.pdf')
summary = d.summary
h1 = d.find_headers('h1')

d.

len(h1)

len(summary)

chaves = list(summary.keys())

headers = list(map(lambda x: x[1], h1))

for c in chaves:
    if c not in headers:
        print(c)


for i, nome in h1:
    if nome not in chaves:
        print(nome)


[i for i in list(summary.keys()) if i not in list(filter(lambda x: x[1], h1))]

xml = d.toxml(d.PDF, d.encoding)
'Ministério da Cultura'

nomes = [i[1] for i in h1]

[i.strip() for i in nomes if i not in summary]

[i for i in summary if i in list(filter(lambda x: x[0], h1))]

len(summary)
h1


for i in d.pages:
    lines = [l for l in i.splitlines()]
    for line in lines:
        if 'Cultura' in line:
            print(line)'''
