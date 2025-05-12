// Omega Space - CanSat Fase Nacional
// Código principal de vuelo: adquisición de datos, control de motores, almacenamiento y transmisión
// Sensores: BME280 (clima), ICM20948 (IMU), GPS PA1010D (I2C), MAX9814 (micrófono), microSD
// Autores: Equipo Omega Space - IES Alcántara - Región de Murcia

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME280.h>
#include <Adafruit_ICM20948.h>
#include <Adafruit_GPS.h>
#include <SPI.h>
#include <SD.h>

// Constantes del entorno
#define SEALEVELPRESSURE_HPA 1013.25  // Presión a nivel del mar

// Pines del sistema
#define SD_CS 8             // Chip Select de la microSD
#define AUDIO_PIN A0        // Entrada analógica del micrófono
#define NUM_MUESTRAS 100    // Muestras para el cálculo de nivel sonoro

// Pines del controlador de motores (L298N)
#define MOTOR_A_IN1 5
#define MOTOR_A_IN2 6
#define MOTOR_B_IN1 9
#define MOTOR_B_IN2 10
#define VELOCIDAD_MOTOR 60      // PWM de motor
#define ANGULO_UMBRAL 35        // Umbral de corrección en grados

// Objetos de sensores
Adafruit_BME280 bme;
Adafruit_ICM20948 icm;
sensors_event_t accel, gyro, temp_event;
Adafruit_GPS gps(&Wire);  // GPS por I2C

// Variables de estado
int paquete = 0;
float altitudAnterior = 0;
float ay_offset = 0;
float az_offset = 0;

void setup() {
  Serial.begin(115200);
  Serial1.begin(9600);        // Comunicación con APC220
  Wire.begin();

  pinMode(LED_BUILTIN, OUTPUT);  // LED de actividad

  // Inicialización de sensores
  if (!bme.begin(0x76)) while (1);
  if (!icm.begin_I2C()) while (1);
  if (!gps.begin(0x60)) while (1);

  gps.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  gps.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ);
  gps.sendCommand(PGCMD_ANTENNA);

  if (!SD.begin(SD_CS)) while (1);

  File file = SD.open("datos.csv", FILE_WRITE);
  if (file && file.size() == 0) {
    file.println("Etiqueta,Temp,Presion,Humedad,Alt_BME,Lat,Lon,Alt_GPS,Ax,Ay,Az,Gx,Gy,Gz,NivelAudio,Paquete");
    file.close();
  }

  // Pines de motores
  pinMode(MOTOR_A_IN1, OUTPUT);
  pinMode(MOTOR_A_IN2, OUTPUT);
  pinMode(MOTOR_B_IN1, OUTPUT);
  pinMode(MOTOR_B_IN2, OUTPUT);

  // Calibración de inclinación inicial
  icm.getEvent(&accel, &gyro, &temp_event);
  ay_offset = accel.acceleration.y;
  az_offset = accel.acceleration.z;
}

void loop() {
  // Sensor BME280
  float temp_bme = bme.readTemperature();
  float pres = bme.readPressure() / 100.0F;
  float alt_bme = bme.readAltitude(SEALEVELPRESSURE_HPA);
  float humedad = bme.readHumidity();

  // Detección de descenso
  bool descendiendo = (alt_bme < altitudAnterior);
  altitudAnterior = alt_bme;

  // IMU (ICM20948)
  icm.getEvent(&accel, &gyro, &temp_event);
  float ax = accel.acceleration.x;
  float ay = accel.acceleration.y;
  float az = accel.acceleration.z;
  float gx = gyro.gyro.x;
  float gy = gyro.gyro.y;
  float gz = gyro.gyro.z;

  // Corrección de inclinación inicial
  float ay_corr = ay - ay_offset;
  float az_corr = az - az_offset;
  float roll = atan2(ay_corr, az_corr) * 180.0 / PI;

  // GPS
  for (int i = 0; i < 10; i++) {
    char c = gps.read();
    if (gps.newNMEAreceived()) gps.parse(gps.lastNMEA());
  }
  float lat = gps.fix ? gps.latitude : 0.0;
  float lon = gps.fix ? gps.longitude : 0.0;
  float alt_gps = gps.fix ? gps.altitude : 0.0;

  // Nivel de audio
  int nivelAudio = capturarNivelAudio();

  // Construcción de trama
  String trama = "Omega," +
                 String(temp_bme, 2) + "," + String(pres, 2) + "," + String(humedad, 2) + "," + String(alt_bme, 2) + "," +
                 String(lat, 6) + "," + String(lon, 6) + "," + String(alt_gps, 2) + "," +
                 String(ax, 4) + "," + String(ay, 4) + "," + String(az, 4) + "," +
                 String(gx, 4) + "," + String(gy, 4) + "," + String(gz, 4) + "," +
                 String(nivelAudio) + "," + String(paquete);

  Serial.println(trama);
  Serial1.println(trama);

  // LED de confirmación
  digitalWrite(LED_BUILTIN, HIGH);
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);

  // Guardado en microSD
  File file = SD.open("datos.csv", FILE_WRITE);
  if (file) {
    file.println(trama);
    file.close();
  }

  // Activar motores solo si está descendiendo y a más de 100 m
  if (descendiendo && alt_bme > 100.0) {
    if (roll > ANGULO_UMBRAL) ajustarMotores(true);
    else if (roll < -ANGULO_UMBRAL) ajustarMotores(false);
    else detenerMotores();
  } else {
    detenerMotores();
  }

  paquete++;
  delay(500);
}

int capturarNivelAudio() {
  long suma = 0;
  for (int i = 0; i < NUM_MUESTRAS; i++) {
    int lectura = analogRead(AUDIO_PIN) - 512;
    suma += lectura * lectura;
    delayMicroseconds(200);
  }
  return sqrt(suma / NUM_MUESTRAS);
}

void ajustarMotores(bool corregirDerecha) {
  if (corregirDerecha) {
    analogWrite(MOTOR_A_IN1, VELOCIDAD_MOTOR);
    digitalWrite(MOTOR_A_IN2, LOW);
    digitalWrite(MOTOR_B_IN1, LOW);
    analogWrite(MOTOR_B_IN2, VELOCIDAD_MOTOR);
  } else {
    digitalWrite(MOTOR_A_IN1, LOW);
    analogWrite(MOTOR_A_IN2, VELOCIDAD_MOTOR);
    analogWrite(MOTOR_B_IN1, VELOCIDAD_MOTOR);
    digitalWrite(MOTOR_B_IN2, LOW);
  }
}

void detenerMotores() {
  digitalWrite(MOTOR_A_IN1, LOW);
  digitalWrite(MOTOR_A_IN2, LOW);
  digitalWrite(MOTOR_B_IN1, LOW);
  digitalWrite(MOTOR_B_IN2, LOW);
}
