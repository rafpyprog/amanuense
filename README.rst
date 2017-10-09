Amanuense
=========

Parser do Diário Oficial da União (D.O.U)

Tutorial
--------


.. code-block:: python


    from amanuense.diario import Diario

    pdf = '/home/rafael/Área de Trabalho/cartesiano/tests/data/DOUS3.pdf'
    diario = Diario(pdf)

    # Quantidade de páginas do documento
    diario.page_count

    # Sumário do D.O.U conforme apresentado na primeira página do documento
    diario.summary

    # Retorna o conteúdo publicado por um determinado órgão do Governo
    PR = 'Presidência da República'
    diario.section_contents(PR)
