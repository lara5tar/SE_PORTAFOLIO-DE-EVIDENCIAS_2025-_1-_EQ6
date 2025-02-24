int sensores = {A0, A1, A2, A3, A4, A5, A6, A7};

void setup(){
    Serial.begin(9600);
}

int totalLecturas = 30;
int valoresPromedio[30];
int valoresMenor[30];
int valoresMayor[30];
int valoresMediana[30];
int valoresModa[30];
int valoresNormal[30];
int valoresDesviacionEstandar[30];

void loop(){
    for (int i = 0; i < totalLecturas; i++){
        valoresPromedio[i] = analogRead(sensores[0]);
        valoresMenor[i] = analogRead(sensores[1]);
        valoresMayor[i] = analogRead(sensores[2]);
        valoresMediana[i] = analogRead(sensores[3]);
        valoresModa[i] = analogRead(sensores[4]);
        valoresNormal[i] = analogRead(sensores[5]);

        delayMicroseconds(100);
    }

    Serial.print("i");

    promedio();
    valorMenor();
    valorMayor();
    mediana();
    moda();
    normal();

    Serial.println("F");
    
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

void normal(){
    int normal = 0;

    for (int i = 0; i < totalLecturas; i++){
        normal += valoresNormal[i];
    }

    normal /= totalLecturas;

    Serial.print(String(normal) + ", ");
}
