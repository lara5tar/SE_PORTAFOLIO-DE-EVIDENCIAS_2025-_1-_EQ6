int actuadores[] = {8, 9, 10, 11};

void setup() {
  for (int i = 0; i < 4; i++) {
    pinMode(actuadores[i], OUTPUT);
  }
}

void loop() {
  for (int i = 0; i < 4; i++) {
    digitalWrite(actuadores[i], HIGH); 
    delay(100);
    digitalWrite(actuadores[i], LOW); 
    delay(100);
  }
  delay(100);
}
