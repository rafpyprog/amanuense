Amanuense
=========


.. image:: https://raw.githubusercontent.com/rafpyprog/amanuense/master/ext/logo.png
    :target: https://github.com/rafpyprog/amanuense


Parser do Diário Oficial da União (D.O.U)

Instalação
----------


.. code-block::


    pip install amanuense


Tutorial
--------


.. code-block:: python


    from amanuense.diario import Diario

    pdf = '/path/diario_oficial.pdf'
    diario = Diario(pdf)

    # Quantidade de páginas do documento
    diario.page_count

    # Sumário do D.O.U conforme apresentado na primeira página do documento
    diario.summary

    # Retorna o conteúdo publicado por um determinado órgão do Governo
    PR = 'Presidência da República'
    diario.section_contents(PR)
