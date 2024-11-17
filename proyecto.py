"""
*** Proyecto: Sistemas de Comunicaciones ***
             Semestre 2025-1
    
    Integrantes:

    - Liliana Marlene Becerril Velez
    - Francisco Daniel López Campillo
    - Jaime Manuel Miranda Serrano
    - Marco Alejandro Vigi Garduño
"""

# Importamos todas las librerías necesarias para el proyecto.
import serial
import numpy as np
import matplotlib.pyplot as plt
import time
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import os
import customtkinter as ctk
from CTkMenuBar import *

# Inicializamos variables globales.
stop_threads = False    # Bandera de control para saber si los hilos se deben detener.
update_thread = None    # Bandera de control para saber cuándo debe de actualizarse el hilo en tiempo real.
ser = None              # Comunicación serial con Arduino.
is_compiled = False     # Bandera para verificar si el programa ha sido compilado y cargado para iniciar comunicación.


def initialize_serial(port):
    """
    Inicializa la comunicación serial con el puerto proporcionado por el usuario.

    Parameters:
    port (int): Puerto serial 
    """
    global ser
    try:
        # Configuramos el puerto serial proporcionado por el usuario con la velocidad de 115200 baudios.
        ser = serial.Serial(port, 115200, timeout=1)
        # Realizamos impresion en la terminal de la conexión exitosa.
        print(f"Conexión establecida en el puerto {port}. \nIniciando análisis de datos. Para iniciar comunicacion con otras configuraciones, reinicie el programa.\n")
        start_update_thread()  # Iniciamos el hilo para actualizar la gráfica de forma continua.
        # Mostramos en el cuadro de texto de la terminal la posible salida con sus parametros para una mayor legibilidad.
        terminal_output.configure(state=tk.NORMAL)  # Hacemos que el cuadro de texto sea editable temporalmente.
        terminal_output.insert(tk.END, f"Conexión establecida en el puerto {port}. \nIniciando análisis de datos. Para iniciar comunicacion con otras configuraciones, reinicie el programa\n") # Imprimimos la validacion en el cuadro de texto de la terminal.
        terminal_output.configure(state=tk.DISABLED)  # Volvemos el cuadro de texto no editable.
        terminal_output.yview(tk.END)  # Realizamos un desplazamiento hacia abajo para mayor legibilidad.
    # En caso de ocurrir algun error, mandamos la excepción.
    except serial.SerialException as e:
        # Realizamos impresion en la terminal que la conexión tuvo un error.
        print(f"Error al abrir el puerto serial, verifica que estes introduciendo un puerto correcto\n")
        ser = None
        # Mostramos en el cuadro de texto de la terminal la posible salida con sus parametros para una mayor legibilidad.
        terminal_output.configure(state=tk.NORMAL)  # Hacemos que el cuadro de texto sea editable temporalmente.
        terminal_output.insert(tk.END, f"Error al abrir el puerto, verifica que estes introduciendo un puerto correcto. (Visualiza el administrador de dispositivos).\n") # Imprimimos la validacion en el cuadro de texto de la terminal.
        terminal_output.configure(state=tk.DISABLED)  # Volvemos el cuadro de texto no editable.
        terminal_output.yview(tk.END)  # Realizamos un desplazamiento hacia abajo para mayor legibilidad.

