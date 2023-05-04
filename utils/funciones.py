import os
import time
import numpy as np
import cv2
import piexif
import imghdr
from scipy import fftpack
from datetime import datetime


# Funciones para detectar si un pdf ha sido modificado
# -----------------Pdf-----------------------------------
#-------------------------------------------------------

# Funcion para ver la fecha de modificacion 
def ultima_fecha(ruta):

    estado = os.stat(ruta)
    ultima_fe = time.localtime(estado.st_mtime)
    day = int(ultima_fe[0]) 
    month = int(ultima_fe[1])
    year = int(ultima_fe[2])
    cero = 0

    if month < 10:
        month = ('{}{}'.format(cero,month))

    if year < 10:
        year = ('{}{}'.format(cero,year))

    ultima_fe = int(('{}{}{}'.format(day,month,year)))

    return ultima_fe

# Funcion para ver la hora de modificacion
def ultima_fecha_hora(ruta):

    estado = os.stat(ruta)
    ultima_fe = time.localtime(estado.st_mtime)    
    hora = int(ultima_fe[3])
    minu = int(ultima_fe[4])
    secon = '00'
    cero = 0

    if hora < 10:
        hora = ('{}{}'.format(cero,hora))

    if minu < 10:
        minu = ('{}{}'.format(cero,minu))
    
    hour = int(('{}{}{}'.format(hora,minu,secon)))
    
    return hour

# Fecha de creacion del documento
def creacion_fecha(creationdate, moddate):

    if creationdate != None:
        year = creationdate[2:6]
        day = creationdate[6:8]
        month = creationdate[8:10]
        creation_date = int(('{}{}{}'.format(year,day,month)))
    else:
        year = '00'
        day = '00'
        month = '00'
        creation_date = int(('{}{}{}'.format(year,day,month)))

    return creation_date

# Hora de creacion del documento
def creacion_fecha_hora(creationdate, moddate):

    if creationdate != None:
        hour = creationdate[10:12]
        minu = creationdate[12:14]
        secon = '00'
        cero = 0

        creation_hora = int(('{}{}{}'.format(hour,minu,secon)))
    else:
        hour = '00'
        minu = '00'
        secon = '00'
        cero = 0
        creation_hora = int(('{}{}{}'.format(hour,minu,secon)))

    return creation_hora

# Fecha de modificacion desde metadatos
def modifica_fecha(moddate):

    if moddate != None:
        year = moddate[2:6]
        day = moddate[6:8]
        month = moddate[8:10]
        modifi = int(('{}{}{}'.format(year,day,month)))
    else:
        year = '00'
        day = '00'
        month = '00'
        modifi = int(('{}{}{}'.format(year,day,month)))

    return modifi

# Hora de modificacion desde metadatos
def modifica_fecha_hora(moddate, info):

    if moddate != None:
        hour = moddate[10:12]
        minu = moddate[12:14]
        secon = '00'
        cero = 0

        modifi_hora = int(('{}{}{}'.format(hour,minu,secon)))
    else:
        creationdate = info.get('/CreationDate')
        hour = creationdate[10:12]
        minu = creationdate[12:14]
        secon = '00'
        cero = 0

        modifi_hora = int(('{}{}{}'.format(hour,minu,secon)))

    return modifi_hora

# Funciones para detectar si un imagen ha sido Manipulada
# -----------------IMG-----------------------------------
#-------------------------------------------------------

