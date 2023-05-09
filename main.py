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
#--------------- GET LOG CASOS----------------------------------------------------#
#---------------------------------------------------------------------------------#

"""
Keyword arguments: None
argument -- Consulta los casos de un documento
Return: array -> data
"""
@app.get("/api/log_casos", status_code=HTTP_200_OK)
async def read_log_casos():
    data = conn.read_log_casos()
    return data

"""
Keyword arguments: Id
argument -- consulta los casos de un documento por id
Return: array -> data
"""
@app.get("/api/log_casos/{id}", status_code=HTTP_200_OK)
async def read_log_casos_id(id: int):
    data = conn.read_log_casos_id(id)
    return data



#---------------------------------------------------------------------------------#
#--------------- POST-------------------------------------------------------------#
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
            data = {
                'name': name,
                'dni': dni,
                'newName': newName,
                'log_caso': 0,
            }

            data.update({'log_caso': 0})

            tipo = 'img'
            
            # Analizar la imagen utilizando diferentes técnicas.
            results = {}
            results['tipo'] = tipo
            results['filename'] = document.filename
            results['resultado'] = funciones.detect_manipulation(ruta)
            #results['manipulation_pattern'] = funciones.detect_manipulation_pattern(ruta)
            results['noise'] = funciones.detect_noise(ruta)
            results['metadata'] = funciones.detect_metadata(ruta)
            results['compression'] = funciones.detect_compression(ruta)
            results['brightness'] = funciones.analyze_brightness(ruta)
            if results['resultado'] == 'La imagen probablemente no ha sido Manipulada':
                if results['metadata'] != True:
                    results['resultado'] = 'La imagen probablemente no ha sido Manipulada'
                    data.update({'log_caso': 221})
                    conn.log_casos(data)
                else:
                    results['resultado'] = 'La imagen probablemente ha sido Manipulada'
                    data.update({'log_caso': 211})
                    conn.log_casos(data)
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
                # 'fecha': fecha,
                # 'hora': hora,
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
                'newName': newName,
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
    # fecha = list[5]
    # hora = list[6]
    creatorCont = list[5]
    authorCont = list[6]
    producerCont = list[7]
    creatorName = list[8]
    autorName = list[9]
    producerName = list[10]
    name = list[11]
    phone = list[12]
    dni = list[13]
    id_apocrifo = list[14]
    id_document = list[15]
    newName = list[16]

    data = {
        "creator": creatorName,
        "autor": autorName,
        "producer": producerName,
        "name": name,
        "phone": phone,
        "dni": dni,
        'id_apocrifo': id_apocrifo,
        'newName': newName
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
    date = creacion_fecha
    hour = 144500

    if creatorCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 111
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif producerCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 112
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha == 0 and modifica_fecha != 0:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 113
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha_hora != modifica_fecha_hora:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 114
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif creacion_fecha == 0:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 115
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo"
    elif authorCont >= 1:
        conn.status(apocrifo)
        conn.info_apocrifo(data)
        log_caso = 116
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este documento posiblemente es apocrifo o el autor de este documento ha intentado subir documentos posiblemente apocrifos anteriormente"
    # elif date > fecha:
    #     conn.status(apocrifo)
    #     conn.info_apocrifo(data)
    #     resultado = "Este documento posiblemente es apocrifo"
    # elif hour > hora:
    #     conn.status(apocrifo)
    #     conn.info_apocrifo(data)
    #     resultado = "Este documento posiblemente es apocrifo"
    else:
        conn.status(autentico)
        log_caso = 121
        data['log_caso'] = log_caso
        conn.log_casos(data)
        resultado = "Este docuemto es autentico"

    return resultado



