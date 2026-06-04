import csv, os

# Ruta base: carpeta donde está este archivo
BASE = os.path.dirname(os.path.abspath(__file__)) #Obtiene la carpeta donde está este archivo.
EMPLEADOS_PATH   = os.path.join(BASE, 'data', 'empleados.csv')   #Ruta absoluta a empleados.csv.
SOLICITUDES_PATH = os.path.join(BASE, 'data', 'solicitudes.csv') #Ruta absoluta a solicitudes.csv.

# ─── EMPLEADOS ───────────────────────────────────────────────
print("EMPLEADOS")
print("─" * 65)
print(f'{"Legajo":<8} {"Nombre":<20} {"Area":<12} {"Disponibles":>11} {"Tomados":>8}')
print("─" * 65)

with open(EMPLEADOS_PATH, "r", encoding="utf-8") as f: #Abre empleados.csv en modo lectura.
    dict_empleados = csv.DictReader(f) #Lee el CSV como lista de diccionarios, usando la primera fila como claves.
    for emp in dict_empleados: #Por cada empleado en el CSV...
        disponibles = int(emp["dias_disponibles"]) #Convierte dias_disponibles de string a entero.
        tomados     = int(emp["dias_tomados"])     #Convierte dias_tomados de string a entero.
        print(f"{emp["legajo"]:<8} {emp["nombre"]:<20} {emp["area"]:<12} {disponibles:>11} {tomados:>8}")

# ─── SOLICITUDES ─────────────────────────────────────────────
print()

with open(SOLICITUDES_PATH, "r", encoding="utf-8") as f: #Abre solicitudes.csv en modo lectura.
    dict_solicitudes = list(csv.DictReader(f)) #Lee el CSV como lista de diccionarios.

print(f"SOLICITUDES REGISTRADAS: {len(dict_solicitudes)}") #Muestra la cantidad de solicitudes registradas.
if dict_solicitudes: #Si hay solicitudes registradas...
    print("─" * 75)
    for sol in dict_solicitudes: #Por cada solicitud en el CSV...
        print(f"  {sol["id"]} | {sol["nombre"]:<20} | {sol["dias"]} dias | {sol["fecha_inicio"]} → {sol["fecha_fin"]} | {sol["estado"]}")
else: #Si no hay solicitudes registradas...
    print("(sin solicitudes registradas)")