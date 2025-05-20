#include <WiFi.h>
#include <FirebaseESP32.h>
#include <time.h>

// Configuración de WiFi
#define WIFI_SSID "CampusTD"
#define WIFI_PASSWORD "1Gestudio"

// Configuración de Firebase
#define FIREBASE_HOST "https://embebidos-pi-default-rtdb.firebaseio.com/"
#define FIREBASE_AUTH ""

// Define pines para LDRs
#define LDR_PIN1 34 // Pin analógico para la fotoresistencia 1
#define LDR_PIN2 35 // Pin analógico para la fotoresistencia 2
#define LDR_PIN3 32 // Pin analógico para la fotoresistencia 3
#define LDR_PIN4 33 // Pin analógico para la fotoresistencia 4

// Define pines para actuadores
#define RELAY_PIN1 26 // Pin para control de relé para foco 1
#define RELAY_PIN2 27 // Pin para control de relé para foco 2
#define PWM_PIN1 25   // Pin PWM para control de foco 3
#define PWM_PIN2 14   // Pin PWM para control de foco 4

// Configuración PWM
#define PWM_CHANNEL1 0
#define PWM_CHANNEL2 1
#define PWM_FREQ 5000    // Frecuencia PWM 5kHz
#define PWM_RESOLUTION 8 // Resolución 8-bit (0-255)

// Define objetos de Firebase
FirebaseData firebaseData;
FirebaseJson json;

// Variables para control
int lightValues[4] = {0, 0, 0, 0};  // Valores de control de intensidad para los 4 focos
unsigned long lastLdrUpdate = 0;    // Timestamp de la última actualización del LDR
unsigned long lastControlCheck = 0; // Timestamp del último chequeo de control
unsigned long lastUpdateTime = 0;   // Timestamp de la última actualización

// Intervalos de tiempo (ms)
const long LDR_UPDATE_INTERVAL = 5000;    // Enviar datos del sensor cada 5 segundos
const long CONTROL_CHECK_INTERVAL = 3000; // Verificar señales de control cada 3 segundos

void setup()
{
  // Inicialización del puerto serie
  Serial.begin(115200);
  Serial.println();

  // Configurar pines de sensores
  pinMode(LDR_PIN1, INPUT);
  pinMode(LDR_PIN2, INPUT);
  pinMode(LDR_PIN3, INPUT);
  pinMode(LDR_PIN4, INPUT);

  // Configurar pines de actuadores
  pinMode(RELAY_PIN1, OUTPUT);
  pinMode(RELAY_PIN2, OUTPUT);
  digitalWrite(RELAY_PIN1, LOW); // Inicialmente apagado
  digitalWrite(RELAY_PIN2, LOW); // Inicialmente apagado

  // Configurar canales PWM
  ledcSetup(PWM_CHANNEL1, PWM_FREQ, PWM_RESOLUTION);
  ledcSetup(PWM_CHANNEL2, PWM_FREQ, PWM_RESOLUTION);
  ledcAttachPin(PWM_PIN1, PWM_CHANNEL1);
  ledcAttachPin(PWM_PIN2, PWM_CHANNEL2);
  ledcWrite(PWM_CHANNEL1, 0); // Inicialmente apagado
  ledcWrite(PWM_CHANNEL2, 0); // Inicialmente apagado

  // Conectar a WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(300);
  }
  Serial.println();
  Serial.print("Conectado con IP: ");
  Serial.println(WiFi.localIP());

  // Configurar Firebase
  Firebase.begin(FIREBASE_HOST, FIREBASE_AUTH);
  Firebase.reconnectWiFi(true);

  // Configurar tiempo para timestamp
  configTime(0, 0, "pool.ntp.org");

  Serial.println("Sistema iniciado - Modo de operación con Firebase");
  Serial.println("Actualizando 4 sensores LDR a Firebase y leyendo comandos de control para 4 focos");
}

void loop()
{
  unsigned long currentMillis = millis();

  // Verificar conexión WiFi
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("WiFi desconectado. Intentando reconectar...");
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    delay(5000); // Esperar 5 segundos para reconexión
    return;      // Saltar esta iteración
  }

  // Enviar datos de sensores a Firebase periódicamente
  if (currentMillis - lastLdrUpdate >= LDR_UPDATE_INTERVAL)
  {
    updateLdrsToFirebase();
    lastLdrUpdate = currentMillis;
  }

  // Verificar señales de control desde Firebase periódicamente
  if (currentMillis - lastControlCheck >= CONTROL_CHECK_INTERVAL)
  {
    checkControlFromFirebase();
    lastControlCheck = currentMillis;
  }
}

