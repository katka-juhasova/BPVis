import logging
import json
import urllib
import chardet
from typing import List
from constant import COLORS
from constant import COLUMNS
from constant import LUA_LINE_HEIGHT
import dash_html_components as html


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class LuaCode:
    def __init__(self, path=None, url=None):
        if all(arg is None for arg in {path, url}):
            raise ValueError('Expected either path or url argument')

        if path:
            with open(path) as f:
                self.data = json.load(f)
        else:
            log.debug('Loading data file from {}'.format(url))
            with urllib.request.urlopen(url) as url_data:
                self.data = json.loads(url_data.read().decode())

        self.source_code = self.__read_source_code()
        self.tag_table = [dict() for _ in range(len(self.source_code))]
        self.color_text_table = list()

    # read original lua source code
    def __read_source_code(self) -> str:
        # if there's path provided read form it, otherwise read from url
        if self.data['path']:
            raw_data = open(self.data['path'], 'rb').read()

        else:
            log.debug('Loading module file from {}'.format(self.data['url']))
            url_file = urllib.request.urlopen(self.data['url'])
            raw_data = url_file.read()

        chardet_result = chardet.detect(raw_data)
        if chardet_result['encoding'] not in ['ascii', 'utf-8']:
            raw_data = raw_data.decode('iso-8859-1').encode('utf-8')

        return raw_data.decode('utf-8')

    # builds tag table so that every character from source file has color
    # assigned according to the container from json file
    def __add_color(self, node: dict):
        position = node['position'] - 1
        for i in range(position, position + node['characters_count']):
            self.tag_table[i]['container'] = node['container']
            self.tag_table[i]['char'] = self.source_code[i]

            if 'children' in node:
                for child in node['children']:
                    self.__add_color(child)

    def __build_tag_table(self):
        # assign container to each character form source code
        for node in self.data['nodes']:
            self.__add_color(node)

        # add None container to characters which don't belong anywhere
        for i, byte in enumerate(self.tag_table):
            if not byte:
                byte['container'] = None
                byte['char'] = self.source_code[i]

            if byte['char'] == '\n':
                byte['container'] = None

        # remove '\r'
        self.tag_table = list(
            filter(lambda b: b['char'] != '\r', self.tag_table)
        )

        # add comments and other code segments which don't belong to any
        # container to 'comment' container
        for byte in self.tag_table:
            if not byte['container'] and not byte['char'].isspace():
                byte['container'] = 'comment'

        # make spaces in comments colorful instead of white
        for i, byte in enumerate(self.tag_table):
            if (
                    byte['char'] == ' '
                    and i - 1 >= 0
                    and i + 1 < len(self.tag_table)
                    and self.tag_table[i - 1]['container'] == 'comment'
                    and self.tag_table[i + 1]['container'] == 'comment'
            ):
                byte['container'] = 'comment'

        # handle white spaces in the beginning of the line
        # it's about keeping tabs white in the final image
        for i, byte in enumerate(self.tag_table):
            if byte['char'] == '\n':
                j = i + 1

                while (j < len(self.tag_table) and
                       self.tag_table[j]['char'].isspace()):
                    self.tag_table[j]['container'] = None
                    j += 1

    # from tag_table builds list of directories, where each element consists of
    # hex color and text (not just char anymore)
    def __build_color_text_table(self):
        self.color_text_table.append(
            {'text': self.tag_table[0]['char'],
             'color': COLORS[self.tag_table[0]['container']]}
        )

        for i in range(1, len(self.tag_table)):
            if (
                    self.tag_table[i]['container'] ==
                    self.tag_table[i - 1]['container']
            ):
                self.color_text_table[-1]['text'] += self.tag_table[i]['char']
            else:
                self.color_text_table.append(
                    {'text': self.tag_table[i]['char'],
                     'color': COLORS[self.tag_table[i]['container']]}
                )

    def get_children(self, parent_id: str) -> List:
        children = list()
        child_id = 1
        for section in self.color_text_table:
            if section['text'] == '\n' and not section['color']:
                children.append(html.Br())

            elif not section['color']:
                children.append(section['text'])

            else:
                children.append(
                    html.Span(
                        id='{}{}'.format(parent_id, child_id),
                        children=section['text'],
                        style={
                            'background-color': section['color']
                        }
                    )
                )

                child_id += 1

        return children

    # children may contain pure string element, html.Br() or html.Span element
    # with corresponding color background
    def view(self, dash_id: str, columns: str):
        self.__build_tag_table()
        self.__build_color_text_table()
        children = self.get_children(dash_id)

        return html.Pre(
            id=dash_id,
            children=children,
            style={
                'background-color': COLORS['code-background'],
                'font-family': 'Courier, monospace',
                'color': 'black',
                'font-size': '10px',
                'line-height': LUA_LINE_HEIGHT,
                'padding': '20px',
                'max-height': '80vh',
                'overflow': 'auto'
            },
            className=COLUMNS[columns]
        )
