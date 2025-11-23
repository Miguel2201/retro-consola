import os
import subprocess
import sys
import pygame
import threading
import shutil
import time
import pyudev
import subprocess as sp

# --- Configuracion ---
RUTA_ROMS = os.path.expanduser('~/roms')
EXTENSIONES_VALIDAS = ['.nes', '.sfc', '.smc', '.gba']
RUTA_MEDNAFEN = '/usr/games/mednafen' 

# Colores (R, G, B)
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_SELECCION = (255, 255, 0)
COLOR_USB = (0, 255, 0) # Verde para mensajes de USB

# Variables Globales para comunicación entre hilos
juegos_encontrados = []
mensaje_usb = ""
necesita_recargar = False

# --- Funciones del Sistema (Juegos) ---

def encontrar_juegos(ruta):
    """Busca en una carpeta todos los archivos con extensiones validas."""
    try:
        lista = [f for f in os.listdir(ruta) if any(f.lower().endswith(ext) for ext in EXTENSIONES_VALIDAS) and not f.startswith('._')]
        return sorted(lista)
    except FileNotFoundError:
        os.makedirs(ruta, exist_ok=True)
        return []

# --- Funciones de USB (Adaptadas de usbdetect.py) ---

def auto_mount(path):
    """Monta el dispositivo usando pmount (no pide password)."""
    # pmount monta en /media/nombre_dispositivo
    args = ["pmount", path]
    sp.run(args, stdout=sp.DEVNULL, stderr=sp.DEVNULL)

def get_mount_point(path):
    """Obtiene el punto de montaje del dispositivo."""
    time.sleep(1)
    args = ["findmnt", "-unl", "-S", path]
    cp = sp.run(args, capture_output=True, text=True)
    if cp.stdout:
        return cp.stdout.split(" ")[0]
    return None

def copiar_juegos_desde_usb(origen, destino):
    global mensaje_usb, necesita_recargar
    count = 0
    mensaje_usb = "USB Detectada. Buscando juegos..."
    
    if not os.path.exists(destino):
        os.makedirs(destino)

    # Recorrer la USB (incluyendo subcarpetas)
    for root, dirs, files in os.walk(origen):
        for file in files:
            if any(file.lower().endswith(ext) for ext in EXTENSIONES_VALIDAS):
                ruta_origen = os.path.join(root, file)
                ruta_destino = os.path.join(destino, file)
                
                # Copiar solo si no existe en destino
                if not os.path.exists(ruta_destino):
                    mensaje_usb = f"Copiando: {file}..."
                    try:
                        shutil.copy2(ruta_origen, ruta_destino)
                        count += 1
                    except Exception as e:
                        print(f"Error copiando {file}: {e}")

    if count > 0:
        mensaje_usb = f"¡Exito! Se copiaron {count} juegos nuevos."
        necesita_recargar = True # Avisar al hilo principal que actualice la lista
    else:
        mensaje_usb = "USB escaneada. No hay juegos nuevos."
    
    time.sleep(3) # Dejar el mensaje unos segundos
    mensaje_usb = "" # Borrar mensaje

def hilo_monitor_usb():
    """Función que corre en segundo plano monitoreando USBs."""
    context = pyudev.Context()
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block", device_type="partition")
    
    print("Sistema de detección USB iniciado en segundo plano...")

    # Bucle infinito de detección
    for action, device in monitor:
        if action == "add":
            dev_node = "/dev/" + device.sys_name
            print(f"Dispositivo detectado: {dev_node}")
            
            # Intentar montar
            auto_mount(dev_node)
            mount_point = get_mount_point(dev_node)
            
            if mount_point:
                print(f"Montado en: {mount_point}")
                copiar_juegos_desde_usb(mount_point, RUTA_ROMS)
            else:
                print("No se pudo obtener el punto de montaje.")

# --- Interfaz Grafica ---

