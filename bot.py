from datetime import datetime, timedelta  #Importa datetime para manejar fechas y timedelta para calcular la fecha de fin.
from database import buscar_empleado, verificar_saldo, registrar_solicitud  #Importa las funciones de acceso a datos desde database.py.

#Constantes que representan cada estado posible de la máquina de estados.
#Cada una corresponde a un paso del diagrama BPMN.
ESTADO_INICIO = "INICIO" #Estado inicial, muestra el menú principal.
ESTADO_IDENTIFICACION = "IDENTIFICACION" #Esperando que el usuario ingrese su legajo.
ESTADO_SOLICITUD_DIAS = "SOLICITUD_DIAS" #Esperando que el usuario ingrese la cantidad de días.
ESTADO_VALIDAR_SALDO = "VALIDAR_SALDO" #El sistema verifica el saldo disponible (tarea de servicio).
ESTADO_INGRESO_FECHA = "INGRESO_FECHA" #Esperando que el usuario ingrese la fecha de inicio.
ESTADO_CONFIRMACION = "CONFIRMACION" #Esperando que el usuario confirme o cancele la solicitud.

class VacaBot:  #Define la clase principal del chatbot.

    def __init__(self):  #Método constructor, se ejecuta al crear una instancia de VacaBot.
        self.reiniciar()  #Llama a reiniciar() para inicializar todos los atributos de la sesión.

    def reiniciar(self): #Resetea todos los atributos de la sesión a sus valores iniciales.
        self.estado = ESTADO_INICIO #El estado vuelve al inicio del flujo.
        self.empleado = None #No hay empleado identificado.
        self.dias = None #No hay cantidad de días definida.
        self.fecha_inicio = None #No hay fecha de inicio definida.
        self.fecha_fin = None #No hay fecha de fin calculada.
        self.reintentos = 0 #Contador de errores consecutivos en cero.
        self.modo_consulta = False #No está en modo consulta de saldo.

    def procesar(self, entrada): #Método principal que recibe el input del usuario y lo dirige al estado correspondiente.
        entrada = entrada.strip() #Elimina espacios en blanco al inicio y al final del input.
        if entrada.lower() in ("salir", "exit", "cancelar"): #Si el usuario quiere salir en cualquier momento...
            self.reiniciar() #Resetea la sesión.
            return self._respuesta_cancelacion() #Retorna el mensaje de cancelación.
        estados = { #Diccionario que mapea cada estado con su metodo.
            ESTADO_INICIO: self._estado_inicio,
            ESTADO_IDENTIFICACION: self._estado_identificacion,
            ESTADO_SOLICITUD_DIAS: self._estado_solicitud_dias,
            ESTADO_VALIDAR_SALDO: self._estado_validar_saldo,
            ESTADO_INGRESO_FECHA: self._estado_ingreso_fecha, 
            ESTADO_CONFIRMACION: self._estado_confirmacion, 
        }
        metodo_actual = estados.get(self.estado) #Obtiene el estado correspondiente al momento actual.
        return metodo_actual(entrada) if metodo_actual else "Estado desconocido. Escribi 'salir' para reiniciar." #Ejecuta el estado si existe, si no retorna mensaje de error.

    def _estado_inicio(self, entrada): #Estado INICIO, gestiona el menú principal.
        if entrada in ("1", "solicitar"): #Si el usuario elige opción 1...
            self.estado = ESTADO_IDENTIFICACION #Avanza al estado de identificación.
            return "
SOLICITUD DE VACACIONES
" + "─"*35 + "
Ingresa tu numero de legajo:
"
        elif entrada in ("2", "consultar"): #Si el usuario elige opción 2...
            self.estado = ESTADO_IDENTIFICACION #Avanza al estado de identificación.
            self.modo_consulta = True #Activa el modo consulta de saldo.
            return "
CONSULTA DE SALDO
" + "─"*35 + "
Ingresa tu numero de legajo:
"
        else: #Si el input no es válido...
            self.reintentos += 1 #Incrementa el contador de reintentos.
            if self.reintentos >= 3: #Si superó 3 intentos fallidos...
                self.reintentos = 0 #Resetea el contador.
                return "Demasiados intentos. Escribe 1 o 2.
"
            return "Opcion no valida. Escribe 1 o 2.
