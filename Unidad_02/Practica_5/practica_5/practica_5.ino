#include <Adafruit_Sensor.h>
#include <DHT.h>

#define DHTPIN 4       // Pin DATA del DHT11 conectado a GPIO 3
#define DHTTYPE DHT11  // Tipo de sensor (DHT11)

DHT dht(DHTPIN, DHTTYPE);

int actuadores[] = {5, 18, 19};

// int totalHoras = 24;

// int temperaturas[24];
// int humedades[24];

int totalLecturas = 30;

int temperaturas[30];
int humedades[30];

void setup() {
  Serial.begin(115200); 

  for (int i = 0; i < 3; i++) {
    pinMode(actuadores[i], OUTPUT);
  }
  
  dht.begin(); 
}

void loop() {
  delay(2000);  
  float humedad = dht.readHumidity();
  float temperatura = dht.readTemperature(); 

  if (isnan(humedad) || isnan(temperatura)) {
      Serial.println("Error");
      return;
  }
  
  for (int i = 0; i < totalLecturas; i++){
    temperaturas[i] = temperatura;
    humedades[i] = humedad;
  }


  mediana();


  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');  // Lee hasta el salto de línea
    
    // Buscar el comando '1' o '0' y la identificación del LED
    char comando = input.charAt(0);  // El primer carácter es el comando (1 o 0)
    int commaIndex = input.indexOf(',');  // Busca la coma que separa el comando del LED
    
    if (commaIndex != -1 && input != NULL) {
      String ledStr= input.substring(commaIndex + 1);  
       int led = ledStr.toInt();
      // Dependiendo del comando, prende o apaga el LED
      if (comando == '1') { 
          digitalWrite(led, HIGH);  
      } else if (comando == '0') {  
          digitalWrite(led, LOW);  // Apaga el LED en pin 12
      }
    }
  }
}

void mediana(){
    for (int i = 0; i < totalLecturas; i++){
        for (int j = i + 1; j < totalLecturas; j++){
            if (temperaturas[i] > temperaturas[j]){
                int aux = temperaturas[i];
                temperaturas[i] = temperaturas[j];
                temperaturas[j] = aux;
            }

            if (humedades[i] > humedades[j]){
                int aux = humedades[i];
                humedades[i] = humedades[j];
                humedades[j] = aux;
            }
        }
    }
    
    
    Serial.println("f, " + String(temperaturas[totalLecturas / 2]) + ", " + String(humedades[totalLecturas / 2]) );
}