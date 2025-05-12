import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation as R
from matplotlib import cm
from matplotlib.colors import Normalize, to_hex
from matplotlib import colormaps
import re

# Crear carpeta de resultados si no existe
os.makedirs("resultados", exist_ok=True)

# Cargar archivo desde ./data/uploads
data_dir = "./data/uploads"
file_name = next((f for f in os.listdir(data_dir) if f.endswith(".csv")), None)

if not file_name:
    raise FileNotFoundError("No se encontró archivo CSV en ./data/uploads")

# Leer y limpiar datos
df = pd.read_csv(os.path.join(data_dir, file_name), on_bad_lines="skip")
if "Identificador" not in df.columns:
    raise ValueError("No se encontró la columna 'Identificador' en el archivo CSV.")
df = df[df["Identificador"] == "OMEGA"].copy()

# Limpiar nombres
df.columns = (
    df.columns
    .str.strip()
    .str.replace("\xa0", "_", regex=False)
    .str.replace(" ", "_")
    .str.lower()
)

# Crear columna de tiempo (asumiendo 0.5s entre muestras)
df["tiempo_s"] = df.index * 0.5

# Buscar nombres de columnas de acelerómetro aunque tengan tildes o variantes
acel_x_col = next((c for c in df.columns if 'acel' in c and 'x' in c), None)
acel_y_col = next((c for c in df.columns if 'acel' in c and 'y' in c), None)
acel_z_col = next((c for c in df.columns if 'acel' in c and 'z' in c), None)
if not all([acel_x_col, acel_y_col, acel_z_col]):
    raise ValueError(f"No se encontraron columnas de acelerómetro. Columnas disponibles: {list(df.columns)}")
df["acelerometro_x"] = pd.to_numeric(df[acel_x_col], errors="coerce")
df["acelerometro_y"] = pd.to_numeric(df[acel_y_col], errors="coerce")
df["acelerometro_z"] = pd.to_numeric(df[acel_z_col], errors="coerce")

# Convertir columnas relevantes a numérico
df["altitud"] = pd.to_numeric(df["altitud"], errors="coerce")
df["temperatura"] = pd.to_numeric(df["temperatura"], errors="coerce")
df["gyroscopio_x"] = pd.to_numeric(df["gyroscopio_x"], errors="coerce")
df["gyroscopio_y"] = pd.to_numeric(df["gyroscopio_y"], errors="coerce")
df["gyroscopio_z"] = pd.to_numeric(df["gyroscopio_z"], errors="coerce")
df = df.dropna(subset=["altitud", "temperatura", "gyroscopio_x", "gyroscopio_y", "gyroscopio_z", "acelerometro_x", "acelerometro_y", "acelerometro_z"])

if len(df) < 2:
    raise ValueError("No hay suficientes datos válidos para graficar.")

# Suavizar altitud para evitar saltos bruscos
if len(df) > 11:
    df["altitud_suave"] = savgol_filter(df["altitud"], 11, 3)  # ventana 11, polinomio grado 3
else:
    df["altitud_suave"] = df["altitud"]

# Magnitud del giroscopio
df["gyro_mag"] = np.sqrt(df["gyroscopio_x"]**2 + df["gyroscopio_y"]**2 + df["gyroscopio_z"]**2)

# Trayectoria 3D: solo eje Z (altitud)
df["x"] = 0
df["y"] = 0
df["z"] = df["altitud_suave"]

# --- GRAFICA 3D FIJA (honesta) ---
zmin = float(df["z"].min()) - 2
zmax = float(df["z"].max()) + 2
inicio = dict(x=0, y=0, z=df["z"].iloc[0])
fin = dict(x=0, y=0, z=df["z"].iloc[-1])
apogeo_idx = df["z"].idxmax()
apogeo = dict(x=0, y=0, z=df["z"].loc[apogeo_idx])

trayectoria = go.Scatter3d(
    x=df["x"], y=df["y"], z=df["z"],
    mode="lines",
    line=dict(color="cyan", width=4),
    name="Trayectoria"
)
puntos = go.Scatter3d(
    x=[inicio["x"], apogeo["x"], fin["x"]],
    y=[inicio["y"], apogeo["y"], fin["y"]],
    z=[inicio["z"], apogeo["z"], fin["z"]],
    mode="markers+text",
    marker=dict(size=[10, 14, 10], color=["green", "gold", "red"]),
    text=["Inicio", "Apogeo", "Fin"],
    textposition="top center",
    name="Eventos"
)
fig3d_fija = go.Figure(
    data=[trayectoria, puntos],
    layout=go.Layout(
        title="Trayectoria 3D de la Lata Satélite (Altitud Real)",
        scene=dict(
            xaxis_title="X (fijo)",
            yaxis_title="Y (fijo)",
            zaxis_title="Altitud (m)",
            zaxis=dict(range=[zmin, zmax]),
            bgcolor="black"
        ),
        template="plotly_dark"
    )
)
fig3d_fija.write_html("resultados/trayectoria_lata_3d_fija.html")

