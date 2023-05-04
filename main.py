import os
import PyPDF2
from fastapi import FastAPI, File, UploadFile, Response, Form
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND, HTTP_200_OK
from model.user_connection import UserConnection
from utils import funciones
from datetime import datetime
from werkzeug.utils import secure_filename
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()
conn = UserConnection()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



"""
Keyword arguments: list, id
argument -- Inserta el analisis final de un documento
Return: Response 204
"""
@app.put("/api/update_document/{id_document}", status_code=HTTP_204_NO_CONTENT)
async def update_documents(list, id: int):
    data = list
    conn.update_documents(data)
    return Response(status_code=HTTP_204_NO_CONTENT)

#---------------------------------------------------------------------------------#
#--------------- Creator, Producer y Autor Consulta ------------------------------#
#---------------------------------------------------------------------------------#

"""
Keyword arguments: creator
argument -- Cuenta las couidencias de un creador en la blacklist
Return: array -> data
"""
@app.get("/api/consulta_creator", status_code=HTTP_200_OK)
async def consulta_creator(creator: str):
    data = conn.consulta_creator(creator)
    return data

"""
Keyword arguments: producer
argument -- Cuenta las couidencias de un productor en la blacklist
Return: array -> data
"""
@app.get("/api/consulta_producer", status_code=HTTP_200_OK)
async def consulta_producer(producer: str):
    data = conn.consulta_producer(producer)
    return data

"""
Keyword arguments: autor
argument -- Cuenta las couidencias de un autor en documentos apocrifos
Return: array -> data 
"""
@app.get("/api/consulta_autor", status_code=HTTP_200_OK)
async def consulta_autor(autor: str):
    data = conn.consulta_autor(autor)
    return data


#---------------------------------------------------------------------------------#
#--------------- GET -------------------------------------------------------------#
#---------------------------------------------------------------------------------#

"""
Keyword arguments: name, phone, dni, file
argument -- devuelve el resultado del analisis de un documento
Return: resultado
"""
@app.post("/uploadfile/{name}/{phone}/{dni}")
async def create_upload_file(name: str, phone: int, dni: int, files: List[UploadFile] = File(...)):

    now = datetime.now()
    time = now.strftime("%Y%H%M%S")

    resultados = []
    for file in files:

        document = file

        if document != '':
            newName = time + document.filename
            with open("./uploads/"+newName, "wb") as f:
                f.write(file.file.read())

        if not os.path.exists("uploads"):
            os.mkdir("uploads")

        ruta = 'uploads/' + newName

        filename = secure_filename(document.filename)
        extension = filename.rsplit('.', 1)[1].lower()

        if extension != 'pdf':
            tipo = 'img'
            print('Analizando imagen: ' + filename)

            # Analizar la imagen utilizando diferentes técnicas.
            results = {}
            results['tipo'] = tipo
            results['filename'] = document.filename
            results['manipulation'] = funciones.detect_manipulation(ruta)
            #results['manipulation_pattern'] = funciones.detect_manipulation_pattern(ruta)
            #results['noise'] = funciones.detect_noise(ruta)
            #results['metadata'] = funciones.detect_metadata(ruta)
            #results['compression'] = funciones.detect_compression(ruta)
            #results['brightness'] = funciones.analyze_brightness(ruta)
        else:
            pdfReader = PyPDF2.PdfReader(open(ruta, 'rb'))
            info = pdfReader.metadata
            creatorName = str(info.get('/Creator'))
            autorName = str(info.get('/Author'))
            creationdate = info.get('/CreationDate')
            moddate = info.get('/ModDate')
            producerName = str(info.get('/Producer'))
            title = str(info.get('/Title'))
            funciones.ultima_fecha(ruta)
            fecha = funciones.ultima_fecha(ruta)
            funciones.ultima_fecha_hora(ruta)
            hora = funciones.ultima_fecha_hora(ruta)

            funciones.creacion_fecha(creationdate, moddate)
            creation_date = funciones.creacion_fecha(creationdate, moddate)

            funciones.creacion_fecha_hora(creationdate, moddate)
            creacion_fecha_hora = funciones.creacion_fecha_hora(creationdate, moddate)

            funciones.modifica_fecha(moddate)
            modifica_fecha = funciones.modifica_fecha(moddate)

            funciones.modifica_fecha_hora(moddate, info)
            modifica_fecha_hora = funciones.modifica_fecha_hora(moddate, info)

            id = conn.consulta_id()

            data = {
                'creator': creatorName,
                'autor': autorName,
                'produccer': producerName,
                'title': title,
                'creation_date': creation_date,
                'last_date': fecha,
                'id_document': id
            }

            await update_documents(data, id)
            creatorCont = await consulta_creator(creatorName)
            authorCont = await consulta_autor(autorName)
            producerCont = await consulta_producer(producerName)
            tipo = 'pdf'
            id_apocrifo = conn.next_id_apocrifo()
            id_status = conn.consulta_id()

            data = {
                'tipo': tipo,
                'creation_date': creation_date,
                'creacion_fecha_hora': creacion_fecha_hora,
                'modifica_fecha': modifica_fecha,
                'modifica_fecha_hora': modifica_fecha_hora,
                'fecha': fecha,
                'hora': hora,
                'creatorCont': creatorCont,
                'authorCont': authorCont,
                'producerCont': producerCont,
                'creatorName': creatorName,
                'autorName': autorName,
                'producerName': producerName,
                'name': name,
                'phone': phone,
                'dni': dni,
                'id_apocrifo': id_apocrifo,
                'id_status': id_status,
            }

            data = list(data.values())

            resultado = await analisis_endpoint(data)

            results = {}
            results['filename'] = document.filename
            results['resultado'] = resultado
        
        resultados.append(results)

    return resultados

#---------------------------------------------------------------------------------#
#--------------- Analisis  -------------------------------------------------------#
#---------------------------------------------------------------------------------#

"""
Keyword arguments: list
argument -- Realiza el analisis de un documento cuando es pdf
Return: resultado
"""
@app.post("/analisis/")
async def analisis_endpoint(list):
    tipo = list[0]
    creacion_fecha = list[1]
    creacion_fecha_hora = list[2]
    modifica_fecha = list[3]
    modifica_fecha_hora = list[4]
    fecha = list[5]
    hora = list[6]
    creatorCont = list[7]
    authorCont = list[8]
    producerCont = list[9]
    creatorName = list[10]
    autorName = list[11]
    producerName = list[12]
    name = list[13]
    phone = list[14]
    dni = list[15]
    id_apocrifo = list[16]
    id_document = list[17]

    data = {
        "creator": creatorName,
        "autor": autorName,
        "producer": producerName,
        "name": name,
        "phone": phone,
        "dni": dni,
        'id_apocrifo': id_apocrifo
    }

    apocrifo = {
        'status': 'APOCRIFO',
        'id_document': id_document
    }

    autentico = {
        'status': 'AUTENTICO',
        'id_document': id_document
    }
    

    tipo = 'pdf'
    date = creacion_fecha + 9305
    hour = 144500

    if creatorCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif authorCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo o el autor de este documento ha intentado subir documentos posiblemente apocrifos anteriormente"
    elif producerCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha != modifica_fecha:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha_hora != modifica_fecha_hora:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha == 0:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif date > fecha:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif hour > hora:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        resultado = "Este documento posiblemente es apocrifo"
    else:
        conn.status(autentico)
        resultado = "Este docuemto es autentico"

    return resultado