def start_serial_communication():

    #Inicia la comunicación serial al hacer clic en el botón 'Iniciar comunicación'.
    
    # Definimos nuestra bandera para validar que ya se compilo y ejecuto el archivo en arduino.
    global is_compiled

    # Verificamos si el programa ha sido compilado antes de iniciar la comunicación.
    if not is_compiled:
        # Realizamos impresion en la terminal el error en donde no se ha compilado el programa en Arduino.
        terminal_output.configure(state=tk.NORMAL)  # Hacemos que el cuadro de texto sea editable temporalmente.
        terminal_output.insert(tk.END, "Error: Primero debes compilar el programa antes de iniciar la comunicación.\n") # Imprimimos la validacion en el cuadro de texto de la terminal.
        terminal_output.configure(state=tk.DISABLED)    # Volvemos el cuadro de texto no editable.
        terminal_output.yview(tk.END)   # Realizamos un desplazamiento hacia abajo para mayor legibilidad.
        return  # Salimos de la función ya que aun no se compila el programa.

    # En caso en el que ya se compilo previamente el programa, procedemos a empezar con la comunicación serial.
    port = port_entry.get()  # Obtenemos el puerto desde la entrada de texto que proporcionó el usuario.
    # Si el usuario no ingresó un puerto valido, mostramos en la terminal el error.
    if not port:
        # Realizamos impresion en la terminal que la conexión tuvo un error.
        print("Por favor, ingrese un puerto válido.")
        terminal_output.configure(state=tk.NORMAL)  # Hacemos que el cuadro de texto sea editable temporalmente.
        terminal_output.insert(tk.END, f"Por favor, ingrese un puerto válido.\n") # Imprimimos la validacion en el cuadro de texto de la terminal.
        terminal_output.configure(state=tk.DISABLED)  # Volvemos el cuadro de texto no editable.
        terminal_output.yview(tk.END)  # Realizamos un desplazamiento hacia abajo para mayor legibilidad.
        return  # Salimos de la función ya que no se proporcionó un puerto válido.
    # En caso de que ya se compiló y se proporcionó un puerto valido, inicializamos la comunicación con el puerto serial.
    initialize_serial(port)

def read_data():
    """
    Realiza la lectura del arreglo proveniente de Arduino que contiene el conjunto de datos.
    Returns:
    data ([]): Arreglo proveniente de arduino. Si ocurre un error o no hay datos, se devuelve una lista vacia.
    """
    global ser
    # Verifica si la conexión serial no está abierta o si no existe
    if not ser or not ser.is_open:
        # Si la conexión no está abierta o no existe, devuelve una lista vacía
        return [] 
    
    try:
        # Creamos una lista vacía para almacenar los datos leídos del puerto serial
        data = [] 
        # Ciclo para leer datos hasta que tengamos al menos 512 datos en la lista
        while len(data) < 512:
            if stop_threads:
                return []
            # Lee una línea de datos del puerto serial
            line = ser.readline()
            # Verifica si la línea leída no está vacía
            if line:
                try:
                    # Decodifica la línea en formato UTF-8 y convierte el valor a entero
                    value = int(line.decode('utf-8').strip())
                     # Agrega el valor a la lista 'data'
                    data.append(value)
                
                except ValueError:
                    # Si no se puede convertir la línea a entero (por ejemplo, si no es un número válido),
                    # se ignora esa línea y se pasa a la siguiente.
                    continue
        # Retorna la lista con los 512 datos leídos del puerto serial
        return data
    except serial.SerialException:
        # Si ocurre un error en la conexión serial (por ejemplo, la desconexión del dispositivo),
        # retorna una lista vacía.
        return []