def mejorar_html_plotly(path_html, titulo):
    with open(path_html, 'r', encoding='utf-8') as f:
        html = f.read()
    # Agregar lang="es" a <html>
    html = re.sub(r'<html(.*?)>', r'<html\1 lang="es">', html, count=1)
    # Agregar <meta name="viewport"> en <head>
    html = re.sub(r'(<head.*?>)', r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1">', html, count=1)
    # Agregar o reemplazar <title>
    if '<title>' in html:
        html = re.sub(r'<title>.*?</title>', f'<title>{titulo}</title>', html, count=1)
    else:
        html = re.sub(r'(<head.*?>)', r'\1\n    <title>' + titulo + '</title>', html, count=1)
    with open(path_html, 'w', encoding='utf-8') as f:
        f.write(html)

mejorar_html_plotly("resultados/trayectoria_lata_3d_fija.html", "Trayectoria 3D de la Lata Satélite (Altitud Real)")

# --- ANIMACION 3D: Lata sube y baja, inclinación oscilante proporcional al giro ---
frames = []
for i in range(0, len(df), 5):
    trayectoria = go.Scatter3d(
        x=df["x"][:i+1], y=df["y"][:i+1], z=df["z"][:i+1],
        mode="lines",
        line=dict(color="cyan", width=4),
        name="Trayectoria"
    )
    # Oscilación suave: ángulo pequeño proporcional a la magnitud del giroscopio
    osc_ang = 0.0005 * df["gyro_mag"].iloc[i]  # factor ajustable
    roll = osc_ang * np.sin(i/15)
    pitch = osc_ang * np.cos(i/15)
    yaw = 0
    # Crear cilindro orientado
    theta = np.linspace(0, 2 * np.pi, 20)
    z_lata = np.array([0, 1.5])
    theta_grid, z_grid = np.meshgrid(theta, z_lata)
    x_cil = 0.05 * np.cos(theta_grid)
    y_cil = 0.05 * np.sin(theta_grid)
    z_cil = z_grid
    puntos = np.stack([x_cil.flatten(), y_cil.flatten(), z_cil.flatten()], axis=1)
    rot = R.from_euler('xyz', [roll, pitch, yaw])
    puntos_rot = rot.apply(puntos)
    x_cil_r = puntos_rot[:,0].reshape(x_cil.shape)
    y_cil_r = puntos_rot[:,1].reshape(y_cil.shape)
    z_cil_r = puntos_rot[:,2].reshape(z_cil.shape) + df["z"].iloc[i]
    lata = go.Surface(
        x=x_cil_r,
        y=y_cil_r,
        z=z_cil_r,
        showscale=False,
        colorscale=[[0, 'red'], [1, 'darkred']],
        opacity=0.9,
        name="Lata"
    )
    frames.append(go.Frame(data=[trayectoria, lata], name=str(i)))
fig_anim = go.Figure(
    data=[frames[0].data[0], frames[0].data[1]],
    layout=go.Layout(
        title="Animación 3D de la Lata Satélite (Altitud real y oscilación suave)",
        scene=dict(
            xaxis_title="X (fijo)",
            yaxis_title="Y (fijo)",
            zaxis_title="Altitud (m)",
            zaxis=dict(range=[zmin, zmax]),
            bgcolor="black"
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="▶️ Play", method="animate", args=[None, {"frame": {"duration": 50, "redraw": True}, "fromcurrent": True}])]
        )],
        template="plotly_dark"
    ),
    frames=frames
)
fig_anim.write_html("resultados/animacion_lata_3d_suave.html")
mejorar_html_plotly("resultados/animacion_lata_3d_suave.html", "Animación 3D de la Lata Satélite")

# --- GRAFICAS 2D ---
fig_alt = px.line(df, x="tiempo_s", y=["altitud", "altitud_suave"],
                  labels={"value": "Altitud (m)", "tiempo_s": "Tiempo (s)", "variable": "Serie"},
                  title="Altitud vs Tiempo (Original y Suavizada)")
