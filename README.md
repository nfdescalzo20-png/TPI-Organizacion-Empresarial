
VacaBot — Sistema de Gestión de Vacaciones

Organización Empresarial — UTN TUP

Chatbot de consola que automatiza el proceso de solicitud de vacaciones,
siguiendo el flujo modelado en el diagrama BPMN 2.0.

Estructura del proyecto =

vacabot/
├── VacaBot.ipynb      ← notebook principal (Google Colab)
├── main.py            ← punto de entrada
├── bot.py             ← máquina de estados (lógica BPMN)
├── database.py        ← capa de acceso a datos
└── data/
    └── empleados.csv ← base de datos de empleados
    └── solicitudes.csv ← base de datos de solicitudes
