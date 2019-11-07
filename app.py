# -*- coding: utf-8 -*- 

import base64
import io
import datetime as dt
import time
import re

import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt

import plotly.graph_objs as go

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import json
import geog
import shapely.geometry

from IPython.display import display

# Constants
img_width = 1200
img_height = 800
scale_factor = 0.60

fontsize_dft = 1
markersize_dft = 1

#-------------------------------------------------------------------------------
# Rotinas de Apoio
#-------------------------------------------------------------------------------

def dms2dd(aux):
    '''
    Converte graus-minutos-segundos da Anatel em float.
    Exemplo de uso (coordenada de latitude): 
    07S074490 significa -7 graus, 7 minutos, 44.90 segundos.
    '''
    degrees = int(aux[:2])
    direction = aux[2]
    minutes = int(aux[3:5])
    seconds = int(aux[5:])/100

    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction in ('S','W'):
        dd *= -1
        
    return dd

def gera_lista_de_cores(n):
    '''
    Gera uma lista de n cores igualmente espaçadas.
    Exemplo de uso (três cores):
    cores = gera_lista_de_cores(3)
    print(cores)
    '''
    cm = plt.get_cmap('gist_rainbow')
    return [cm(1.0*i/n) for i in range(n)]

def gera_dict_de_cores(lista):
    '''
    Partindo de uma lista recebida como parâmetro de entrada,
    cria um dicionário que associa elementos da lista a cores.
    Exemplo de uso (três categorias):
    dict_de_cores = gera_dict_de_cores(['A','B','C'])
    print(dict_de_cores)
    '''
    cores = gera_lista_de_cores(len(lista))
    return {op:cor for (op,cor) in zip(lista,cores)}

def gera_polygon_from_point(p,n,r):
    '''
    Gera n pontos localizados ao redor de p com raio r metros.
    Exemplo de uso (20 pontos e raio de 1 km):
    p = shapely.geometry.Point([-90.0, 29.9])
    n = 20
    r = 1000
    print(gera_polygon_from_point(p,n,r))
    '''
    angles = np.linspace(0, 360, n)
    polygon = geog.propagate(p, angles, r)
    return shapely.geometry.Polygon(polygon)

def gera_str_menor(text,n):
    '''
    Se o comprimento de text é menor que n: não muda nada.
    Caso contrário: encurta text o suficiente para que fique 
    com n caracteres, sendo os 3 últimos '...'.
    Restrição: se n for menor que 4, usa n = 4.
    '''
    if(text is None):
        return ''
    
    if(n<4):
        n = 4
        
    if(len(text)>n):
        return text[:(n-3)] + '...'
    else:
        return text

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def plota_mapa_base(fig,ax,df):

    df.plot(color='#e6fff7', linewidth=0.8, ax=ax, edgecolor='0.5')

    return fig, ax

def plota_annotations(fig,ax,anotacao):
    
    y = 0.150
    dy = 0.025
    for anot in anotacao:     
        ax.annotate(anot,
                    xy=(0.025, y), 
                    xycoords='figure fraction',
                    horizontalalignment='left', 
                    verticalalignment='top',
                    fontsize=4, 
                    color='#555555')
        y += dy

    return fig, ax

def plota_camada_sedes(fig,ax,dfm,dfsedes,nome,flag_nomes):

    dfsedes.plot(ax=ax, marker='.', color='black', label=nome, markersize=markersize_dft)
    
    if(flag_nomes):
        for idx,row in dfm.iterrows():
            ax.annotate(gera_str_menor(row['Nome_Munic'],24)
                        ,xy=row['geometry'].representative_point().coords[0]
                        ,horizontalalignment='center'
                        ,fontsize=fontsize_dft
                        ,label=nome
                        ,color='black')

    return fig, ax

