int actuador = 10;

setup(){
    Serial.begin(9600);
    Serial.setTimeout(100);
    pinMode(actuador, OUTPUT);
}

int v;

loop(){
    if(Serial.available() > 0){
        v = Serial.readString().toInt();
        digitalWrite(actuador, v);     
    }
    delay(1000);
}