import serial
import time

arduino_port = 'COM4'
baud_rate = 9600

try:
    arduino = serial.Serial(arduino_port, baud_rate, timeout=1)
    time.sleep(1)

    while True:
        user_input = input("Введите 0-255: ")
        if user_input.lower() == 'q':
            print("Завершение работы.")
            break
        

        try:
            value = int(user_input)
            if 0 <= value <= 255:

                arduino.write(f"{value}\n".encode())
                print(f"Отправлено: {value}")
                
                time.sleep(0.1)
                while arduino.in_waiting:
                    response = arduino.readline().decode().strip()
                    print(f"Arduino: {response}")
            else:
                print("диапазон 0-255.")
        except ValueError:
            print("целое число.")
            
except serial.SerialException as e:
    print(f"Ошибка: Не удалось открыть порт  {e}")
except Exception as e:
    print(f"Произошла неизвестная ошибка: {e}")
finally:
    if 'arduino' in locals() and arduino.is_open:
        arduino.close()
        print("Соединение закрыто.")