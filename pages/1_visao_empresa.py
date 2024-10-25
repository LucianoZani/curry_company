#Libraries
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import folium_static
from haversine import haversine
from PIL import Image

st.set_page_config( page_title='Visão Empresa', page_icon='📊', layout='wide' )

#====================================================#
                   #Funções
#====================================================#
def country_maps(df1):
    df_aux = df1.loc[:,['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']].groupby(['City','Road_traffic_density']).median().reset_index()
    map_ = folium.Map()

    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                  location_info['Delivery_location_longitude']],
                  popup=location_info[['City', 'Road_traffic_density']]).add_to(map_)

    folium_static( map_, width=1440 ,  height=600 )
    
def order_share_by_week(df1):
    df_aux01 = df1.loc[:, ['ID','Week_of_year']].groupby('Week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Week_of_year','Delivery_person_ID']].groupby('Week_of_year').nunique().reset_index()
    df_aux = pd.merge(df_aux01,df_aux02, how= 'inner')
    df_aux['Order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='Week_of_year', y='Order_by_deliver')
    return fig
    
def order_by_week(df1):
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['Week_of_year', 'ID']].groupby('Week_of_year').count().reset_index()
    fig = px.line(df_aux, x='Week_of_year', y='ID')
    return fig
    
def traffic_order_city(df1):
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City','Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[df_aux['City'] != 'NaN ',:]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
    fig = px.scatter(df_aux, x='City', y = 'Road_traffic_density', size = 'ID')
    return fig

def traffic_order_share(df1):
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
    df_aux['Percent_value'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux,values='Percent_value', names='Road_traffic_density')
    return fig

def order_metric(df1): 
    cols = ['ID', 'Order_Date']
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID')
    return fig

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
df1 = pd.read_csv( r'C:\Users\lucia\Documents\python\repos\dataset\train.csv' )


#====================================================#
                   #Limpando dos dados
#====================================================#

#df1 = df1.clean_code()
df1 = clean_code(df1)







#====================================================#
               #Barra Lateral
#====================================================#


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
st.sidebar.markdown('## Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]

#Filtro de transito
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, : ]


#====================================================#
               #Layout Streamlit
#====================================================#

st.header('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )

with tab1:
    with st.container():
        #Order Metric
        fig = order_metric(df1)
        st.markdown( '## Orders by Day' )
        st.plotly_chart(fig)
        
    with st.container():              
        col1,col2 = st.columns( 2 )
        with col1:
            fig = traffic_order_share(df1)
            st.markdown( '## Traffic Order Share' )
            st.plotly_chart(fig)
            
                  
        with col2:
            fig = traffic_order_city(df1)
            st.markdown( '## Traffic Order City' )
            st.plotly_chart(fig)

    
with tab2:
    fig = order_by_week(df1)
    st.markdown( '## Order by Week' )
    st.plotly_chart(fig)
    
    
    fig = order_share_by_week(df1)
    st.markdown( '## Order Share by Week' )
    st.plotly_chart(fig)
    

  
with tab3:
    st.markdown( '## Country Maps' )
    country_maps(df1)

    
    


    
















