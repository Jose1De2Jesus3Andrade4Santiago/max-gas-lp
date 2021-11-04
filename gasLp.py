#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tabula
import os
import io
import requests
from bs4 import BeautifulSoup

from datetime import datetime
import pandas as pd
from io import StringIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


# In[2]:


curren_folder =  os.getcwd()
folder_pdf = 'D:\\ACTINVER\\Proyectos actinver\\Z Info Combustibles\\Archivos_pdf'
save_path = 'C:\\Users\\mrchu\\Desktop\\Nueva carpeta (2)'


# # Descarga del archivo PDF

# In[3]:


def get_date():
    '''
    Return the current day and month
    '''
    return datetime.today().strftime('%d-%b')


# In[4]:


def get_url():
    '''
    Find the most recent pdf uploaded to the page and return its url to download 
    '''
    url = "https://www.gob.mx/cre/documentos/precios-maximos-aplicables-de-gas-lp?idiom=es"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')
    a =  soup.find_all(attrs={"class" : "btn btn-default"})
    name = soup.find_all(attrs={"class" : "col-md-10"})
    return 'https://www.gob.mx/' + a[0]['href'], name[0].text


# In[5]:


def download_pdf(url: str):
    '''
    Download a pdf from its url and return it as a list of df
    '''
    data = tabula.read_pdf(url, stream=True,pages='all',pandas_options={'header': None})   
    return data


# # Conversion de PDF a CSV

# In[6]:


def get_name_from_data(pdf_name: str):
    name = pdf_name.lower().replace(' ','_')
    names= name.split('_')
    days = []
    months = []
    year = 0
    try:
        year = int(names[-1][0:4]) 
    except:
        year = 2021

    
    for name in names:
        if len(name) > 0 and len(name) < 3:
            try:
                aux = int(name)
                days.append(aux)
            except:
                pass
        
        if name in ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre']:
            months.append(name)
    return f'{days[0]}-{months[0][0:3]}-{year}', year, months[0][0:3],days[0]


# In[7]:


def send_mail(date: str, destinatario_ : str, content_attached):

    # Iniciamos los parámetros del script
    remitente = 'actinverdc@gmail.com'
    destinatarios = [destinatario_]
    asunto = 'Información de precios Máximos de Gas LP ' + date
    cuerpo = ''
    nombre_adjunto = 'MaximosGasLp.xlsx'

    # Creamos el objeto mensaje
    mensaje = MIMEMultipart()

    # Establecemos los atributos del mensaje
    mensaje['From'] = remitente
    mensaje['To'] = ", ".join(destinatarios)
    mensaje['Subject'] = asunto

    # Agregamos el cuerpo del mensaje como objeto MIME de tipo texto
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Creamos un objeto MIME base
    adjunto_MIME = MIMEBase('application', 'octet-stream')
    # Y le cargamos el archivo adjunto
    adjunto_MIME.set_payload(content_attached)
    # Codificamos el objeto en BASE64
    encoders.encode_base64(adjunto_MIME)
    # Agregamos una cabecera al objeto
    adjunto_MIME.add_header('Content-Disposition', "attachment; filename= %s" % nombre_adjunto)
    # Y finalmente lo agregamos al mensaje
    mensaje.attach(adjunto_MIME)

    # Creamos la conexión con el servidor
    sesion_smtp = smtplib.SMTP('smtp.gmail.com', 587)

    # Ciframos la conexión
    sesion_smtp.starttls()

    # Iniciamos sesión en el servidor
    sesion_smtp.login('actinverdc@gmail.com','Actinver2021')

    # Convertimos el objeto mensaje a texto
    texto = mensaje.as_string()

    # Enviamos el mensaje
    sesion_smtp.sendmail(remitente, destinatarios, texto)

    # Cerramos la conexión
    sesion_smtp.quit()


# In[8]:


def pdf_to_csv():
    '''
    return a csv from a dataframe list
    '''
    pdf_url, pdf_name = get_url()
    df_list = download_pdf(pdf_url)
    #print(pdf_name)
    df = pd.DataFrame()
    
    for data_frame in df_list:
        
        aux = data_frame.dropna(how='all', axis=1,thresh=5)
        aux = aux.dropna(how='all', axis=0,thresh=5)
        aux.columns = ['Región', 'Estado', 'Municipio', 'Precio Litro', 'Precio Kg']
        aux = aux[~aux.Municipio.str.contains('Municipio')]
        #display(aux.head(100))
        df = pd.concat([df, aux],  ignore_index=True)
       
    name,year,month,day = get_name_from_data(pdf_name)
    df = df.assign(Fecha = name)
    date = f'{day} de {month} de {year}'
    
    #Convert the dataframe to bytes-like object
    towrite = io.BytesIO()
    df.to_excel(towrite)  # write to BytesIO buffer
    towrite.seek(0)
    towrite = towrite.read()
    
    #Send te email
    send_mail(date, '314159735@pcpuma.acatlan.unam.mx', towrite)
    
    #df.to_csv(save_path + '\\' + f'MaximosGasLP_{year}_{month}_{day}.csv', index=False, encoding='latin-1')


# In[9]:


pdf_to_csv()


# In[10]:


#print(df_list[0])


# In[11]:


#get_name_from_data('PRECIOS_MA_X_VIGENTES_29_DE_AGOSTO_4_DE_SEPTIEMBRE_2021.pdf')

