# main.py
import sys
from traductor import Traductor, InvalidConfig, PageFault

def parsear_config(filename="configuracion.txt"):
    """
    Lee el archivo de configuración y lo convierte en un diccionario
    para pasarlo a la clase Traductor.
    """
    config_raw = {}
    print(f"📄 Leyendo configuración desde '{filename}'...")
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            # Ignorar comentarios y líneas vacías
            if line.strip().startswith('#') or not line.strip():
                continue
            
            # Separar clave y valor
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Convertir 'None' a un objeto None de Python
                if value.lower() == 'none':
                    config_raw[key] = None
                else:
                    config_raw[key] = value
    
    # Mapear los nombres del archivo de configuración a los parámetros del constructor
    config = {}
    mapeo = {
        'tamaño_pagina': 'tam_pag',
        'marcos_fisicos': 'marcos_fisicos',
        'paginas_virtuales': 'pag_virtuales',
        'memoria_fisica': 'memoria_fisica',
        'memoria_virtual': 'memoria_virtual'
    }
    
    for key, value in config_raw.items():
        if key in mapeo:
            config[mapeo[key]] = value
        else:
            config[key] = value
    
    return config

def parsear_tabla_paginas(filename="tabla_paginas.txt"):
    """
    Lee la tabla de páginas desde el archivo.
    Primero lee los formatos de configuración, luego los datos.
    """
    tabla = {}
    formato_vpn = "hex"  # Por defecto
    formato_entrada = "hex"  # Por defecto
    
    print(f"🗺️  Leyendo tabla de páginas desde '{filename}'...")
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            # Ignorar comentarios y líneas vacías
            if line.startswith('#') or not line:
                continue
            
            # Leer configuración de formatos
            if line.startswith('formato numero de página ='):
                formato_vpn = line.split('=')[1].strip()
                continue
            elif line.startswith('formato entrada de página ='):
                formato_entrada = line.split('=')[1].strip()
                continue
            
            # Leer datos de la tabla
            parts = line.split()
            if len(parts) == 2:
                vpn_str, marco_str = parts
                try:
                    # Convertir según el formato especificado
                    if formato_vpn == "hex":
                        vpn = int(vpn_str, 16)
                    elif formato_vpn == "dec":
                        vpn = int(vpn_str, 10)
                    elif formato_vpn == "bin":
                        vpn = int(vpn_str, 2)
                    else:
                        print(f"  [Advertencia] Formato de página no reconocido: {formato_vpn}")
                        continue
                    
                    if formato_entrada == "hex":
                        marco = int(marco_str, 16)
                    elif formato_entrada == "dec":
                        marco = int(marco_str, 10)
                    elif formato_entrada == "bin":
                        marco = int(marco_str, 2)
                    else:
                        print(f"  [Advertencia] Formato de entrada no reconocido: {formato_entrada}")
                        continue
                    
                    # Asumimos que si una página está en el archivo, está presente en memoria
                    tabla[vpn] = {"presente": 1, "marco": marco}
                    
                except ValueError as e:
                    print(f"  [Advertencia] Ignorando línea mal formada en tabla de páginas: '{line}' - Error: {e}")
    
    print(f"  📋 Formatos detectados: página={formato_vpn}, entrada={formato_entrada}")
    print(f"  📊 Entradas cargadas: {len(tabla)} páginas")
    return tabla

def imprimir_resultado(resultado):
    """Formatea e imprime el diccionario de resultados de la traducción."""
    print("\n--- ✅ Traducción Exitosa ---")
    print(f"  Dirección Virtual  : {resultado['direccion_virtual_bin']} (DEC: {int(resultado['direccion_virtual_bin'], 2)})")
    print(f"    - Página Virtual : {resultado['pagina_virtual_bin']} (DEC: {resultado['pagina_virtual_dec']})")
    print(f"    - Desplazamiento : {resultado['desplazamiento_bin']} (DEC: {resultado['desplazamiento_dec']})")
    print("-" * 20)
    print(f"  Dirección Física   : {resultado['direccion_fisica_bin']} (DEC: {resultado['direccion_fisica_dec']}) (HEX: {format(resultado['direccion_fisica_dec'], 'X')})")
    print(f"    - Marco Físico   : {resultado['marco_fisico_bin']} (DEC: {resultado['marco_fisico_dec']})")
    print(f"    - Desplazamiento : {resultado['desplazamiento_bin']} (DEC: {resultado['desplazamiento_dec']})")
    print("-----------------------------\n")

def main():
    """Función principal que ejecuta el programa."""
    try:
        # Cargar configuración y tabla de páginas
        config_params = parsear_config()
        tabla_paginas = parsear_tabla_paginas()
        
        # Crear la instancia del traductor
        traductor = Traductor(**config_params)
        print("\n✅ ¡Traductor inicializado correctamente!")
        print(f"   - Arquitectura: {traductor.tamano_direccion_virtual()} bits virtuales -> {traductor.tamano_direccion_fisica()} bits físicos.")
        print(f"   - {traductor.pag_virtuales} páginas virtuales, {traductor.marcos_fisicos} marcos físicos.\n")

    except FileNotFoundError as e:
        print(f"❌ ERROR FATAL: No se encontró el archivo '{e.filename}'. Asegúrate de que exista en la misma carpeta.")
        sys.exit(1)
    except (InvalidConfig, ValueError) as e:
        print(f"❌ ERROR FATAL en la configuración: {e}")
        sys.exit(1)

    # Bucle interactivo para el usuario
    print("--- Ingrese la dirección virtual y su formato (ej: '3F9A hex', '1024 dec') ---")
    print("--- Escriba 'salir' o 'exit' para terminar. ---")
    
    while True:
        try:
            entrada = input("\n> ").strip()
            if entrada.lower() in ['salir', 'exit']:
                print("👋 ¡Hasta luego!")
                break

            partes = entrada.split()
            if len(partes) != 2:
                print("  [Error] Formato incorrecto. Debes ingresar la dirección y el formato (hex, dec, bin).")
                continue
            
            direccion_str, formato = partes
            formato = formato.lower()
            
            # Convertir la dirección de entrada a un entero
            base_map = {'hex': 16, 'dec': 10, 'bin': 2}
            if formato not in base_map:
                print(f"  [Error] Formato '{formato}' no reconocido. Usa 'hex', 'dec' o 'bin'.")
                continue
            
            direccion_virtual_dec = int(direccion_str, base_map[formato])
            
            # Realizar la traducción
            resultado = traductor.traduccion_direccion_decimal(direccion_virtual_dec, tabla_paginas)
            
            # Imprimir el resultado
            imprimir_resultado(resultado)

        except PageFault as e:
            print(f"\n--- ❌ Fallo de Página (Page Fault) ---")
            print(f"  La página virtual {e.pagina_virtual} no está cargada en un marco de memoria física.")
            print("--------------------------------------\n")
        except ValueError as e:
            print(f"  [Error] El valor de la dirección no es válido o está fuera de rango: {e}")
        except Exception as e:
            print(f"  [Error inesperado] Ocurrió un problema: {e}")


if __name__ == "__main__":
    main()