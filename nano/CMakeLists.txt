#=============================================================================#
# Author: MarkStevens
# Date:   2012/04/17
#                                                                             #
# Description: Arduino nano board for measuring weight.
#                                                                             #
#=============================================================================#

cmake_minimum_required(VERSION 2.8)
#====================================================================#
#  Settings                                                          #
#====================================================================#

#set(CMAKE_SOURCE_DIR /home/pi/nebree8/nano) # Source dir
set(CMAKE_SOURCE_DIR /home/mark/nebree8/nano) # Source dir
set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/../arduino-cmake/cmake/ArduinoToolchain.cmake) # Arduino Toolchain
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic")
set(ARDUINO_SDK_VERSION "1.6.9")
set(ARDUINO_SDK /home/mark/nebree8/Arduino-1.6.9)
set(ARDUINO_SDK_PATH /home/mark/nebree8/Arduino-1.6.9)

project(LoadCellNano C CXX)
#set(ARDUINO_SDK /usr/share/arduino-1.0.6)
#set(ARDUINO_SDK /usr/share/arduino)
set(FIRMWARE_NAME nano_controller)


set(${FIRMWARE_NAME}_BOARD nano328)               # Arduino Target board
set(${FIRMWARE_NAME}_SRCS  nano_controller.cc)

set(${FIRMWARE_NAME}_PORT /dev/ttyUSB0)            # Serial upload port
#link_directories(/home/pi/nebree8/arduino)
#link_directories(/home/pi/nebree8/arduino/MS5803)
#link_directories(/home/pi/nebree8/MS5803-14BA_Breakout/Libraries/Arduino/MS5803)
#set(${FIRMWARE_NAME}_LIBS MS5803)  # Pressure sensor library.
set(${FIRMWARE_NAME}_NO_AUTOLIBS false)

#====================================================================#
#  Target generation                                                 #
#====================================================================#
generate_arduino_firmware(${FIRMWARE_NAME})
#target_link_libraries(${FIRMWARE_NAME} LINK_PUBLIC MS5803)
