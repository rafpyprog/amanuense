import re
from subprocess import PIPE, Popen

from .utils import count_pdf_pages
from .summary import make_summary

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
            '\n*<text.*?>N.*?(ICP-Brasil)\..*?\d{1,3}</text>\n*',
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


'''
def serialize_pages(n):
    import json
    d = Diario(f'/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS{n}.pdf')
    j = json.dumps(d.pages)
    with open(f'dou{n}.pages', 'w') as f:
        f.write(j)


serialize_pages(2)

d = Diario(f'/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS1.pdf')
p = d.pages[0]
d.summary

for i in p.splitlines():
    print(i)
    break
    pattern = '\n*<text.*?(>)(?<=[A-Z][a-z]).*\s?\.\s{1,2}[0-9]{1,3}</text>\n*'
    pattern = '(?<=.*>)[A-Z][a-z]'
    if re.match(pattern, i) is not None:
        print(re.match(pattern, i))


for n, i in enumerate(p):
    print(n)
    if i.find('ICP-Brasil') != -1:
        raise ValueError
p[0].splitlines()[10:25]



re.search('</i></text>',p[0].splitlines()[24])

p[0][:2500].splitlines()'''
