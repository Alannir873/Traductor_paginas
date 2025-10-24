# main_lru.py - Simulador de Paginación con Algoritmo LRU
import sys
from collections import OrderedDict  # Para implementar LRU de manera sencilla
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
            if line.strip().startswith('#') or not line.strip():
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.lower() == 'none':
                    config_raw[key] = None
                else:
                    config_raw[key] = value
    
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

def parsear_tabla_paginas(filename="tabla_paginas.txt", bits_para_marco=0):
    """
    Lee la tabla de páginas, guardando la entrada raw para interpretar los bits de control.
    """
    tabla = {}
    formato_vpn = "hex"
    formato_entrada = "hex"
    
    print(f"🗺️  Leyendo tabla de páginas desde '{filename}'...")
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            
            if line.startswith('#') or not line:
                continue
            
            if line.startswith('formato numero de página ='):
                formato_vpn = line.split('=')[1].strip()
                continue
            elif line.startswith('formato entrada de página ='):
                formato_entrada = line.split('=')[1].strip()
                continue
            
            parts = line.split()
            if len(parts) == 2:
                vpn_str, entrada_str = parts
                try:
                    base_vpn = {'hex': 16, 'dec': 10, 'bin': 2}.get(formato_vpn, 16)
                    vpn = int(vpn_str, base_vpn)
                    
                    base_entrada = {'hex': 16, 'dec': 10, 'bin': 2}.get(formato_entrada, 16)
                    entrada_int = int(entrada_str, base_entrada)

                    mascara_marco = (1 << bits_para_marco) - 1
                    mascara_presente = 1 << bits_para_marco
                    
                    bit_presente = 1 if (entrada_int & mascara_presente) != 0 else 0
                    numero_marco = entrada_int & mascara_marco
                    
                    tabla[vpn] = {
                        "presente": bit_presente, 
                        "marco": numero_marco, 
                        "raw_entrada": entrada_int
                    }
                    
                except ValueError as e:
                    print(f"  [Advertencia] Ignorando línea mal formada en tabla de páginas: '{line}' - Error: {e}")

    print(f"  📋 Formatos detectados: página={formato_vpn}, entrada={formato_entrada}")
    print(f"  📊 Entradas cargadas: {len(tabla)} páginas")
    return tabla

def interpretar_bits_de_control(raw_entrada, bits_para_marco):
    """
    Analiza la entrada de la tabla de páginas y devuelve una explicación de los bits de control.
    """
    if raw_entrada is None:
        return "    No existe una entrada en la tabla para esta página."
        
    mascara_presente = 1 << bits_para_marco
    mascara_proteccion = 1 << (bits_para_marco + 1)
    mascara_modificado = 1 << (bits_para_marco + 2)
    mascara_referida = 1 << (bits_para_marco + 3)
    mascara_cache = 1 << (bits_para_marco + 4)
    
    presente = (raw_entrada & mascara_presente) != 0
    proteccion = (raw_entrada & mascara_proteccion) != 0
    modificado = (raw_entrada & mascara_modificado) != 0
    referida = (raw_entrada & mascara_referida) != 0
    cache = (raw_entrada & mascara_cache) != 0
    
    info = [
        f"    Entrada en Tabla (DEC): {raw_entrada} (BIN: {format(raw_entrada, 'b')})",
        "    ----------------------------------",
        f"    - Bit Presente/Ausente: {'1 (Presente)' if presente else '0 (Ausente)'}",
        f"    - Bit de Protección:    {'1 (Solo Lectura)' if proteccion else '0 (Lectura/Escritura)'}",
        f"    - Bit de Modificado:    {'1 (Sí)' if modificado else '0 (No)'}",
        f"    - Bit de Referido:      {'1 (Sí)' if referida else '0 (No)'}",
        f"    - Bit de Caché:         {'1 (Inhabilitado)' if cache else '0 (Habilitado)'}"
    ]
    return "\n".join(info)

