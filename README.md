# 🛰️ Omega Space - CanSat 2025

¡Bienvenidos al repositorio oficial del proyecto **Omega Space CanSat 2025**! Este proyecto ha sido desarrollado por estudiantes de secundaria de la Región de Murcia (España) con el objetivo de diseñar y construir un mini satélite funcional con fines de rescate y reconocimiento.

## 🎯 Objetivo de la Misión

El CanSat está diseñado como una herramienta autónoma de reconocimiento en situaciones de emergencia. Su misión principal es mejorar la capacidad de localización y seguridad en entornos de difícil acceso.

### Funcionalidades principales

- 🔥 **Cámara térmica AMG8833** para detectar fuentes de calor en condiciones de baja visibilidad.
- 📡 **Sistema FPV** para visualización en tiempo real durante la misión.
- 🪂 **Paracaídas dirigible con control activo**, que permite un descenso estable y guiado.

## 🧠 Proyecto Científico

Buscamos demostrar cómo la tecnología aeroespacial puede ayudar en labores humanitarias. Nuestro CanSat incorpora tecnologías avanzadas para:

- Detección térmica en zonas de rescate.
- Orientación automática mediante acelerómetro y controladores de motor.
- Localización GPS en tiempo real.
- Transmisión de datos a la Estación de Tierra usando APC220.

## 🧩 Componentes Técnicos

| Componente        | Función |
|-------------------|--------|
| **Arduino Nano** | CPU principal del sistema |
| **Cámara térmica AMG8833** | Identificación de fuentes de calor |
| **Sensor BMP280** | Altitud, presión y temperatura ambiental |
| **MPU6050** | Detección de orientación e inclinación |
| **GPS BN-220** | Geolocalización precisa |
| **APC220** | Comunicación con la estación de tierra |
| **Cámara FPV** | Streaming de vídeo en vivo |
| **Motor DC + L298N Mini** | Control del paracaídas durante el descenso |

## ⚙️ Diseño y Fabricación

- Diseño estructural impreso en 3D, optimizado para cámaras y cuerdas del paracaídas.
- Paracaídas de tipo parapente (rectangular) para mayor estabilidad.
- Sistema de **estabilización activa** con motores que corrigen la inclinación detectada por el MPU6050.

## 🛰️ Estación de Tierra

Utilizamos **Serial Studio**, una herramienta multiplataforma para visualizar en tiempo real los datos enviados por el CanSat. La estación se compone de:

- Ordenador portátil con Serial Studio
- Arduino Nano conectado a un módulo APC220
- Antena Yagi para maximizar la recepción de señal

## 🗓️ Planificación

Nuestro trabajo se ha dividido en 3 fases principales:
1. **Diseño y planificación** (noviembre)
2. **Desarrollo del CanSat y estación de tierra** (diciembre-febrero)
3. **Pruebas y validación** (marzo)

Total: más de 50 horas de trabajo colaborativo documentado.

## 👥 Organización del equipo

El equipo está dividido en cuatro subgrupos:

- **Tierra**: interfaz de la estación y visualización de datos.
- **Aire**: programación y comunicaciones del satélite.
- **Diseño**: estructura y ensamblaje físico.
- **Comunicaciones**: documentación, difusión y gestión del repositorio.

<img src="CanSat-Code/images/imagen_equipo.jpg" width="400">


## 📢 Difusión y Patrocinio

Estamos comprometidos con la visibilidad del proyecto y la divulgación científica. Contamos con redes sociales activas y un programa de patrocinio basado en:

- Visibilidad de marca
- Apoyo a la educación STEM
- Acceso a talento joven

Síguenos en nuestras redes:
- Instagram: [@omegaspace.cansat](https://instagram.com/omegaspace.cansat)
- Twitter: [@SpaceOmega84376](https://twitter.com/SpaceOmega84376)

---

© 2025 - Omega Space Team  
Mentores: José Ángel Martínez  
Colaboradores: IES Alcántara · MMMacademy  
