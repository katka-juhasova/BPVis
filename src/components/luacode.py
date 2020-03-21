import json
import chardet
from typing import List
import dash_html_components as html
from src.constant import COLUMNS
from src.constant import COLORS


# read original lua source code
def _read_source_code(data: dict) -> str:
    raw_data = open(data['path'], 'rb').read()
    chardet_result = chardet.detect(raw_data)

    if chardet_result['encoding'] not in ['ascii', 'utf-8']:
        raw_data = raw_data.decode('iso-8859-1').encode('utf-8')

    return raw_data.decode("utf-8")


# builds tag table so that every character from source file has color
# assigned according to the container from json file
def _add_color(node: dict, source_code: str, tag_table: List[dict]):
    position = node['position'] - 1
    for i in range(position, position + node['characters_count']):
        tag_table[i]['container'] = node['container']
        tag_table[i]['char'] = source_code[i]

        if 'children' in node:
            for child in node['children']:
                _add_color(child, source_code, tag_table)


def _build_tag_table(path: str) -> List[dict]:
    with open(path) as f:
        data = json.load(f)

    source_code = _read_source_code(data)
    tag_table = [dict() for _ in range(len(source_code))]

    # assign container to each character form source code
    for node in data['nodes']:
        _add_color(node, source_code, tag_table)

    # add None container to characters which don't belong anywhere
    for i, byte in enumerate(tag_table):
        if not byte:
            byte['container'] = None
            byte['char'] = source_code[i]

    # remove '\r'
    tag_table = list(filter(lambda b: b['char'] != '\r', tag_table))

    # handle white spaces in the beginning of the line
    # it's about keeping tabs white in the final image
    for i, byte in enumerate(tag_table):
        if byte['char'] == '\n':
            j = i + 1

            while (j < len(tag_table) and
                   tag_table[j]['char'].isspace()):
                tag_table[j]['container'] = None
                j += 1

    return tag_table


# from tag_table builds list of directories, where each element consists of
# hex color and text (not just char anymore)
def _build_color_text_table(tag_table: List[dict]):
    color_text_table = list()
    color_text_table.append(
        {'text': tag_table[0]['char'],
         'color': COLORS[tag_table[0]['container']]}
    )

    for i in range(1, len(tag_table)):
        if tag_table[i]['container'] == tag_table[i - 1]['container']:
            color_text_table[-1]['text'] += tag_table[i]['char']
        else:
            color_text_table.append(
                {'text': tag_table[i]['char'],
                 'color': COLORS[tag_table[i]['container']]}
            )

    return color_text_table


# children may contain pure string element, html.Br() or html.Span element
# with corresponding color background
def view_code(path: str, columns: str):
    tag_table = _build_tag_table(path)
    color_text_table = _build_color_text_table(tag_table)

    pre_children = list()
    for section in color_text_table:
        if section['text'] == '\n' and not section['color']:
            pre_children.append(html.Br())

        elif not section['color']:
            pre_children.append(section['text'])

        else:
            pre_children.append(
                html.Span(
                    children=section['text'],
                    style={
                        'background-color': section['color']
                    }
                )
            )

    return html.Pre(
        children=pre_children,
        style={
            'background-color': "#E4E4E4",
            'font-family': 'Courier, monospace',
            'color': 'black',
            'font-size': '10px',
            'padding': '20px',
            'max-height': '800px',
            'overflow': 'auto'
        },
        className=COLUMNS[columns]
    )
