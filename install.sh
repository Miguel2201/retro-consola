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
mkdir -p /home/pi/.mednafen


# 3. COPIAR ARCHIVOS DEL PROYECTO
echo "[+] Instalando archivos del sistema..."

chmod +x /home/pi/retro-consola/lanzador.py

# Copiar configuración de Mednafen
if [ -f "config/mednafen.cfg" ]; then
    cp /home/pi/retro-consola/config/mednafen.cfg /home/pi/.mednafen/
    echo "[OK] Configuración de Mednafen cargada."
else
    echo "[!] ADVERTENCIA: No se encontró mednafen.cfg, se usará el default."
fi

# 5. CONFIGURAR SERVICIOS DE ARRANQUE
echo "[+] Configurando arranque automático..."
sudo cp /home/pi/retro-consola/services/splash-screen.service /etc/systemd/system/
sudo cp /home/pi/retro-consola/services/lanzador.service /etc/systemd/system/

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
chown -R pi:pi /home/pi/retro-consola/roms
chown -R pi:pi /home/pi/retro-consola/assets
chown -R pi:pi /home/pi/.mednafen
chown pi:pi /home/pi/retro-consola/lanzador.py

echo "============================================="
echo "✅ INSTALACIÓN COMPLETADA"
echo "   - Juegos de prueba descargados."
echo "   - Detección USB configurada en el lanzador."
echo "============================================="
echo "Reiniciando en 5 segundos..."
sleep 5
sudo reboot