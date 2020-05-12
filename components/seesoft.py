import logging
import json
import urllib
import chardet
from PIL import Image
from PIL import ImageDraw
from constant import COLORS
from constant import COLUMNS
from constant import LUA_LINE_HEIGHT
import plotly.graph_objects as go
import base64
from io import BytesIO
import dash_core_components as dcc


BYTE_WIDTH = 5
BYTE_HEIGHT = 10
MARGIN_SIZE = 20
MAX_VIEW_WIDTH = 200
MIN_VIEW_HEIGHT = 200
MAX_VIEW_HEIGHT = 750
MAX_SMALL_VIEW_WIDTH = 230
MIN_SMALL_VIEW_HEIGHT = 200
MAX_SMALL_VIEW_HEIGHT = 650

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler())


class SeeSoft:
    def __init__(self, path=None, url=None, data=None, img_path=None,
                 comments=True):
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

        # self.img_width = 0
        # self.img_height = 0
        self.byte_width = BYTE_WIDTH
        self.byte_height = BYTE_HEIGHT
        self.margin_size = MARGIN_SIZE
        self.comments = comments
        self.source_code = self.__read_source_code()
        self.tag_table = [dict() for _ in range(len(self.source_code))]

        self.img_path = img_path or 'image.png'
        self.bin_img = BytesIO()

        self.__build_tag_table()
        self.img_width = ((self.__max_line() * self.byte_width)
                          + 2 * self.margin_size)
        self.img_height = ((self.__lines_count() * self.byte_height)
                           + 2 * self.margin_size)

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

        if self.comments:
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

        else:
            # delete comments and code segments without container
            self.tag_table = list(
                filter(lambda b: b['container'] or b['char'] == '\n',
                       self.tag_table)
            )

            # remove empty lines from te beginning of the file where there
            # might have been comments
            while self.tag_table[0]['char'].isspace():
                del self.tag_table[0]

            # reduce empty lines sequence to <= 2
            i = 0
            while i < len(self.tag_table) - 3:
                if (self.tag_table[i]['char'] == '\n'
                        and self.tag_table[i + 1]['char'] == '\n'
                        and self.tag_table[i + 2]['char'] == '\n'
                        and self.tag_table[i + 3]['char'] == '\n'):
                    del self.tag_table[i]
                else:
                    i += 1

        # handle white spaces in the beginning of the line
        # it's about keeping tabs white in the final image
        for i, byte in enumerate(self.tag_table):
            if byte['char'] == '\n':
                j = i + 1

                while (j < len(self.tag_table) and
                       self.tag_table[j]['char'].isspace()):
                    self.tag_table[j]['container'] = None
                    j += 1

    def __max_line(self) -> int:
        max_len = 0
        local_len = 0

        for byte in self.tag_table:
            if byte['char'] == '\n':
                if local_len > max_len:
                    max_len = local_len
                local_len = 0
            elif byte['char'] == '\t':
                local_len += 4
            else:
                local_len += 1

        return max_len

    def __lines_count(self) -> int:
        count = 1

        for byte in self.tag_table:
            if byte['char'] == '\n':
                count += 1

        return count

    def draw(self, byte_width=None, byte_height=None,
             margin_size=None, img_path=None):
        # self.byte_width = byte_width or BYTE_WIDTH
        # self.byte_height = byte_height or BYTE_HEIGHT
        # self.margin_size = margin_size or MARGIN_SIZE
        # self.img_path = img_path or self.img_path
        #
        # self.__build_tag_table()
        # self.img_width = ((self.__max_line() * self.byte_width)
        #                   + 2 * self.margin_size)
        # self.img_height = ((self.__lines_count() * self.byte_height)
        #                    + 2 * self.margin_size)

        image = Image.new('RGB', (self.img_width, self.img_height),
                          color=COLORS['empty'])
        draw = ImageDraw.Draw(image)

        row = 0
        column = 0
        for byte in self.tag_table:

            if byte['char'] == '\n':
                row += 1
                column = 0
            elif byte['char'] == '\t':
                # when the character is '\t' just write rectangle of size 4
                x = self.margin_size + column * self.byte_width
                y = self.margin_size + row * self.byte_height

                draw.rectangle(
                    (x, y, x + 4 * self.byte_width, y + self.byte_height),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 4
            else:
                x = self.margin_size + column * self.byte_width
                y = self.margin_size + row * self.byte_height

                draw.rectangle(
                    (x, y, x + self.byte_width, y + self.byte_height),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 1

        image.save(self.bin_img, format='PNG')

    def __add_traces(self, fig):
        # NOTE: first line from the file has the highest y value in the graph
        row = self.__lines_count() - self.margin_size / self.byte_height + 1
        column = 0
        # id of the corresponding section from lua code can be determined
        # with section number
        section_num = 1
        x = list()
        y = list()
        # position in pixels for later scroll interaction
        custom_data = list()
        # id of line in lua code, which is represented by particular trace
        text = list()

        for i, byte in enumerate(self.tag_table):
            # when moving to the next line, add the accumulated trace to
            # the figure and clear the trace
            if byte['char'] == '\n':
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        customdata=custom_data,
                        text=text,
                        mode='markers',
                        marker_opacity=0,
                        hoverinfo='none'
                    )
                )

                row -= 1
                column = 0
                x.clear()
                y.clear()
                custom_data.clear()
                text.clear()

            elif byte['char'] == '\t':
                # when the character is '\t' shift the beginning of the trace
                column += 4

            elif byte['container'] is not None:
                # add point representing character to the trace
                x.append(
                    self.margin_size
                    + column * self.byte_width
                    + self.byte_width * 0.5
                )

                y.append(
                    self.margin_size
                    + row * self.byte_height
                    + self.byte_height * 0.5
                )

                custom_data.append(
                    # without margin size so that there's some space above
                    # the chosen line
                    (self.__lines_count() - row - 2) * LUA_LINE_HEIGHT
                )

                text.append(section_num)

                column += 1
                # increment section number when the container has changed
                if (
                        i > 0 and
                        byte['container'] != self.tag_table[i - 1]['container']
                ):
                    section_num += 1

            else:
                column += 1

        # the text might not end with '\n', therefore last trace might not
        # have been added at this point
        if x and y:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    customdata=custom_data,
                    text=text,
                    mode='markers',
                    marker_opacity=0,
                    hoverinfo='none'
                )
            )

    # count sizes for the seesoft view and keep the ratio
    def count_small_width_and_height(self, width: int or str,
                                     height: int or str):
        # if either value is string (e.g. '80vh'), no calculation is involved
        # if both are set there's no need for any calculation
        if type(width) is str or type(height) is str:
            return width, height
        if width and height:
            return width, height
        else:
            width = MAX_SMALL_VIEW_WIDTH
            height = (width / self.img_width) * self.img_height
            if height > MAX_SMALL_VIEW_HEIGHT:
                height = MAX_SMALL_VIEW_HEIGHT
            elif height < MIN_SMALL_VIEW_HEIGHT:
                height = MIN_SMALL_VIEW_HEIGHT

        return width, height

    # count sizes for the seesoft view and keep the ratio
    def count_width_and_height(self, width: int or str, height: int or str):
        # if either value is string (e.g. '80vh'), no calculation is involved
        # if both are set there's no need for any calculation
        if type(width) is str or type(height) is str:
            return width, height
        if width and height:
            return width, height
        else:
            width = MAX_VIEW_WIDTH
            height = (width / self.img_width) * self.img_height
            if height > MAX_VIEW_HEIGHT:
                height = MAX_VIEW_HEIGHT
            elif height < MIN_VIEW_HEIGHT:
                height = MIN_VIEW_HEIGHT

        return width, height

    def get_figure(self, height_scale=None, small=False,
                   width=None, height=None) -> go.Figure:
        if small:
            width, height = self.count_small_width_and_height(width, height)
        else:
            width, height = self.count_width_and_height(width, height)

        fig = go.Figure()

        # with open('assets/seesoft.png', 'rb') as img_file:
        #     encoded_string = base64.b64encode(img_file.read()).decode()
        encoded_string = base64.b64encode(self.bin_img.getvalue()).decode()
        encoded_image = 'data:image/png;base64,' + encoded_string

        # add invisible scatter trace
        fig.add_trace(
            go.Scatter(
                x=[0, self.img_width],
                y=[0, self.img_height],
                mode='markers',
                marker_opacity=0,
                hoverinfo='none'
            )
        )

        # configure axes
        fig.update_xaxes(
            visible=False,
            range=[0, self.img_width],
            fixedrange=True
        )

        fig.update_yaxes(
            visible=False,
            range=[0, self.img_height],
            fixedrange=True,
            # ensure that the aspect ratio stays constant
            scaleanchor='x',
            scaleratio=1
        )

        # add image
        fig.add_layout_image(
            dict(
                x=0,
                sizex=self.img_width,
                y=self.img_height,
                sizey=self.img_height,
                xref='x',
                yref='y',
                opacity=1,
                layer='below',
                sizing='stretch',
                source=encoded_image
            )
        )

        # configure other layout
        fig.update_layout(
            width=width,
            height=height,
            margin={'l': 0, 'r': 0, 't': 0, 'b': 0, 'autoexpand': False}
        )

        if not small:
            self.__add_traces(fig)

        return fig

    def view(self, dash_id: str, columns=None, width=None, height=None):
        # width, height = self.count_width_and_height(width, height)

        return dcc.Graph(
            id=dash_id,
            figure=self.get_figure(),
            config={
                'displayModeBar': False
            },
            style={
                'width': width,
                'height': height,
                'max-height': '750px'
            },
            # className=COLUMNS[columns]
        )
