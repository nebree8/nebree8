#ifndef NEBREE8_ARDUINO_LED_MODULE_H_
#define NEBREE8_ARDUINO_LED_MODULE_H_

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"

namespace nebree8 {

class LedModule : public arduinoio::UCModule {
 public:
  LedModule(const uint16_t num_leds, const uint8_t pin_number) {
    pinMode(pin_number, OUTPUT);
    neopixel_ = new Adafruit_NeoPixel(num_leds, pin_number, NEO_GRB + NEO_KHZ800);
  }

  // X, Y coordinates in the robot, in inches
  void LightRegion(float x, float y, uint16_t r, uint16_t g, uint16_t b) {
    // 17 every 11 inches
    const float kLedsPerInch = 1.545;
    neopixel_->setPixelColor(static_cast<uint16_t>(x / kLedsPerInch), r, g, b);
    neopixel_->show();
  }

  virtual const arduinoio::Message* Tick() {
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    return false;
  }

  ~LedModule() {
    delete neopixel_;
  }

 private:
  Adafruit_NeoPixel *neopixel_;
};

}  // namespace nebree8

#endif  // NEBREE8_ARDUINO_LED_MODULE_H_
