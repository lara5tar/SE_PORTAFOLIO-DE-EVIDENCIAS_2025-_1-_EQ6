
int sensores[] = {A0, A1, A2, A3, A4, A5};

void setup(){
    Serial.begin(9600);
}

int totalLecturas = 30;
int valoresPromedio[30];
int valoresMenor[30];
int valoresMayor[30];
int valoresMediana[30];
int valoresModa[30];

void loop(){
    for (int i = 0; i < totalLecturas; i++){
        valoresPromedio[i] = analogRead(sensores[0]);
        valoresMenor[i] = analogRead(sensores[1]);
        valoresMayor[i] = analogRead(sensores[2]);
        valoresMediana[i] = analogRead(sensores[3]);
        valoresModa[i] = analogRead(sensores[4]);

        delayMicroseconds(100);
    }

    Serial.print("f, ");
    promedio();
    valorMenor();
    valorMayor();
    mediana();
    moda();

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

    Serial.print(String(moda));

    // Serial.print(String(moda) + ", ");
}


// con un sensor que varie, monitorear 12 horas ininterrumpidas, lectura cada 5 minutos que sea con timestamp, numero de lectura, valor, fecha y hora



// suma de cuadraados . minimizacion optimo que todos los valores ean 0
// one max porblem - que todos los valores sean 1
//     vector binario.  maximisacion
// valor absoluto. minimizacion que todos los valores ean 0

