import matplotlib.pyplot as plt
import mplfinance as mpf
import yfinance as yf
import streamlit as st
import pandas as pd
import re
from datetime import date
import datetime

st.set_page_config(page_title="Gráfico Diario", page_icon=":chart_with_upwards_trend:",layout='wide')

st.set_option('deprecation.showPyplotGlobalUse', False)

@st.cache_data()
def get_sp500():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    df_sp500 = pd.read_html(url)[0]
    return df_sp500

df_sp500 = get_sp500()


df_sp500['Symbol'].replace('BRK.B','BRK-B',inplace=True)
df_sp500['Symbol'].replace('BF.B','BF-B',inplace=True)
symbols=list(df_sp500['Symbol'].unique())

# Creando un df con solo las columnas del nombre de la empresa y simbolo
tickers=df_sp500.filter(['Security','Symbol'])
tickers['Ticker'] = tickers['Security'] + ' (' + tickers['Symbol'] + ')'
tickers=list(tickers['Ticker'].unique())




selected_ticker = st.sidebar.selectbox('Ingrese Ticker',tickers,index=0)

# Obteniendo del formato "nombre_empresa (ticker)" el "ticker"
regexTicker=re.compile(r'\((\w*[-]?\w*)\)$')
mo=regexTicker.search(selected_ticker)
var=mo.group()[1:-1]



# **********SLIDER***********

# Obtiene el precio
@st.cache_data()
def get_yfinance_price():
    data1=pd.read_csv('imagen/adj_close_hasta_2023_feb_24.csv')
    data1['Date'] = pd.to_datetime(data1['Date'])
    data1.set_index(data1['Date'],inplace=True)
    data1.drop(columns='Date',inplace=True)
    
    data2 = yf.download(symbols,start='2023-02-28',end=date.today() + datetime.timedelta(days=1))['Adj Close']
    data2.reset_index(inplace=True)
    data2['Date'] = pd.to_datetime(data2['Date'])
    data2.set_index(data2['Date'],inplace=True)
    data2.drop(columns='Date', inplace=True)
    
    data=pd.concat([data1,data2])
    return data

data = get_yfinance_price()

# Obtiene el volume
@st.cache_data()
def get_yfinance_volume():
    data1=pd.read_csv('imagen/volume_hasta_2023_feb_24.csv')
    data1['Date'] = pd.to_datetime(data1['Date'])
    data1.set_index(data1['Date'],inplace=True)
    data1.drop(columns='Date',inplace=True)
    
    data2 = yf.download(symbols,start='2023-02-24',end=date.today() + datetime.timedelta(days=1))['Volume']
    data2.reset_index(inplace=True)
    data2['Date'] = pd.to_datetime(data2['Date'])
    data2.set_index(data2['Date'],inplace=True)
    data2.drop(columns='Date', inplace=True)
    
    data=pd.concat([data1,data2])
    return data

volume = get_yfinance_volume()


inicio=data[var].first_valid_index().date()
fin=date.today() #data[var].last_valid_index().date()


fecha_inicio=st.sidebar.slider('Fechas',inicio,fin,fin-datetime.timedelta(days=180))



mm_menor=50
mm_mayor=200
lista=['50 y 200', '5 y 20']

media_movil=st.sidebar.radio('Medias Móviles',lista)

if media_movil==lista[0]:
    tupla=(50,200)
else:
    tupla=(5,20)
 



aapl=yf.Ticker(var)
df=aapl.history(start=fecha_inicio, end=fin + datetime.timedelta(days=1))
# df['MA5'] = df['Close'].rolling(window=50).mean()
# df['MA10'] = df['Close'].rolling(window=200).mean()



mpf.plot(df, type='candle', #addplot=add_plot, 
         mav=tupla, title=f'Gráfico Diario de {selected_ticker}',
         ylabel='Precio de cierre ($)', xlabel='Fecha', 
         figsize=(10, 4),volume=True)
st.pyplot()



## Recomendación

def volume_outlier(data):
    
    data=data.tail(20)
    bp=plt.boxplot(data)
    if data.iloc[-1] in bp['fliers'][0].get_data()[1] and data.iloc[-1]>data.iloc[-2]:
        return 'ok'
    else:
        return 'error'
    
resultado = volume.apply(volume_outlier, axis=0)

resultado=resultado.reset_index()
resultado.columns=['ticker','resultado']
resultado=resultado[resultado['resultado']=='ok']
resultado.reset_index(drop=True,inplace=True)

if st.button('**Mostrar Recomendación**'):
    st.header('Recomendación:')
    st.write(resultado.iloc[:,0])






hide_st_style='''
            <style>
            header {visibility: hidden;}
            </style>
            '''
st.markdown(hide_st_style, unsafe_allow_html=True)