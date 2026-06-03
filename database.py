import csv #Importa el módulo para leer y escribir archivos CSV.
import os #Importa el módulo para trabajar con rutas y archivos del sistema.
from datetime import datetime #Importa datetime para generar el ID de la solicitud.

EMPLEADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "empleados.csv") #Construye la ruta absoluta al archivo empleados.csv.
SOLICITUDES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "solicitudes.csv") #Construye la ruta absoluta al archivo solicitudes.csv.

def buscar_empleado(legajo): #Permite buscar el legajo de un empleado en el dataset de empleados, y crea un diccionario con los datos del mismo.
  with open(EMPLEADOS, "r", encoding="utf-8") as f: #Abre el archivo empleados.csv en modo lectura.
      dict_empleados = csv.DictReader(f) #Lee el CSV como lista de diccionarios, usando la primera fila como claves.
      for i in dict_empleados: #Se repite por cada elemento del diccionario.
        if i["legajo"].upper() == legajo.upper(): #Compara el legajo de la fila con el buscado, reemplaza los valores numericos de formato string a entero, y devuelve el diccionario.
          i["dias_disponibles"] = int(i["dias_disponibles"])
          i["dias_tomados"] = int(i["dias_tomados"])
          return i
  return None #Si no encuentra el legajo, devuelve None.

def verificar_saldo(legajo, dias_solicitados): #Verifica que los dias solicitados por el empleado no excedan los dias disponibles.
    empleado = buscar_empleado(legajo) #Busca al empleado en el dataset.
    if not empleado: #Si el empleado no existe, devuelve False.
      return False
    return empleado["dias_disponibles"] >= dias_solicitados #Si el empleado existe, verifica que los dias solicitados sean menores o iguales a lo dias disponibles. Devuelve un booleano.

def registrar_solicitud(legajo, dias, fecha_inicio, fecha_fin): #Funcion que registra la solicitud de vacaciones del empleado y descuenta los dias disponibles.
    id_solicitud = f"SOL-{datetime.now().strftime('%Y%m%d%H%M%S')}" #Genera un ID único combinando "SOL-" con la fecha y hora actual.
    empleados = [] #Lista donde se van a guardar todas las filas del CSV
    with open(EMPLEADOS, "r", encoding="utf-8") as f: #Abre empleados.csv en modo lectura.
        dict_empleados = csv.DictReader(f) #Variable que contiene una lista de diccionarios con los datos del CSV.
        encabezado = dict_empleados.fieldnames #Variable que contiene los nombres de las columnas.
        for i in dict_empleados: #Por cada diccionario en la lista de diccionarios...
          if i["legajo"].upper() == legajo.upper(): #Si esta fila es el empleado que hizo la solicitud...
            i["dias_disponibles"] = int(i["dias_disponibles"]) - dias  #Descuenta los días solicitados del saldo.
            i["dias_tomados"] = int(i["dias_tomados"]) + dias #Suma los días al contador de días tomados
          empleados.append(i) #Agrega la fila a la lista de empleados.

    with open(EMPLEADOS, "w", encoding="utf-8", newline="") as f: #Abre empleados.csv en modo escritura.
        writer = csv.DictWriter(f, fieldnames=encabezado) #Crea el escritor usando las columnas guardadas antes.
        writer.writeheader() #Escribe la primera fila con los nombres de columnas.
        writer.writerows(empleados) #Escribe todas las filas de empleados con el saldo actualizado.

    existe = os.path.exists(SOLICITUDES) #Verifica si solicitudes.csv ya existe.
    with open(SOLICITUDES, "a", encoding="utf-8", newline="") as f: #Abre solicitudes.csv en modo append.
      writer = csv.DictWriter(f, fieldnames=["id","legajo","nombre","dias","fecha_inicio","fecha_fin","estado"]) #Define las columnas del archivo de solicitudes.
      if not existe: #Si el archivo no existe...
        writer.writeheader() #Escribe el encabezado con los nombres de columnas.
      nombre = buscar_empleado(legajo)["nombre"] if buscar_empleado(legajo) else legajo #Variable que contiene el nombre del empleado.
      writer.writerow({ #Escribe una nueva fila con los datos de la solicitud.
          "id":          id_solicitud,
          "legajo":      legajo.upper(),
          "nombre":      nombre,
          "dias":        dias,
          "fecha_inicio": fecha_inicio,
          "fecha_fin":   fecha_fin,
          "estado":      "APROBADA",})

    return id_solicitud #Retorna el ID para mostrárselo al usuario como comprobante.


def obtener_solicitudes(legajo): #Funcion que devuelve las solicitudes registradas para un legajo.
    if not os.path.exists(SOLICITUDES): #Si solicitudes.csv no existe todavía...
        return [] #Retorna una lista vacía.
    with open(SOLICITUDES, "r", encoding="utf-8") as f: #Abre solicitudes.csv en modo lectura.
        dict_empleados = csv.DictReader(f) #Variable que contiene una lista de diccionarios con los datos del CSV.
        return [fila for fila in dict_empleados if fila["legajo"] == legajo.upper()] #Retorna solo las filas que corresponden al legajo buscado.
