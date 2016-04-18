#ifndef NEBREE8_ARDUINO_LED_MODULE_H_
#define NEBREE8_ARDUINO_LED_MODULE_H_

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"

namespace nebree8 {

const char* SET_LED = "ONE_LED";
const int SET_LED_LENGTH = 7;
const char* SET_ALL_LED = "ALL_LED";
const int SET_ALL_LED_LENGTH = 7;
const int LED_Y_ROWS = 1;
// Lower value = more decay.
const float X_DECAY = 8.0;
const float Y_DECAY = 0.5;

class LedModule : public arduinoio::UCModule {
 public:
  LedModule(const uint16_t num_leds, const uint8_t pin_number) {
    pinMode(pin_number, OUTPUT);
    num_leds_ = num_leds;
    neopixel_ = new Adafruit_NeoPixel(num_leds, pin_number, NEO_GRB + NEO_KHZ800);
  }

  // X, Y coordinates in the robot, in inches
  void LightRegion(float x, float y, uint16_t r, uint16_t g, uint16_t b) {
    // 17 every 11 inches
    const float kLedsPerInch = 1.545;
    // Decay by dist squared
    const int nearby_x = static_cast<uint16_t>(x * kLedsPerInch);
    for (int led_x = max(nearby_x - 3, 0);
        led_x <= min(nearby_x + 3, num_leds_); ++led_x) {
      for (int led_y = 0; led_y < LED_Y_ROWS; ++led_y) {
        float led_x_inches = 0.0;
        float led_y_inches = 0.0;
        GetLedInches(led_x, led_y, &led_x_inches, &led_y_inches);
        const float dist_squared_decay =
          (x - led_x_inches) * (x - led_x_inches) * X_DECAY +
          (y - led_y_inches) * (y - led_y_inches) * Y_DECAY;
        float amplitude = 1.0 / (1.0 + dist_squared_decay);
        uint16_t red_amp = static_cast<uint16_t>(amplitude * r);
        uint16_t green_amp = static_cast<uint16_t>(amplitude * g);
        uint16_t blue_amp = static_cast<uint16_t>(amplitude * b);
        if (red_amp + green_amp + blue_amp != 0 ||
            r + g + b == 0) {
          neopixel_->setPixelColor(GetLedIndex(led_x, led_y),
              red_amp, green_amp, blue_amp);
//static_cast<uint16_t>(x * kLedsPerInch), r, g, b);
        }
      }
    }
    //neopixel_->setPixelColor(static_cast<uint16_t>(x * kLedsPerInch), r, g, b);
    neopixel_->show();
  }

  // X,Y == 0 at the front corner by the electronics box.
  int GetLedIndex(const int led_x, const int led_y) {
    if (led_y == 0) {
      return max(0, led_x);
    } else if (led_y == 1) {
      const int kLedFarRightMiddle = 200;
      return min(num_leds_, kLedFarRightMiddle - led_x);
    } else {
      const int kLedFarRightBack = 200;
      return min(num_leds_, kLedFarRightBack + led_x);
    }
  }

  void GetLedInches(const int led_x, const int led_y, float *x, float *y) {
    const float kInchesPerLed = 0.647;
    *x = led_x * kInchesPerLed;
    *y = led_y * 4.0;
  }

  virtual const arduinoio::Message* Tick() {
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, SET_LED, SET_LED_LENGTH) == 0) {
      char red = command[SET_LED_LENGTH];
      char green = command[SET_LED_LENGTH + 1];
      char blue = command[SET_LED_LENGTH + 2];
      command += SET_LED_LENGTH + 3;
      const float *x_y_pos = (const float*) command;
      float x = x_y_pos[0];
      float y = x_y_pos[1];
      LightRegion(x, y, red, green, blue);
      return true;
    }
    return false;
  }

  ~LedModule() {
    delete neopixel_;
  }

 private:
  int num_leds_ = 300;
  Adafruit_NeoPixel *neopixel_;
};

}  // namespace nebree8

#endif  // NEBREE8_ARDUINO_LED_MODULE_H_