def imprimir_resultado(resultado, bits_del_marco):
    """
    Formatea e imprime el diccionario de resultados, incluyendo la interpretación de bits.
    """
    print("\n--- ✅ Traducción Exitosa ---")
    print(f"  Dirección Virtual  : {resultado['direccion_virtual_bin']} (DEC: {int(resultado['direccion_virtual_bin'], 2)}) (HEX: {resultado['direccion_virtual_hex']})")
    print(f"    - Página Virtual : {resultado['pagina_virtual_bin']} (DEC: {resultado['pagina_virtual_dec']})")
    print(f"    - Desplazamiento : {resultado['desplazamiento_bin']} (DEC: {resultado['desplazamiento_dec']})")
    print("-" * 20)
    print(f"  Dirección Física   : {resultado['direccion_fisica_bin']} (DEC: {resultado['direccion_fisica_dec']}) (HEX: {format(resultado['direccion_fisica_dec'], 'X')})")
    print(f"    - Marco Físico   : {resultado['marco_fisico_bin']} (DEC: {resultado['marco_fisico_dec']})")
    print(f"    - Desplazamiento : {resultado['desplazamiento_bin']} (DEC: {resultado['desplazamiento_dec']})")
    print("-" * 20)
    print("  Análisis de la Entrada de Tabla de Páginas:")
    print(interpretar_bits_de_control(resultado['raw_entrada'], bits_del_marco))
    print("------------------------------------------\n")

