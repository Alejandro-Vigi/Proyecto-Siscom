//Proyecto: Melodic Spectrum
//Materia: Sistemas de comunicaciones
//Integrantes:
//     Becerril Vélez Liliana Marlene
//     López Campillo Francisco Daniel
//     Miranda Serrano Jaime Manuel
//     Vigi Garduño Marco Alejandro 
//Ultima modificacion: 16/nov/2024
//Este código es un afinador de guitarra que utiliza un micrófono conectado a un Arduino para leer las frecuencias 
//de las cuerdas y mostrar ajustes en una pantalla LCD. Lee valores analógicos del micrófono y los almacena 
//en un arreglo, luego, realiza una autocorrelación para identificar el período de la señal y, con una máquina de estados, 
//detecta picos para determinar la frecuencia. Calcula la frecuencia en Hertz y la compara con rangos predefinidos para 
//identificar la nota (Mi bajo, La, Re, Sol, Si, Mi alto). Muestra la frecuencia y la nota en la pantalla LCD, indicando si
//la cuerda necesita ser apretada o soltada para afinarse correctamente. Además, enciende LEDs específicos para cada nota y
// envía la frecuencia y los valores del arreglo a la consola serial para monitoreo.
// Afinación de la guitarra: mi_l, la, re, sol, si, mi_h. [82,5 - 110 - 146,83 - 196 - 247 - 330 Hz]
#include <LiquidCrystal_I2C.h> // Biblioteca para manejar el LCD a través del protocolo I2C
#define LENGTH 512 // Espacio de memoria reservado para almacenar 512 muestras
byte senal[LENGTH]; // Etiqueta para el arreglo que guardará las muestras de audio
int cont; // Variable que cuenta la cantidad de muestras leídas
// Frecuencia de muestreo en kHz
const float frec_muestreo = 9065; // Configuración de la frecuencia de muestreo en 9.065 Hz
LiquidCrystal_I2C lcd(0x27, 16, 2); // Dirección I2C del LCD (otras opciones: 0x3F, 0x20)
int longitud = sizeof(senal); // Longitud del arreglo senal
int i, k; // Variables para los bucles de análisis de datos
long suma, suma_old; // Variables para almacenar las sumas en el proceso de autocorrelación
int umbral = 0; // Inicialización del umbral para la detección de picos
float frec_fund = 0; // Inicialización de la variable para calcular la frecuencia detectada
byte estado = 0; // Estado de la máquina de detección de picos

// Pines para los LEDs que indican la cuerda detectada
const int lede = 2;
const int ledA = 3;
const int ledD = 4;
const int ledG = 5;
const int ledB = 10;
const int ledE = 11;

void setup() {
  // Inicialización del puerto serial para depuración
  Serial.begin(115200);
  cont = 0; // Inicializar el contador en cero

  // Configurar los pines de los LEDs como salidas
  pinMode(lede, OUTPUT);
  pinMode(ledA, OUTPUT);
  pinMode(ledD, OUTPUT);
  pinMode(ledG, OUTPUT);
  pinMode(ledB, OUTPUT);
  pinMode(ledE, OUTPUT);

  lcd.init(); // Configuración inicial del LCD
  lcd.backlight(); // Encender la retroiluminación
  lcd.clear(); // Limpiar el contenido de la pantalla
  lcd.setCursor(0, 0); // Posicionar en la fila superior
  lcd.print("Melodic");
  lcd.setCursor(0, 1); // Posicionar en la fila inferior
  lcd.print("        Spectrum");
  delay(5000); // Pausa de 5 segundos para que se lea el mensaje

  // Mostrar mensaje inicial en el LCD
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Nota Detectada:");
  lcd.setCursor(15, 0);
  lcd.print("-");
}

void loop() {
  if (cont < LENGTH) { // Mientras no se hayan leído todas las muestras
    cont++; // Incrementar el contador de muestras
    senal[cont] = analogRead(A0) >> 2; // Capturar la señal del micrófono y almacenar en senal
  }
  else { // Una vez que se completó el muestreo
    for (int j = 0; j < LENGTH; j++) {
      Serial.println(senal[j]); // Enviar cada muestra al monitor serial
    }
    suma = 0; // Inicializar la suma para autocorrelación
    estado = 0; // Inicializar el estado de detección de picos
    int n_ciclos = 0; // Cantidad de ciclos de la señal inicializado en cero

    for (i = 0; i < longitud; i++) { // Recorrer todas las muestras para autocorrelación
      suma_old = suma; // Actualizar la suma anterior
      suma = 0; // Reiniciar la suma en cada iteración
      for (k = 0; k < longitud - i; k++) 
        suma += (senal[k] - 128) * (senal[k + i] - 128) / 256; // Calcular la autocorrelación

      // Detección de picos utilizando una máquina de estados
      if ((estado == 2) && (suma - suma_old) <= 0) {
        n_ciclos = i; // Guardar la cantidad de ciclos hasta que se detecta un pico
        estado = 3;
      }
      if (estado == 1 && (suma > umbral) && (suma - suma_old) > 0) estado = 2;
      if (!i) {
        umbral = suma * 0.5; // Configurar el umbral en la primera iteración
        estado = 1;
      }
    }

    // Calcular la frecuencia en Hz si se ha detectado un periodo válido
    if (umbral > 100) {
      frec_fund = frec_muestreo / n_ciclos;
      if (frec_fund < 400) {

        // Identificar la nota en función de la frecuencia detectada
        // Nota Mi grave (82.5 Hz)
        if ((frec_fund > 68.75) && (frec_fund < 96.25)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("e");
          digitalWrite(lede, HIGH);
          if (frec_fund < 81) lcd.print("Ajuste: apretar");
          else if (frec_fund > 83.2) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(lede, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        // Nota La (110 Hz)
        if ((frec_fund > 96.25) && (frec_fund < 128.415)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("A");
          digitalWrite(ledA, HIGH);
          if (frec_fund < 106) lcd.print("Ajuste: apretar");
          else if (frec_fund > 114) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(ledA, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        // Nota Re (146.83 Hz)
        if ((frec_fund > 128.415) && (frec_fund < 171.415)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("D");
          digitalWrite(ledD, HIGH);
          if (frec_fund < 143.0) lcd.print("Ajuste: apretar");
          else if (frec_fund > 151.0) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(ledD, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        // Nota Sol (196.0 Hz)
        if ((frec_fund > 171.415) && (frec_fund < 221.47)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("G");
          digitalWrite(ledG, HIGH);
          if (frec_fund < 194.00) lcd.print("Ajuste: apretar");
          else if (frec_fund > 198.0) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(ledG, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        // Nota Si (246.94 Hz)
        if ((frec_fund > 221.47) && (frec_fund < 288.285)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("B");
          digitalWrite(ledB, HIGH);
          if (frec_fund < 243.0) lcd.print("Ajuste: apretar");
          else if (frec_fund > 251.0) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(ledB, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        // Nota Mi agudo (329.63 Hz)
        if ((frec_fund > 288.285) && (frec_fund < 370.975)) {
          lcd.setCursor(0, 1);
          lcd.print(frec_fund + 5);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("E");
          digitalWrite(ledE, HIGH);
          if (frec_fund < 323.5) lcd.print("Ajuste: apretar");
          else if (frec_fund > 332.0) lcd.print("Ajuste: soltar ");
          else lcd.print("Ajuste: afinada");
          delay(1500);
          digitalWrite(ledE, LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }
      }
    }
    cont = 0;
    lcd.setCursor(0, 1);
    lcd.print("                "); // Borrar la línea de frecuencia
  }
}
