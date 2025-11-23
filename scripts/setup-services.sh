#!/bin/bash
# Configuración de servicios y arranque automático

# Crear servicio systemd para la consola retro
cat > /etc/systemd/system/retro-consola.service << 'EOF'
[Unit]
Description=Consola Retro Service
After=graphical.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/retro-consola
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
ExecStart=/usr/bin/python3 /home/pi/retro-consola/lanzador.py
Restart=always
RestartSec=5

[Install]
WantedBy=graphical.target
EOF

# Deshabilitar pantalla de bienvenida de Raspberry Pi
rm -f /etc/xdg/autostart/piwiz.desktop

# Configurar arranque automático sin login
systemctl enable lightdm
systemctl set-default graphical.target

# Habilitar servicio de la consola retro
systemctl daemon-reload
systemctl enable retro-consola.service

# Configurar resolución de pantalla
cat >> /boot/config.txt << 'EOF'

# Configuración para Consola Retro
hdmi_group=2
hdmi_mode=85
hdmi_drive=2
disable_overscan=1
EOF

echo "Servicios configurados correctamente"