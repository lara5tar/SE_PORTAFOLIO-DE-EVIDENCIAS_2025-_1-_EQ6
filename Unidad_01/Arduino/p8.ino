int sensor = A0;
int actuador = 6;

setup(){
    Serial.begin(9600);
        pinMode(sensor, INPUT);
}

int v;

loop(){
    int v = analogRead(sensor); 
    v = v / 4;
    analogWrite(actuador, v);
    delay(1000);
}