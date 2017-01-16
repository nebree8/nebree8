#ifndef NEBREE8_ARDUINO_SERVO_MODULE_H_
#define NEBREE8_ARDUINO_SERVO_MODULE_H_

#include <string.h>

#include <Servo.h>
#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"

namespace nebree8 {

const char* SERVO = "SERV";
const int SERVO_LENGTH = 4;

const int MAX_SIGNAL = 2300;
const int MIN_SIGNAL = 400;

class ServoModule : public arduinoio::UCModule {
 public:
   ServoModule(const char pin,
       const char start_speed) : pin_(pin), start_speed_(start_speed) {
    servo_.attach(pin_);
    servo_.write(start_speed);
  }

  virtual const arduinoio::Message* Tick() {
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (length > SERVO_LENGTH &&
        (strncmp(command, SERVO, SERVO_LENGTH) == 0)) {
      const char command_pin = command[SERVO_LENGTH];
      if (command_pin == pin_) {
        char speed = command[SERVO_LENGTH + 1];
        servo_.write(speed);
        return true;
      }
    }
    return false;
  }

 private:
  Servo servo_;
  const char pin_;
  const char start_speed_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_SERVO_MODULE_H_
