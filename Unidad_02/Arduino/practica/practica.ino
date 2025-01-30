int sensor1 = A0;
int sensor2 = A1;
int sensor3 = A2;
int sensor4 = A3;

void setup(){
    Serial.begin(9600);
}

int totalLecturas = 30;
int valoresPromedio[totalLecturas];
int valoresMenor[totalLecturas];
int valoresMayor[totalLecturas];
int valoresMediana[totalLecturas];
int valoresModa[totalLecturas];

void loop(){
    for (int i = 0; i < totalLecturas; i++){
        valoresPromedio[i] = analogRead(sensor1);
        valoresMenor[i] = analogRead(sensor2);
        valoresMayor[i] = analogRead(sensor3);
        valoresMediana[i] = analogRead(sensor4);
        delayMicroseconds(100);
    }

    promedio();
    valorMenor();
    valorMayor();
    mediana();

    Serial.println("");

    delay(1000);

}

void promedio (){
    int prom = 0;

    for (int i = 0; i < totalLecturas; i++){
        prom += valoresPromedio[i];
    }

    prom /= totalLecturas;
    
    Serial.print(String(prom) + ", ");
}

void valorMenor(){
    int valorMenor = 1024; // porque es el valor maximo que puede leer el ADC

    for (int i = 0; i < totalLecturas; i++){
        if (valoresMenor[i] < valorMenor){
            valorMenor = valoresMenor[i];
        }
    }
    
    Serial.print(String(valorMenor) + ", ");
}

void valorMayor(){
    int valorMayor = -1; // porque es el valor maximo que puede leer el ADC

    for (int i = 0; i < totalLecturas; i++){
        if (valoresMayor[i] > valorMayor){
            valorMayor = valoresMayor[i];
        }
    }

    
    Serial.print(String(valorMayor) + ", ");
}

void mediana(){
    for (int i = 0; i < totalLecturas; i++){
        for (int j = i + 1; j < totalLecturas; j++){
            if (valoresMediana[i] > valoresMediana[j]){
                int aux = valoresMediana[i];
                valoresMediana[i] = valoresMediana[j];
                valoresMediana[j] = aux;
            }
        }
    }
    
    
    Serial.print(String(valoresMediana[totalLecturas / 2]) + ", ");
}

void moda(){
    int moda = 0;
    int repeticiones = 0;

    for (int i = 0; i < totalLecturas; i++){
        int repeticionesTemp = 0;

        for (int j = 0; j < totalLecturas; j++){
            if (valoresModa[i] == valoresModa[j]){
                repeticionesTemp++;
            }
        }

        if (repeticionesTemp > repeticiones){
            moda = valoresModa[i];
            repeticiones = repeticionesTemp;
        }
    }

    Serial.print(String(moda) + ", ");
}


// con un sensor que varie, monitorear 12 horas ininterrumpidas, lectura cada 5 minutos que sea con timestamp, numero de lectura, valor, fecha y hora



// suma de cuadraados . minimizacion optimo que todos los valores ean 0
// one max porblem - que todos los valores sean 1
//     vector binario.  maximisacion
// valor absoluto. minimizacion que todos los valores ean 0

