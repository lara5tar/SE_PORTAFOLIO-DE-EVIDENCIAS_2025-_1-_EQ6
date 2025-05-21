#include <WiFi.h>
#include <HTTPClient.h>

// Reemplaza con tus credenciales
const char *ssid = "TD Campus_C";
const char *password = "1Gestudio";

const String firebaseHost = "https://embebidos-pi-default-rtdb.firebaseio.com";
const String sensorPath = "/sensores.json";
const String controlPath = "/control/estado_foco.json";

// Si usas token, descomenta esta línea y añádelo al final de cada URL con "?auth=TU_TOKEN"
// const String authToken = "TU_TOKEN";

// Pines para un sensor y un LED
const int ldrPin = 33; // Pin del único sensor LDR
const int ledPin = 2;  // Pin del único LED

unsigned long lastSend = 0;
unsigned long lastCheck = 0;

void setup()
{
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);

  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi...");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
}

void loop()
{
  unsigned long currentMillis = millis();

  // Leer sensor y mandar a Firebase cada 5 segundos
  if (currentMillis - lastSend >= 5000)
  {
    // Leer valor del sensor
    int ldrValue = analogRead(ldrPin);

    // Enviar datos a Firebase
    sendSensorToFirebase(ldrValue);
    lastSend = currentMillis;
  }

  // Verificar estado del foco cada 3 segundos
  if (currentMillis - lastCheck >= 3000)
  {
    checkFocoFromFirebase();
    lastCheck = currentMillis;
  }
}

void sendSensorToFirebase(int value)
{
  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    String url = firebaseHost + sensorPath; // + "?auth=" + authToken;

    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // Crear JSON con los datos
    String payload = "{";
    payload += "\"timestamp\":" + String(time(nullptr)) + ",";

    // Dato del LDR
    payload += "\"ldr_value\":" + String(value) + "";
    payload += "}";

    int httpCode = http.POST(payload);

    if (httpCode > 0)
    {
      Serial.println("Datos enviados: " + payload);
    }
    else
    {
      Serial.println("Error al enviar datos");
    }

    http.end();
  }
}

void checkFocoFromFirebase()
{
  if (WiFi.status() == WL_CONNECTED)
  {
    HTTPClient http;
    String url = firebaseHost + controlPath; // + "?auth=" + authToken;

    http.begin(url);
    int httpCode = http.GET();

    if (httpCode == 200)
    {
      String response = http.getString();
      response.trim(); // quitar espacios y saltos

      Serial.println("Estado del foco: " + response);

      if (response == "\"on\"")
      {
        digitalWrite(ledPin, HIGH);
      }
      else if (response == "\"off\"")
      {
        digitalWrite(ledPin, LOW);
      }
    }
    else
    {
      Serial.println("Error al leer estado del foco");
    }

    http.end();
  }
}
