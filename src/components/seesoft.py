import json
import chardet
from PIL import Image
from PIL import ImageDraw
from src.constant import COLORS
from src.constant import COLUMNS
import plotly.graph_objects as go
import base64
import dash_core_components as dcc


BYTE_WIDTH = 5
BYTE_HEIGHT = 10
MARGIN_SIZE = 20
TOOLBOX_SIZE = 50


class SeeSoft:
    def __init__(self, path: str, comments=True):
        with open(path) as f:
            self.data = json.load(f)

        self.img_path = 'image.png'
        self.img_width = 0
        self.img_height = 0
        self.byte_width = BYTE_WIDTH
        self.byte_height = BYTE_HEIGHT
        self.margin_size = MARGIN_SIZE
        self.toolbox_size = 0
        self.comments = comments
        self.source_code = self.__read_source_code()
        self.bytes = [dict() for _ in range(len(self.source_code))]

    def __read_source_code(self) -> str:
        raw_data = open(self.data['path'], 'rb').read()
        chardet_result = chardet.detect(raw_data)

        if chardet_result['encoding'] not in ['ascii', 'utf-8']:
            raw_data = raw_data.decode('iso-8859-1').encode('utf-8')

        return raw_data.decode("utf-8")

    def __add_color(self, node: dict):
        position = node['position'] - 1
        for i in range(position, position + node['characters_count']):
            self.bytes[i]['container'] = node['container']
            self.bytes[i]['char'] = self.source_code[i]

            if 'children' in node:
                for child in node['children']:
                    self.__add_color(child)

    def __build_byte_table(self):
        # assign container to each character form source code
        for node in self.data['nodes']:
            self.__add_color(node)

        # add None container to characters which don't belong anywhere
        for i, byte in enumerate(self.bytes):
            if not byte:
                byte['container'] = None
                byte['char'] = self.source_code[i]

            if byte['char'] == '\n':
                byte['container'] = None

        # remove '\r'
        self.bytes = list(filter(lambda b: b['char'] != '\r', self.bytes))

        if self.comments:
            # add comments and other code segments which don't belong to any
            # container to 'comment' container
            for byte in self.bytes:
                if not byte['container'] and not byte['char'].isspace():
                    byte['container'] = 'comment'

            # make spaces in comments colorful instead of white
            for i, byte in enumerate(self.bytes):
                if (
                        byte['char'] == ' '
                        and i - 1 >= 0
                        and i + 1 < len(self.bytes)
                        and self.bytes[i - 1]['container'] == 'comment'
                        and self.bytes[i + 1]['container'] == 'comment'
                ):
                    byte['container'] = 'comment'

        else:
            # delete comments and code segments without container
            self.bytes = list(
                filter(lambda b: b['container'] or b['char'] == '\n',
                       self.bytes)
            )

        # remove empty lines from te beginning of the file
        while self.bytes[0]['char'].isspace():
            del self.bytes[0]

        # handle white spaces in the beginning of the line
        # it's about keeping tabs white in the final image
        for i, byte in enumerate(self.bytes):
            if byte['char'] == '\n':
                j = i + 1

                while (j < len(self.bytes) and
                       self.bytes[j]['char'].isspace()):
                    self.bytes[j]['container'] = None
                    j += 1

        # reduce empty lines sequence to <= 2
        i = 0
        while i < len(self.bytes) - 3:
            if (self.bytes[i]['char'] == '\n'
                    and self.bytes[i + 1]['char'] == '\n'
                    and self.bytes[i + 2]['char'] == '\n'
                    and self.bytes[i + 3]['char'] == '\n'):
                del self.bytes[i]
            else:
                i += 1

    def __max_line(self) -> int:
        max_len = 0
        local_len = 0

        for byte in self.bytes:
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

        for byte in self.bytes:
            if byte['char'] == '\n':
                count += 1

        return count

    def draw(self, toolbox=False, byte_width=None, byte_height=None,
             margin_size=None, img_path=None):
        self.byte_width = byte_width or BYTE_WIDTH
        self.byte_height = byte_height or BYTE_HEIGHT
        self.margin_size = margin_size or MARGIN_SIZE
        self.toolbox_size = TOOLBOX_SIZE if toolbox else 0
        self.img_path = img_path or self.img_path

        self.__build_byte_table()
        self.img_width = ((self.__max_line() * self.byte_width)
                          + 2 * self.margin_size)
        self.img_height = ((self.__lines_count() * self.byte_height)
                           + 2 * self.margin_size + self.toolbox_size)

        image = Image.new('RGB', (self.img_width, self.img_height),
                          color='white')
        draw = ImageDraw.Draw(image)

        row = 0
        column = 0
        for byte in self.bytes:

            if byte['char'] == '\n':
                row += 1
                column = 0
            elif byte['char'] == '\t':
                # when the character is '\t' just write rectangle of size 4
                x = self.margin_size + column * self.byte_width
                y = (self.toolbox_size + self.margin_size
                     + row * self.byte_height)

                draw.rectangle(
                    (x, y, x + 4 * self.byte_width, y + self.byte_height),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 4
            else:
                x = self.margin_size + column * self.byte_width
                y = (self.toolbox_size + self.margin_size
                     + row * self.byte_height)

                draw.rectangle(
                    (x, y, x + self.byte_width, y + self.byte_height),
                    fill=COLORS[byte['container'] or 'empty']
                )

                column += 1

        image.save(self.img_path)

    def __add_traces(self, fig, scale_factor):
        # note: first line from the file has the highest y value in the graph
        row = (self.__lines_count()
               - self.margin_size / self.byte_height
               - self.toolbox_size / self.byte_height
               + 1)
        column = 0
        x = list()
        y = list()

        for byte in self.bytes:

            # when moving to the next line, add the accumulated trace to
            # the figure and clear the trace
            if byte['char'] == '\n':
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        mode='markers',
                        marker_opacity=0,
                        hoverinfo='none'
                    )
                )

                row -= 1
                column = 0
                x.clear()
                y.clear()

            elif byte['char'] == '\t':
                # when the character is '\t' shift the beginning of the trace
                column += 4

            elif byte['container'] is not None:
                # add point representing character to the trace
                x.append(
                    (self.margin_size
                     + column * self.byte_width
                     + self.byte_width * 0.5
                     ) * scale_factor
                )

                y.append(
                    (self.toolbox_size
                     + self.margin_size
                     + row * self.byte_height
                     + self.byte_height * 0.5
                     ) * scale_factor
                )

                column += 1

            else:
                column += 1

        # the text might not end with '\n', therefore last trace might not
        # have been added at this point
        if x and y:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    mode="markers",
                    marker_opacity=0,
                    hoverinfo='none'
                )
            )

    def get_figure(self):
        fig = go.Figure()

        scale_factor = 0.5
        with open(self.img_path, "rb") as img_file:
            encoded_string = base64.b64encode(img_file.read()).decode()
        encoded_image = "data:image/png;base64," + encoded_string

        # add invisible scatter trace
        fig.add_trace(
            go.Scatter(
                x=[0, self.img_width * scale_factor],
                y=[0, self.img_height * scale_factor],
                mode="markers",
                marker_opacity=0
            )
        )

        # configure axes
        fig.update_xaxes(
            visible=False,
            range=[0, self.img_width * scale_factor],
            fixedrange=True
        )

        fig.update_yaxes(
            visible=False,
            range=[0, self.img_height * scale_factor],
            fixedrange=True,
            # ensure that the aspect ratio stays constant
            scaleanchor="x"
        )

        # add image
        fig.add_layout_image(
            dict(
                x=0,
                sizex=self.img_width * scale_factor,
                y=self.img_height * scale_factor,
                sizey=self.img_height * scale_factor,
                xref="x",
                yref="y",
                opacity=1.0,
                layer="below",
                sizing="stretch",
                source=encoded_image
            )
        )

        # configure other layout
        fig.update_layout(
            width=self.img_width * scale_factor,
            height=self.img_height * scale_factor,
            margin={"l": 0, "r": 0, "t": 0, "b": 0, 'autoexpand': False}
        )

        self.__add_traces(fig, scale_factor)

        return fig


def seesoft_view(dash_id: str, seesoft: SeeSoft, columns: str):
    return dcc.Graph(
        id=dash_id,
        figure=seesoft.get_figure(),
        className=COLUMNS[columns]
    )
