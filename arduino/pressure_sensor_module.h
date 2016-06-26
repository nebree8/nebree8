#ifndef NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_
#define NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_

#include <string.h>

#include "../arduinoio/lib/uc_module.h"
#include "../arduinoio/lib/message.h"
#include "../arduinoio/lib/timed_callback.h"
#include "../MS5803-14BA_Breakout/Libraries/Arduino/src/SparkFun_MS5803_I2C.h"

namespace nebree8 {

const size_t kPressureSize = 4 * 3 + 1; // 4 bytes per float, plus state

const char* GET_PRESSURE = "GETP";
const int GET_PRESSURE_LENGTH = 4;
// No further arguments needed.
//
// Replies with message:
// command[0:3] = pressure
// command[4] = state

const char* HOLD_PRESSURE = "HOLDP";
const int HOLD_PRESSURE_LENGTH = 5;
// command[0:3] = min pressure float
// command[4:7] = max pressure float
// command[8] = hold (if not 0x01, the device just reads and waits).
// command[9] = pressure valve pin

const char* external_MOVE = "MOVE";
const int external_MOVE_LENGTH = 4;
const char* external_MDONE = "MDONE";
const int external_MDONE_LENGTH = 5;

class PressureSensorModule : public arduinoio::UCModule {
 public:
  PressureSensorModule() {
    sensor_ = new MS5803(ADDRESS_HIGH);  // Default address is 0x76, based on jumpers soldered.
    sensor_->reset();
    sensor_->begin();
    timed_callback_ = NULL;
    outgoing_message_ready_ = false;
    state_ = DEPRESSURIZED;
    moving_do_nothing_ = false;
  }

  enum State {
    DEPRESSURIZED,
    INCREASE_PRESSURE,
    MAINTAIN_PRESSURE,
    ERROR
  };

  virtual const arduinoio::Message* Tick() {
    if (outgoing_message_ready_) {
      outgoing_message_ready_ = false;
      return &message_;
    }
    if (timed_callback_ == NULL) {
      timed_callback_ = new arduinoio::TimedCallback<PressureSensorModule>(
          state_ == ERROR ? 2000 : 200, this,
          &PressureSensorModule::ReadPressure);
    }
    timed_callback_->Update();
    return NULL;
  }

  void ReadPressure() {
    timed_callback_ = NULL;
    if (moving_do_nothing_) return;
    float *pressure_float = (float*) pressure_;
    pressure_float[0] = sensor_->getPressure(ADC_512);  // lower-level precision
    pressure_float[1] = last_reading_;
    pressure_float[2] = second_last_reading_;
    switch (state_) {
      case MAINTAIN_PRESSURE:
        if (pressure_float[0] < hold_pressure_mbar_min_) {
          OpenPressureValve();
          state_ = INCREASE_PRESSURE;
          second_last_reading_ = 0.0f;
          last_reading_ = 0.0f;
        } else {
          ClosePressureValve();
        }
        break;
      case INCREASE_PRESSURE:
        if (pressure_float[0] > hold_pressure_mbar_max_) {
          ClosePressureValve();
          state_ = MAINTAIN_PRESSURE;
      //} else if (pressure_float[0] <= last_reading_ &&
      //           pressure_float[0] <= second_last_reading_) {
      //  // Error -- valve is open, but pressure isn't increasing!
      //  // TODO: this is likely to fire when starting up.
      //  ClosePressureValve();
      //  state_ = ERROR;
        }
        break;
      case ERROR:
        // Try again. Note that the time delay will keep this from overpressuring or wasting all our gas.
        last_reading_ = 0.0f;
        second_last_reading_ = 0.0f;
        state_ = MAINTAIN_PRESSURE;
      default:
        ClosePressureValve();
        break;
    }
    second_last_reading_ = last_reading_;
    last_reading_ = pressure_float[0];
  }

  virtual bool AcceptMessage(const arduinoio::Message &message) {
    int length;
    const char* command = (const char*) message.command(&length);
    if (strncmp(command, HOLD_PRESSURE, HOLD_PRESSURE_LENGTH) == 0) {
      command = (const char*) message.command(&length) + HOLD_PRESSURE_LENGTH;
      if (command[8] == 0x01) {  // hold pressure
        const float *pressure_limits = (const float*) command;
        hold_pressure_mbar_min_ = pressure_limits[0];
        hold_pressure_mbar_max_ = pressure_limits[1];
        pressure_valve_pin_ = command[9];
        state_ = MAINTAIN_PRESSURE;
      } else {
        state_ = DEPRESSURIZED;
        ClosePressureValve();
      }
      moving_do_nothing_ = false;
      return true;
    } else if (strncmp(command, GET_PRESSURE, GET_PRESSURE_LENGTH) == 0) {
      const int kOutgoingAddress = 99;
      pressure_[kPressureSize - 1] = state_;
      message_.Reset(kOutgoingAddress, kPressureSize, pressure_);
      outgoing_message_ready_ = true;
      moving_do_nothing_ = false;
      return true;
    } else if (strncmp(command, external_MOVE, external_MOVE_LENGTH) == 0) {
      ClosePressureValve();
      if (state_ == INCREASE_PRESSURE) {
        state_ = MAINTAIN_PRESSURE;
      }
      moving_do_nothing_ = true;
    } else if (strncmp(command, external_MDONE, external_MDONE_LENGTH) == 0) {
      moving_do_nothing_ = false;
    }
    return false;
  }

  void ClosePressureValve() {
    SetPressureValve(0x0);
  }

  void OpenPressureValve() {
    SetPressureValve(0x1);
  }

  void SetPressureValve(char on) {
  //pinMode(pressure_valve_pin_, OUTPUT);
  //digitalWrite(pressure_valve_pin_, on == 0x01 ? HIGH : LOW);
    const int kLocalAddress = 0;
    const int kSetIoSize = 8;
    char command[kSetIoSize];
    strncpy(command, "SET_IO", 6);
    command[6] = pressure_valve_pin_;
    command[7] = on;
    message_.Reset(kLocalAddress, kSetIoSize, (unsigned char*) command);
    outgoing_message_ready_ = true;
  }

 private:
  MS5803* sensor_;
  arduinoio::Message message_;
  arduinoio::TimedCallback<PressureSensorModule> *timed_callback_;
  unsigned char pressure_[kPressureSize];

  State state_;
  float hold_pressure_mbar_min_;
  float hold_pressure_mbar_max_;

  unsigned char pressure_valve_pin_;

  float last_reading_;
  float second_last_reading_;

  bool outgoing_message_ready_;
  bool moving_do_nothing_;
};

}  // namespace nebree8
#endif  // NEBREE8_ARDUINO_PRESSURE_SENSOR_MODULE_H_
