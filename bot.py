from datetime import datetime, timedelta
from database import buscar_empleado, verificar_saldo, registrar_solicitud

ESTADO_INICIO = "INICIO"
ESTADO_IDENTIFICACION = "IDENTIFICACION"
ESTADO_SOLICITUD_DIAS = "SOLICITUD_DIAS"
ESTADO_VALIDAR_SALDO = "VALIDAR_SALDO"
ESTADO_INGRESO_FECHA = "INGRESO_FECHA"
ESTADO_CONFIRMACION = "CONFIRMACION"

class VacaBot:
    def __init__(self):
        self.reiniciar()

    def reiniciar(self):
        self.estado = ESTADO_INICIO
        self.empleado = None
        self.dias = None
        self.fecha_inicio = None
        self.fecha_fin = None
        self.reintentos = 0
        self.modo_consulta = False

    def procesar(self, entrada):
        entrada = entrada.strip()
        if entrada.lower() in ("salir", "exit", "cancelar"):
            self.reiniciar()
            return self._respuesta_cancelacion()
        estados = {
            ESTADO_INICIO: self._estado_inicio,
            ESTADO_IDENTIFICACION: self._estado_identificacion,
            ESTADO_SOLICITUD_DIAS: self._estado_solicitud_dias,
            ESTADO_VALIDAR_SALDO: self._estado_validar_saldo,
            ESTADO_INGRESO_FECHA: self._estado_ingreso_fecha,
            ESTADO_CONFIRMACION: self._estado_confirmacion,
        }
        metodo_actual = estados.get(self.estado)
        return metodo_actual(entrada) if metodo_actual else "Estado desconocido. Escribi salir para reiniciar."

    def _estado_inicio(self, entrada):
        if entrada in ("1", "solicitar"):
            self.estado = ESTADO_IDENTIFICACION
            return "\nSOLICITUD DE VACACIONES\n" + "─"*35 + "\nIngresa tu numero de legajo:\n"
        elif entrada in ("2", "consultar"):
            self.estado = ESTADO_IDENTIFICACION
            self.modo_consulta = True
            return "\nCONSULTA DE SALDO\n" + "─"*35 + "\nIngresa tu numero de legajo:\n"
        else:
            self.reintentos += 1
            if self.reintentos >= 3:
                self.reintentos = 0
                return "Demasiados intentos. Escribe 1 o 2.\n"
            return "Opcion no valida. Escribe 1 o 2.\n"

    def _estado_identificacion(self, entrada):
        if not entrada.upper().startswith("E") or len(entrada) != 4:
            return "Formato incorrecto. Debe ser E seguido de 3 numeros\nLegajo: "
        empleado = buscar_empleado(entrada)
        if not empleado:
            self.reintentos += 1
            if self.reintentos >= 3:
                self.reintentos = 0
                return "Legajo no encontrado tras varios intentos. Verifica con RRHH.\nEscribe salir o intenta otro legajo: "
            return f"Legajo {entrada.upper()} no existe. Intenta de nuevo: "
        self.empleado = empleado
        self.reintentos = 0
        if self.modo_consulta:
            self.reiniciar()
            return (f"\n{empleado['nombre']} ({empleado['area']})"
                    f"\nDias disponibles: {empleado['dias_disponibles']}"
                    f"\nDias tomados: {empleado['dias_tomados']}"
                    f"\nTotal anual: 20\n"
                    f"\n1 → Solicitar vacaciones\n2 → Consultar saldo\nsalir → Salir\n")
        self.estado = ESTADO_SOLICITUD_DIAS
        return (f"\nBienvenido, {empleado['nombre']} ({empleado['area']})"
                f"\nDias disponibles: {empleado['dias_disponibles']}\n"
                f"\n¿Cuantos dias quieres solicitar? ")

    def _estado_solicitud_dias(self, entrada):
        if not entrada.isdigit():
            return "Ingresa un numero entero.\n¿Cuantos dias? "
        dias = int(entrada)
        if dias <= 0:
            return "La cantidad debe ser mayor a cero.\n¿Cuantos dias? "
        if dias > 30:
            return "No puedes solicitar mas de 30 dias por solicitud.\n¿Cuantos dias? "
        self.dias = dias
        self.estado = ESTADO_VALIDAR_SALDO
        return self._estado_validar_saldo(entrada)

    def _estado_validar_saldo(self, entrada):
        saldo_ok = verificar_saldo(self.empleado["legajo"], self.dias)
        if not saldo_ok:
            disponibles = self.empleado["dias_disponibles"]
            self.estado = ESTADO_SOLICITUD_DIAS
            if disponibles == 0:
                return "\nSin saldo disponible este anio. Contacta a RRHH.\nEscribe salir o una nueva cantidad: "
            return (f"\nPediste {self.dias} dias pero solo tienes {disponibles} disponibles."
                    f"\nIngresa una nueva cantidad (max {disponibles}): ")
        self.estado = ESTADO_INGRESO_FECHA
        return (f"\nSaldo OK: {self.dias} dias verificados."
                f"\n¿Fecha de inicio? Formato DD/MM/AAAA\n: ")

    def _estado_ingreso_fecha(self, entrada):
        try:
            fecha = datetime.strptime(entrada, "%d/%m/%Y")
        except ValueError:
            return "Formato invalido. Usa DD/MM/AAAA\n: "
        if fecha.date() < datetime.today().date():
            return "La fecha no puede ser anterior a hoy. Ingresa una fecha futura: "
        from datetime import timedelta
        fecha_fin = fecha + timedelta(days=self.dias - 1)
        self.fecha_inicio = entrada
        self.fecha_fin = fecha_fin.strftime("%d/%m/%Y")
        mes = fecha.month
        aviso = ("\nTemporada alta (dic/ene/jul): requiere aprobacion adicional de RRHH.\n" if mes in (12, 1, 7) else "")
        self.estado = ESTADO_CONFIRMACION
        return (f"\nRESUMEN DE SOLICITUD\n" + "─"*35 +
                f"\nEmpleado: {self.empleado['nombre']}"
                f"\nArea: {self.empleado['area']}"
                f"\nDias: {self.dias}"
                f"\nDesde: {self.fecha_inicio}"
                f"\nHasta: {self.fecha_fin}"
                f"\nAprobador: {self.empleado['jefe']}"
                f"\n{aviso}" + "─"*35 +
                f"\ns → Confirmar   n → Cancelar\n: ")

    def _estado_confirmacion(self, entrada):
        if entrada.lower() in ("s", "si", "confirmar"):
            return self._estado_registro()
        elif entrada.lower() in ("n", "no", "cancelar"):
            self.reiniciar()
            return self._respuesta_cancelacion()
        return "Responde s para confirmar o n para cancelar: "

    def _estado_registro(self):
        from database import registrar_solicitud
        id_sol = registrar_solicitud(self.empleado["legajo"], self.dias, self.fecha_inicio, self.fecha_fin)
        nombre = self.empleado["nombre"]
        jefe = self.empleado["jefe"]
        dias, inicio, fin = self.dias, self.fecha_inicio, self.fecha_fin
        saldo = self.empleado["dias_disponibles"] - self.dias
        self.reiniciar()
        return (f"\nSOLICITUD REGISTRADA EXITOSAMENTE\n" + "─"*40 +
                f"\nID         : {id_sol}"
                f"\nEstado     : APROBADA"
                f"\nDias       : {dias}"
                f"\nPeriodo    : {inicio} al {fin}"
                f"\nRestantes  : {saldo}\n" + "─"*40 +
                f"\nNotificacion enviada a RRHH y a {jefe}.\n"
                f"\n1 → Solicitar vacaciones\n2 → Consultar saldo\nsalir → Salir\n")

    def _respuesta_cancelacion(self):
        return ("\nSolicitud cancelada. No se registro ningun cambio.\n"
                "\n1 → Solicitar vacaciones\n2 → Consultar saldo\nsalir → Salir\n")

    def _mostrar_bienvenida(self):
        return ("              VACABOT           \n"
                "Sistema de Gestion de Vacaciones\n"
                "\n1 → Solicitar vacaciones"
                "\n2 → Consultar saldo disponible"
                "\nsalir → Salir del sistema\n"
                "\nOpcion: ")
