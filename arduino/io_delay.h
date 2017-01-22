#ifndef NEBREE8_ARDUINO_IO_DELAY_H_
#define NEBREE8_ARDUINO_IO_DELAY_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"

namespace nebree8 {

const char* IO_DELAY = "DELAY";
const int IO_DELAY_LENGTH = 5;

class IODelay : public arduinoio::UCModule {
 public:
  IODelay() {
    timed_callback_ = NULL;
    pin_ = 0;
    on_ = 0;
    outgoing_message_ready_ = false;
  }

  void ToggleIO() {
    const int kLocalAddress = 0;
    const int kSetIoSize = 8;
    char command[kSetIoSize];
    strncpy(command, "SET_IO", 6);
    command[6] = pin_;
    command[7] = on_;
    message_.Reset(kLocalAddress, kSetIoSize, (unsigned char*) command);
    outgoing_message_ready_ = true;
    timed_callback_ = NULL;
  }

  virtual const arduinoio::Message* Tick() {
    if (outgoing_message_ready_) {
      outgoing_message_ready_ = false;
      return &message_;
    }
    if (timed_callback_ != NULL) {
      timed_callback_->Update();
    }
    return NULL;
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, IO_DELAY, IO_DELAY_LENGTH) == 0) {
      for (int i = IO_DELAY_LENGTH; i < length - 1; i += 2) {
        pin_ = command[IO_DELAY_LENGTH];
        on_ = command[IO_DELAY_LENGTH + 1];
        // Tenths of a second
        const unsigned long delay =
            static_cast<unsigned long>(command[IO_DELAY_LENGTH + 2]);
        ToggleIO();
        // Flip it.
        // Dies even with this off and no message sending.
        on_ = on_ == 0x0 ? 0x1 : 0x0;
        timed_callback_ = new arduinoio::TimedCallback<IODelay>(
            100L * delay,
            this,
            &IODelay::ToggleIO);
        return true;
      }
    }
    return false;
  }

 private:
  bool first_;
  char pin_;
  char on_;
  bool outgoing_message_ready_;
  arduinoio::Message message_;

  arduinoio::TimedCallback<IODelay> *timed_callback_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_UC_IO_MODULE_H_
