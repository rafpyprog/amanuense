from subprocess import PIPE, Popen


def count_pdf_pages(filepath, encoding='utf-8'):
    ''' PDF page count'''
    p = Popen(['pdfinfo', filepath], stdout=PIPE, stderr=PIPE)
    stdout, err = p.communicate()
    info = stdout.decode(encoding).splitlines()
    page_count = [int(i.split(':')[-1].strip()) for i in info if i.startswith('Pages')][0]
    return page_count