# --- CLASE DE SIMULACIÓN CON ALGORITMO LRU ---
class SimuladorPaginacionLRU:
    """
    Gestiona el estado de la memoria física y la tabla de páginas usando el algoritmo LRU
    (Least Recently Used) para el reemplazo de páginas.
    
    ALGORITMO LRU EXPLICADO:
    ========================
    LRU (Least Recently Used) significa "Menos Recientemente Usado".
    
    ¿Cómo funciona?
    1. Mantenemos un registro del orden en que se accedieron las páginas
    2. Cuando necesitamos liberar un marco, sacamos la página que fue usada hace MÁS tiempo
    3. Cada vez que accedemos a una página, la movemos al final de la lista (más reciente)
    
    Ventajas del LRU:
    - Es más eficiente que FIFO porque considera el patrón de uso
    - Las páginas que se usan frecuentemente tienden a permanecer en memoria
    - Mejor rendimiento en la mayoría de casos reales
    
    Implementación:
    - Usamos OrderedDict de Python que mantiene el orden de inserción
    - Las claves son los números de página
    - Los valores son los números de marco
    - Al acceder a una página, la movemos al final con move_to_end()
    - Al reemplazar, sacamos la primera página (la menos reciente)
    """
    
    def __init__(self, config_params, tabla_paginas_inicial):
        print("--- 🏁 Iniciando Simulador de Paginación con LRU ---")
        print("📚 ALGORITMO LRU: Menos Recientemente Usado")
        print("   - Mantiene registro del orden de acceso a páginas")
        print("   - Reemplaza la página usada hace más tiempo")
        print("   - Mejor rendimiento que FIFO en casos reales")
        print("=" * 50)
        
        self.traductor = Traductor(**config_params)
        self.tabla_paginas = tabla_paginas_inicial
        
        self.bits_marco = self.traductor.bits_marco_fisico()
        self.num_marcos_totales = self.traductor.marcos_fisicos
        
        # Estructuras para gestionar la memoria física con LRU
        self.marcos_libres = list(range(self.num_marcos_totales))
        
        # OrderedDict para implementar LRU de manera sencilla
        # Clave: número de página, Valor: número de marco
        # El orden representa cuándo fue accedida cada página (primera = menos reciente)
        self.lru_cache = OrderedDict()
        
        # Inicializar el estado de la memoria basado en la tabla de páginas
        print("🔧 Inicializando memoria con páginas presentes...")
        for pagina, entrada in self.tabla_paginas.items():
            if entrada["presente"] == 1:
                marco = entrada["marco"]
                if marco in self.marcos_libres:
                    self.marcos_libres.remove(marco)
                    # Agregar a la cache LRU (las páginas iniciales se consideran "accedidas" al inicio)
                    self.lru_cache[pagina] = marco
                    print(f"   📄 Página {pagina} → Marco {marco} (cargada inicialmente)")
                else:
                    print(f"[Advertencia] El marco {marco} está asignado a múltiples páginas. Revisa tabla_paginas.txt")
        
        print(f"\n📊 Estado Inicial de la Memoria:")
        print(f"   - Marcos Totales: {self.num_marcos_totales}")
        print(f"   - Marcos Libres: {len(self.marcos_libres)} {self.marcos_libres}")
        print(f"   - Marcos Ocupados: {len(self.lru_cache)}")
        print(f"   - Orden LRU (menos reciente → más reciente): {list(self.lru_cache.keys())}")
        print("=" * 50)

    def _encontrar_marco_libre(self):
        """
        Obtiene un marco libre. Si no hay, aplica el algoritmo de reemplazo LRU.
        """
        if self.marcos_libres:
            # Hay marcos libres, usamos el primero
            marco_asignado = self.marcos_libres.pop(0)
            print(f"   [Memoria] ✅ Marco libre encontrado: {marco_asignado}")
            return marco_asignado
        else:
            # No hay marcos libres, se aplica el algoritmo de reemplazo LRU
            print("   [Memoria] ⚠️  ¡Memoria física llena! Aplicando algoritmo LRU...")
            return self._algoritmo_reemplazo_lru()

    def _algoritmo_reemplazo_lru(self):
        """
        ALGORITMO LRU EXPLICADO PASO A PASO:
        ====================================
        
        1. IDENTIFICAR LA PÁGINA A REEMPLAZAR:
           - En OrderedDict, el primer elemento es el menos recientemente usado
           - popitem(last=False) saca el primer elemento (FIFO del OrderedDict)
        
        2. LIBERAR EL MARCO:
           - Obtenemos el marco asociado a esa página
           - Actualizamos la tabla de páginas (bit presente = 0)
        
        3. MOSTRAR INFORMACIÓN:
           - Explicamos por qué se eligió esa página
           - Mostramos el estado antes y después del reemplazo
        """
        print("\n   🔄 EJECUTANDO ALGORITMO LRU:")
        print("   " + "="*40)
        
        # Paso 1: Identificar la página menos recientemente usada
        pagina_a_sacar, marco_liberado = self.lru_cache.popitem(last=False)
        
        print(f"   📋 Paso 1: Identificando página a reemplazar...")
        print(f"      - Página menos reciente: {pagina_a_sacar}")
        print(f"      - Marco a liberar: {marco_liberado}")
        print(f"      - Estado LRU antes: {list(self.lru_cache.keys())} + [{pagina_a_sacar}]")
        
        # Paso 2: Actualizar la tabla de páginas
        print(f"   📋 Paso 2: Actualizando tabla de páginas...")
        mascara_presente = 1 << self.bits_marco
        self.tabla_paginas[pagina_a_sacar]["presente"] = 0
        # Volteamos el bit de presente a 0, conservando los demás bits
        self.tabla_paginas[pagina_a_sacar]["raw_entrada"] &= ~mascara_presente
        
        print(f"      - Bit presente de página {pagina_a_sacar} → 0 (ausente)")
        print(f"      - Marco {marco_liberado} liberado y disponible")
        
        # Paso 3: Mostrar resultado
        print(f"   📋 Paso 3: Reemplazo completado")
        print(f"      - Página {pagina_a_sacar} removida de memoria")
        print(f"      - Marco {marco_liberado} disponible para nueva página")
        print(f"      - Estado LRU después: {list(self.lru_cache.keys())}")
        print("   " + "="*40)
        
        return marco_liberado

    def _actualizar_lru(self, pagina_virtual):
        """
        ACTUALIZACIÓN LRU EXPLICADA:
        ============================
        
        Cada vez que accedemos a una página (hit o miss), debemos actualizar
        su posición en la lista LRU para reflejar que fue "usada recientemente".
        
        En OrderedDict:
        - move_to_end() mueve la página al final (más reciente)
        - Si la página no existe, se agrega al final
        """
        if pagina_virtual in self.lru_cache:
            # La página ya está en memoria, la movemos al final (más reciente)
            self.lru_cache.move_to_end(pagina_virtual)
            print(f"   [LRU] 📄 Página {pagina_virtual} movida al final (más reciente)")
        else:
            # La página no está en memoria, se agregará cuando se cargue
            print(f"   [LRU] 📄 Página {pagina_virtual} será agregada cuando se cargue")

    def _manejar_fallo_de_pagina(self, pagina_virtual, entrada_actual):
        """
        Orquesta el proceso de cargar una página a memoria usando LRU.
        """
        print(f"--- ❌ Fallo de Página (Page Fault) en página {pagina_virtual} ---")
        print("   🚀 Iniciando carga de página a memoria física...")
        
        # 1. Encontrar un marco donde cargar la página
        marco_asignado = self._encontrar_marco_libre()
        
        # 2. Cargar la página y actualizar LRU
        self.lru_cache[pagina_virtual] = marco_asignado  # Se agrega al final (más reciente)
        
        # 3. Actualizar la tabla de páginas para la nueva página
        raw_entrada_actual = entrada_actual.get("raw_entrada", 0) if entrada_actual else 0
        
        # Creamos la nueva entrada de la tabla
        # Limpiamos los bits del marco anterior (si los había)
        mascara_marco = (1 << self.bits_marco) - 1
        raw_nueva = raw_entrada_actual & ~mascara_marco
        
        # Añadimos el nuevo marco
        raw_nueva |= marco_asignado
        
        # Ponemos el bit de presente en 1
        mascara_presente = 1 << self.bits_marco
        raw_nueva |= mascara_presente
        
        # Actualizamos la tabla de páginas en memoria
        self.tabla_paginas[pagina_virtual] = {
            "presente": 1,
            "marco": marco_asignado,
            "raw_entrada": raw_nueva
        }
        
        print(f"   [Memoria] ✅ Página {pagina_virtual} cargada exitosamente en el marco {marco_asignado}.")
        print(f"   [LRU] 📊 Nuevo orden LRU: {list(self.lru_cache.keys())}")
        print("------------------------------------------\n")

    def traducir_direccion(self, direccion_virtual_dec, direccion_str, formato):
        """
        Intenta traducir una dirección. Si falla, maneja el fallo y reintenta.
        Incluye actualización del LRU en cada acceso.
        """
        print(f"🎯 Intentando traducir: {direccion_str} ({formato}) [DEC: {direccion_virtual_dec}]")
        
        # Extraer número de página para actualizar LRU
        bits_o = self.traductor.bits_desplazamiento()
        pagina_virtual = direccion_virtual_dec >> bits_o
        
        try:
            # --- PRIMER INTENTO ---
            resultado = self.traductor.traduccion_direccion_decimal(
                direccion_virtual_dec, self.tabla_paginas
            )
            
            # ✅ HIT: La página está en memoria, actualizamos LRU
            print(f"   [LRU] ✅ HIT en página {pagina_virtual} - actualizando orden LRU")
            self._actualizar_lru(pagina_virtual)
            print(f"   [LRU] 📊 Orden LRU actualizado: {list(self.lru_cache.keys())}")
            
            # Imprimir resultado
            imprimir_resultado(resultado, self.bits_marco)
            
        except PageFault as e:
            # --- MISS: Fallo de página ---
            print(f"   [LRU] ❌ MISS en página {pagina_virtual} - página no está en memoria")
            
            # Imprimir el análisis de por qué falló
            print("\n  📋 Análisis de la Entrada de Tabla de Páginas (Causa del Fallo):")
            raw_entrada = e.entrada.get('raw_entrada') if e.entrada else None
            print(interpretar_bits_de_control(raw_entrada, self.bits_marco))
            
            # Manejar el fallo (cargar la página, reemplazar si es necesario)
            self._manejar_fallo_de_pagina(e.pagina_virtual, e.entrada)
            
            # --- SEGUNDO INTENTO (después de cargar la página) ---
            print("   🔄 Reintentando traducción...")
            try:
                resultado_exitoso = self.traductor.traduccion_direccion_decimal(
                    direccion_virtual_dec, self.tabla_paginas
                )
                
                # ✅ Ahora es un HIT, actualizamos LRU
                print(f"   [LRU] ✅ HIT después de cargar página {pagina_virtual}")
                self._actualizar_lru(pagina_virtual)
                print(f"   [LRU] 📊 Orden LRU final: {list(self.lru_cache.keys())}")
                
                imprimir_resultado(resultado_exitoso, self.bits_marco)
            except Exception as e_retry:
                print(f"  [Error Inesperado] Falló incluso después de manejar el Page Fault: {e_retry}")

        except ValueError as e:
            print(f"  [Error] El valor de la dirección no es válido o está fuera de rango: {e}")
        except Exception as e:
            print(f"  [Error inesperado] Ocurrió un problema: {e}")

