from src.components.luacode import LuaCode
import os
import dash
import dash_html_components as html
from src.components.seesoft import SeeSoft
from dash.dependencies import Input, Output


path = '/home/katka/Desktop/FIIT/BP/BPVis/data'
files = list()

# r=root, d=directories, f=files
# list all json files
for r, d, f in os.walk(path):
    for file in f:
        if '.json' in file:
            files.append(os.path.join(r, file))


seesoft_left = SeeSoft(files[1], comments=True)
seesoft_left.draw(img_path='assets/image_left.png')

seesoft_right = SeeSoft(files[0], comments=True)
seesoft_right.draw(img_path='assets/image_right.png')

luacode_left = LuaCode(files[1])
luacode_right = LuaCode(files[0])

# external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']

app = dash.Dash(__name__)

app.layout = html.Div(
    html.Div([
        html.Div(
            [
                html.H1(children='Source code visualization',
                        className='ten columns'),
            ],
            className="row"
        ),
        html.Div(id='hidden-div-left',
                 style={'display': 'none'}),
        html.Div(id='hidden-div-right',
                 style={'display': 'none'}),
        html.Div(
            children=[
                luacode_left.view(dash_id='lua-code-left', columns='4'),
                html.Div(
                    children=seesoft_left.view(dash_id='see-soft-left'),
                    style={
                        'display': 'flex',
                        'justify-content': 'center'
                    },
                    className='two columns'
                ),
                html.Div(
                    children=seesoft_right.view(dash_id='see-soft-right'),
                    style={
                        'display': 'flex',
                        'justify-content': 'center',
                    },
                    className='two columns'
                ),
                luacode_right.view(dash_id='lua-code-right', columns='4'),
            ],
            className="row"
        ),
        html.Pre(id='click-data'),
    ], className='ten columns offset-by-one')
)

# only works properly when seesoft is drawn with comments
# seesoft and luacode interaction for left part of the screen
app.clientside_callback(
    '''
    function scroll_lua_code_left(clickData) {
        if (clickData) {
            var element = document.getElementById("lua-code-left");
            element.scrollTop = clickData.points[0].customdata;

            var element_text_id = "lua-code-left" + clickData.points[0].text;
            var element_text = document.getElementById(element_text_id);
            var color = element_text.style.backgroundColor;
            
            if (color == "rgb(255, 173, 122)") {
                element_text.classList.remove("require_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("require_animate");
            }     
            else if (color == "rgb(117, 235, 135)") {
                element_text.classList.remove("variable_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("variable_animate");
            }
            else if (color == "rgb(158, 203, 255)") {
                element_text.classList.remove("function_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("function_animate");
            }
            else if (color == "rgb(229, 141, 240)") {
                element_text.classList.remove("interface_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("interface_animate");
            }
            else if (color == "rgb(255, 236, 145)") {
                element_text.classList.remove("other_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("other_animate");
            }
            else if (color == "rgb(228, 228, 228)") {
                element_text.classList.remove("comment_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("comment_animate");
            }
        }
        return "";
    }
    ''',
    Output('hidden-div-left', 'children'),
    [Input('see-soft-left', 'clickData')]
)

# seesoft and luacode interaction for the right part of the screen
app.clientside_callback(
    '''
    function scroll_lua_code_right(clickData) {
        if (clickData) {
            var element = document.getElementById("lua-code-right");
            element.scrollTop = clickData.points[0].customdata;

            var element_text_id = "lua-code-right" + clickData.points[0].text;
            var element_text = document.getElementById(element_text_id);
            var color = element_text.style.backgroundColor;

            if (color == "rgb(255, 173, 122)") {
                element_text.classList.remove("require_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("require_animate");
            }     
            else if (color == "rgb(117, 235, 135)") {
                element_text.classList.remove("variable_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("variable_animate");
            }
            else if (color == "rgb(158, 203, 255)") {
                element_text.classList.remove("function_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("function_animate");
            }
            else if (color == "rgb(229, 141, 240)") {
                element_text.classList.remove("interface_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("interface_animate");
            }
            else if (color == "rgb(255, 236, 145)") {
                element_text.classList.remove("other_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("other_animate");
            }
            else if (color == "rgb(228, 228, 228)") {
                element_text.classList.remove("comment_animate");
                void element_text.offsetWidth; 
                element_text.classList.add("comment_animate");
            }
        }
        return "";
    }
    ''',
    Output('hidden-div-right', 'children'),
    [Input('see-soft-right', 'clickData')]
)

# @app.callback(
#     Output('click-data', 'children'),
#     [Input('see-soft-left', 'clickData')])
# def print_stuff(clickData):
#     return json.dumps(clickData, indent=2)


if __name__ == '__main__':
    app.run_server(debug=True)
