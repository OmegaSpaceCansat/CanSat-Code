import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Cambia este puerto por el correspondiente en tu sistema
# Ejemplo en Windows: 'COM3'
# Ejemplo en Linux/Mac: '/dev/ttyUSB0' o '/dev/ttyACM0'
PORT = 'COM25'
BAUD_RATE = 115200

ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

# Inicializa figura
fig, ax = plt.subplots()
data = np.zeros((8, 8))
im = ax.imshow(data, cmap='inferno', vmin=20, vmax=40)
plt.colorbar(im)

def update(frame):
    global data
    values = []

    # Leer 64 valores (8x8) de la matriz
    while len(values) < 64:
        line = ser.readline().decode('utf-8').strip()
        if line == "" or line.startswith("-") or "Inicializando" in line:
            continue  # Ignorar líneas vacías o de separación
        try:
            row = [float(val) for val in line.split()]
            values.extend(row)
        except ValueError:
            continue  # En caso de error de conversión, saltar

    if len(values) == 64:
        data = np.array(values).reshape((8, 8))
        im.set_array(data)

    return [im]

ani = FuncAnimation(fig, update, interval=500)
plt.title("Cámara Térmica AMG8833")
plt.show()