def plota_camada_acudes(fig,ax,df,nome,flag_nomes):

    df_temp = df.copy()
    df_temp['geometry']=[x.representative_point() for x in df_temp['geometry']]
    df_temp['Cor']=[(r,g,b,0.25) for (r,g,b,a) in df_temp['Cor']]
    df_temp.plot(ax=ax, marker='.', color=df_temp['Cor'], label=nome, markersize=markersize_dft)

    df.plot(ax=ax,color=df['Cor'],label=nome, markersize=markersize_dft)

    if(flag_nomes):
        for idx,row in df.iterrows():
            nome = '' if (row['Nome'] is None) else row['Nome'].replace('Aç. ','')
            ax.annotate(gera_str_menor(nome,14)
                        ,xy=row['geometry'].representative_point().coords[0]
                        ,horizontalalignment='center'
                        ,fontsize=fontsize_dft
                        ,label=nome
                        ,color=row['Cor'])

    return fig, ax

def plota_camada_rodovias(fig,ax,df,nome,flag_nomes):
    df.plot(ax=ax, color=df['Cor'], label=nome, linewidth=1)

    if(flag_nomes):
        for idx,row in df.iterrows():
            if(row['CodRodov'] is None) or (row['geometry'] is None):
                continue

            codigo = '' if (row['CodRodov'] is None) else str(row['CodRodov'])
            ax.annotate(gera_str_menor(codigo,14)
                        ,xy=row['geometry'].representative_point().coords[0]
                        ,horizontalalignment='center'
                        ,fontsize=fontsize_dft
                        ,label=nome
                        ,color=row['Cor'])

    return fig, ax
    
# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def gera_encoded_image_infra(fig,ax,camadas_do_mapa,flag_nomes):
    '''
    Plota_camada_sedes: Manda df_de_municipios para a rotina de desenho de sedes 
    para usar a area como filtro dos municípios que devem ser desenhados.
    '''

    if type(camadas_do_mapa) is str:
        camadas_do_mapa = camadas_do_mapa.split()
    
    if('sedes_municipais' in camadas_do_mapa):
        fig,ax = plota_camada_sedes(fig,ax,df_de_municipios,df_de_sedes_de_municipios,'Sedes',flag_nomes)

    if('acudes' in camadas_do_mapa):
        fig,ax = plota_camada_acudes(fig,ax,df_de_acudes,'Açudes',flag_nomes)
        
    if('rodovias_br' in camadas_do_mapa):
        temp = df_de_rodovias[df_de_rodovias['Classific']=='BR']
        fig,ax = plota_camada_rodovias(fig,ax,temp,'BR',flag_nomes)
        
    if('rodovias_pb' in camadas_do_mapa):
        temp = df_de_rodovias[df_de_rodovias['Classific']=='PB']
        fig,ax = plota_camada_rodovias(fig,ax,temp,'PB',flag_nomes)
        
    return fig,ax

def gera_encoded_image_eletrica(fig,ax,camadas_do_mapa,flag_nomes):

    return fig,ax

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def gera_encoded_image(camadas_do_mapa_infra,camadas_do_mapa_eletrica,flag_nomes):
    
    fig, ax = plt.subplots(1)
    fig, ax = plota_mapa_base(fig,ax,df_de_municipios)

    anotacao = ['Sedes, Açudes e Rodovias obtidos no portal AESA, em 30/10/2019.']
    fig, ax = plota_annotations(fig,ax,anotacao)
    
    tem_leg = False
    if(len(camadas_do_mapa_infra)>0):
        fig, ax = gera_encoded_image_infra(fig,ax,camadas_do_mapa_infra,flag_nomes)
        tem_leg = True
        
    if(len(camadas_do_mapa_eletrica)>0):
        fig, ax = gera_encoded_image_eletrica(fig,ax,camadas_do_mapa_eletrica,flag_nomes)
        tem_leg = True
        
    if(tem_leg):
        ax.legend(fontsize=4)

    ax.margins(x=0, y=0.2)
    ax.axis('off')

    fig.savefig('mapa_paraiba.png', dpi=600, bbox_inches='tight', pad_inches = 0)

    return base64.b64encode(open('mapa_paraiba.png', 'rb').read())

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def gera_div_esquerda_Infra():
    return html.Div(children=[
                    dcc.Markdown(children=r'Infra:'),
                    dcc.Dropdown(id='dropdown_camadas_do_mapa_infra'
                        ,options=dropdown_camadas_do_mapa_infra_options
                        ,value=dropdown_camadas_do_mapa_infra_value
                        ,multi=True)]
                    ,style={'border': '2px solid lightgray'
                            ,'margin-top':'10px'
                            ,'padding':'10px'})

