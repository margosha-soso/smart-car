import serial
import time
import os

# === НАСТРОЙКИ ПОДКЛЮЧЕНИЯ ===
BLUETOOTH_PORT = 'COM4'   # Ваш порт для Bluetooth
BAUD_RATE = 115200        # Скорость (должна совпадать со скетчем)

# === ФУНКЦИИ УПРАВЛЕНИЯ ===
def send_command(connection, command):
    """Отправляет команду на Arduino"""
    connection.write(command.encode())
    print(f"📤 Отправлено: {command}")

def wait_for_response(connection, timeout=0.3):
    """Читает ответ от Arduino"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if connection.in_waiting > 0:
            response = connection.readline().decode().strip()
            if response:
                print(f"📥 Arduino: {response}")

def print_menu():
    """Выводит меню управления"""
    os.system('cls' if os.name == 'nt' else 'clear')  # Очистка экрана
    print("="*50)
    print(" 🤖 УПРАВЛЕНИЕ РОБОТОМ ПО BLUETOOTH")
    print("="*50)
    print("  🔼 F  - Вперёд")
    print("  🔽 B  - Назад")
    print("  ◀️ L  - Поворот налево")
    print("  ▶️ R  - Поворот направо")
    print("  ⏹ S  - Стоп")
    print("-"*50)
    print("  📊 +  - Увеличить скорость")
    print("  📉 -  - Уменьшить скорость")
    print("  ❌ Q  - Выйти из программы")
    print("="*50)
    print(f"Текущая скорость: {speedMotor} (0-255)")

# === ОСНОВНАЯ ПРОГРАММА ===
def main():
    global speedMotor
    speedMotor = 180  # Начальная скорость
    
    print("="*50)
    print(" 🤖 РОБОТ С УПРАВЛЕНИЕМ ПО BLUETOOTH")
    print("="*50)
    
    try:
        # Подключаемся к Arduino по Bluetooth
        print(f"\n🔌 Подключение к {BLUETOOTH_PORT} на скорости {BAUD_RATE} бод...")
        arduino = serial.Serial(BLUETOOTH_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Ждём, пока установится соединение
        
        print(f"Успешно подключено к {BLUETOOTH_PORT}!")
        print("💡 Светодиод на модуле должен гореть постоянно")
        
        # Отправляем команду стоп для проверки
        send_command(arduino, 'S')
        time.sleep(0.2)
        wait_for_response(arduino)
        
        print_menu()
        
        # Основной цикл управления
        while True:
            # Получаем команду от пользователя
            command = input("\n🚗 Введите команду: ").strip().upper()
            
            # Обработка выхода
            if command == 'Q':
                print("\n🛑 Завершение работы...")
                send_command(arduino, 'S')
                time.sleep(0.2)
                wait_for_response(arduino)
                break
            
            # Управление скоростью
            if command == '+':
                speedMotor = min(255, speedMotor + 10)
                print(f"⬆️ Скорость увеличена до: {speedMotor}")
                print_menu()
                continue

            elif command == '-':
                speedMotor = max(0, speedMotor - 10)
                print(f"⬇️ Скорость уменьшена до: {speedMotor}")
                print_menu()
                continue
            
            # Обработка команд движения
            if command in ['F', 'B', 'L', 'R', 'S']:
                send_command(arduino, command)
                time.sleep(0.1)
                wait_for_response(arduino)
            else:
                print("❌ Неизвестная команда!")
                print("   Доступные команды: F, B, L, R, S, +, -, Q")
                
    except serial.SerialException as e:
        print(f"\n❌ ОШИБКА: Не удалось открыть порт {BLUETOOTH_PORT}")
        print("   Возможные причины:")
        print("   1. Bluetooth-модуль не сопряжён с ноутбуком")
        print("   2. В Arduino IDE открыт 'Монитор порта' (закройте его)")
        print("   3. Неправильный порт (проверьте в Диспетчере устройств)")
        print(f"\n   Техническая информация: {e}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем")
        send_command(arduino, 'S')
        
    except Exception as e:
        print(f"\n❌ Непредвиденная ошибка: {e}")
        
    finally:
        # Закрываем соединение, если оно было открыто
        if 'arduino' in locals() and arduino.is_open:
            arduino.close()
            print("\n🔌 Соединение с роботом закрыто")
        print("\n👋 До свидания!")

# Запуск программы
if __name__ == "__main__":
    main()