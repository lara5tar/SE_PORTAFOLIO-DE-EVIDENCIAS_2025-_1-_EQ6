//  procesamiento de datos
    //  normalmente leermos unicamente una vez cada sensor y mandamos la informacion al puerto serial
    //  esto es incorrecto debido a que podrian generarse inconsistencias en las lecturas, 
    //  por lo que debe buscarse tratar de aminorar esta situacion mediante el preprocesamiento

    //priemra aproximacion... medidas de tendencia central... 

int sensor = A0;

void setup(){
    Serial.begin(9600);
}

int totalLecturas = 30;
int valor[30];

void loop(){
    for (int i = 0; i < totalLecturas; i++>){
        valor[i] = analogRead(sensor);
        delayMicroseconds(100);
    }


    for (int i = 0; i < totalLecturas; i++){
        for (int j = i + 1; j < totalLecturas; j++){
            if (valor[i] > valor[j]){
                int aux = valor[i];
                valor[i] = valor[j];
                valor[j] = aux;
            }
        }
    }
    
    //ejercicio 1 - moda
    
    Serial.println(valor[totalLecturas / 2]);

    delay(10);
}

//3 potenciomentros d manera modularziada aplicandole un porceso diferente generar 100000 valor en un archivo, calcular la desviacion estandar

// usar 4 potenciomentros generar un metodo media moda ... al mismo tiempo en el mismo for leer los 4 , general el vector de los 4, aplicar al sensor uno mediana ,
//  2 moda .... mandar a python hasata 100 guardar en un archvo, por columna calcular la desviacion estandar

