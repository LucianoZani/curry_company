#Libraries
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image

st.set_page_config( page_title='Visão Restaurantes', page_icon='🍜', layout='wide' )

#====================================================#
                   #Funções
#====================================================#
def avg_std_type_or_order(df1):

    """
    Esta função caulcula o tempo médio e o desvio padrão por cidade e tipo de pedido
    input:
    Dataframe
    Output:
    Dataframe
    
    """
    df_aux = df1.loc[:, ['City','Type_of_order','Time_taken(min)']].groupby(['City','Type_of_order']).agg( {'Time_taken(min)': ['mean','std'] })
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux = df_aux.reset_index()
    return df_aux
    
def avg_std_city(df1):

    """
    Esta função calcula o tempo médio e o desvio padrão por cidade.
    input:
    Dataframe  = (df1)
    Output:
    Grafico de barras com semi-reta 
    
    """
    df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg( {'Time_taken(min)': ['mean','std'] })
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux = df_aux.reset_index()

    #Plotando o grafico de barras
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['Time_mean'], error_y=dict( type='data', array=df_aux['Time_std'])))
    fig.update_layout(barmode='group')
    return fig
    
def avg_std_of_city_traffic(df1):

    """
    Esta função calcula o tempo medio de entrega agrupado por cidade e tipo de tráfego.
    input: 
    Dataframe = (df1)
    Output:
    Gráfico sunburst
    
    """
    df_aux = df1.loc[:, ['City', 'Road_traffic_density','Time_taken(min)']].groupby(['City','Road_traffic_density']).agg( {'Time_taken(min)': ['mean','std'] })
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux = df_aux.reset_index()
                
    #plotando grafigo Sunburst
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Time_mean',
                        color='Time_std', color_continuous_scale='RdBu',
                        color_continuous_midpoint=np.average(df_aux['Time_std']))
    return fig
