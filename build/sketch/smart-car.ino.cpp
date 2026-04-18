#include <Arduino.h>
#line 1 "C:\\Users\\user\\Desktop\\margo\\smart-car\\smart-car.ino"
// void setup() {
//   pinMode(9, OUTPUT);
// }

// void loop() {
//   digitalWrite(9, HIGH);  // полное включение
//   delay(1000);
//   digitalWrite(9, LOW);   // выключение
//   delay(1000);
// }




const int ledPin = 9;
int brightness = 0;

#line 18 "C:\\Users\\user\\Desktop\\margo\\smart-car\\smart-car.ino"
void setup();
#line 24 "C:\\Users\\user\\Desktop\\margo\\smart-car\\smart-car.ino"
void loop();
#line 18 "C:\\Users\\user\\Desktop\\margo\\smart-car\\smart-car.ino"
void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
  Serial.println("Arduino готов к работе. Введите число от 0 до 255:");
}

void loop() {
  if (Serial.available() > 0) {
    brightness = Serial.parseInt();
    if (brightness >= 0 && brightness <= 255) {
      analogWrite(ledPin, brightness);
      Serial.print("Яркость установлена на: ");
      Serial.println(brightness);
    } else {
      Serial.println("Ошибка: введите число от 0 до 255.");
    }
  }
}








