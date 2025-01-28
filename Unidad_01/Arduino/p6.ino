long v;
setup(){
    Serial.begin(9600);
}

loop(){
    v = millis();
    Serial.println(v);
    delay(1000);
}