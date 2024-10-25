import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🏠"
    
)



#image_path = 'C:\\Users\\lucia\\Documents\\python\\repos\\dashboard\\logo.png'

image = Image.open('logo.png')
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('## Powered by Luciano Zani')

st.write( "# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dasboard foi construído para acompanhar o crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de acompanhamento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais do crescimento dos restaurantes.
    ### Ask for help:
    - Time de Data Science no Discord
        - @Luciano-Zani
    """ )
