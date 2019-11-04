
import dash
import dash_core_components as dcc
import dash_html_components as html
import os
import glob
import pandas as pd
from dash.dependencies import Input, Output
from faker import Factory
import plotly.offline as py
import plotly.graph_objs as go 
from IPython.display import Image
import base64


def transform(x):
    if len(x) == 6:
        x=x.replace('_','-0')
    else:
        x=x.replace('_','-')
        x=x.replace('b-1','1')
        x=x.replace('b-2','3')
        x=x.replace('b-3','5')
        x=x.replace('b-4','7')
        x=x.replace('b-5','9')
        x=x.replace('b-6','11')     
        x=x.replace('t-1','1')
        x=x.replace('t-2','4')
        x=x.replace('t-3','7')
        x=x.replace('t-4','10')        
        x=x.replace('s-1','1')
        x=x.replace('s-2','7')   
    return x

folder ='C:\\Users\\Pessoal\\Desktop\\Base_MBTSA'
extension = 'csv'
separator = ','
dict_color = {'PRECTOT' : '#FF0000','RH2M': '#00FF00' ,'PS': '#0000FF'  ,'T2M': '#FF00FF'  ,'T2M_MIN': '#00FFFF' , 'T2M_MAX':'#FFFF00'  , 'WS50M_MAX' :'#000000', 'WS50M_MIN' :'#70DB93'
                , 'WS10M_MAX' : '#5C3317', 'WS10M_MIN': '#9F5F9F', 'WS50M': '#B5A642', 'WS10M':'#D9D919' , 'QV2M':'#A62A2A',
                   'T2M_MAX_MAXIMO': '#8C7853', 'WS50M_MAX_MAXIMO': '#A67D3D'
                ,'WS10M_MAX_MAXIMO': '#5F9F9F', 'T2M_MIN_MINIMO':'#D98719',
                  'WS50M_MIN_MINIMO': '#5C4033',  'WS10M_MIN_MINIMO': '#2F4F2F',  'PRECTOT_SUM': '#4A766E'}  

extension = '*.' + extension
os.chdir(folder)
files= glob.glob(extension)

def transf(x):
    x=x.replace('mensal_bi_tri_se_an_','')
    x=x.replace('_geral.csv','')
    return x
temp=pd.read_csv(files[0],sep=',',nrows=1)
variables = temp.columns
variables = variables[1:]

new_files=[transf(x) for x in files]

external_stylesheets = ['https://codepen.io/g4b1b13l/pen/VwwrYdL.css']

list_ron=['mensal','bimestral','trimestral','semestral','anual']

image_directory = 'C://Users//Pessoal//Desktop//Base_MBTSA//10_09_2019//'

list_of_images = [os.path.basename(x) for x in glob.glob('{}*.png'.format(image_directory))]




app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Mapa-Climatologico'



app.layout = html.Div([
	html.Div(

        [html.H1(children= 'Mapa Climatológico'),
       
        ]
              , 

         style={
        'font-size': '10px',
        #'height': '75px',
        'margin': '-10px -10px -10px',
        #'background-color': '#808080',
        'text-align': 'center',
        #'border-radius': '2px',
        #'display': 'flex',
        #'margin-left': '0',
        } 
        ),

	html.Div([

	html.Div([
	html.Label('Variavel'),
    dcc.Dropdown(
    	id = 'variavel',
        options=[
            {'label': j, 'value': j} for j in variables
        ],
        value='',
        multi=True
    ),



    html.Label('Tempo'),
    dcc.Dropdown(
    	id = 'tipo',
        options=[
            {'label': a, 'value': a} for a in list_ron
        ],
        value='',
        multi=False
    ),

    html.Label('Municipio'),
    dcc.Dropdown(
    	id='filename1',
        options=[
            {'label': v, 'value': v} for v in new_files
        ],
        value='',
        multi = True
    ),

    dcc.Graph(id = 'feature-graphic'),
    ],
    className='six columns'),

	html.Div([

    html.Label('Mapa-Colorido'),
    dcc.Dropdown(
    	id='image-dropdown',
        options=[
            {'label': v, 'value': v} for v in list_of_images
        ],
        value='',
        multi = False
    ),

    html.Img(id='image',style={'width': '100%', 'display': 'inline-block', 'height': '500px'})


    ],
    className='six columns'),
	],
	className='row',
	style={
		'margin-top':'18px',
        } 
		),


],  style={'width': '100%',
            'display': 'inline-block'})



@app.callback(Output('feature-graphic', 'figure'),
    [Input('filename1', 'value'),
     Input('variavel', 'value'),
     Input('tipo','value')])


def update_graph(filename1,variavel,tipo): 
	

    fake = Factory.create()
    fig=go.Figure()
    trace=[]
    buttons=[]
    print(filename1)
    for filename1 in filename1:
        filename1='mensal_bi_tri_se_an_' + filename1 + '_geral.csv'
        item=pd.read_csv(filename1,sep=',')
        if(tipo=='mensal'):
            item=item[1:432]
        if(tipo=='bimestral'):
            item=item[432:648]
        if(tipo=='trimestral'):
            item=item[648:792]
        if(tipo=='semestral'):
            item=item[792:864]
        if(tipo=='anual'):
            item=item[864:900]    
        item.rename(columns={'Unnamed: 0': 'Tempo'},inplace=True)
        item['Tempo']=item['Tempo'].apply(transform)
        variables = item.columns
        variables = variables[1:]
        nama = filename1.replace('mensal_bi_tri_se_an_', '')
        nama = nama.replace('_geral.csv', '')
        for var in variavel:
            fig.add_trace((go.Scatter(
            x=item['Tempo'],
            y=item[var],
            name = var + ' ' + nama,
            visible=True,
            cliponaxis=False,
            line = dict(color = fake.hex_color()),
            opacity = 0.8)))
            #for x in variables:
             #   fig.add_trace((go.Scatter(
             #   x=item['Tempo'],
             #   y=item[x],
             #   name = x,
             #   visible=True,
             #   line = dict(color = dict_color[x]),
             #   opacity = 0.8)))
            #for item in variables:
             #   flag=[x==item for x in variables]
             #   buttons.append(dict(label=item,        
             #   method="update",
             #   args=[{"visible": flag},
             #   {"title": "Gráfico da " + item,      
             #   }]))
        fig.layout.update(
        updatemenus=[
        go.layout.Updatemenu(
        active=1,
        buttons=list(buttons),)])
        fig.update_layout(
        xaxis=go.layout.XAxis(
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
        )
        fig.update_layout(title='Analise Das Variaveis',
        xaxis={'title': 'TEMPO' + '(' + tipo + ')'},
        )
    print(variavel,flush=True)
    if not variavel:
    	return go.Figure()    	
    else:
    	return go.Figure(fig)


@app.callback(
    dash.dependencies.Output('image', 'src'),
    [dash.dependencies.Input('image-dropdown', 'value')])
def update_image_src(image_path):

	if not image_path:
	    return None 
	image_path = 'C://Users//Pessoal//Desktop//Base_MBTSA//10_09_2019//' + image_path
	encoded_image = base64.b64encode(open(image_path, 'rb').read())
	return 'data:image/png;base64,{}'.format(encoded_image.decode())


if(__name__ == '__main__'):
	app.run_server(debug=True) 

