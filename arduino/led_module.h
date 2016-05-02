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
const char* LED_GO = "LED_GO";
const int LED_GO_LENGTH = 6;
const int LED_Y_ROWS = 3;
// Higher value = more decay.
const float X_DECAY = 8.0;
const float Y_DECAY = 1.0;

const uint16_t PIXELS_PER_BLOCK = 300;

class LedModule : public arduinoio::UCModule {
 public:
  LedModule(const uint16_t num_leds, const uint8_t pin_number) {
    pinMode(pin_number, OUTPUT);
    num_leds_ = num_leds;
    for (int i = 0; i * PIXELS_PER_BLOCK < num_leds; ++i) {
      neopixel_[i] = new Adafruit_NeoPixel(PIXELS_PER_BLOCK, pin_number, NEO_GRB + NEO_KHZ800);
    }
    for (uint16_t i = 0; i < num_leds_; i += 1) {
      neopixel_[0]->setPixelColor(i, 0, 0, 0);
    }
    UpdatePixels();
  }

  // X, Y coordinates in the robot, in inches
  void LightRegion(const float x, const float y, const uint8_t r,
      const uint8_t g, const uint8_t b) {
    // 300 every 16 feet.
    const float kLedsPerInch = 1.5625;
    // Decay by dist squared
    const int nearby_x = static_cast<uint16_t>(x * kLedsPerInch);
    const int kNearbyLedCount = 2;
    for (uint16_t led_x = max(nearby_x - kNearbyLedCount, 0);
        led_x <= min(nearby_x + kNearbyLedCount, num_leds_); ++led_x) {
      for (uint16_t led_y = 0; led_y < LED_Y_ROWS; ++led_y) {
        float led_x_inches = 0.0;
        float led_y_inches = 0.0;
        GetLedInches(led_x, led_y, &led_x_inches, &led_y_inches);
        uint8_t dist_squared_decay =
          max(1, static_cast<uint8_t>(
              (x - led_x_inches) * (x - led_x_inches) * X_DECAY +
              (y - led_y_inches) * (y - led_y_inches) * Y_DECAY));
        uint8_t red_amp = static_cast<uint8_t>(r / dist_squared_decay);
        uint8_t green_amp = static_cast<uint8_t>(g / dist_squared_decay);
        uint8_t blue_amp = static_cast<uint8_t>(b / dist_squared_decay);
        if (red_amp > 16 || green_amp > 16 || blue_amp > 16 ||
            (r == 0 && g == 0 && b == 0)) {
          const uint16_t index = GetLedIndex(led_x, led_y);
          neopixel_[index / PIXELS_PER_BLOCK]->setPixelColor(index,
              red_amp, green_amp, blue_amp);
        }
//static_cast<uint16_t>(x * kLedsPerInch), r, g, b);
      }
    }
  }

  void UpdatePixels() {
    for (int i = 0; i * PIXELS_PER_BLOCK < num_leds_; ++i) {
      neopixel_[i]->show();
    }
  }

  // X,Y == 0 at the front corner by the electronics box.
  uint16_t GetLedIndex(const uint16_t led_x, const uint16_t led_y) {
    const int kLedFarRightMiddle = 171;
    if (led_y == 0) {
      return min(max(0, led_x), 86);
    } else if (led_y == 1) {
      return max(87, min(num_leds_, kLedFarRightMiddle - led_x));
    } else {
      return min(num_leds_, kLedFarRightMiddle + 1 + led_x);
    }
  }

  void GetLedInches(const float led_x, const float led_y, float *x, float *y) {
    const float kInchesPerLed = 0.64;
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
    } else if (strncmp(command, SET_ALL_LED, SET_ALL_LED_LENGTH) == 0) {
      char red = command[SET_ALL_LED_LENGTH];
      char green = command[SET_ALL_LED_LENGTH + 1];
      char blue = command[SET_ALL_LED_LENGTH + 2];
      for (int i = 0; i < num_leds_; ++i) {
        neopixel_[i / PIXELS_PER_BLOCK]->setPixelColor(i, red, green, blue);
      }
      return true;
    } else if (strncmp(command, LED_GO, LED_GO_LENGTH) == 0) {
      UpdatePixels();
      return true;
    }
    return false;
  }

  ~LedModule() {
    for (int i = 0; i * PIXELS_PER_BLOCK < num_leds_; ++i) {
      delete neopixel_[i];
    }
  }

 private:
  int tick;
  uint8_t tick_red, tick_blue, tick_green;
  int num_leds_ = 300;
  Adafruit_NeoPixel *neopixel_[3];
};

}  // namespace nebree8

#endif  // NEBREE8_ARDUINO_LED_MODULE_H_
