import logging
import json
import urllib
import chardet
from typing import List
from constant import COLORS
from constant import LUA_LINE_HEIGHT
import dash_html_components as html


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class LuaCode:
    """
    Class for visualization of the original source code. Sections are
    highlighted according to the type of statement that they represent
    (require, variable, function, interface, other).

    Attributes
    ----------
    data : dict
        pre-processed data read from the JSON file
    source_code : str
        read original source code, structure of which is represented in
        the attribute data
    tag_table : list of dict
        dict for each character from the source code, each dict consists of
        the character and the type of the statement (require, variable etc.)
    color_text_table : list of dict
        each dict consists of string (statement or part of the statement)
        and the color assigned accordingly to the type of the statement

    Methods
    -------
    get_children(parent_id):
        Returns list of html.Span objects which can be later used as children
        for html.Pre component.
    view(dash_id)
        Returns html.Pre object which contains the colorful representation of
        the original source code.
    """

    def __init__(self, path=None, url=None, data=None):
        """
        According to the parameters given, the preprocessed data are read
        from JSON file (parameter path) or from the given url or
        simply copied from the given parameter data. If none of
        the parameters is provided, the function raises an error. Furthermore,
        the original source code is read and tag_table and color_text_table
        are initialized.

        Parameters
        ----------
        path : str or None, optional
            path to the JSON file, which contains preprocessed LUA source code
            (default is None)
        url : str or None, optional
            url of the JSON file, which contains preprocessed LUA source code
            (default is None)
        data : dict or None, optional
            preprocessed data already read from JSON file
        """

        if data:
            self.data = data
        else:
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

    def __read_source_code(self) -> str:
        """
        Reads and returns LUA source code from path or url from the data.

        Returns
        --------
        str
            original LUA source code which was preprocessed and stored in
            JSON file
        """

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

    def __add_color(self, node: dict):
        """
        Adds color to the tag_table for each character included in the given
        node. Colors are assigned according to the container type of the node.

        Parameters
        ----------
        node : dict
            information about the node such as type of container (type of
            statement), order in the source code, number of the children etc.
        """

        position = node['position'] - 1
        for i in range(position, position + node['characters_count']):
            self.tag_table[i]['container'] = node['container']
            self.tag_table[i]['char'] = self.source_code[i]

            if 'children' in node:
                for child in node['children']:
                    self.__add_color(child)

    def __build_tag_table(self):
        """
        Builds tag_table so that every character of the source code has color
        assigned according to their container type.
        """

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
                    and (self.tag_table[i + 1]['container'] == 'comment'
                         or self.tag_table[i + 1]['char'].isspace())
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

    def __build_color_text_table(self):
        """
        Builds list of dict (color_text_table) based on tag_table, where
        each element consists of hex color and text (not just char anymore)
        as the adjoining characters with the same container type are merged.
        """

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
        """
        Builds tag_table and color_text_table. Then returns list of html.Span
        objects which can be later used as children for html.Pre component.

        Parameters
        ----------
        parent_id : str
            id of the parent component (e.g. html.Pre component) so that the
            html.Span elements can have ids derived from the parent id

        Returns
        -------
        list
            list of html.Span instances determined from the color_text_table
        """

        self.__build_tag_table()
        self.__build_color_text_table()

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
    def view(self, dash_id: str):
        """
        Returns html.Pre object which contains the colorful representation of
        the original source code.

        Parameters
        ----------
        dash_id : str
            id of the html.Pre component

        Returns
        --------
        html.Pre
            html.Pre instance of the colorful representation of the original
            source code
        """

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
                'height': '730px',
                'overflow': 'auto'
            }
        )