def avg_distance_city(df1):
    
    """
    Esta função calcula a distançia média de distribuição por cidade e plota um gráfico de pizza com uma parte destacada.
    input:
    Dataframe = (df1)
    Output:
    Grafico de pizza com valor destacado
    
    """
    #Destribuição da distancia media por cidade
    df1['Distance'] = ( df1.loc[:, ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude'] ]
                           .apply( lambda x: haversine( 
                                (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1) )
    distancia_media = df1.loc[:, ['Distance', 'City']].groupby('City').mean().reset_index()

    # pull is given as a fraction of the pie radius
    fig = go.Figure(data=[go.Pie(labels=distancia_media['City'], values= distancia_media['Distance'], pull=[0, 0.1, 0])])
    return fig
    
def stats_time_delivery(df1, festival, op):
    
    """
    Esta função tem a calcula o tempo medio e desvio padão durante fora do festival.
    Input:
    Dataframe = df1
    festival = 'Yes'(para calculo durante o festival) e 'No'(para culculo fora do festival)
    op = 'Time_mean'(Calcula o tempo medio de entrega) e 'Time_std'(Calcula o desvio padão)
    Output:
    Unico valor com 2 casas decimais
    
    """
    df_aux = df1.loc[:, ['Festival','Time_taken(min)']].groupby(['Festival']).agg( {'Time_taken(min)': ['mean','std'] })
    df_aux.columns = ['Time_mean', 'Time_std']
    df_aux = df_aux.reset_index()
    df_aux = df_aux.loc[df_aux['Festival'] == festival, op].values[0]
    df_aux = round(df_aux, 2)
    return df_aux


def distance(df1):
    
    """
    Está função calcula a distancia média entre os restaurantes e os locais de entreaga.
    Input:
    Dataframe = (df1)
    Output:
    Unico valor com 2 casas decimais
    """
    df1['Distance'] = ( df1.loc[:, ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude', 'Delivery_location_longitude'] ]
                            .apply( lambda x: haversine( (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                         (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1) )
    distancia_media = round(df1['Distance'].mean(), 2)
    return distancia_media


def clean_code( df1 ):
    
    """ 
    Esta função tem a respondabilidade de limpar o dataframe
    Tipos de limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo de coluna de dados
    3. Remoção dos espaços das variaveis de texto
    4. Formatação das colunas das datas
    5. Limpeza da coluna de tempo (remoção do texto da variavel numerica)

    Input: Dataframe
    Output: Dataframe
        
    """
    # 1. Removendo NaN
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    # 2. Convertendo a coluna Age de texto para numero
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # 3. Convertendo a coluna Ratings de texto para numero decimal (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # 4. Convertendo a coluna Ordem Date de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format= '%d-%m-%Y')
    
    # 5. Convertendo a coluna multiple_deliveries de texto para numero inteiro (int)
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # 6. Removendo espaços dento de String/ texto / object (acessando a str)
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    # 7. Limpando a coluna de time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

#__________Inicio da estrutura lógica do codigo___________

#====================================================#
                   #Import Dataset
#====================================================#

df1 = pd.read_csv( 'dataset/train.csv' )

#====================================================#
                   #Limpando dos dados
#====================================================#

df1 = clean_code(df1)

#====================================================#
               #Barra Lateral
#====================================================#

st.header('Marketplace - Visão Restaurantes')

#image_path = 'C:\\Users\\lucia\\Documents\\python\\repos\\dashboard\\logo.png'

image = Image.open('logo.png')
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown( '## Selecione uma data limite ')

#Slider
date_slider = st.sidebar.slider(
    'Até qual valor?' ,
    value=pd.Timestamp( '2022-4-13' ).date(),
    min_value=pd.Timestamp('2022-2-11' ).date(),
    max_value=pd.Timestamp('2022-4-6' ).date(),
    format='DD/MM/YYYY' )
date_slider = pd.Timestamp(date_slider)

st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    [ 'Low', 'Medium', 'High' , 'Jam' ],
    default = [ 'Low', 'Medium', 'High' , 'Jam' ] )

st.sidebar.markdown("""___""")
st.sidebar.markdown('## Powered by Luciano Zani')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, : ]

#====================================================#
               #Layout Streamlit
#====================================================#

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.markdown( '### Overal Metrics' )
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6, gap='Large' )

        #Quantidade de entregadores unicos
        with col1:
            sinlgle_person_id = df1.loc[: ,  'Delivery_person_ID'].nunique()
            col1.metric( 'Entregodores unicos', sinlgle_person_id )

        #Distandia media entre os Restaurantes e os locais de entrega
        with col2:
            distancia_media = distance(df1)
            st.metric( 'Distancia média (km)', distancia_media )

        #Tempo medio de entrega durante o festival
        with col3:
            df_aux = stats_time_delivery(df1, 'Yes', 'Time_mean')
            st.metric( 'Tm entrega Festival (min)', df_aux )

        #Desvio padrão do tempo medio de entrega durante o festival
        with col4:
            df_aux = stats_time_delivery(df1, 'Yes', 'Time_std')
            st.metric( 'Desvpad entrega Festival', df_aux )

        #Tmepo medio de entrega sem festival
        with col5:
            df_aux = stats_time_delivery(df1, 'No', 'Time_mean')
            st.metric( 'Tm entrega s/ Festival (min)', df_aux )

        #Desvio padrão do tempo medio de entrega sem festival
        with col6:
            df_aux = stats_time_delivery(df1, 'Yes', 'Time_std')
            st.metric( 'Desvpad entrega s/ Festival', df_aux )

    st.markdown( """___""" )


    with st.container():
        st.markdown( '### Distribuição de distância média por cidade' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            
            fig = avg_distance_city(df1)
            st.plotly_chart(fig)

        
        # Distribuição média e o desvio padrão de entrega por cidade e tipo de tráfego
        with col2:
                fig = avg_std_of_city_traffic(df1)
                st.plotly_chart(fig)

    st.markdown( """___""" )


    with st.container():
        st.markdown( '### Distribuição do Tempo' )
        
        col1, col2 = st.columns( 2, gap='Large')

        #Tempo e desvio padrao por cidade
        with col1:
            fig = avg_std_city(df1)
            st.plotly_chart(fig)


        #Tempo medio e desvio padrão por cidade e tipo de pedido
        with col2:
            df_aux = avg_std_type_or_order(df1)
            st.dataframe(df_aux)

            
            

    
        
    












