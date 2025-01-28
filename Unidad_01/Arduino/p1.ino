int sensor = A0;

void setup() {
  Serial.begin(9600);

}
int v;

void loop() {
  v = analogRead(sensor);
  Serial.println(v);
  delay(1000);
}

// PROYECTO UNIDAD 1

// AG - que vincule arduino con python (Extension de la practica 1)

//  generar poblacion (generar matriz de soluciones / vectores)
//  iniciar ciclo 
    //  seleccionar padres - tamaño n 
    //  generar hijos - curza
    //  aplicar muta sobre los hijos
    //  seleccion ambienta quedarse con los n mejores individuas entre poblacion anterior e hijos
    //  si no se llega a coindicion de paro, enconces volcer a 2
//  imprimir la mejor solucion encontrada

//  condicion de paro = total de iteraciones o llegar al optimo global

//  problemas a optimizar 
    //  suma de cuadrados de los individuos de un vector - optimo 
    //  ?
    //  ?


//  variables configurables
//  n = tamaño de la poblacion
//  m = tamaño de los vectores
//  probabilidad de mutacion: 0.5%
//  gen = total de generaciones

//  poner valor varibales chicos, grandes o pequeños y documentar commo se comportan

//  los datos obtenidos son obtenidos de los potenciometros, leer varios y optimizar

//  tiene que ir en modulos

//  para el 4 de febrero