void updateLdrsToFirebase()
{
  // Obtener timestamp actual
  time_t now;
  time(&now);

  // Leer valores de los 4 LDRs
  int ldrValue1 = analogRead(LDR_PIN1);
  int ldrValue2 = analogRead(LDR_PIN2);
  int ldrValue3 = analogRead(LDR_PIN3);
  int ldrValue4 = analogRead(LDR_PIN4);

  // Crear JSON con datos
  json.clear();
  json.set("ldr_value1", ldrValue1);
  json.set("ldr_value2", ldrValue2);
  json.set("ldr_value3", ldrValue3);
  json.set("ldr_value4", ldrValue4);
  json.set("timestamp", (int)now);

  // Enviar datos a Firebase
  String path = "/sensores/datos_" + String(now);

  if (Firebase.set(firebaseData, path, json))
  {
    Serial.print("LDR1: ");
    Serial.print(ldrValue1);
    Serial.print(" | LDR2: ");
    Serial.print(ldrValue2);
    Serial.print(" | LDR3: ");
    Serial.print(ldrValue3);
    Serial.print(" | LDR4: ");
    Serial.println(ldrValue4);
  }
  else
  {
    Serial.println("Error al enviar LDRs a Firebase");
    Serial.println("Motivo: " + firebaseData.errorReason());
  }
}

void checkControlFromFirebase()
{
  // Verificar el último comando de control en Firebase
  if (Firebase.getJSON(firebaseData, "/control"))
  {
    if (firebaseData.dataType() == "json")
    {
      FirebaseJson &json = firebaseData.jsonObject();

      // Buscar el último registro (valor timestamp más alto)
      unsigned long highestTimestamp = 0;
      String latestKey = "";

      // Identificar todas las claves
      FirebaseJsonData result;
      size_t count = json.iteratorBegin();
      String key;

      for (size_t i = 0; i < count; i++)
      {
        json.iteratorGet(i, result);
        if (result.type == "object" && result.key.length() > 0)
        {
          key = result.key;

          // Convertir la clave (timestamp) a entero
          unsigned long timestamp = strtoul(key.c_str(), NULL, 10);
          if (timestamp > highestTimestamp)
          {
            highestTimestamp = timestamp;
            latestKey = key;
          }
        }
      }
      json.iteratorEnd();

      // Si encontramos una entrada y es más reciente que nuestra última actualización
      if (highestTimestamp > 0 && highestTimestamp > lastUpdateTime)
      {
        bool valuesChanged = false;

        // Obtener los valores pwm para los 4 focos
        for (int i = 1; i <= 4; i++)
        {
          FirebaseJsonData pwmValue;
          String valuePath = latestKey + "/pwm_value" + String(i);
          json.get(pwmValue, valuePath);

          if (pwmValue.success)
          {
            int newValue = pwmValue.intValue;
            if (newValue != lightValues[i - 1])
            {
              lightValues[i - 1] = newValue;
              valuesChanged = true;
            }
          }
        }

        // Si algún valor cambió, actualizamos los focos
        if (valuesChanged)
        {
          controlLights();
          Serial.print("Nuevos valores de control desde Firebase (timestamp: ");
          Serial.print(highestTimestamp);
          Serial.print("): ");
          Serial.print(lightValues[0]);
          Serial.print(", ");
          Serial.print(lightValues[1]);
          Serial.print(", ");
          Serial.print(lightValues[2]);
          Serial.print(", ");
          Serial.println(lightValues[3]);

          lastUpdateTime = highestTimestamp;
        }
      }
    }
  }
  else
  {
    Serial.println("Error al leer control de Firebase");
    Serial.println("Motivo: " + firebaseData.errorReason());
  }
}

void controlLights()
{
  // Control ON/OFF para focos con relé
  // Se enciende si el valor es mayor a 128 (50%)
  if (lightValues[0] > 128)
  {
    digitalWrite(RELAY_PIN1, HIGH);
    Serial.println("Foco 1: ENCENDIDO");
  }
  else
  {
    digitalWrite(RELAY_PIN1, LOW);
    Serial.println("Foco 1: APAGADO");
  }

  if (lightValues[1] > 128)
  {
    digitalWrite(RELAY_PIN2, HIGH);
    Serial.println("Foco 2: ENCENDIDO");
  }
  else
  {
    digitalWrite(RELAY_PIN2, LOW);
    Serial.println("Foco 2: APAGADO");
  }

  // Control PWM para focos 3 y 4
  ledcWrite(PWM_CHANNEL1, lightValues[2]);
  ledcWrite(PWM_CHANNEL2, lightValues[3]);
  Serial.print("Foco 3: ");
  Serial.print(lightValues[2]);
  Serial.print(" | Foco 4: ");
  Serial.println(lightValues[3]);
}
