int pots [4]= {A0,A1,A2,A3};
int values[4];

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);
}

void loop() {
  for(int i = 0; i < 4; i++){
    values[i] = analogRead(pots[i]);
    delay(1000); // Corrected typo
  }

  String c;

  c = "i" + String( values[0]) + "-" + String(values[1]) + "-" + String(values[2]) + "-" + String(values[3]) + "F";

  Serial.print(c);
}