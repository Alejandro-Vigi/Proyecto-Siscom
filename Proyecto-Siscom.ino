//La afinación de la Guitarra: mi_l, la, re, sol, si, mi_h. [82,5 - 110 - 146,83 - 196 - 247 - 330 Hz]
#include <LiquidCrystal_I2C.h> // Incluir la libreria que opera el LCD vía I2C
#define LENGTH 512 // Se define un espacio de memoria de 512 bytes
byte rawData[LENGTH]; // Se le asigna una etiqueta al espacio de memoria donde se va a muestrear la frecuencia  
int count; // Se define un entero llamado count
// Sample frecuency in khz
const float sample_freq = 9065; // frecuencia de muestreo en 9070 Hz
LiquidCrystal_I2C lcd(0x27, 16, 2); //0x3F ó 0x20 ó 0x27 Otras posibles direcciones
int len = sizeof(rawData); // Guardar la longitud de rawData en len
int i, k; // Definir dos variables enteras para recorrer los datos
long sum, sum_old; // Definir dos variables decimales para guardar la suma de los datos
int thresh = 0; // inicializar umbral en cero
float freq_per = 0; // inicializar freq_per en cero
byte pd_state = 0; // inicializar pd_state en cero

//Declaración de pines para el led
const int lede=2;
const int ledA=3;
const int ledD=4;
const int ledG=5;
const int ledB=6;
const int ledE=7; 

void setup() {
  // analogReference(EXTERNAL); //connect to 3.3 V
  // analogRead(A0); 
  Serial.begin(115200); // inicializa puerto serial a 115.200 bps
  count = 0; // inicializa count en cero
  
  //Definir los leds como salidas
  pinMode(lede , OUTPUT);
  pinMode(ledA , OUTPUT);
  pinMode(ledD , OUTPUT);
  pinMode(ledG , OUTPUT);
  pinMode(ledB , OUTPUT);
  pinMode(ledE , OUTPUT);

  lcd.init(); // inicializa LCD
  lcd.backlight(); // encienda luz de fondo del LCD
  lcd.clear(); // Limpiar el LCD
  lcd.setCursor(0, 0); // Ubicarse en fila superior, primera columna
  lcd.print("Melodic"); 
  lcd.setCursor(0, 1); // Ubicarse en fila inferior, primera columna
  lcd.print("        Spectrum");
  delay(5000); // Espere 5 segundos

  //Inicial test
  lcd.clear();
  lcd.setCursor(0, 0); // Ubicarse en fila superior, primera columna
  lcd.print("Nota Detectada:");
  lcd.setCursor(15, 0); // Ubicarse en fila superior, 15va columna
  lcd.print("-");
}

void loop() {
  if (count < LENGTH) { // Si no se ha terminado de muestrear
    count++; // incremente cuenta en 1
    rawData[count] = analogRead(A2) >> 2; // Siga leyendo la entrada de microfono
  }
  else { // Si ya terminó de leer el micrófono
    for (int j = 0; j < LENGTH; j++) {
      Serial.println(rawData[j]); // Imprime cada dato en una nueva línea
    }
    sum = 0; // iniciar sum
    pd_state = 0; // iniciar pd_state en 0
    int period = 0; // // iniciar period en 0
    for (i = 0; i < len; i++) { // Recorrer el vector de memoria
      //Autocorrelation
      sum_old = sum; // guardar sum en sum_old
      sum = 0; // iniializar sum en 0
      for (k = 0; k < len - i; k++) sum += (rawData[k] - 128) * (rawData[k + i] - 128) / 256; // Hallar sum
      //Peak Detect State Machine
      if ((pd_state == 2) && (sum - sum_old) <= 0)
      {
        period = i;
        pd_state = 3;
      }
      if (pd_state == 1 && (sum > thresh) && (sum - sum_old) > 0) pd_state = 2;
      if (!i) {
        thresh = sum * 0.5;
        pd_state = 1;
      }
    }
        //Frequency identified in Hz
    if (thresh > 100) {
      freq_per = sample_freq / period;
      if (freq_per < 400) {
        //Serial.print("FRECUENCIA: ");
        //Serial.println(freq_per); // Enviar la frecuencia al puerto serial
        //Serial.println(freq_per);

//E low note (82.5 Hz)
        if ((freq_per > 68.75) && (freq_per < 96.25)) { //Rango en el cual se va a identificar la frecuencia como "Mi, bajo"
          lcd.setCursor(0,1);
          lcd.print(freq_per);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("e");
          digitalWrite(lede , HIGH);
          if (freq_per < 81) { // si la frecuencia está por debajo --> Apretar
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 83.2) { // si la frecuencia está por encima --> Soltar
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500);
          }
          if ((freq_per >= 81) && (freq_per <= 83.2)) { // Si la frecuencia está en este rango considérela como afinada
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(lede , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        //A note (110 Hz)
        if ((freq_per > 96.25) && (freq_per < 128.415)) { //Rango en el cual se va a identificar la frecuencia como "La"
          lcd.setCursor(0,1);
          lcd.print(freq_per);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("A");
          digitalWrite(ledA , HIGH);
          if (freq_per < 106) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 114) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500);
          }
          if ((freq_per >= 108) && (freq_per <= 112)) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(ledA , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }


        //D note (146.83 Hz)
        if ((freq_per > 128.415) && (freq_per < 171.415)) { //Rango en el cual se va a identificar la frecuencia como "Re"
          lcd.setCursor(0,1);
          lcd.print(freq_per);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("D");
          digitalWrite(ledD , HIGH);
          if (freq_per < 143.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 151.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500);
          }
          if ((freq_per >= 145.0) && (freq_per <= 149.0)) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(ledD , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        //G note (196.0 Hz)
        if ((freq_per > 171.415) && (freq_per < 221.47)) { //Rango en el cual se va a identificar la frecuencia como "Sol"
          lcd.setCursor(0,1);
          lcd.print(freq_per);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("G");
          digitalWrite(ledG , HIGH);
          if (freq_per < 194.00) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 198.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500);
          }
          if ((freq_per >= 194.0) && (freq_per <= 198.0)) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(ledG , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        //B note (246.94 Hz)
        if ((freq_per > 221.47) && (freq_per < 288.285)) { //Rango en el cual se va a identificar la frecuencia como "Si"
          lcd.setCursor(0,1);
          lcd.print(freq_per);
          delay(500);
          lcd.setCursor(15, 0);
          lcd.print("B");
          digitalWrite(ledB , HIGH);
          if (freq_per < 243.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 251.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500); 
          }
          if ((freq_per >= 245.0) && (freq_per <= 249.0)) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(ledB , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }

        //E high note (329.63 Hz)
        if ((freq_per > 288.285) && (freq_per < 370.975)) { //Rango en el cual se va a identificar la frecuencia como "Mi, alto"
          lcd.setCursor(0,1);
          lcd.print(freq_per+5);
          delay(500);
          freq_per=freq_per;
          lcd.setCursor(15, 0);
          lcd.print("E");
          digitalWrite(ledE , HIGH);
          if (freq_per < 323.5) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: apretar");
            delay(1500);
          }
          if (freq_per > 332.0) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: soltar ");
            delay(1500);
          }
          if ((freq_per >= 323.5) && (freq_per <= 332.0)) {
            lcd.setCursor(0, 1);
            lcd.print("Ajuste: afinada");
            delay(1500);
          }
          digitalWrite(ledE , LOW);
          lcd.setCursor(15, 0);
          lcd.print("-");
        }
      }
    }
    count = 0;
    lcd.setCursor(0, 1);
    lcd.print("                ");
  }
}