def main():
    """
    Función principal que ejecuta el simulador con LRU leyendo un archivo de direcciones.
    """
    bits_del_marco = 0
    try:
        config_params = parsear_config()
        tabla_paginas_inicial = parsear_tabla_paginas("tabla_paginas.txt", bits_para_marco=Traductor(**config_params).bits_marco_fisico())

        # --- INICIALIZAR EL SIMULADOR CON LRU ---
        simulador = SimuladorPaginacionLRU(config_params, tabla_paginas_inicial)

    except FileNotFoundError as e:
        print(f"❌ ERROR FATAL: No se encontró el archivo '{e.filename}'. Asegúrate de que exista en la misma carpeta.")
        sys.exit(1)
    except (InvalidConfig, ValueError) as e:
        print(f"❌ ERROR FATAL en la configuración: {e}")
        sys.exit(1)

    # --- BUCLE DE PROCESAMIENTO POR LOTES ---
    archivo_direcciones = "direcciones_virtuales.txt"
    print(f"--- 📂 Procesando direcciones desde '{archivo_direcciones}' ---")
    try:
        with open(archivo_direcciones, 'r') as f:
            for i, linea in enumerate(f):
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue
                
                print(f"\n==================== PASO {i+1}: {linea} ====================")
                
                partes = linea.split()
                if len(partes) != 2:
                    print(f"  [Error] Formato incorrecto en línea: '{linea}'. Omitiendo.")
                    continue
                
                direccion_str, formato = partes
                formato = formato.lower()
                
                base_map = {'hex': 16, 'dec': 10, 'bin': 2}
                if formato not in base_map:
                    print(f"  [Error] Formato '{formato}' no reconocido. Omitiendo.")
                    continue
                
                try:
                    direccion_virtual_dec = int(direccion_str, base_map[formato])
                    simulador.traducir_direccion(direccion_virtual_dec, direccion_str, formato)
                except ValueError:
                     print(f"  [Error] Valor de dirección no válido: '{direccion_str}'. Omitiendo.")

    except FileNotFoundError:
        print(f"❌ ERROR FATAL: No se encontró el archivo de direcciones '{archivo_direcciones}'.")
        print("Por favor, crea este archivo con una dirección por línea (ej: '4000 dec' o 'FA0 hex').")
        sys.exit(1)
    except Exception as e:
        print(f"  [Error inesperado] Ocurrió un problema durante la simulación: {e}")

if __name__ == "__main__":
    main()
