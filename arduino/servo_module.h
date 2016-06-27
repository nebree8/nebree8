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

const int NEUTRAL = 0;
const int MAX_SIGNAL = 2300;
const int MIN_SIGNAL = 400;

class ServoModule : public arduinoio::UCModule {
 public:
   ServoModule() {
    servo_.attach(13);
    servo_.write(NEUTRAL);
  //unsigned long kUsecDelay = 4000000;
  //timed_callback_ = NULL;
  //new TimedCallback<ServoModule>(kUsecDelay, this,
  //    &ServoModule::TurnOn);
  }

  virtual const arduinoio::Message* Tick() {
  //if (timed_callback_ != NULL) {
  //  timed_callback_->Update();
  //}
    return NULL;
  }

  void TurnOff() {
    servo_.write(0);
    //timed_callback_ = NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (length > SERVO_LENGTH &&
        (strncmp(command, SERVO, SERVO_LENGTH) == 0)) {
      char pin = command[SERVO_LENGTH];
      char speed = command[SERVO_LENGTH + 1];
      //servo_.attach(pin);
      int full_speed = 10 * speed;
      if (speed != 0) {
        full_speed = 400;
      }
      servo_.write(full_speed);
      return true;
    }
    return false;
  }

 private:
  Servo servo_;
//arduinoio::TimedCallback<ServoModule> *timed_callback_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_SERVO_MODULE_H_
