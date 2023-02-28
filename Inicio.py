import yfinance as yf
import pandas as pd
from datetime import date
import numpy as np
import seaborn as sns
import streamlit as st
import altair as alt
from numerize.numerize import numerize
import plotly.express as px
import colorlover as cl
import datetime

sns.set()

st.set_page_config(page_title="Inicio",layout='wide')
st.image('imagen/sp500.jpg')
st.title('S&P 500 APP')

st.markdown('''
      Esta app muestra la situación del mercado bursátil en el presente siglo, con lo cual se genera recomendaciones de inversión en base a indicadores clave como la tasa rentabilidad compuesta anual, media móvil y volumen.
      * **Librerías Python:** yfinance, pandas, mplfinance, altair, plotly.express.
      * **Fuentes:** [Wikipedia](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
      
''')



@st.cache_data()
def get_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df_sp500 = pd.read_html(url)[0]
    return df_sp500

df_sp500 = get_sp500()



df_sp500['Symbol'].replace('BRK.B','BRK-B',inplace=True)
df_sp500['Symbol'].replace('BF.B','BF-B',inplace=True)



symbols = df_sp500['Symbol'].to_list()

@st.cache_data()
def get_yfinance():
    df=pd.read_csv('imagen/adj_close_hasta_2023_feb_24.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index(df['Date'],inplace=True)
    df.drop(columns='Date',inplace=True)
    
    df2 = yf.download(symbols,start='2023-02-28',end=date.today() + datetime.timedelta(days=1))['Adj Close']
    df2.reset_index(inplace=True)
    df2['Date'] = pd.to_datetime(df2['Date'])
    df2.set_index(df2['Date'],inplace=True)
    df2.drop(columns='Date', inplace=True)
    
    df=pd.concat([df,df2])
    return df

df = get_yfinance()



# cambiando los sectores a español



df_sp500['GICS Sector'].replace('Industrials','Industriales',inplace=True)
df_sp500['GICS Sector'].replace('Health Care','Salud',inplace=True)
df_sp500['GICS Sector'].replace('Information Technology','Tecnología de la Información',inplace=True)
df_sp500['GICS Sector'].replace('Communication Services','Servicios de Comunicación',inplace=True)
df_sp500['GICS Sector'].replace('Consumer Staples','Consumo Básico',inplace=True)
df_sp500['GICS Sector'].replace('Consumer Discretionary','Consumo Discrecional',inplace=True)
df_sp500['GICS Sector'].replace('Utilities','Servicios Públicos',inplace=True)
df_sp500['GICS Sector'].replace('Financials','Financiero',inplace=True)
df_sp500['GICS Sector'].replace('Materials','Materiales',inplace=True)
df_sp500['GICS Sector'].replace('Real Estate','Bienes Raíces',inplace=True)
df_sp500['GICS Sector'].replace('Energy','Energía',inplace=True)



# Funcion para obtener la cantidad de acciones
# @st.cache_data()
# def shares (row):
#   share = yf.Ticker(row['Symbol']).get_shares_full(start='2000-01-01', end=None)[-1]
#   return share

# Aplico la función para obtener la cantidad de acciones en cada empresa


# df_sp500['Shares'] = df_sp500.apply(shares,axis=1)
df_acciones=pd.read_csv('imagen/df_acciones.csv')
df_sp500=pd.merge(df_sp500,df_acciones,left_on='Symbol',right_on='symbol')

df_sp500.drop(columns=['symbol'],inplace=True)
df_sp500.rename(columns={'acciones':'Shares'},inplace=True)



df.reset_index(inplace=True)
df['Date'] = pd.to_datetime(df['Date'])
df.set_index(df['Date'],inplace=True)
df.drop(columns='Date', inplace=True)


# Agregar el precio actual de la acción al df_sp500
precio_anterior = df.iloc[-2,:]
precio_anterior.rename('Precio_Anterior', inplace=True)
df_sp500 = pd.merge(df_sp500, precio_anterior.to_frame().reset_index(), left_on='Symbol', right_on='index')
df_sp500.drop(columns='index', inplace=True)


# hasta aqui todo bien





# Obtener info inicial
ticker=[]
fecha_inicial=[]
precio_inicial=[]
for i in symbols:
  ticker.append(i)
  fecha_inicial.append(df[i].first_valid_index())
  precio_inicial.append(df.loc[df[i].first_valid_index()][i])

df_info_inicial = pd.DataFrame({'ticker':ticker, 'fecha_inicial':fecha_inicial, 'precio_inicial':precio_inicial})


# Agregando la fecha inicial y precio inicial (donde empezó a cotizar en sp500) al df_sp500
df_sp500 = pd.merge(df_sp500, df_info_inicial, left_on='Symbol', right_on='ticker')
df_sp500.drop(columns='ticker', inplace=True)




# Obtener info actual
ticker=[]
fecha_actual=[]
precio_actual=[]
for i in symbols:
  ticker.append(i)
  fecha_actual.append(df[i].last_valid_index())
  precio_actual.append(df.loc[df[i].last_valid_index()][i])

df_info_actual = pd.DataFrame({'ticker':ticker, 'fecha_actual':fecha_actual, 'precio_actual':precio_actual})



# Agregando la fecha inicial y precio inicial (donde empezó a cotizar en sp500) al df_sp500
df_sp500 = pd.merge(df_sp500, df_info_actual, left_on='Symbol', right_on='ticker')
df_sp500.drop(columns='ticker', inplace=True)



# Calcular la diferencia entre las fechas en años
df_sp500["Tiempo"] = (df_sp500["fecha_actual"] - df_sp500["fecha_inicial"]).dt.days / 365


# Calcular la tasa de interés compuesta anual
df_sp500["tasa_interes_compuesta"] = (df_sp500["precio_actual"] / df_sp500["precio_inicial"]) ** (1 / df_sp500["Tiempo"]) - 1

# Creando el valor de mercado por empresa
df_sp500['valor_mercado_empresa'] = df_sp500['Shares']*df_sp500['precio_actual']


# Calculando el valor de mercado por sector
sector = df_sp500.groupby('GICS Sector')['valor_mercado_empresa'].sum()
sector.to_frame().reset_index().rename(columns={'valor_mercado_empresa':'valor_mercado_sector'})


df_sp500 = pd.merge(df_sp500, sector.to_frame().reset_index().rename(columns={'valor_mercado_empresa':'valor_mercado_sector'}), on='GICS Sector')



df_sp500['pesos'] = df_sp500['valor_mercado_empresa']/df_sp500['valor_mercado_sector']
# df_sp500.drop(columns='rentabilidad_ponderada',inplace=True)

df_sp500['rentabilidad_ponderada'] = round(df_sp500['tasa_interes_compuesta']*df_sp500['pesos']*100,2)
# st.write(df_sp500.head())
# st.write(df.head())

# st.write(df_sp500.head())
# st.write(df.head())
# st.write(df_sp500.groupby('GICS Sector')['rentabilidad_ponderada'].sum().sort_values().plot(kind='barh'))


#-----------------------
df_sp500['%Var'] = round(((df_sp500['precio_actual']-df_sp500['Precio_Anterior'])/df_sp500['Precio_Anterior'])*100,2)
#-----------------------



# SP500 GRAFICO
st.header('Índice S&P 500 - Cotización Histórica')
fecha_inicial=df_sp500['fecha_inicial'].min().date()
fecha_final=df_sp500['fecha_actual'].max().date()

fecha_inicial=st.sidebar.slider('S&P500',fecha_inicial,fecha_final)
sp500=yf.Ticker('^GSPC')
this=sp500.history(start=fecha_inicial, end=date.today())['Close']


fig = px.line(this,labels={'value':'Valor', 'Date':'Fecha'})
st.plotly_chart(fig,use_container_width=True)



# GRAFICO PIE CHART
pie, bar = st.columns(2)


sectores = df_sp500['GICS Sector'].value_counts()
sectores = sectores.reset_index()
sectores.columns = ['GICS Sector','Cant']



fig = px.pie(sectores,values='Cant',names='GICS Sector')
pie.header('Composición por Sectores')
pie.write(fig)



# GRAFICO DE BARRAS

bar.header('Rentabilidad por Sector')
# st.subheader('1. What is the total amount each customer spent at the restaurant?')
p = alt.Chart(df_sp500.groupby('GICS Sector')['rentabilidad_ponderada'].sum().to_frame().reset_index()).mark_bar().encode(
    x=alt.X('rentabilidad_ponderada', axis=alt.Axis(title='Tasa Rentabilidad Compuesta Anual (%)', titleFontWeight='bold',labelFontSize=16)),
    y=alt.Y('GICS Sector',sort='-x',axis=alt.Axis(title='Sector',labelLimit=200, titleFontWeight='bold',labelFontSize=16))
)
p = p.properties(
    width=600, #alt.Step(120)  # controls width of bar.
    height=400
)
bar.write(p)













distinct_sector=sorted(list(df_sp500['GICS Sector'].unique()))

selected_sector = st.sidebar.multiselect(
    "Elige un sector",
    distinct_sector,distinct_sector)


df_sector = df_sp500[df_sp500['GICS Sector'].isin(selected_sector)]
df_sector.sort_values('rentabilidad_ponderada',ascending=False,inplace=True)
df_sector.reset_index(drop=True, inplace=True)
df_sector['tasa_interes_compuesta'] = round(df_sector['tasa_interes_compuesta']*100,1)
df_sector['Tiempo'] = round(df_sector['Tiempo'],1)




def numerize_column(x):
    return numerize(x)

df_sector['columna_numerizada'] = df_sector['valor_mercado_empresa'].apply(numerize_column)

df_sector['valor_mercado_empresa'] = round(df_sector['valor_mercado_empresa'],0)




df_sector['fecha_inicial'] = df_sector['fecha_inicial'].dt.date

data=df_sector[['GICS Sector','Symbol','Security','fecha_inicial','precio_inicial','precio_actual','Tiempo','tasa_interes_compuesta','pesos','valor_mercado_empresa','columna_numerizada','rentabilidad_ponderada','%Var']]
data.rename(columns={'GICS Sector':'Sector','Symbol':'Símbolo', 'Security':'Empresa', 'fecha_inicial':'Fecha_Inicio','precio_inicial':'Precio_Inicio', 'precio_actual':'Precio_Actual','Tiempo':'Tiempo (años)', 'tasa_interes_compuesta':'Tasa_Compuesta_Anual (%)', 'pesos':'Peso','valor_mercado_empresa':'Valor_Mercado', 'columna_numerizada':'Valor_Mercado_Numerizado', 'rentabilidad_ponderada':'Rentabilidad_Ponderada' },inplace=True)





# GRAFICO DE TREEMAP

# Cargar datos de ejemplo


# Crear treemap



# red = cl.to_numeric(cl.scales['9']['seq']['Reds'])
# black = (0, 0, 0)
# green = cl.to_numeric(cl.scales['9']['seq']['Greens'])

# custom_scale = cl.to_hex(cl.interp(red + [black] + green, 100))




st.header('Treemap de Valor de Mercado por Sector / Empresa (Market Cap)')
fig = px.treemap(data, path=['Sector','Símbolo'], values="Valor_Mercado", color="%Var",
                 color_continuous_scale= [(0, 'rgb(255, 0, 0)'), (0.5, 'rgb(80, 80, 80)'), (1, 'rgb(0, 255, 0)')],labels={'hello'})

# Agregar el treemap a Streamlit
st.plotly_chart(fig,use_container_width=True, width=0, height=0)






# DATAFRAME

st.header('Información por Empresa')
cant_empresas  = data.shape[0]



st.write(f'''
      Sector(es) seleccionado(s): **{selected_sector}**.
      
''')

st.dataframe(data.iloc[:,:-1])

st.write(f'''
      Tamaño: **{cant_empresas} empresas**.
      
''')


hide_st_style='''
            <style>
            header {visibility: hidden;}
            </style>
            '''
st.markdown(hide_st_style, unsafe_allow_html=True)