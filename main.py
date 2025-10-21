from machine import Pin, SoftI2C
import time
import ssd1306

# Importa el paquete de la librería que acabas de crear
import max30102 

# --- Configuración de la pantalla OLED ---
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
OLED_I2C_ADDR = 0x3C

# --- Configuración del I2C ---
# Usando SoftI2C para mayor compatibilidad. Puedes usar I2C(0, ...) si lo prefieres.
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=400000)

# --- Inicialización de la pantalla OLED ---
try:
    display = ssd1306.SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=OLED_I2C_ADDR)
    display.fill(0)
    display.text("Iniciando...", 0, 0)
    display.show()
    time.sleep(1)
except Exception as e:
    print(f"Error al iniciar la pantalla OLED: {e}")
    while True: pass

# --- Inicialización del sensor MAX30102 ---
try:
    # Crea una instancia del sensor desde la librería
    sensor = max30102.MAX30102(i2c=i2c)

    if not sensor.check_part_id():
        print("Sensor MAX30102 no encontrado o ID incorrecto.")
        display.fill(0)
        display.text("Sensor Error", 0, 10)
        display.show()
        while True: pass
    
    # Configura el sensor con los ajustes recomendados para pulsoximetría
    sensor.setup_sensor()
    print("Sensor MAX30102 configurado.")
    
except Exception as e:
    print(f"Error al iniciar el sensor MAX30102: {e}")
    while True: pass


# --- Bucle Principal ---
while True:
    # Revisa si hay nuevos datos en la FIFO del sensor
    sensor.check()
    
    # Si hay datos disponibles en el búfer
    if sensor.available():
        # Lee el valor más antiguo del búfer
        red_reading = sensor.pop_red_from_storage()
        ir_reading = sensor.pop_ir_from_storage()

        # Muestra los datos crudos en el monitor serie (REPL) para depuración
        print(f"RAW - Red: {red_reading}, IR: {ir_reading}")

        # Actualiza la pantalla OLED con los valores crudos
        display.fill(0)
        
        # Muestra el valor del LED Rojo
        display.text("Red:", 0, 10)
        display.text(str(red_reading), 40, 10)
        
        # Muestra el valor del LED Infrarrojo
        display.text("IR:", 0, 35)
        display.text(str(ir_reading), 40, 35)

        display.show()
    
    # Pequeña pausa
    time.sleep_ms(20)