def gera_div_esquerda_RedeEletrica():
    return html.Div(children=[
                    dcc.Markdown(children=r'Rede Elétrica:'),
                    dcc.Dropdown(id='dropdown_camadas_do_mapa_eletrica'
                        ,options=dropdown_camadas_do_mapa_eletrica_options
                        ,value=dropdown_camadas_do_mapa_eletrica_value
                        ,multi=True)]
                    ,style={'border': '2px solid lightgray'
                            ,'margin-top':'10px'
                            ,'padding':'10px'})

def gera_div_esquerda_HabilitaTexto():
    return html.Div(children=[
                    dcc.Markdown(children=r'Texto:'),
                    dcc.Dropdown(id='dropdown_camadas_do_mapa_habilitatexto'
                        ,options=flag_options
                        ,value=flag_value)]
                    ,style={'border': '2px solid lightgray'
                            ,'margin-top':'10px'
                            ,'padding':'10px'})

def gera_div_esquerda():
    return html.Div(className="four columns"
                    ,children=[
                     dcc.Markdown(children=r'Camadas:')
                    ,gera_div_esquerda_Infra()
                    ,gera_div_esquerda_RedeEletrica()
                    ,gera_div_esquerda_HabilitaTexto()]
                    ,style={'border': '2px solid lightgray'
                            ,'margin-top':'10px'
                            ,'padding':'10px'
                            ,'background-color':'#ffffff'
                            ,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'})

def gera_div_direita():
    return html.Div(className="eight columns",children=[
                html.Div(dcc.Graph(id='imagem_do_mapa')
                    ,style={ 'display': 'flex'
                            ,'align-items': 'center'
                            ,'justify-content': 'center'})]
                ,style={'border': '2px solid lightgray' 
                        ,'margin-top':'10px'
                        ,'background-color':'#ffffff'
                        ,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'})

# def gera_layout(external_css):
def gera_layout():
    return html.Div(className="row",children=[
                    # html.Link(href=external_css,rel='stylesheet'),
                    html.Div(children=[
                        html.H3('Clima - Energia PB'),
                        html.P('DEE e DEER do CEAR/UFPB')
                    ],style={'textAlign': 'center'
                             ,'border': '2px solid lightgray'
                             ,'box-shadow': '0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19)'
                             ,'background-color':'#eefefe'}),

                    html.Div([gera_div_esquerda(),gera_div_direita()])]
                    ,style={'border': '2px solid lightgray'
                            ,'margin':'10px'
                            ,'padding':'10px'
                            ,'background-color':'#eeffee'})

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

def carrega_dados_em_dfs(dict_arq):

    df_de_municipios = gpd.read_file(dict_arq['municipios'])

    # ---------------------------------------------------------

    df_de_sedes_de_municipios = gpd.read_file(dict_arq['sedes_de_municipios'])

    # ---------------------------------------------------------

    df_de_acudes = gpd.read_file(dict_arq['acudes'])
    df_de_acudes['Cor'] = [(0,0,1,0.80) for x in df_de_acudes['Nome']]

    # ---------------------------------------------------------

    df_de_rodovias = gpd.read_file(dict_arq['rodovias'])
    df_de_rodovias['Cor'] = [((1,0,0,0.50) if (x =='BR') else (0,1,0,0.50)) for x in df_de_rodovias['Classific']]

    # ---------------------------------------------------------

    return (df_de_municipios, df_de_sedes_de_municipios, df_de_acudes, df_de_rodovias)

#-------------------------------------------------------------------------------
# Leitura dos dados de entrada
#-------------------------------------------------------------------------------

dict_nomes_de_arquivo = {
    'municipios': 'municipios.shp',
    'sedes_de_municipios': 'sedes_municipais.shp',
    'acudes': 'Acudagem_Principal.shp',
    'rodovias': 'Rodovias.shp',
}

(df_de_municipios
, df_de_sedes_de_municipios
, df_de_acudes
, df_de_rodovias) = carrega_dados_em_dfs(dict_nomes_de_arquivo)

#-------------------------------------------------------------------------------
# Dash
#-------------------------------------------------------------------------------
 
dropdown_camadas_do_mapa_infra_options = [{'label': 'Sedes', 'value': 'sedes_municipais'}
                                         ,{'label': 'Açudes', 'value': 'acudes'}
                                         ,{'label': 'Rodovias - BR', 'value': 'rodovias_br'}
                                         ,{'label': 'Rodovias - PB', 'value': 'rodovias_pb'}]
dropdown_camadas_do_mapa_infra_value = ''

# -----

dropdown_camadas_do_mapa_eletrica_options = [{'label': 'SIN', 'value': 'rede_sin'}
                                            ,{'label': 'EPB', 'value': 'rede_epb'}
                                            ,{'label': 'Geração Solar', 'value': 'geracao_solar'}
                                            ,{'label': 'Geração Eólica', 'value': 'geracao_eolica'}
                                            ,{'label': 'Geração Térmica', 'value': 'geracao_termica'}
                                            ,{'label': 'Geração Hidrelétrica', 'value': 'geracao_hidreletrica'}]
dropdown_camadas_do_mapa_eletrica_value = ''

# -----

flag_options = [{'label': 'Ligado', 'value': 'ligado'}
               ,{'label': 'Desligado', 'value': 'desligado'}]
flag_value = 'ligado'

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

app = dash.Dash('[Clima-Energia]')

encoded_image = gera_encoded_image(dropdown_camadas_do_mapa_infra_value
                                   ,dropdown_camadas_do_mapa_eletrica_value
                                   ,(flag_value == 'ligado'))

# meu_external_stylesheets = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# app.layout = gera_layout(meu_external_stylesheets)
app.layout = gera_layout()

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

@app.callback(Output('imagem_do_mapa', 'figure'),
    [Input('dropdown_camadas_do_mapa_infra', 'value')
    ,Input('dropdown_camadas_do_mapa_eletrica', 'value')
    ,Input('dropdown_camadas_do_mapa_habilitatexto', 'value')])
def update_img(opt_infra,opt_eletrica,opt_habilitatexto):

    flag_nomes = (opt_habilitatexto == 'ligado')
    encoded_image = gera_encoded_image(opt_infra,opt_eletrica,flag_nomes)
    
    figure={
        'data': [
            go.Scatter(
                x=[0, img_width * scale_factor],
                y=[0, img_height * scale_factor],
                mode="markers",
                marker_opacity=0
            )
        ],
        'layout': go.Layout(
            xaxis={'visible': False, 'range': [0, img_width * scale_factor]},
            yaxis={'visible': False, 'range': [0, img_height * scale_factor]
                    , 'scaleanchor': "x"},
            images=[go.layout.Image(
                x=0,
                sizex=img_width * scale_factor,
                y=img_height * scale_factor,
                sizey=img_height * scale_factor,
                xref="x",
                yref="y",
                opacity=1.0,
                layer="below",
                source='data:image/png;base64,{}'.format(encoded_image.decode()))],
            width=img_width * scale_factor,
            height=img_height * scale_factor,
            margin={"l": 0, "r": 0, "t": 0, "b": 0},
            autosize=True,
        )
    }
    return figure

# ---------------------------------------------------------
# ---------------------------------------------------------
# ---------------------------------------------------------

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)

#-------------------------------------------------------------------------------
