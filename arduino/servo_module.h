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

class ServoModule : public arduinoio::UCModule {
 public:
  virtual const arduinoio::Message* Tick() {
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (length > SERVO_LENGTH &&
        (strncmp(command, SERVO, SERVO_LENGTH) == 0)) {
      char pin = command[SERVO_LENGTH];
      char speed = command[SERVO_LENGTH + 1];
      servo_.attach(pin);
      servo_.write(speed);
      return true;
    }
    return false;
  }

 private:
  Servo servo_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_SERVO_MODULE_H_
