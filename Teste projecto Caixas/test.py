#pip3 install xlsx2html

from xlsx2html import xlsx2html
import pdb

COL_AND_LIN_STYLE = """
    font-family: sans-serif;
    font-weight: bold;
    background-color: #f5f5f5;
"""

def append_headers(data, html):
    # Table header:
    html.append('<tr style="%(stl)s">'%{ 'stl': COL_AND_LIN_STYLE, })
    
    html.append('<th></th>')
    for col in data['cols']:
        if col['hidden']:
            continue
        html.append('<th>%(titleindex)s</th>' % { 'titleindex': col['index'] } )
    
    html.append('</tr>')

def append_linenr(trow, i):
    trow.append('<td style="%(stl)s text-align: right;">%(linenr)d</td>'%{ 'stl': COL_AND_LIN_STYLE, 'linenr': i })

infilename = "F.O. 09- Brazão Interpatium . branco ibiza.xlsx"

#in_stream = xlsx2html(infilename)
#in_stream.seek(0)
#print(in_stream.read())

xlsx2html(infilename, 'output.html', append_headers=append_headers, append_linenr=append_linenr, default_cell_border="1px dotted gray")


"""
        <style>
        table, th, td {
            border: 1px solid !important;
            border-color: yellow;
            white-space: nowrap;
        }
        </style>
"""
