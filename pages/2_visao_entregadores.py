#Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image

st.set_page_config( page_title='Visão Emtregadores', page_icon='🚚', layout='wide' )

#====================================================#
                   #Funções
#====================================================#
def rating_of_weather(df1):
    rating_of_weather = ( df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                             .groupby('Weatherconditions').agg( {'Delivery_person_Ratings': ['mean','std']}) )
    rating_of_weather.columns = ['Delivery_mean', 'Delivery_std']
    rating_of_weather.reset_index()
    return rating_of_weather
    
def mean_traffic(df1):
    mean_traffic = ( df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                        .groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean','std']}))
    mean_traffic.columns = ['Delivery_mean', 'Delivery_std']
    mean_traffic.reset_index()
    return mean_traffic
    
def last_delivers(df1):
    df2  = df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']].groupby(['City','Delivery_person_ID']).max().sort_values(['City','Time_taken(min)']).reset_index()
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', : ].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', : ].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', : ].head(10)
    df_aux = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
    return df_aux
    
def top_delivers(df1):
    df2  = ( df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
                .groupby(['City','Delivery_person_ID']).min().sort_values(['City','Time_taken(min)']).reset_index() )
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', : ].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', : ].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', : ].head(10)
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index(drop=True)
    return df3

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


#________________#Estrutura logica____________________



#====================================================#
                   #Import Dataset
#====================================================#

df1 = pd.read_csv( r'C:\Users\lucia\Documents\python\repos\dataset\train.csv' )

#====================================================#
                   #Limpando dos dados
#====================================================#

df1 = clean_code(df1)

#====================================================#
               #Barra Lateral
#====================================================#

st.header('Marketplace - Visão Entregadores')

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
        st.title( 'Overal Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='Large' )

        #A maior idade dos entregadores
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age' ].max()
            col1.metric( 'Maior Idade', maior_idade )
            
         #A menor idade dos entregadore
        with col2:  
            menor_idade = df1.loc[:,'Delivery_person_Age' ].min()
            col2.metric( 'Menor idade', menor_idade )
            
        #A melhor condição de veiculo
        with col3:
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condição de veículo', melhor_veiculo )
            
        #A Pior condição de veiculo
        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condição de veículo', pior_veiculo )

    st.markdown( """___""" )


    with st.container():
        st.title( 'Avaliações' )

        col1, col2 = st.columns( 2 )

        #Avaliação media por entregador
        with col1:
            st.markdown( '##### Avaliação média por Entregador' )
            rating_mean_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                 .groupby('Delivery_person_ID').mean().reset_index() )
            st.dataframe( rating_mean_deliver )

        with col2:
            #Avaliação média por trânsito
            mean_traffic = mean_traffic(df1)
            st.markdown( '##### Avaliação média por Trânsito' )
            st.dataframe( mean_traffic )

            #Avaliação média por clima
            rating_of_weather = rating_of_weather(df1)
            st.markdown( '##### Avaliação média por Clima' )
            st.dataframe( rating_of_weather )
            
    st.markdown( """___""" )

    with st.container():
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )

        #Top 10 entregadores mais rapidos
        with col1:
            df3 = top_delivers(df1)
            st.markdown( '##### Top Entregadores mais rápidos' )
            st.dataframe( df3 )
        
        #Top 10 entregadores mais lentos
        with col2:
            df_aux = last_delivers(df1)
            st.markdown( '##### Top Entregadores mais lentos' )
            st.dataframe( df_aux )
            
    st.markdown( """___""" )
        


















