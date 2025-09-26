import math

class PageFault(Exception):
    def __init__(self, pagina_virtual):
        super().__init__(f"Fallo de página en la página virtual {pagina_virtual}")
        self.pagina_virtual = pagina_virtual

class InvalidConfig(Exception):
    pass

class Traductor:
    def __init__(self, tam_pag, marcos_fisicos=None, pag_virtuales=None, memoria_fisica=None, memoria_virtual=None):
        # Procesar el tamaño de página primero (siempre necesario)
        if isinstance(tam_pag, str):
            self.tam_pag = self._parsear_tamaño_a_bytes(tam_pag)
        else:
            self.tam_pag = int(tam_pag)
        
        # Determinar configuración basada en los parámetros proporcionados
        if marcos_fisicos is not None and pag_virtuales is not None:
            # Opción A: Se dan marcos y páginas directamente
            self.marcos_fisicos = int(marcos_fisicos)
            self.pag_virtuales = int(pag_virtuales)
            self.memoria_fisica = self.marcos_fisicos * self.tam_pag
            self.memoria_virtual = self.pag_virtuales * self.tam_pag
            
        elif memoria_fisica is not None and memoria_virtual is not None:
            # Opción B: Se dan tamaños de memoria total
            self.memoria_fisica = self._parsear_tamaño_a_bytes(memoria_fisica)
            self.memoria_virtual = self._parsear_tamaño_a_bytes(memoria_virtual)
            
            if self.memoria_fisica % self.tam_pag != 0 or self.memoria_virtual % self.tam_pag != 0:
                raise InvalidConfig("Los tamaños de memoria deben ser múltiplos del tamaño de página.")
            
            self.marcos_fisicos = self.memoria_fisica // self.tam_pag
            self.pag_virtuales = self.memoria_virtual // self.tam_pag
        else:
            raise InvalidConfig("Debe proporcionar 'marcos_fisicos' y 'pag_virtuales', O 'memoria_fisica' y 'memoria_virtual'.")

        # Validaciones básicas
        for nombre, valor in [
            ("tam_pag", self.tam_pag),
            ("marcos_fisicos", self.marcos_fisicos),
            ("pag_virtuales", self.pag_virtuales),
        ]:
            if valor <= 0:
                raise InvalidConfig(f"{nombre} debe ser > 0")
            if not self._es_potencia_de_dos(valor):
                raise InvalidConfig(f"{nombre} debe ser potencia de 2 (recibido {valor})")

    def _parsear_tamaño_a_bytes(self, tamaño):
        """Convierte un string de tamaño (ej: '1 MiB') a bytes."""
        if isinstance(tamaño, int):
            return tamaño
        
        tamaño = str(tamaño).strip().lower()
        unidades = {'b': 1, 'bytes': 1, 'kib': 2**10, 'mib': 2**20, 'gib': 2**30}
        
        import re
        match = re.match(r'^(\d+\.?\d*)\s*([a-z]+)$', tamaño)
        if not match:
            raise ValueError(f"Formato de tamaño no reconocido: '{tamaño}'")
        
        valor, unidad = match.groups()
        if unidad not in unidades:
            raise ValueError(f"Unidad desconocida: '{unidad}'")
        
        return int(float(valor) * unidades[unidad])

    @staticmethod
    def _es_potencia_de_dos(x):
        return (x & (x - 1)) == 0

    # ---------- Conversores simples ----------
    def decimal_a_binario(self, numero):
        return format(numero if numero >= 0 else (1 * numero), 'b') if numero >= 0 else "-" + format(-numero, 'b')

    def hexa_a_binario(self, numero_hex):
        return format(int(numero_hex, 16), 'b')

    def decimal_a_hexa(self, numero):
        return (format(numero, 'x') if numero >= 0 else "-" + format(-numero, 'x')).upper()

    # ---------- Cálculos de bits ----------
    def bits_desplazamiento(self):
        return int(math.log2(self.tam_pag))

    def bits_marco_fisico(self):
        return int(math.log2(self.marcos_fisicos))

    def bits_pagina_virtual(self):
        return int(math.log2(self.pag_virtuales))

    def tamano_direccion_fisica(self):
        return self.bits_marco_fisico() + self.bits_desplazamiento()

    def tamano_direccion_virtual(self):
        return self.bits_pagina_virtual() + self.bits_desplazamiento()

    # ---------- Utilidades internas ----------
    def _fmtb(self, valor, bits):
        """Formato binario con padding a 'bits'."""
        return format(valor, f'0{bits}b')

    # ---------- Traducciones ----------
    def traduccion_direccion_decimal(self, direccion_virtual, tabla_paginas):
        """
        Traduce una dirección virtual (int) a dirección física usando 'tabla_paginas'.

        tabla_paginas: dict[int_pagina] -> dict con al menos:
            {
              "presente": 0|1 (o bool),
              "marco": int (0..marcos_fisicos-1),
              # Opcionalmente: "R","M","prot","cache_off", etc.
            }
        """
        bits_v = self.bits_pagina_virtual()
        bits_o = self.bits_desplazamiento()
        total_bits_virt = bits_v + bits_o

        # Rango válido de direcciones virtuales
        max_dv = (1 << total_bits_virt) - 1
        if not (0 <= direccion_virtual <= max_dv):
            raise ValueError(
                f"Dirección virtual fuera de rango: {direccion_virtual} (máx {max_dv})"
            )

        # Extraer página y offset con máscaras (más robusto que slicing de strings)
        pagina = direccion_virtual >> bits_o
        desplazamiento = direccion_virtual & ((1 << bits_o) - 1)

        # Consultar tabla de páginas
        entrada = tabla_paginas.get(pagina)
        if not entrada or int(entrada.get("presente", 0)) == 0:
            # No presente -> fallo de página
            raise PageFault(pagina)

        marco = int(entrada["marco"])
        # Validar que el marco sea válido
        if not (0 <= marco < self.marcos_fisicos):
            raise InvalidConfig(f"Marco inválido en tabla: {marco}")

        # Construir dirección física
        direccion_fisica = (marco << bits_o) | desplazamiento

        # Armar un resultado explicativo
        resultado = {
            "pagina_virtual_dec": pagina,
            "desplazamiento_dec": desplazamiento,
            "marco_fisico_dec": marco,
            "direccion_fisica_dec": direccion_fisica,
            "pagina_virtual_bin": self._fmtb(pagina, bits_v),
            "desplazamiento_bin": self._fmtb(desplazamiento, bits_o),
            "marco_fisico_bin": self._fmtb(marco, self.bits_marco_fisico()),
            "direccion_virtual_bin": self._fmtb(direccion_virtual, total_bits_virt),
            "direccion_fisica_bin": self._fmtb(direccion_fisica, self.tamano_direccion_fisica()),
            # Pasar también flags si vienen:
            "flags": {k: entrada[k] for k in entrada.keys() - {"marco"}}
        }
        return resultado

    def traduccion_direccion_hex(self, direccion_virtual_hex, tabla_paginas):
        """Atajo para traducir recibiendo una dirección virtual en hexadecimal (string)."""
        dv = int(direccion_virtual_hex, 16)
        return self.traduccion_direccion_decimal(dv, tabla_paginas)


