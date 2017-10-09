def parse_font_spec(first_page):
    specs = first_page.findall('fontspec')
    return specs
