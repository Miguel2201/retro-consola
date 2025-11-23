#!/bin/bash

# ====================================================
# INSTALADOR FINAL CONSOLA RETRO (Usuario: pi)
# ====================================================

set -e # Detener si hay error

echo "🎮 Iniciando instalación..."

# 1. INSTALAR DEPENDENCIAS
echo "[+] Instalando sistema base..."
sudo apt-get update
# Agregamos 'wget' para descargar juegos y 'pmount' para tu script de python
sudo apt-get install -y python3-pygame mednafen fbi mpg123 joystick pmount git wget

# 2. PREPARAR CARPETAS
echo "[+] Creando directorios en /home/pi..."
mkdir -p /home/pi/roms
mkdir -p /home/pi/splash
mkdir -p /home/pi/.mednafen

# 3. DESCARGAR JUEGOS DE EJEMPLO (HOMEBREW/LEGALES)
# Esto asegura que la consola tenga algo que jugar al terminar
echo "[+] Descargando juegos Homebrew de ejemplo..."
cd /home/pi/roms
cp -r roms/* /home/pi/roms/

# Volver a la raíz del instalador
cd -

# 4. COPIAR ARCHIVOS DEL PROYECTO
echo "[+] Instalando archivos del sistema..."

# Copiar lanzador
cp lanzador.py /home/pi/
chmod +x /home/pi/lanzador.py

# Copiar assets
cp assets/logo.png /home/pi/splash/
cp assets/sonido.mp3 /home/pi/splash/

# Copiar configuración de Mednafen
if [ -f "config/mednafen.cfg" ]; then
    cp config/mednafen.cfg /home/pi/.mednafen/
    echo "[OK] Configuración de Mednafen cargada."
else
    echo "[!] ADVERTENCIA: No se encontró mednafen.cfg, se usará el default."
fi

# 5. CONFIGURAR SERVICIOS DE ARRANQUE
echo "[+] Configurando arranque automático..."
sudo cp services/splash-screen.service /etc/systemd/system/
sudo cp services/lanzador.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable splash-screen.service
sudo systemctl enable lanzador.service

# 6. AJUSTES DE PANTALLA (Centrado y Resolución)
echo "[+] Forzando resolución 1080p y corrigiendo bordes..."
CONFIG="/boot/config.txt"
# Desactiva overscan y fuerza HDMI
grep -qxF 'disable_overscan=1' $CONFIG || echo 'disable_overscan=1' | sudo tee -a $CONFIG
grep -qxF 'hdmi_group=2' $CONFIG || echo 'hdmi_group=2' | sudo tee -a $CONFIG
grep -qxF 'hdmi_mode=82' $CONFIG || echo 'hdmi_mode=82' | sudo tee -a $CONFIG
# Fuerza salida de audio por HDMI
grep -qxF 'dtparam=audio=on' $CONFIG || echo 'dtparam=audio=on' | sudo tee -a $CONFIG

# 7. PERMISOS FINALES
echo "[+] Ajustando permisos de usuario..."
chown -R pi:pi /home/pi/roms
chown -R pi:pi /home/pi/splash
chown -R pi:pi /home/pi/.mednafen
chown pi:pi /home/pi/lanzador.py

echo "============================================="
echo "✅ INSTALACIÓN COMPLETADA"
echo "   - Juegos de prueba descargados."
echo "   - Detección USB configurada en el lanzador."
echo "============================================="
echo "Reiniciando en 5 segundos..."
sleep 5
sudo reboot