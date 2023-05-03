from datetime import date
from pydantic import BaseModel
from typing import Optional
from fastapi import UploadFile, File

class UserSchema(BaseModel):
    name: str
    dni: int
    id_ciudad: int
    phone: int
    email: str
    address: str
    photo: Optional[str]

class InvestigatorSchema(BaseModel):
    id_user: int
    id_product: Optional[int]
    id_service: Optional[int]
    id_city: int
    id_investigator: int
    value: int
    document: Optional[str]

class InvestigatorsSchema(BaseModel):
    name: str
    dni: int

class DocumentsSchema(BaseModel):
    id_user: Optional[int]
    id_city: Optional[int]
    id_investigator: Optional[int]
    creator: Optional[str]
    autor: Optional[str]
    produccer: Optional[str]
    title: Optional[str]
    creationdate: int
    last_date: int

class AnalisisSchema(BaseModel):
    status: str

class ApocrifoSchema(BaseModel):
    creator: str
    autor: str
    producer: str
    name: str
    phone: int
    dni: int

class AnalisisPdfSchema(BaseModel):
    tipo: str
    creacion_fecha: int
    creacion_fecha_hora: int
    modifica_fecha: int
    modifica_fecha_hora: int
    fecha: int
    hora: int
    creatorCont: int
    authorCont: int
    producerCont: int
    creatorName: str
    autorName: str
    producerName: str
    _name_client: str
    _phone: str
    _dni: str

class Resultado(BaseModel):
    tipo : str
    creacion_fecha : int
    creacion_fecha_hora: int
    modifica_fecha: int
    modifica_fecha_hora: int
    fecha: int
    hora: int
    creatorCont: int
    authorCont: int
    producerCont: int
    creatorName: str
    autorName: str
    producerName: str
    _name_client: str
    _phone: str
    _dni: str

class DocumentoShema(BaseModel):
    document: UploadFile = File(...)

class Datos(BaseModel):
    tipo: str
    creation_date: int
    creacion_fecha_hora: int
    modifica_fecha: int
    modifica_fecha_hora: int
    fecha: int
    hora: int
    creatorCont: int
    authorCont: int
    producerCont: int
    creatorName: str
    autorName: str
    producerName: str


class productservices(BaseModel):
    name: str
    id_type: int
    report_date: date