"

    def _estado_identificacion(self, entrada): #Estado IDENTIFICACION, valida el legajo ingresado.
        if not entrada.upper().startswith("E") or len(entrada) != 4: #Si el formato no es correcto...
            return "Formato incorrecto. Debe ser E seguido de 3 numeros
Legajo: " #Pide reingresar.
        empleado = buscar_empleado(entrada) #Busca el legajo en la base de datos.
        if not empleado: #Si el legajo no existe en el CSV...
            self.reintentos += 1 #Incrementa el contador de reintentos.
            if self.reintentos >= 3: #Si superó 3 intentos fallidos...
                self.reintentos = 0 #Resetea el contador.
                return "Legajo no encontrado tras varios intentos. Verifica con RRHH.
Escribe 'salir' o intenta otro legajo: "
            return f"Legajo '{entrada.upper()}' no existe. Intenta de nuevo: "
        self.empleado  = empleado #Guarda los datos del empleado en la sesión.
        self.reintentos = 0 #Resetea el contador de reintentos.
        if self.modo_consulta: #Si está en modo consulta de saldo...
            self.reiniciar() #Resetea la sesión al terminar la consulta.
            return (f"
{empleado['nombre']} ({empleado['area']})"
                    f"
Dias disponibles: {empleado['dias_disponibles']}"
                    f"
Dias tomados: {empleado['dias_tomados']}"
                    f"
Total anual: 20
"
                    f"
1 → Solicitar vacaciones
2 → Consultar saldo
salir → Salir
") #Muestra el saldo y vuelve al menú.
        self.estado = ESTADO_SOLICITUD_DIAS #Si no es consulta, avanza al estado de solicitud de días.
        return (f"
Bienvenido, {empleado['nombre']} ({empleado['area']})"
                f"
Dias disponibles: {empleado['dias_disponibles']}
"
                f"
¿Cuantos dias quieres solicitar? ") #Muestra bienvenida y solicita cantidad de días.

    def _estado_solicitud_dias(self, entrada): #Estado SOLICITUD_DIAS, valida la cantidad de días ingresada.
        if not entrada.isdigit(): #Si el input no es un número entero, retorna mensaje de error.
            return "Ingresa un numero entero.
¿Cuantos dias? " 
        dias = int(entrada) #Convierte el input a entero.
        if dias <= 0: #Si el número es cero o negativo, retorna mensaje de error.
            return "La cantidad debe ser mayor a cero.
¿Cuantos dias? "
        if dias > 30: #Si el número supera el máximo permitido,retorna mensaje de error.
            return "No puedes solicitar mas de 30 dias por solicitud.
¿Cuantos dias? "
        self.dias  = dias #Guarda la cantidad de días en la sesión.
        self.estado = ESTADO_VALIDAR_SALDO #Avanza al estado de validación de saldo.
        return self._estado_validar_saldo(entrada) #Llama directamente al estado de validación (tarea de servicio automática).

    def _estado_validar_saldo(self, entrada): #Estado VALIDAR_SALDO, consulta el saldo en la base de datos.
        saldo_ok = verificar_saldo(self.empleado["legajo"], self.dias) #Consulta si el empleado tiene saldo suficiente.
        if not saldo_ok: #Si el saldo es insuficiente...
            disponibles = self.empleado["dias_disponibles"] #Obtiene los días disponibles del empleado.
            self.estado = ESTADO_SOLICITUD_DIAS #Vuelve al estado de solicitud de días.
            if disponibles == 0: #Si no tiene ningún día disponible,retorna mensaje de error.
                return "
Sin saldo disponible este año. Contacta a RRHH.
Escribe 'salir' o una nueva cantidad: "
            return (f"
Pediste {self.dias} dias pero solo tienes {disponibles} disponibles."
                    f"
Ingresa una nueva cantidad (max {disponibles}): ")
        self.estado = ESTADO_INGRESO_FECHA  #Si el saldo es suficiente, avanza al estado de ingreso de fecha.
        return (f"
Saldo OK: {self.dias} dias verificados."
                f"
¿Fecha de inicio? Formato DD/MM/AAAA
: ")  #Solicita la fecha de inicio.

    def _estado_ingreso_fecha(self, entrada):  #Estado INGRESO_FECHA, valida la fecha ingresada por el usuario.
        try:
            fecha = datetime.strptime(entrada, "%d/%m/%Y") #Intenta convertir el input al formato DD/MM/AAAA.
        except ValueError: #Si el formato es incorrecto, retorna mensaje de error.
            return "Formato invalido. Usa DD/MM/AAAA
: "
        if fecha.date() < datetime.today().date(): #Si la fecha es anterior a hoy, retorna mensaje de error.
            return "La fecha no puede ser anterior a hoy. Ingresa una fecha futura: " #Camino infeliz: fecha en el pasado.
        fecha_fin = fecha + timedelta(days=self.dias - 1) #Calcula la fecha de fin sumando los días solicitados.
        self.fecha_inicio = entrada #Guarda la fecha de inicio en la sesión.
        self.fecha_fin    = fecha_fin.strftime("%d/%m/%Y") #Guarda la fecha de fin formateada en la sesión.
        mes   = fecha.month #Obtiene el mes de la fecha de inicio.
        aviso = ("
Temporada alta (dic/ene/jul): requiere aprobacion adicional de RRHH.
"
                 if mes in (12, 1, 7) else "") #Si es temporada alta genera un aviso, si no queda vacío.
        self.estado = ESTADO_CONFIRMACION #Avanza al estado de confirmación.
        return (f"
RESUMEN DE SOLICITUD
" + "─"*35 +
                f"
Empleado: {self.empleado['nombre']}" +
                f"
Area: {self.empleado['area']}" +
                f"
Dias: {self.dias}" +
                f"
Desde: {self.fecha_inicio}" +
                f"
Hasta: {self.fecha_fin}" +
                f"
Aprobador: {self.empleado['jefe']}" +
                f"
{aviso}" + "─"*35 +
                f"
s → Confirmar   n → Cancelar
: ") #Muestra el resumen completo de la solicitud.

    def _estado_confirmacion(self, entrada):  #Estado CONFIRMACION, procesa la decisión del usuario.
        if entrada.lower() in ("s", "si", "confirmar"):    #Si el usuario confirma...
            return self._estado_registro()                 #Llama al estado de registro (tarea de servicio).
        elif entrada.lower() in ("n", "no", "cancelar"):  #Si el usuario cancela...
            self.reiniciar()                               #Resetea la sesión.
            return self._respuesta_cancelacion()           #Retorna mensaje de cancelación.
        return "Responde 's' para confirmar o 'n' para cancelar: "  #Retorna para input no reconocido.

    def _estado_registro(self): #Estado REGISTRO, graba la solicitud en la base de datos y notifica (tarea de servicio).
        id_sol = registrar_solicitud(self.empleado["legajo"], self.dias,
                                     self.fecha_inicio, self.fecha_fin) #Llama a database.py para registrar y descontar días.
        nombre = self.empleado["nombre"] #Guarda el nombre antes de reiniciar la sesión.
        jefe = self.empleado["jefe"] #Guarda el jefe antes de reiniciar la sesión.
        dias, inicio, fin = self.dias, self.fecha_inicio, self.fecha_fin #Guarda los datos de la solicitud antes de reiniciar.
        saldo = self.empleado["dias_disponibles"] - self.dias #Calcula el saldo restante después del descuento.
        self.reiniciar() #Resetea la sesión para dejarla lista para una nueva consulta.
        return (f"
SOLICITUD REGISTRADA EXITOSAMENTE
" + "─"*40 +
                f"
ID         : {id_sol}" +
                f"
Estado     : APROBADA" +
                f"
Dias       : {dias}" +
                f"
Periodo    : {inicio} al {fin}" +
                f"
Restantes  : {saldo}
" + "─"*40 +
                f"
Notificacion enviada a RRHH y a {jefe}.
"
                f"
1 → Solicitar vacaciones
2 → Consultar saldo
salir → Salir
") #Muestra el comprobante con el ID generado.

    def _respuesta_cancelacion(self): #Genera el mensaje de cancelación, se usa cuando el usuario cancela o escribe 'salir'.
        return ("
Solicitud cancelada. No se registro ningun cambio.
"
                "
1 → Solicitar vacaciones
2 → Consultar saldo
salir → Salir
") #Informa la cancelación y muestra el menú.

    def _mostrar_bienvenida(self): #Genera el mensaje de bienvenida que se muestra al iniciar el chatbot.
        return ("              VACABOT           
"
                "Sistema de Gestion de Vacaciones
"
                "
1 → Solicitar vacaciones"
                "
2 → Consultar saldo disponible"
                "
salir → Salir del sistema
"
                "
Opcion: ")  #Muestra el título y las opciones disponibles.
