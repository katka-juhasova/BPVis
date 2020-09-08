import logging
import json
import urllib
import chardet
from PIL import Image
from PIL import ImageDraw
from constant import COLORS
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
    """
    Class for visualization of the small colorful representation of
    the original source code. Sections are highlighted according to the type
    of statement that they represent (require, variable, function, etc.).

    Attributes
    ----------
    data : dict
        pre-processed data read from the JSON file
    byte_width : int
        width of one byte (char) in pixels
    byte_height : int
        height of one byte (char) in pixels
    margin_size : int
        size (in pixels) of margins
    source_code : str
        read original source code, structure of which is represented in
        the attribute data
    tag_table : list of dict
        dict for each character from the source code, each dict consists of
        the character and the type of the statement (require, variable etc.)
    bin_img :
        binary representation of the small colorful image of the original
        source code
    img_width : int
        total image width in pixels
    img_height : int
        total image height in pixels

    Methods
    -------
    draw()
        Creates the image representation of the source code. The image is
        stored in the attribute bin_image.
    count_small_width_and_height(width, height)
        Counts and returns width and height of the seesoft figure while
        preserving the ratio. This calculation uses MAX_SMALL_VIEW_HEIGHT,
        MIN_SMALL_VIEW_HEIGHT and MAX_SMALL_VIEW_WIDTH as limits.
    count_width_and_height(width, height)
        Counts and returns width and height of the seesoft figure while
        preserving the ratio. This calculation uses MAX_VIEW_HEIGHT,
        MIN_VIEW_HEIGHT and MAX_VIEW_WIDTH as limits.
    get_figure(small=False, width=None, height=None)
        Returns go.Figure instance containing the colorful image representation
        of the LUA source code.
    view(dash_id, width=None, height=None)
        Returns dcc.Graph instance containing the colorful image representation
        of the LUA source code.
    """

    def __init__(self, path=None, url=None, data=None):
        """
        According to the parameters given, the preprocessed data are read
        from JSON file (parameter path) or from the given url or
        simply copied from the given parameter data. If none of
        the parameters is provided, the function raises an error. Furthermore,
        the original source code is read, tag_table is built and all
        the other attributes are initialized.

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

        self.byte_width = BYTE_WIDTH
        self.byte_height = BYTE_HEIGHT
        self.margin_size = MARGIN_SIZE
        self.source_code = self.__read_source_code()
        self.tag_table = [dict() for _ in range(len(self.source_code))]
        self.bin_img = BytesIO()

        self.__build_tag_table()
        self.img_width = ((self.__max_line() * self.byte_width)
                          + 2 * self.margin_size)
        self.img_height = ((self.__lines_count() * self.byte_height)
                           + 2 * self.margin_size)

    def __read_source_code(self) -> str:
        """
        Reads and returns LUA source code from path or url given in the data.

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
        Builds tag_table so that every character from source file has color
        assigned according to the container type.
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

    def __max_line(self) -> int:
        """
        Counts the length (in characters) of the longest line of the LUA
        source code.

        Returns
        -------
        int
            length of the longest line of the LUA source code
        """

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
        """
        Counts the number of lines of the LUA source code.

        Returns
        -------
        int
            number of lines of the LUA source code
        """

        count = 1

        for byte in self.tag_table:
            if byte['char'] == '\n':
                count += 1

        return count

    def draw(self):
        """
        Creates the image representation of the source code. The image is
        stored in self.bin_image.
        """

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
        """
        Adds invisible traces to the graph for each statement. These traces
        shall be later used for easier navigation through the luacode
        visualization.

        Parameters
        ----------
        fig : go.Figure
            instance of go.Figure where the traces are added and where
            the image stored in self.bin_image shall be set as background
        """

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

    def count_small_width_and_height(self, width: int or str,
                                     height: int or str):
        """
        Counts width and height of the seesoft figure while preserving
        the ratio. This calculation uses MAX_SMALL_VIEW_HEIGHT,
        MIN_SMALL_VIEW_HEIGHT and MAX_SMALL_VIEW_WIDTH as limits.

        Parameters
        ----------
        width : int or str
            pre-set width of the view
        height : int or str
            pre-set height of the view

        Returns
        -------
        int or str, int or str
            width and height of the figure (in pixels or as a string)
        """

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

    def count_width_and_height(self, width: int or str, height: int or str):
        """
        Counts width and height of the seesoft figure while preserving
        the ratio. This calculation uses MAX_VIEW_HEIGHT, MIN_VIEW_HEIGHT and
        MAX_VIEW_WIDTH as limits.

        Parameters
        ----------
        width : int or str
            pre-set width of the view
        height : int or str
            pre-set height of the view

        Returns
        -------
        int or str, int or str
            width and height of the view (in pixels or as a string)
        """

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

    def get_figure(self, small=False, width=None, height=None) -> go.Figure:
        """
        Returns figure containing the colorful image representation of the
        source code. It's optional to choose smaller version of the figure or
        to pre-set the width and height.

        Parameters
        ----------
        small : bool, optional
            determines the size of the figure, if True, the size limits are
            set by MAX_SMALL_VIEW_HEIGHT, MIN_SMALL_VIEW_HEIGHT and
            MAX_SMALL_VIEW_WIDTH (default is None)
        width : int or str or None, optional
            pre-set width of the figure (default is None)
        height : int or str or None, optional
            pre-set height of the figure (default is None)

        Return
        ------
        go.Figure
             go.Figure instance containing the colorful representation of
             the source code
        """

        if small:
            width, height = self.count_small_width_and_height(width, height)
        else:
            width, height = self.count_width_and_height(width, height)

        fig = go.Figure()

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

    def view(self, dash_id: str, width=None, height=None):
        """
        Returns dcc.Graph object which contains the colorful image
        representation of the LUA source code. It's optional to set the width
        and the height of the graph in pixels.

        Parameters
        ----------
        dash_id : str
            id of the dcc.Graph component
        width : int or None, optional
            width of graph in pixels (default is None)
        height : int or None, optional
            height of graph in pixels (default is None)

        Return
        --------
        dcc.Graph
            dcc.Graph instance containing the colorful image representation of
            the LUA source code
        """

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
            }
        )
