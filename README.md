# VacaBot — Sistema de Gestión de Vacaciones
**Organización Empresarial — UTN TUP**

Chatbot de consola que automatiza el proceso de solicitud de vacaciones, siguiendo el flujo modelado en el diagrama BPMN 2.0.

## Estructura del proyecto

    vacabot/
    ├── Manual de Usuario.pdf   ← manual que contiene instrucciones de uso  
        ├── status.py           ← estado de la base de datos de empleados y solicitudes   
        ├── main.py             ← punto de entrada
        ├── bot.py              ← máquina de estados (lógica BPMN)
        ├── database.py         ← capa de acceso a datos
    └── data/
        ├── empleados.csv       ← base de datos de empleados
        └── solicitudes.csv     ← base de datos de solicitudes
## Cómo ejecutar el proyecto

### Pasos

**1. Clonar el repositorio**

    git clone https://github.com/nfdescalzo20-png/TPI-Organizacion-Empresarial.git

**2. Entrar a la carpeta**

    cd TPI-Organizacion-Empresarial

**3. Ejecutar el bot**

    python main.py

**4. Consultar el estado de la base de datos (opcional)**

    python status.py

Muestra los empleados, sus saldos disponibles y las solicitudes registradas.

### Legajos de prueba
| Legajo | Empleado | Días disponibles | Escenario |
|--------|----------|-----------------|-----------|
| E001 | Ana Garcia | 15 | Flujo normal |
| E002 | Luis Perez | 3 | Saldo bajo |
| E003 | Maria Lopez | 20 | Saldo completo |
| E004 | Juan Martinez | 0 | Sin saldo (camino infeliz) |

### Comandos del bot
| Comando | Acción |
|---------|--------|
| `1` | Solicitar vacaciones |
| `2` | Consultar saldo disponible |
| `salir` | Cerrar el bot |
| `s` | Confirmar solicitud |
| `n` | Cancelar solicitud |
