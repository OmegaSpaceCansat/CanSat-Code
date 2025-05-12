import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -------- CONFIGURACIÓN --------
NOMBRE_ARCHIVO = "datos.csv"

# Nombres de columna que usamos en el Arduino
COLUMNAS = ["Etiqueta", "Temp", "Presion", "humedad", "Altitud","Latitud", "Longitud", "AltGPS", "Ax", "Ay", "Az", "Gx", "Gy", "Gz", "nivelAudio", "Paquete"]

# -------- CARGA DE DATOS --------
if not os.path.exists(NOMBRE_ARCHIVO):
    print(f"❌ No se encontró el archivo '{NOMBRE_ARCHIVO}' en esta carpeta.")
    exit()

# Leer CSV sin encabezados y forzar nombres de columnas
df = pd.read_csv(NOMBRE_ARCHIVO, names=COLUMNAS, on_bad_lines='skip', header=None)

# Verificar columnas necesarias
if "nivelAudio" not in df.columns or "Paquete" not in df.columns:
    print(f"❌ El archivo no contiene las columnas esperadas.")
    print("Columnas detectadas:", df.columns.tolist())
    exit()

# Usar Paquete como índice
df.set_index("Paquete", inplace=True)

# -------- GRÁFICO DE LÍNEA --------
plt.figure(figsize=(10, 4))
plt.plot(df["nivelAudio"], color="blue", linewidth=1)
plt.title("Nivel de Sonido durante el Vuelo")
plt.xlabel("Paquete")
plt.ylabel("Nivel de Audio (RMS)")
plt.grid(True)
plt.tight_layout()
plt.savefig("audio_linea.png")
print("📈 Gráfico de línea guardado como 'audio_linea.png'")
plt.show()

# -------- HEATMAP / ESPECTROGRAMA VISUAL --------
plt.figure(figsize=(10, 2))
sns.heatmap([df["nivelAudio"].values], cmap="magma", cbar=True, xticklabels=False, yticklabels=False)
plt.title("Espectrograma Visual del Audio")
plt.tight_layout()
plt.savefig("audio_heatmap.png")
print("🔥 Espectrograma visual guardado como 'audio_heatmap.png'")
plt.show()
