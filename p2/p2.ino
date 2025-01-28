int sensor = 10;
void setup() {
  Serial.begin(9600);
  pinMode(sensor, INPUT);
}

int v;

void loop() {
  v = digitalRead(Sensor);
  Serial.println(v);
  delay(1000);
}
