#include <Adafruit_Sensor.h>
#include <DHT.h>

#define DHTPIN 3

#define DHTTYPE DHT11  

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200); 
  Serial.println("Iniciando sensor DHT11...");
  
  dht.begin(); 
}

void loop() {
  delay(2000);  

  float humedad = dht.readHumidity();
  float temperatura = dht.readTemperature(); 

  if (isnan(humedad) || isnan(temperatura)) {
    Serial.println("Error al leer el sensor DHT11");
    return;
  }

  Serial.print("Temperatura: ");
  Serial.print(temperatura);
  Serial.println(" °C");

  Serial.print("Humedad: ");
  Serial.print(humedad);
  Serial.println(" %");

  Serial.println("------------------------");
}
