import re
from subprocess import PIPE, Popen


def get_line_value(line):
    open_tag = re.search('^\n*<text.*?>', line).span()
    line = line[open_tag[1]:].replace('</text>', '').strip()
    line = line.replace('<b>', '').replace('</b>', '')
    return line


def get_content_value(line):
    if line.strip().startswith('<text'):
        open_tag = re.search('^\n*<text.*?>', line).span()
        line = line[open_tag[1]:].replace('</text>', '').strip()
        line = line.replace('<b>', '').replace('</b>', '')
    else:
        return ''
    return line


def count_pdf_pages(filepath, encoding='utf-8'):
    ''' PDF page count'''
    p = Popen(['pdfinfo', filepath], stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    info = stdout.decode(encoding).splitlines()
    page_count = [int(i.split(':')[-1].strip())
                  for i in info if i.startswith('Pages')][0]
    return page_count
