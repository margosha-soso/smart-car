// Пины для Motor Shield L298P
#define PWMA 3   // Скорость левых моторов
#define PWMB 11   // Скорость правых моторов  
#define DIRA 12  // Направление левых моторов
#define DIRB 13  // Направление правых моторов

int speedMotor = 150; // Базовая скорость (0-255)

void setup() {
  // Настройка пинов моторов
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DIRA, OUTPUT);
  pinMode(DIRB, OUTPUT);
  
  // Принудительная остановка моторов при старте
  digitalWrite(DIRA, LOW);
  digitalWrite(DIRB, LOW);
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);
  
  // Инициализация связи
  Serial.begin(115200);
  
  Serial.println("Робот готов к работе!");
  Serial.println("Команды: F - вперёд, B - назад, L - влево, R - вправо, S - стоп");
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    switch (command) {
      case 'F': // Вперёд
        digitalWrite(DIRA, HIGH);
        digitalWrite(DIRB, HIGH);
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("ВПЕРЁД");
        break;
        
      case 'B': // Назад
        digitalWrite(DIRA, LOW);
        digitalWrite(DIRB, LOW);
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("НАЗАД");
        break;
        
      case 'L': // Поворот налево
        digitalWrite(DIRA, LOW);   // Левые назад
        digitalWrite(DIRB, HIGH);  // Правые вперёд
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("ВЛЕВО");
        break;
        
      case 'R': // Поворот направо
        digitalWrite(DIRA, HIGH);  // Левые вперёд
        digitalWrite(DIRB, LOW);   // Правые назад
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("ВПРАВО");
        break;
        
      case 'S': // Стоп
        digitalWrite(DIRA, LOW);
        digitalWrite(DIRB, LOW);
        analogWrite(PWMA, 0);
        analogWrite(PWMB, 0);
        Serial.println("СТОП");
        break;
    }
  }
}

void setup() {
  // Настройка пинов моторов
  pinMode(PWMA, OUTPUT);
  pinMode(PWMB, OUTPUT);
  pinMode(DIRA, OUTPUT);
  pinMode(DIRB, OUTPUT);

  // Принудительная остановка моторов при старте (чтобы не было рывка)
  digitalWrite(DIRA, LOW);
  digitalWrite(DIRB, LOW);
  analogWrite(PWMA, 0);
  analogWrite(PWMB, 0);

  // Инициализация связи
  Serial.begin(115200);      // Для отладки через USB
  bluetooth.begin(115200);   // Скорость вашего Bluetooth-модуля

  Serial.println("Bluetooth-управление роботом запущено");
  Serial.println("Команды: F - вперёд, B - назад, L - влево, R - вправо, S - стоп");
}

void loop() {
  // Проверяем, пришли ли данные по Bluetooth
  if (bluetooth.available()) {
    char command = bluetooth.read(); // Читаем один символ
    
    // Обработка команды
    switch (command) {
      case 'F': // Вперёд
        digitalWrite(DIRA, HIGH);
        digitalWrite(DIRB, HIGH);
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("Команда: ВПЕРЁД");
        break;
        
      case 'B': // Назад
        digitalWrite(DIRA, LOW);
        digitalWrite(DIRB, LOW);
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("Команда: НАЗАД");
        break;
        
      case 'L': // Поворот налево
        digitalWrite(DIRA, LOW);   // Левые назад
        digitalWrite(DIRB, HIGH);  // Правые вперёд
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("Команда: ВЛЕВО");
        break;
        
      case 'R': // Поворот направо
        digitalWrite(DIRA, HIGH);  // Левые вперёд
        digitalWrite(DIRB, LOW);   // Правые назад
        analogWrite(PWMA, speedMotor);
        analogWrite(PWMB, speedMotor);
        Serial.println("Команда: ВПРАВО");
        break;
        
      case 'S': // Стоп
        digitalWrite(DIRA, LOW);
        digitalWrite(DIRB, LOW);
        analogWrite(PWMA, 0);
        analogWrite(PWMB, 0);
        Serial.println("Команда: СТОП");
        break;
        
      default:
        // Неизвестная команда
        Serial.print("Неизвестная команда: ");
        Serial.println(command);
        break;
    }
  }
}







