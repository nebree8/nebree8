#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif 
#include <SoftwareSerial.h>
#include <Wire.h>  // Needed by cmake to generate the pressure sensor deps. (Gross!)

#include "../HX711/HX711.h"

const int SERIAL_RX_PIN = 0;
const int SERIAL_TX_PIN = 1;
const int LED_SIGNAL_PIN = 51;


//SoftwareSerial *serial;

const int CLK_PIN = 6;
const int DAT_PIN = 7;
HX711 scale(DAT_PIN, CLK_PIN);
float calibration_factor = 600; //-7050 worked for my 440lb max scale setup

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 calibration sketch");
  scale.set_scale();
  scale.tare();
  delay(1000);
  scale.set_scale(calibration_factor); //Adjust to this calibration factor
  pinMode(13, OUTPUT);
}

char g_blink_on = 0;

void loop() {
  Serial.print("Read: ");
  Serial.print(scale.get_units(), 1);
  Serial.print("\n");
  delay(100);
  g_blink_on = g_blink_on == 0 ? 1 : 0;
  digitalWrite(13, g_blink_on);
}
