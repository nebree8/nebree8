#if defined(ARDUINO) && ARDUINO >= 100
  #include "Arduino.h"
#else
  #include "WProgram.h"
#endif 
#include <SoftwareSerial.h>
#include <Wire.h>  // Needed by cmake to generate the pressure sensor deps. (Gross!)

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/serial_module.h"
#include "../arduinoio/lib/arduinoio.h"
#include "blink_module.h"
#include "../arduino/io_delay.h"
#include "../arduino/uc_io_module.h"

const int SERIAL_RX_PIN = 0;
const int SERIAL_TX_PIN = 1;
const int LED_SIGNAL_PIN = 51;

//SoftwareSerial *serial;

arduinoio::ArduinoIO arduino_io;
void setup() {
  Serial.begin(115200);
  arduino_io.Add(new arduinoio::SerialRXModule(NULL, 0));
  //arduino_io.Add(new nebree8::BlinkModule());
  arduino_io.Add(new nebree8::IODelay());
  arduino_io.Add(new nebree8::UCIOModule());
}

void loop() {
  arduino_io.HandleLoopMessages();
}
