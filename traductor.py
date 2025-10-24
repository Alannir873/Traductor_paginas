import math

class PageFault(Exception):
    # Modificamos la excepción para que también pueda llevar la entrada de la tabla
    def __init__(self, pagina_virtual, entrada=None):
        super().__init__(f"Fallo de página en la página virtual {pagina_virtual}")
        self.pagina_virtual = pagina_virtual
        self.entrada = entrada

class InvalidConfig(Exception):
    pass

class Traductor:
    def __init__(self, tam_pag, marcos_fisicos=None, pag_virtuales=None, memoria_fisica=None, memoria_virtual=None):
        if isinstance(tam_pag, str):
            self.tam_pag = self._parsear_tamaño_a_bytes(tam_pag)
        else:
            self.tam_pag = int(tam_pag)
        
        if marcos_fisicos is not None and pag_virtuales is not None:
            self.marcos_fisicos = int(marcos_fisicos)
            self.pag_virtuales = int(pag_virtuales)
            self.memoria_fisica = self.marcos_fisicos * self.tam_pag
            self.memoria_virtual = self.pag_virtuales * self.tam_pag
            
        elif memoria_fisica is not None and memoria_virtual is not None:
            self.memoria_fisica = self._parsear_tamaño_a_bytes(memoria_fisica)
            self.memoria_virtual = self._parsear_tamaño_a_bytes(memoria_virtual)
            
            if self.memoria_fisica % self.tam_pag != 0 or self.memoria_virtual % self.tam_pag != 0:
                raise InvalidConfig("Los tamaños de memoria deben ser múltiplos del tamaño de página.")
            
            self.marcos_fisicos = self.memoria_fisica // self.tam_pag
            self.pag_virtuales = self.memoria_virtual // self.tam_pag
        else:
            raise InvalidConfig("Debe proporcionar 'marcos_fisicos' y 'pag_virtuales', O 'memoria_fisica' y 'memoria_virtual'.")

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

    def decimal_a_binario(self, numero):
        return format(numero if numero >= 0 else (1 * numero), 'b') if numero >= 0 else "-" + format(-numero, 'b')

    def hexa_a_binario(self, numero_hex):
        return format(int(numero_hex, 16), 'b')

    def decimal_a_hexa(self, numero):
        return (format(numero, 'x') if numero >= 0 else "-" + format(-numero, 'x')).upper()

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

    def _fmtb(self, valor, bits):
        return format(valor, f'0{bits}b')

    def traduccion_direccion_decimal(self, direccion_virtual, tabla_paginas):
        bits_v = self.bits_pagina_virtual()
        bits_o = self.bits_desplazamiento()
        total_bits_virt = bits_v + bits_o

        max_dv = (1 << total_bits_virt) - 1
        if not (0 <= direccion_virtual <= max_dv):
            raise ValueError(
                f"Dirección virtual fuera de rango: {direccion_virtual} (máx {max_dv})"
            )

        pagina = direccion_virtual >> bits_o
        desplazamiento = direccion_virtual & ((1 << bits_o) - 1)

        entrada = tabla_paginas.get(pagina)
        if not entrada or int(entrada.get("presente", 0)) == 0:
            # Ahora pasamos la 'entrada' completa a la excepción
            raise PageFault(pagina, entrada=entrada)

        marco = int(entrada["marco"])
        if not (0 <= marco < self.marcos_fisicos):
            raise InvalidConfig(f"Marco inválido en tabla: {marco}")

        direccion_fisica = (marco << bits_o) | desplazamiento

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
            # Añadimos la dirección virtual en hexadecimal al resultado
            "direccion_virtual_hex": self.decimal_a_hexa(direccion_virtual),
            # Pasamos la entrada raw para su posterior interpretación
            "raw_entrada": entrada.get("raw_entrada", 0)
        }
        return resultado

    def traduccion_direccion_hex(self, direccion_virtual_hex, tabla_paginas):
        dv = int(direccion_virtual_hex, 16)
        return self.traduccion_direccion_decimal(dv, tabla_paginas)