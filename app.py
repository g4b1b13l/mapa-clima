import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_gif_component as Gif
import base64
external_stylesheets = ['https://codepen.io/g4b1b13l/pen/VwwrYdL.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server




image_filename = 'C://Users//Pessoal//Desktop//Area de trabalho//davi.jpg'  
encoded_image = base64.b64encode(open(image_filename, 'rb').read())   
app.layout = html. Div([html.Div(children=[
    html.H1(children='Davi noobão!'),

	]),

html.Div([
    html.Img(src='data:image/png;base64,{}'.format(encoded_image.decode()))
])

])

if __name__ == '__main__':
    app.run_server(debug=True,port=3030)
