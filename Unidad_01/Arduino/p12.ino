int sensor = A0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int v = analogRead(sensor);
  Serial.print("Valor del sensor: ");
  Serial.println(v);
  delay(1000);
}