def update_plot(data, sample_rate, line, ax, freq_label):
    """
    Actualiza la gráfica de la frecuencia fundamental obtenida mediante el análisis de Fourier
    Parámetros:
    data (ndarray): Datos de la señal en el dominio del tiempo.
    sample_rate (float): Tasa de muestreo en Hz (muestras por segundo).
    line (matplotlib.lines.Line2D): El objeto de la línea en la gráfica que se actualizará.
    ax (matplotlib.axes.Axes): El objeto de los ejes de la gráfica para realizar ajustes de escala.
    freq_label (tkinter.Label): Etiqueta de la interfaz gráfica que muestra la frecuencia fundamental calculada.

    """
    # Elimina la componente DC (promedio de la señal) para centrar la señal alrededor de 0
    data = data - np.mean(data) 
    # Calcula la Transformada Rápida de Fourier (FFT) de los datos
    fft_result = np.fft.fft(data)
    # Obteniene la magnitud de la FFT (solo la parte real, ya que estamos interesados en la amplitud)
    fft_magnitude = np.abs(fft_result)
    # Número de puntos de datos
    n = len(data)
    # Calcular las frecuencias correspondientes a cada punto de la FFT
    freqs = np.fft.fftfreq(n, d=1/sample_rate)
    positive_freqs = freqs[:n // 2]
    positive_magnitude = fft_magnitude[:n // 2]
    max_index = np.argmax(positive_magnitude)
    fundamental_freq = positive_freqs[max_index]

    if 70 <= fundamental_freq <= 350:
        freq_label.configure(text=f"Frecuencia fundamental: {fundamental_freq:.2f} Hz")
        freq_range = 200
        lower_bound = max(0, fundamental_freq - freq_range)
        upper_bound = fundamental_freq + freq_range
        mask = (positive_freqs >= lower_bound) & (positive_freqs <= upper_bound)
        filtered_freqs = positive_freqs[mask]
        filtered_magnitude = positive_magnitude[mask]
        line.set_xdata(filtered_freqs)
        line.set_ydata(filtered_magnitude)
        ax.relim()
        ax.autoscale_view()
        canvas.draw()

def update():
    global line, ax, sample_rate, freq_label, stop_threads, ser
    
    while not stop_threads:
        if not ser or not ser.is_open:
            break
        data = read_data()
        if not data:
            continue
        update_plot(data, sample_rate, line, ax, freq_label)
        time.sleep(0.05)

def start_update_thread():
    global stop_threads, update_thread
    stop_threads = False
    update_thread = threading.Thread(target=update, daemon=True)
    update_thread.start()

def on_closing():
    global stop_threads, update_thread, ser
    
    stop_threads = True
    if ser and ser.is_open:
        try:
            ser.cancel_read()
        except serial.SerialException:
            pass
    if ser and ser.is_open:
        try:
            ser.close()
        except serial.SerialException:
            pass
    os._exit(0)

# Función para mostrar la ventana "Acerca de"
def show_about():
    # Crear una ventana emergente usando CTkToplevel
    about_window = ctk.CTkToplevel(root)
    about_window.title("Acerca de")
    about_window.geometry("700x330")
    about_window.resizable(False, False)
    
    # Obtener el tamaño de la pantalla y de la ventana emergente
    window_width = 700
    window_height = 330
    screen_width = about_window.winfo_screenwidth()
    screen_height = about_window.winfo_screenheight()
    
    # Calcular las coordenadas para centrar la ventana
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    # Establecer la posición de la ventana emergente
    about_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Crear una etiqueta para el título centrado
    title_label = ctk.CTkLabel(
        about_window,
        text="Sistemas de Comunicaciones\nSemestre 2025 - 1",
        font=("Helvetica", 18, "bold"),
        justify="center"
    )
    title_label.pack(pady=(20, 10))
    
    # Crear un marco para alinear las etiquetas en dos columnas
    frame = ctk.CTkFrame(
        about_window, 
        fg_color="#1a1a1a"
    )
    frame.pack(pady=10, padx=20)
    
    # Listado de integrantes y sus correos
    integrantes = [
        ("Liliana Marlene Becerril Velez", "lilianabecerril@comunidad.unam.mx"),
        ("Francisco Daniel López Campillo", "pacodaniellc_422@comunidad.unam.mx"),
        ("Jaime Manuel Miranda Serrano", "jaime_miranda28@comunidad.unam.mx"),
        ("Marco Alejandro Vigi Garduño", "alejandro.vigi@comunidad.unam.mx")
    ]
    
    # Agregar las etiquetas al marco utilizando grid
    for i, (nombre, correo) in enumerate(integrantes):
        nombre_label = ctk.CTkLabel(
            frame,
            text=nombre,
            font=("Helvetica", 16),
            anchor="w"
        )
        nombre_label.grid(row=i, column=0, sticky="w", padx=(0, 20), pady=1)

        correo_label = ctk.CTkLabel(
            frame,
            text=correo,
            font=("Helvetica", 16),
            anchor="e"
        )
        correo_label.grid(row=i, column=1, sticky="e", pady=5)
    
    # Botón para cerrar la ventana emergente
    close_button = ctk.CTkButton(
        about_window,
        text="Cerrar",
        command=about_window.destroy
    )
    close_button.pack(pady=(20, 0))


# Función para mostrar la ventana "Información"
def show_info():
    # Crear una ventana emergente usando CTkToplevel
    info_window = ctk.CTkToplevel(root)
    info_window.title("Información")
    info_window.geometry("400x170")
    info_window.resizable(False, False)
    
    # Obtener el tamaño de la pantalla y de la ventana emergente
    window_width = 400
    window_height = 170
    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()
    
    # Calcular las coordenadas para centrar la ventana
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    # Establecer la posición de la ventana emergente
    info_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Crear una etiqueta para mostrar el texto en la ventana emergente
    label = ctk.CTkLabel(
        info_window,
        text=(
            "Melodic Spectrum\n"
            "Versión: 1.0\n"
            "Fecha: 18-11-2024\n\n"
            "Copyright © 2024 Melodic Spectrum"
        ),
        font=("Helvetica", 16),
        justify="center"
    )
    label.pack(pady=(20, 0))
    
    # Botón para cerrar la ventana emergente
    close_button = ctk.CTkButton(
        info_window, 
        text="Cerrar", 
        command=info_window.destroy
    )
    close_button.pack(pady=(10, 0))

def show_board():
    # Crear una ventana emergente usando CTkToplevel
    info_window = ctk.CTkToplevel(root)
    info_window.title("Información")
    info_window.geometry("700x600")
    info_window.resizable(False, False)

    # Obtener el tamaño de la pantalla y de la ventana emergente
    window_width = 700
    window_height = 600
    screen_width = info_window.winfo_screenwidth()
    screen_height = info_window.winfo_screenheight()

    # Calcular las coordenadas para centrar la ventana
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    
    # Establecer la posición de la ventana emergente
    info_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Crear una etiqueta para el título centrado
    title_label1 = ctk.CTkLabel(
        info_window,
        text="Placas más comunes",
        font=("Helvetica", 18, "bold"),
        justify="center"
    )
    title_label1.pack(pady=(20, 10))
    
    # Crear un marco para alinear las etiquetas en dos columnas
    frame = ctk.CTkFrame(info_window, fg_color="#1a1a1a")
    frame.pack(pady=10, padx=20)

    # Listado de placas y sus códigos
    placas = [
        ("Arduino Uno", "arduino:avr:uno"),
        ("Arduino Uno Mini", "arduino:avr:unomini"),
        ("Arduino Nano (ATmega328P)", "arduino:avr:nano"),
        ("Arduino Nano Every", "arduino:megaavr:nano_every"),
        ("Arduino Mega 2560", "arduino:avr:mega"),
        ("Arduino Leonardo", "arduino:avr:leonardo"),
        ("Arduino Micro", "arduino:avr:micro"),
        ("Arduino Due", "arduino:sam:arduino_due_x"),
        ("Arduino Nano 33 IoT", "arduino:samd:nano_33_iot"),
        ("Arduino MKR WiFi 1010", "arduino:samd:mkrwifi1010"),
        ("ESP32 Dev Module", "esp32:esp32:esp32"),
        ("ESP8266 NodeMCU", "esp8266:esp8266:nodemcuv2")
    ]

    # Agregar las etiquetas al marco utilizando grid
    for i, (nombre, codigo) in enumerate(placas):
        placa_label = ctk.CTkLabel(frame, text=nombre, font=("Helvetica", 16), anchor="w")
        placa_label.grid(row=i, column=0, sticky="w", padx=(0, 20), pady=1)

        codigo_label = ctk.CTkLabel(frame, text=codigo, font=("Helvetica", 16), anchor="e")
        codigo_label.grid(row=i, column=1, sticky="e", pady=5)

    # Botón para cerrar la ventana emergente
    close_button = ctk.CTkButton(
        info_window, 
        text="Cerrar", 
        command=info_window.destroy
    )
    close_button.pack(pady=(20, 0))

# Botón para limpiar la terminal
def clear_terminal():
    terminal_output.configure(state=tk.NORMAL)  # Hacer el cuadro de texto editable temporalmente
    terminal_output.delete(1.0, tk.END)  # Eliminar todo el contenido
    terminal_output.configure(state=tk.DISABLED)  # Volver el cuadro de texto no editable

def compile_and_upload():
    """
    Función para compilar, cargar el código y luego iniciar la comunicación serial.
    Valida los campos de entrada antes de proceder con la compilación y carga.
    """
    global terminal_output, is_compiled, start_button

    # Si la comunicación ya está en curso, mostramos la advertencia
    if is_compiled:
        show_warning()
        return

    # Obtener los valores de las entradas del usuario
    port = port_entry.get().strip()
    arduino_file = port_entry2.get().strip()
    board_type = port_entry3.get().strip()

    # Validar que todos los campos estén llenos
    if not port or not arduino_file or not board_type:
        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, "Error: Asegúrese de ingresar todos los campos (puerto, ruta del archivo y placa).\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)
        return

    # Validar que la ruta del archivo sea correcta
    if not os.path.isfile(arduino_file):
        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, f"Error: No se encontró el archivo '{arduino_file}'. Verifique la ruta.\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)
        return

    try:
        # Paso 1: Compilar el código utilizando arduino-cli
        compile_command = f"arduino-cli compile --fqbn {board_type} {arduino_file}"
        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, "Compilando el programa...\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)

        compile_result = os.system(compile_command)

        # Verificar si la compilación fue exitosa
        if compile_result != 0:
            terminal_output.configure(state=tk.NORMAL)
            terminal_output.insert(tk.END, "Error durante la compilación. Verifique el puerto y la placa.\n")
            terminal_output.configure(state=tk.DISABLED)
            terminal_output.yview(tk.END)
            return

        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, "Compilación exitosa. Subiendo el código a la placa Arduino...\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)

        # Paso 2: Subir el código a la placa Arduino utilizando el puerto especificado
        upload_command = f"arduino-cli upload -p {port} --fqbn {board_type} {arduino_file}"
        upload_result = os.system(upload_command)

        if upload_result != 0:
            terminal_output.configure(state=tk.NORMAL)
            terminal_output.insert(tk.END, "Error al cargar el programa en la placa. Verifique el puerto y la placa.\n")
            terminal_output.configure(state=tk.DISABLED)
            terminal_output.yview(tk.END)
            return

        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, "Carga exitosa en la placa Arduino. Iniciando comunicación serial...\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)
        
        # Paso 3: Iniciar la comunicación serial si todo fue exitoso
        initialize_serial(port)

        # Marcar el programa como compilado y deshabilitar el botón
        is_compiled = True
        start_button.configure(state=tk.DISABLED)

    except Exception as e:
        terminal_output.configure(state=tk.NORMAL)
        terminal_output.insert(tk.END, f"Error inesperado: {str(e)}\n")
        terminal_output.configure(state=tk.DISABLED)
        terminal_output.yview(tk.END)

# Crear la ventana principal usando customtkinter
root = ctk.CTk()

# Configurar el tema del color (dark-blue, o cualquier otro tema disponible)
ctk.set_default_color_theme("dark-blue")

root.title("Visualización de Frecuencia y Espectro")

# Obtener el tamaño de la pantalla
ancho = root.winfo_screenwidth()
alto = root.winfo_screenheight()

# Definir el tamaño de la ventana
window_width = 900  # Ancho de la ventana
window_height = 800  # Alto de la ventana

# Calcular las coordenadas para centrar la ventana
x = (ancho - window_width) // 2
y = (alto - window_height) // 2

# Establecer la ubicación de la ventana
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Crear la barra de menú usando personalización.
menu = CTkTitleMenu(master=root)
menu_salir = menu.add_cascade("Menu")
submenu_salir = CustomDropdownMenu(widget=menu_salir)
submenu_salir.add_option(option="Salir", command=on_closing)

# Crear el menú "Ayuda" y agregar ambas opciones en un solo submenú
menu_ayuda = menu.add_cascade("Ayuda")
submenu_ayuda = CustomDropdownMenu(widget=menu_ayuda)
submenu_ayuda.add_option(option="Placas comunes", command=show_board)
submenu_ayuda.add_option(option="Contacto", command=show_about)
submenu_ayuda.add_option(option="Acerca de", command=show_info)

# Etiqueta para la frecuencia
freq_label = ctk.CTkLabel(root, text="Frecuencia fundamental: -- Hz", font=("Helvetica", 20, "bold"))
freq_label.pack(pady=(20,0))

# Configuración de Matplotlib y Canvas
fig, ax = plt.subplots(facecolor='#242424')
line, = ax.plot([], [], color='#1f538d', linewidth=3)  # Línea azul aún más gruesa
ax.set_xlabel("Frecuencia (Hz)", color='white', fontsize=12)
ax.set_ylabel("Magnitud", color='white', fontsize=12)
ax.grid(True, color='white', linewidth=0.1)
ax.set_facecolor('#242424')

# Configurar el color de los números de los ejes a blanco
ax.tick_params(axis='x', colors='white')  # Números del eje X en blanco
ax.tick_params(axis='y', colors='white')  # Números del eje Y en blanco

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=ctk.BOTH, expand=True)

# Variables
sample_rate = 9065

# Crear un frame para organizar las etiquetas del puerto serial horizontalmente.
port_frame = ctk.CTkFrame(root, fg_color="#242424")

# Etiqueta para indicar el puerto serial (parte superior)
port_label = ctk.CTkLabel(port_frame, text="Ingrese el puerto serial (Ejemplo: COM3):", font=("Helvetica", 14, "bold"), bg_color="#242424")
port_label.pack(side="left", padx=107, pady=0)  # Empaquetado horizontal, con un pequeño espacio entre las etiquetas

# Etiqueta para ejemplo (parte inferior)
port_entry = ctk.CTkEntry(port_frame, font=("Helvetica", 14, "bold"), bg_color="#242424")
port_entry.pack(side="right", padx=0, pady=0)

# Empaquetar el frame en la ventana principal
port_frame.pack(pady=(0, 0))

# Crear un frame para organizar las etiquetas de la ruta horizontalmente.
port_frame2 = ctk.CTkFrame(root, fg_color="#242424")

# Etiqueta para indicar el puerto serial (parte superior)
rute_label = ctk.CTkLabel(port_frame2, text="Ingrese la ruta del Archivo arduino (Ejemplo: Proyecto-Siscom.ino):\nNota: La carpeta deberá tener el mismo nombre que el archivo .ino", font=("Helvetica", 14, "bold"), bg_color="#242424")
rute_label.pack(side="left", padx=15, pady=(0,0))  # Empaquetado horizontal, con un pequeño espacio entre las etiquetas

# Etiqueta para ejemplo (parte inferior)
port_entry2 = ctk.CTkEntry(port_frame2, font=("Helvetica", 14, "bold"), bg_color="#242424")
port_entry2.pack(side="left", padx=10, pady=(0,0))

# Empaquetar el frame en la ventana principal
port_frame2.pack(pady=(10, 0))

# Crear un frame para organizar el nombre de la placa horizontalmente.
port_frame3 = ctk.CTkFrame(root, fg_color="#242424")

# Etiqueta para indicar el puerto serial (parte superior)
board_label = ctk.CTkLabel(port_frame3, text="Ingrese el nombre de la placa Arduino (Ejemplo: arduino:avr:uno):\nNota: Para visualizar las placas mas comúnes Ayuda > Placas comunes ", font=("Helvetica", 14, "bold"), bg_color="#242424")
board_label.pack(side="left", padx=0, pady=0)  # Empaquetado horizontal, con un pequeño espacio entre las etiquetas

# Etiqueta para ejemplo (parte inferior)
port_entry3 = ctk.CTkEntry(port_frame3, font=("Helvetica", 14, "bold"), bg_color="#242424")
port_entry3.pack(side="left", padx=10, pady=0)

# Empaquetar el frame en la ventana principal
port_frame3.pack(pady=(10, 0))

# Crear un frame para organizar los botones horizontalmente
button_frame = ctk.CTkFrame(root)

# Boton para Compilar y Ejecutar en Arduino
start_button = ctk.CTkButton(button_frame, text="Compilar en Arduino e iniciar comunicación", font=("Helvetica", 15, "bold"), 
                              command=compile_and_upload, fg_color="#1f7346", hover_color="#1a603a", width=30, height=20)  # Definir el mismo tamaño
start_button.pack(side="left", padx=40)  # Empaquetado a la izquierda, con un pequeño espacio

#Boton para limpiar pantalla en la terminal contenida en la interfaz.
clear_button = ctk.CTkButton(button_frame, text="Limpiar Terminal", font=("Helvetica", 15, "bold"), 
                              command=clear_terminal, fg_color="#B22222", hover_color="#8B0000", width=30, height=20)
clear_button.pack(side="right", padx=0)

# Empaquetar el frame que contiene los botones
button_frame.pack(pady=(20, 10))

# Crear el recuadro para la salida de la terminal
terminal_output = ctk.CTkTextbox(root, height=100, width=window_width-40, font=("Helvetica", 12), wrap=tk.WORD, state=tk.DISABLED)
terminal_output.pack(padx=20, pady=(10, 20))

# Manejar el cierre de la ventana
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()