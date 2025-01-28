//  procesamiento de datos
    //  normalmente leermos unicamente una vez cada sensor y mandamos la informacion al puerto serial
    //  esto es incorrecto debido a que podrian generarse inconsistencias en las lecturas, 
    //  por lo que debe buscarse tratar de aminorar esta situacion mediante el preprocesamiento

    //priemra aproximacion... medidas de tendencia central... 

int sensor = A0;

void setup(){
    Serial.begin(9600);
}

//  promedio - media
int totalLecturas = 10;
int valor[10];

void loop(){
    for (int i = 0; i < totalLecturas; i++>){
        valor[i] = analogRead(sensor);
        delayMicroseconds(100);
    }
    
    
    int prom = 0;

    for (int i = 0; i < totalLecturas; i++>){
        prom += valor[i];
    }

    prom /= totalLecturas;
    
    Serial.println(prom);

    delay(10);
}

