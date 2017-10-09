# amanuense
Parser do Diário Oficial da União (D.O.U)

#Tutorial


    from amanuense.diario import Diario

    pdf = '/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS3.pdf'
    diario = Diario(pdf)

    diario.page_count

    # Sumário do D.O.U conforme apresentado na primeira página do documento
    diario.summary

    # Retorna o conteúdo publicado por um determinado órgão do Governo
    diario.section_contents('Presidência da República').splitlines()
