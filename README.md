# Consola Retro - Proyecto de Sistemas Embebidos

Una consola de videojuegos retro implementada en Raspberry Pi con emulación mediante Mednafen.

## Características

- Menú gráfico para selección de juegos
- Emulación de NES, SNES y GameBoy Advance
- Detección automática de USB para agregar juegos
- Interfaz controlada completamente con gamepad
- Arranque automático al menú principal
- Pantalla de inicio personalizada

## Requisitos

- Raspberry Pi (modelos 3B+ o superior recomendados)
- Raspbian Lite o Full (instalación limpia)
- Gamepad USB compatible
- Almacenamiento: mínimo 8GB

## Instalación Automática

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/retro-consola.git

cd retro-consola

sudo bash scripts/install.sh

sudo reboot