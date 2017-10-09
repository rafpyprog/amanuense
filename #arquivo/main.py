import re

from parser import get_headings_font, get_titles_by_heading
from pdfloader import import_PDF

fp = 'DOUS1.pdf'
dou = import_PDF(fp)




[i.text for i in dou.xpath('//text')][:1000]

headings = get_headings_font(dou)

t = get_titles_by_heading(dou, headings['h1'])
