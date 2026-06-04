from bot import VacaBot #Importa la clase VacaBot desde bot.py.

def main(): #Función principal que inicia y mantiene el bucle de conversación del chatbot.
    bot = VacaBot() #Crea una instancia de VacaBot, inicializando la sesión.
    print(bot._mostrar_bienvenida()) #Imprime el mensaje de bienvenida al iniciar el programa.
    while True: #Mantiene el chatbot activo hasta que el usuario decida salir.
        try:
            entrada = input("") #Variable que contiene el input del usuario.
            if entrada.lower() == "salir": #Si el usuario escribe "salir"...
                print("Sistema cerrado.") #Imprime mensaje de cierre y termina de ejecutar el programa.
                break
            print(bot.procesar(entrada)) #Pasa el input al bot y imprime la respuesta.
        except (KeyboardInterrupt, EOFError): #Si el usuario presiona Ctrl+C o cierra el input abruptamente...
            print("Sesion interrumpida.") #Imprime mensaje de interrupción y termina de ejecutar el programa.
            break

if __name__ == "__main__": #Verifica que el archivo se está ejecutando directamente y no importado desde otro archivo.
    main() #Llama a la función principal para iniciar el chatbot.
