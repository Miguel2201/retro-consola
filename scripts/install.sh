#!/bin/bash
# Script de instalación automática para Consola Retro
# Debe ejecutarse en una instalación limpia de Raspbian

set -e  # Detener ejecución en caso de error

echo "=========================================="
echo "    INSTALADOR DE CONSOLA RETRO"
echo "=========================================="

# Verificar que se ejecute como root
if [ "$EUID" -ne 0 ]; then
    echo "Por favor, ejecuta este script como root o con sudo"
    exit 1
fi

# Actualizar sistema
echo "→ Actualizando sistema..."
apt update
apt upgrade -y

# Instalar dependencias del sistema
echo "→ Instalando dependencias del sistema..."
apt install -y \
    python3 \
    python3-pip \
    python3-pygame \
    python3-pyudev \
    mednafen \
    pmount \
    git \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0

# Instalar dependencias de Python
echo "→ Instalando dependencias de Python..."
pip3 install pygame pyudev

# Crear estructura de directorios
echo "→ Creando estructura de directorios..."
mkdir -p /home/pi/retro-consola
mkdir -p /home/pi/roms
mkdir -p /home/pi/assets
mkdir -p /home/pi/.mednafen

# Copiar archivos del proyecto
echo "→ Copiando archivos del proyecto..."
cp -r src/* /home/pi/retro-consola/
cp -r assets/* /home/pi/assets/
cp -r config/* /home/pi/.mednafen/
cp -r roms/* /home/pi/roms/

# Configurar permisos
echo "→ Configurando permisos..."
chown -R pi:pi /home/pi/retro-consola
chown -R pi:pi /home/pi/roms
chown -R pi:pi /home/pi/assets
chmod +x /home/pi/retro-consola/lanzador.py
chmod +x /home/pi/assets/splash-screen.py

# Configurar servicios del sistema
echo "→ Configurando servicios del sistema..."
bash scripts/setup-services.sh

# Configurar Mednafen
echo "→ Configurando Mednafen..."
cat > /home/pi/.mednafen/mednafen.cfg << 'EOF'
# Configuración básica de Mednafen para consola retro
video.fs 1
video.fs.display 0
video.driver opengl
sound.device default
sound.rate 44100
sound.volume 100
nes.xres 640
nes.yres 480
snes.xres 640
snes.yres 480
gba.xres 640
gba.yres 480
EOF

echo "=========================================="
echo "    INSTALACIÓN COMPLETADA"
echo "=========================================="
echo "La consola retro está lista para usar."
echo "Reinicia el sistema para que los cambios surtan efecto."
echo ""
echo "Comandos útiles:"
echo "  sudo systemctl start retro-consola"
echo "  sudo systemctl stop retro-consola"
echo "  sudo systemctl enable retro-consola"
echo "=========================================="