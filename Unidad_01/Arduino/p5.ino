int pinPwm = 6;

void setup(){
    Serial.begin(9600);
    pinMode(pinPwm, OUTPUT);
}

void loop()
{
    for (int i = 0; i < 255; i++)
    {
        analogWrite(pinPwm, i);
        delayMicroseconds(10);
    }
    delay(10);

    for(int i = 255; i > 0; i--)
    {
        analogWrite(pinPwm, i);
        delayMicroseconds(10);
    }
    delay(10);
}