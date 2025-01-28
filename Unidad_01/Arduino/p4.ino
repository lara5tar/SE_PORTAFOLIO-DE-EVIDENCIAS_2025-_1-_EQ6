int actuador = 12;

setup(){
    Serial.begin(9600);
    pinMode(actuador, OUTPUT);
}

loop(){
    digitalWrite(actuador, 1);
    delay(1000);
    digitalWrite(actuador, 0);
    delay(1000);
}