# Funcion con la metodologia de Transformada de Fourier
def detect_manipulation(image_path):
    # Cargue de imagen y conviértada a escala de grises
    img = cv2.imread(image_path)

    # Verificar si la imagen se ha cargado correctamente
    if img is None:
        print("Error: no se pudo cargar la imagen.")
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculo de FFT 2D de la imagen
    fft = fftpack.fft2(gray)

    # Desplazamiento del componente de frecuencia desde cero al centro
    fft_shift = fftpack.fftshift(fft)

    # Calculo de espectro de magnitud de la transformada de Fourier
    magnitude_spectrum = np.abs(fft_shift)

    # Calculo del espectro de fase de la transformada de Fourier
    phase_spectrum = np.angle(fft_shift)

    # Calculo del registro del espectro de magnitud (visualización)
    log_magnitude_spectrum = np.log(magnitude_spectrum + 1)

    # Umbral del espectro de magnitud para identificar regiones manipuladas
    threshold = 0.9 * np.max(log_magnitude_spectrum)
    manipulated_regions = log_magnitude_spectrum > threshold

    # Calculo de FFT 2D inversa de la transformada de Fourier manipulada
    fft_shift[manipulated_regions] = 0
    manipulated_fft = fftpack.ifftshift(fft_shift)
    manipulated_image = np.real(fftpack.ifft2(manipulated_fft))

    # Convierte la imagen manipulada a escala de grises
    manipulated_image = manipulated_image.astype(np.uint8)

    # Calculo de la diferencia entre las imágenes original y manipula
    difference = cv2.absdiff(gray, manipulated_image)

    # Umbral de la diferencia para identificar regiones manipuladas
    threshold = 30
    manipulated_regions = difference > threshold

    # Cuenta el número de píxeles manipulados y el total de píxeles
    num_manipulated_pixels = np.sum(manipulated_regions)
    total_pixels = manipulated_regions.size

    # Calculo del porcentaje de píxeles manipulados
    percent_manipulated = 100 * num_manipulated_pixels / total_pixels

    # Devuelve True si la imagen ha sido manipulada, False en caso contrario

    if percent_manipulated > 0.1:
        return 1
    else:
        return 0

    # return percent_manipulated > 0.1

# Funcion con la metodologia de Laplaciano (Analisis de manipulacion de patrones)
def detect_manipulation_pattern(image_path):
    # Carga la imagen y la convierte a escala de grises.
    img = cv2.imread(image_path)
    
    # Verificar si la imagen se ha cargado correctamente
    if img is None:
        print("Error: no se pudo cargar la imagen.")
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Calcula el Laplaciano de la imagen en escala de grises
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    # Calcula la varianza del laplaciano
    variance = np.var(laplacian)

    # Retorna True si la varianza está por debajo de cierto umbral,
    # indicando que la imagen ha sido manipulada
    return variance < 100

# Funcion con la metodologia de Laplaciano (Analisis de ruido)
def detect_noise(image_path, threshold=10):
    # Carga la imagen y conviérte a escala de grises
    img = cv2.imread(image_path)

    # Comprobar si la imagen se ha cargado correctamente
    if img is None:
        print("Error: could not load image.")
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calcula el Laplaciano de la imagen para detectar bordes
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)

    # Calcula la desviación estándar del Laplaciano para medir el ruido
    std_dev = np.std(laplacian)

    # Comprobar si la desviación estándar está por debajo del umbral
    if std_dev < threshold:
        return False
    else:
        return True
    
# Funcion con la metodologia de analisis de Metadata
def detect_metadata(image_path):
    # Comprobar si la imagen es JPEG o TIFF
    if imghdr.what(image_path) not in ['jpeg', 'tiff']:
        return False

    # Carga la imagen y extrae los datos EXIF
    exif_data = piexif.load(image_path)

    # Comprueba si la imagen tiene datos EXIF
    if exif_data:
        return True
    else:
        return False
    
# Funcion con la metodologia de analisis de compresion
def detect_compression(image_path):
    # Obtiene el tamaño origina de la imagen
    original_size = os.path.getsize(image_path)

    # Carga la imagen y la comprime en JPEG
    img = cv2.imread(image_path)
    _, encoded_img = cv2.imencode('.jpg', img)

    # Obtiene el tamaño de la imagen comprimida
    compressed_size = len(encoded_img)

    # Calcula la relación de compresión
    compression_ratio = compressed_size / original_size

    # Comprueba si la relación de compresión está por encima de un umbral
    threshold = 0.9
    if compression_ratio < threshold:
        return True
    else:
        return False

# Funcion con la metodologia de analisis de brillo
def analyze_brightness(image_path):
    # Carga la imagen
    img = cv2.imread(image_path)

    # Convertir la imagen a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calcula el valor de píxel promedio de la imagen en escala de grises
    average_brightness = cv2.mean(gray)[0]

    # Devuelva True si el brillo promedio es demasiado alto o demasiado bajo
    if average_brightness < 50 or average_brightness > 200:
        return True
    else:
        return False