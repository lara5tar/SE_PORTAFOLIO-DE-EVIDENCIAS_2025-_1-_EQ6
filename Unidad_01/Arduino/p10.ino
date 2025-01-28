int actuadores[] = {8, 9, 10, 11};

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(actuadores[i], OUTPUT); 
  }
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    int v = Serial.parseInt();
    for (int i = 0; i < 4; i++) {
      digitalWrite(actuadores[i], v & (1 << i) ? HIGH : LOW);
    }
  }
}