fig_alt.update_traces(line=dict(width=2))
fig_alt.write_html("resultados/altitud_vs_tiempo.html")
mejorar_html_plotly("resultados/altitud_vs_tiempo.html", "Altitud vs Tiempo")

fig_temp = px.line(df, x="tiempo_s", y="temperatura", title="Temperatura vs Tiempo", labels={"tiempo_s": "Tiempo (s)", "temperatura": "Temperatura (°C)"})
fig_temp.update_traces(line=dict(width=2, color="orange"))
fig_temp.write_html("resultados/temperatura_vs_tiempo.html")
mejorar_html_plotly("resultados/temperatura_vs_tiempo.html", "Temperatura vs Tiempo")

fig_gyro = px.line(df, x="tiempo_s", y="gyro_mag", title="Magnitud del Giroscopio vs Tiempo", labels={"tiempo_s": "Tiempo (s)", "gyro_mag": "Magnitud del Giroscopio (unidades)"})
fig_gyro.update_traces(line=dict(width=2, color="purple"))
fig_gyro.write_html("resultados/giroscopio_vs_tiempo.html")
mejorar_html_plotly("resultados/giroscopio_vs_tiempo.html", "Magnitud del Giroscopio vs Tiempo")

# --- GRAFICA 3D CON COLOR POR INTENSIDAD DE GIRO ---
# Normalizar la magnitud del giroscopio para el color
norm = Normalize(vmin=df["gyro_mag"].min(), vmax=df["gyro_mag"].max())
colormap = colormaps.get_cmap('plasma')
colors = [to_hex(colormap(norm(val))) for val in df["gyro_mag"]]

# Crear segmentos de línea coloreados
segments = []
for i in range(len(df)-1):
    seg = go.Scatter3d(
        x=[df["x"].iloc[i], df["x"].iloc[i+1]],
        y=[df["y"].iloc[i], df["y"].iloc[i+1]],
        z=[df["z"].iloc[i], df["z"].iloc[i+1]],
        mode="lines",
        line=dict(color=colors[i], width=6),
        showlegend=False
    )
    segments.append(seg)
# Marcadores de eventos
puntos = go.Scatter3d(
    x=[inicio["x"], apogeo["x"], fin["x"]],
    y=[inicio["y"], apogeo["y"], fin["y"]],
    z=[inicio["z"], apogeo["z"], fin["z"]],
    mode="markers+text",
    marker=dict(size=[10, 14, 10], color=["green", "gold", "red"]),
    text=["Inicio", "Apogeo", "Fin"],
    textposition="top center",
    name="Eventos"
)
# Barra de color
colorbar_trace = go.Scatter3d(
    x=[None], y=[None], z=[None],
    mode='markers',
    marker=dict(
        colorscale='plasma',
        cmin=df["gyro_mag"].min(),
        cmax=df["gyro_mag"].max(),
        colorbar=dict(title="Magnitud del Giroscopio"),
        showscale=True
    ),
    showlegend=False
)
fig3d_color = go.Figure(
    data=segments + [puntos, colorbar_trace],
    layout=go.Layout(
        title="Trayectoria 3D (Altitud) con Color por Intensidad de Giro",
        scene=dict(
            xaxis_title="X (fijo)",
            yaxis_title="Y (fijo)",
            zaxis_title="Altitud (m)",
            zaxis=dict(range=[zmin, zmax]),
            bgcolor="black"
        ),
        template="plotly_dark"
    )
)
fig3d_color.write_html("resultados/trayectoria_3d_color_giro.html")
mejorar_html_plotly("resultados/trayectoria_3d_color_giro.html", "Trayectoria 3D (Altitud) con Color por Intensidad de Giro")

# Filtrar datos: solo a partir de que la altitud supera el valor inicial + 2 metros
umbral_altura = df["altitud_suave"].iloc[0] + 2
idx_inicio_vuelo = df[df["altitud_suave"] > umbral_altura].index.min()
if idx_inicio_vuelo is not None and not np.isnan(idx_inicio_vuelo):
    df_vuelo = df.loc[idx_inicio_vuelo:].copy()
else:
    df_vuelo = df.copy()

# --- GRAFICA 3D: Altitud, Giroscopio y Acelerómetro (solo acelerómetro, animada) ---
if len(df_vuelo) < 3:
    print("⚠️ No hay suficientes datos de vuelo (altitud > suelo) para graficar la trayectoria 3D del acelerómetro.")