def dibujar_menu(pantalla, fuente_titulo, fuente, juegos, seleccion_actual):
    """Dibuja la lista de juegos en la pantalla de Pygame."""
    pantalla.fill(COLOR_NEGRO) 

    # Dibuja el titulo
    texto_titulo = fuente_titulo.render('Selecciona un juego', True, COLOR_BLANCO)
    pantalla.blit(texto_titulo, (50, 50))

    # Dibuja estado USB (si existe)
    if mensaje_usb:
        texto_usb = fuente.render(mensaje_usb, True, COLOR_USB)
        pantalla.blit(texto_usb, (50, 100)) # Debajo del título

    # Dibuja ayuda
    texto_ayuda = fuente.render('A - Seleccionar | USB - Copia Auto', True, COLOR_BLANCO)
    # Ajustado para resolución dinámica, se dibuja cerca del fondo
    altura_pantalla = pantalla.get_height()
    pantalla.blit(texto_ayuda, (50, altura_pantalla - 60))

    # Dibuja lista de juegos (con scroll simple si son muchos)
    inicio_lista = 150
    max_items = (altura_pantalla - 200) // 40
    
    # Logica simple de scroll para mantener la selección visible
    inicio_indice = max(0, seleccion_actual - max_items + 1)
    fin_indice = min(len(juegos), inicio_indice + max_items)

    for i in range(inicio_indice, fin_indice):
        juego = juegos[i]
        color = COLOR_SELECCION if i == seleccion_actual else COLOR_BLANCO
        # Mostramos solo el nombre, quitamos la extensión para que se vea bonito
        nombre_limpio = os.path.splitext(juego)[0]
        texto_juego = fuente.render(f"{i + 1}. {nombre_limpio}", True, color)
        pos_y = inicio_lista + (i - inicio_indice) * 40
        pantalla.blit(texto_juego, (80, pos_y)) 

    pygame.display.flip() 

# --- Bucle Principal ---

def main():
    global juegos_encontrados, necesita_recargar

    # 1. Iniciar el hilo de detección de USB
    t_usb = threading.Thread(target=hilo_monitor_usb, daemon=True)
    t_usb.start()

    # 2. Carga inicial de juegos
    juegos_encontrados = encontrar_juegos(RUTA_ROMS)

    while True:
        pygame.init()
        pygame.joystick.init()

        # Configurar pantalla
        info_pantalla = pygame.display.Info()
        pantalla = pygame.display.set_mode((info_pantalla.current_w, info_pantalla.current_h), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        fuente_titulo = pygame.font.Font(None, 50)
        fuente = pygame.font.Font(None, 38) 

        if pygame.joystick.get_count() > 0:
            mando = pygame.joystick.Joystick(0)
            mando.init()

        seleccion_actual = 0
        corriendo = True

        while corriendo:
            # Verificar si el hilo USB pide recargar la lista
            if necesita_recargar:
                juegos_encontrados = encontrar_juegos(RUTA_ROMS)
                necesita_recargar = False
                # Reiniciar selección si la lista cambió
                seleccion_actual = 0 

            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                    pygame.quit()
                    sys.exit()

                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_UP:
                        seleccion_actual = (seleccion_actual - 1) % len(juegos_encontrados)
                    elif evento.key == pygame.K_DOWN:
                        seleccion_actual = (seleccion_actual + 1) % len(juegos_encontrados)
                    elif evento.key == pygame.K_RETURN:
                        if juegos_encontrados:
                            corriendo = False
                    elif evento.key == pygame.K_ESCAPE:
                        corriendo = False
                        pygame.quit()
                        sys.exit()

                if evento.type == pygame.JOYHATMOTION:
                    hat_x, hat_y = evento.value
                    if hat_y == 1: 
                        seleccion_actual = (seleccion_actual - 1) % len(juegos_encontrados)
                    elif hat_y == -1: 
                        seleccion_actual = (seleccion_actual + 1) % len(juegos_encontrados)
                
                # Soporte para Joystick Analogico (Ejes) - Común en Xbox
                if evento.type == pygame.JOYAXISMOTION:
                    if evento.axis == 1: # Eje Y vertical
                        if evento.value < -0.5: # Arriba
                             seleccion_actual = (seleccion_actual - 1) % len(juegos_encontrados)
                             # Pequeño delay para no scrollear ultra rápido
                             pygame.time.wait(150) 
                        elif evento.value > 0.5: # Abajo
                             seleccion_actual = (seleccion_actual + 1) % len(juegos_encontrados)
                             pygame.time.wait(150)

                if evento.type == pygame.JOYBUTTONDOWN:
                    if evento.button == 0: 
                        if juegos_encontrados:
                            corriendo = False

            # Dibujar interfaz
            dibujar_menu(pantalla, fuente_titulo, fuente, juegos_encontrados, seleccion_actual)

        # Lanzar juego
        if juegos_encontrados:
            juego_elegido = juegos_encontrados[seleccion_actual]
            ruta_completa_juego = os.path.join(RUTA_ROMS, juego_elegido)

            pygame.quit()
            os.system('clear')
            print(f"Lanzando: {juego_elegido}...")
            
            # Ejecutar mednafen
            subprocess.run([RUTA_MEDNAFEN, ruta_completa_juego])

if __name__ == "__main__":
    main()
