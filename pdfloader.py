import re
from subprocess import Popen, PIPE

from lxml import etree


def clean_up(XML):
    clean_issn = re.sub('\t*<text.*>(ISSN).*?</text>\r*\n', '', XML)
    clean_iccp = re.sub('\t*<text.*>(Ano).*?(ICP-Brasil)\.</text>\r*\n', '',
                        clean_issn, flags=re.DOTALL)
    return clean_iccp

    '''
    document = re.sub(NO_TEXT_ELEMENT, '', document)
    clean_dot = re.sub('\t*<text.*>\.</text>\r*\n', '', clean_ano)
    clean_header = re.sub('<text.*>N.*?(ICP-Brasil)\..*?\d{1,3}</text>\r*\n*', '', clean_dot, flags=re.DOTALL)
    clean_exemplar = re.sub('\t*<text.*>EXEMPLAR DE ASSINANTE DA IMPRENSA NACIONAL</text>\r*\n', '', clean_header)
    clean_document = re.sub('\t*<text.*>COMERCIALIZAÇÃO PROIBIDA POR TERCEIROS</text>\r*\n', '', clean_exemplar)'''



def get_page(xml, page_number):
    ''' Divide a string xml do documento em páginas '''
    pattern = f'(<page number="{page_number}").*?</page>'
    m = re.search(pattern, xml, flags=re.DOTALL)
    page_start, page_end = m.span()
    return xml[page_start:page_end]


def pdftoxml(filepath, encoding='Latin1', decode=False):
    p = Popen(['pdftohtml', '-xml', '-i', '-stdout', '-enc', encoding,
               filepath], stdout=PIPE, stderr=PIPE)
    XML, err = p.communicate()

    if decode is True:
        return XML.decode(encoding)
    else:
        return XML


def count_pdf_pages(filepath, encoding='utf-8'):
    # Conta as páginas do PDF
    p = Popen(['pdfinfo', filepath], stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    info = stdout.decode(encoding).splitlines()
    page_count = [int(i.split(':')[-1].strip()) for i in info if i.startswith('Pages')][0]
    return page_count


def document_pages(document):
    pages = []
    pattern = '<page.*?>.*?</page>'
    limits = [(i.start(), i.end()) for i in re.finditer(pattern, document,
                                                        flags=re.DOTALL)]
    for start, end in [i for i in limits]:
        page = document[start: end]
        pages.append(page)
    return pages


def remove_page_header(page):
    HEADER = '\n*(<text.*?>)(Ano)\s.*?(o-).*?ISSN.*?ICP-Brasil\.</text>\n*'
    HEADER_BACK = '\n*<text.*>N.*?(ICP-Brasil)\..*?\d{1,3}</text>\n*'
    PATTERN = '|'.join([HEADER, HEADER_BACK])
    page = re.sub(PATTERN, '', page, flags=re.DOTALL)
    return page

def import_PDF(filepath):
    PDF = filepath
    document = pdftoxml(PDF, decode=True)
    pages = document_pages(document)
    pages = [remove_page_header(p) for p in pages]
    return pages

class Diario():
    def __init__(self, PDF_filepath):
        self.PDF = PDF_filepath
        self.encoding = 'Latin1'
        self.xml = self.toxml(self.PDF, self.encoding, decode=True)
        self.pages = self.parse_pages()


    def parse_pages(self):
        pages = self.get_pages_from_xml(self.xml)
        pages = [self.remove_page_header(i) for i in pages]
        return pages

    def toxml(filepath, encoding, decode=False):
        PDFTOXML = ['pdftohtml', '-xml', '-i', '-stdout', '-enc', encoding,
                    filepath]
        p = Popen(PDFTOXML, stdout=PIPE, stderr=PIPE)
        xml_content, err = p.communicate()

        if decode is True:
            return xml_content.decode(encoding)
        else:
            return xml_content

    def get_pages_from_xml(self, xml):
        pages = []
        pattern = '<page.*?>.*?</page>'
        limits = [(i.start(), i.end()) for i in re.finditer(pattern, xml,
                                                            flags=re.DOTALL)]
        for start, end in [i for i in limits]:
            page = xml[start: end]
            pages.append(page)
        return pages

    def remove_page_header(self, page):
        HEADER = '\n*(<text.*?>)(Ano)\s.*?(o-).*?ISSN.*?ICP-Brasil\.</text>\n*'
        HEADER_BACK = '\n*<text.*>N.*?(ICP-Brasil)\..*?\d{1,3}</text>\n*'
        PATTERN = '|'.join([HEADER, HEADER_BACK])
        page = re.sub(PATTERN, '', page, flags=re.DOTALL)
        return page
