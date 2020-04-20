/*
  Arduino code to control a 3D printer, modified to collect candy.
  The Arduino collects the candy based on a 2D space, and gets
  input from the Serial port.

  See https://github.com/Tinggaard/mmsm for more.
*/

#include <Stepper.h>

const int stepsPerRevolution = 200;  // steps per revolution
const int motorRPM = 60; // rpm for motors

// factor between revolutions and pixels
// may need to be int
const double factor = 1.0;

const int udRevs = 10; // revs to to up/down
const int udSteps = udRevs * stepsPerRevolution;

// stepper up/down
Stepper stepperUD(stepsPerRevolution, 8, 9, 10, 11);
// stepper left/right
Stepper stepperLR(stepsPerRevolution, 4, 5, 6, 7);


// setup function
void setup() {
  stepperUD.setSpeed(motorRPM);
  stepperLR.setSpeed(motorRPM);

  // reset steppers
  stepperUD.steps(-1000);
  stepperLR.steps(-1000);

  pinMode(13, OUTPUT); // vacuum pump transistor

  // initialize the serial port:
  Serial.begin(9600);
}

// main-loop function
void loop() {
  // step one revolution  in one direction:
  Serial.println("Reading coordinate");
  int x = read();

  // move stepper and collect candy
  move(x, stepperUD, stepperLR);
  Serial.println("Collected a piece of candy")
  delay(500);
}


// custom function to read from serial
// based on this SO answer: https://stackoverflow.com/a/16148228
int read() {
  // 12 is the maximum length of a decimal representation of a 32-bit integer,
  // including space for a leading minus sign and terminating null byte
  byte intBuffer[12];
  String intData = "";
  int delimiter = (int) '\n';


  // read data
  while (Serial.available()) {
    delay(30); // allow buffer to fill
    int ch = Serial.read();

    // if newline, break
    if (ch == delimiter) {
      break;
    }

    // else read
    else {
      intData += (char) ch;
    }
  }

  // Copy read data into a char array for use by atoi
  // Include room for the null terminator
  int intLength = intData.length() + 1;
  intData.toCharArray(intBuffer, intLength);

  // Reinitialize intData for use next time around the loop
  intData = "";

  // Convert ASCII-encoded integer to an int
  int i = atoi(intBuffer);

  return i;

}


// move to motor to coordinate given from argument
void move(int coord, Stepper ud, Stepper lr) {
  // steps to catch the candy
  // revs * steps per rev
  int steps = (coord / factor) * stepsPerRevolution;

  lr.step(steps); // run said steps
  ud.step(udSteps); // lift table
  delay(100); // sleep 100 ms

  digitalWrite(13, HIGH); // start sucking
  delay(100); // sleep 100 ms

  // go back to release candy
  ud.step(-udSteps);
  lr.step(-steps)
  delay(100);

  digitalWrite(13, LOW); // stop sucking
  delay(100); // sleep 100 ms

}