else:
    # Puntos de inicio y final
    marker_inicio = go.Scatter3d(
        x=[df_vuelo["acelerometro_x"].iloc[0]],
        y=[df_vuelo["acelerometro_y"].iloc[0]],
        z=[df_vuelo["altitud_suave"].iloc[0]],
        mode="markers+text",
        marker=dict(size=10, color="green"),
        text=["Inicio"],
        textposition="top center",
        name="Inicio"
    )
    marker_final = go.Scatter3d(
        x=[df_vuelo["acelerometro_x"].iloc[-1]],
        y=[df_vuelo["acelerometro_y"].iloc[-1]],
        z=[df_vuelo["altitud_suave"].iloc[-1]],
        mode="markers+text",
        marker=dict(size=10, color="red"),
        text=["Fin"],
        textposition="top center",
        name="Fin"
    )
    frames = []
    paso = max(1, len(df_vuelo)//100)
    try:
        for i in range(2, len(df_vuelo)+1, paso):
            if i > len(df_vuelo):
                i = len(df_vuelo)
            linea = go.Scatter3d(
                x=df_vuelo["acelerometro_x"].iloc[:i],
                y=df_vuelo["acelerometro_y"].iloc[:i],
                z=df_vuelo["altitud_suave"].iloc[:i],
                mode="lines",
                line=dict(color="orange", width=6),
                name="Acelerómetro (XYZ)"
            )
            tiempo = df_vuelo["tiempo_s"].iloc[min(i-1, len(df_vuelo)-1)]
            texto_tiempo = go.Scatter3d(
                x=[df_vuelo["acelerometro_x"].iloc[min(i-1, len(df_vuelo)-1)]],
                y=[df_vuelo["acelerometro_y"].iloc[min(i-1, len(df_vuelo)-1)]],
                z=[df_vuelo["altitud_suave"].iloc[min(i-1, len(df_vuelo)-1)]],
                mode="text",
                text=[f"Tiempo: {tiempo:.1f} s"],
                textfont=dict(color="white", size=16),
                showlegend=False
            )
            data_frame = [linea, marker_inicio, texto_tiempo]
            if i >= len(df_vuelo):
                data_frame.append(marker_final)
            frames.append(go.Frame(data=data_frame, name=str(i)))
        if frames == [] or frames[-1].data != data_frame:
            frames.append(go.Frame(data=data_frame, name="fin"))
    except Exception as e:
        print(f"⚠️ Error generando la animación 3D: {e}")
    fig3d_acc_anim = go.Figure(
        data=[
            go.Scatter3d(
                x=[df_vuelo["acelerometro_x"].iloc[0]],
                y=[df_vuelo["acelerometro_y"].iloc[0]],
                z=[df_vuelo["altitud_suave"].iloc[0]],
                mode="lines",
                line=dict(color="orange", width=6),
                name="Acelerómetro (XYZ)"
            ),
            marker_inicio
        ],
        layout=go.Layout(
            title="Animación 3D: Trayectoria del Acelerómetro",
            scene=dict(
                xaxis_title="Acelerómetro X",
                yaxis_title="Acelerómetro Y",
                zaxis_title="Altitud (m)",
                bgcolor="#222",
                xaxis=dict(showgrid=True, gridcolor="#444", zerolinecolor="#888", backgroundcolor="#222"),
                yaxis=dict(showgrid=True, gridcolor="#444", zerolinecolor="#888", backgroundcolor="#222"),
                zaxis=dict(showgrid=True, gridcolor="#444", zerolinecolor="#888", backgroundcolor="#222")
            ),
            updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="▶️ Play", method="animate", args=[None, {"frame": {"duration": 10, "redraw": True}, "fromcurrent": True}])]
            )],
            template="plotly_dark"
        ),
        frames=frames
    )
    fig3d_acc_anim.write_html("resultados/animacion_3d_acelerometro.html")
    mejorar_html_plotly("resultados/animacion_3d_acelerometro.html", "Animación 3D: Trayectoria del Acelerómetro")

# Sugerencias de mejora visual:
# - Añadir una barra de color para representar la magnitud de la aceleración en cada punto.
# - Cambiar el color de la línea según la magnitud de la aceleración.
# - Añadir una cuadrícula o fondo con gradiente para mayor contraste.
# - Mostrar el tiempo transcurrido en la animación como texto dinámico.

print("✅ Animación 3D suave y defendible generada: 3D fija, animación 3D y gráficas 2D en la carpeta 'resultados'. Solo la altitud es real, la inclinación es ilustrativa.")
