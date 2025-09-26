# 🌐 Traductor de Direcciones de Páginas Virtuales

## 📋 Descripción

Este programa implementa un **traductor de direcciones virtuales a direcciones físicas** basado en el concepto de **paginación de memoria** de los sistemas operativos. El programa simula la traducción de direcciones que ocurre en el hardware de un sistema con memoria virtual, utilizando una tabla de páginas configurable.

## 🎯 Características Principales

- ✅ **Traducción de direcciones virtuales a físicas** con soporte para múltiples formatos (hexadecimal, decimal, binario)
- ✅ **Configuración flexible** de parámetros del sistema de memoria
- ✅ **Soporte para diferentes formatos** de entrada y salida
- ✅ **Detección y manejo de fallos de página** (Page Faults)
- ✅ **Interfaz interactiva** para pruebas en tiempo real
- ✅ **Validación completa** de configuraciones y datos de entrada
- ✅ **Documentación detallada** de todos los cálculos realizados

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **`Traductor`** (`traductor.py`): Clase principal que maneja toda la lógica de traducción
2. **`index.py`**: Programa principal con interfaz interactiva
3. **`configuracion.txt`**: Archivo de configuración del sistema
4. **`tabla_paginas.txt`**: Tabla de páginas con mapeos virtual→físico

### Flujo de Traducción

```
Dirección Virtual → Extracción de Página → Consulta Tabla → Dirección Física
     ↓                      ↓                    ↓              ↓
   [bits]              [página + offset]    [marco físico]   [bits]
```

## 📁 Estructura de Archivos

```
Traductor_paginas/
├── index.py              # Programa principal
├── traductor.py          # Clase Traductor con lógica de paginación
├── configuracion.txt     # Parámetros del sistema
├── tabla_paginas.txt     # Tabla de páginas
└── README.md            # Este archivo
```

## ⚙️ Configuración del Sistema

### Archivo `configuracion.txt`

El archivo de configuración define los parámetros del sistema de memoria:

```ini
memoria_fisica = 32MiB
memoria_virtual = 64MiB
tamaño_pagina = 2KiB
marcos_fisicos = None
paginas_virtuales = None
```

#### Parámetros Soportados

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `memoria_fisica` | Tamaño total de memoria física | `32MiB`, `1024KiB` |
| `memoria_virtual` | Tamaño total de memoria virtual | `64MiB`, `2GiB` |
| `tamaño_pagina` | Tamaño de cada página/marco | `4KiB`, `2KiB` |
| `marcos_fisicos` | Número de marcos físicos | `16`, `32` |
| `paginas_virtuales` | Número de páginas virtuales | `32`, `64` |

#### Unidades de Medida Soportadas

- **b**: bits
- **B**: bytes
- **KiB**: Kibibytes (2¹⁰ bytes)
- **MiB**: Mebibytes (2²⁰ bytes)
- **GiB**: Gibibytes (2³⁰ bytes)

### Archivo `tabla_paginas.txt`

Define el mapeo entre páginas virtuales y marcos físicos:

```ini
formato numero de página = hex
formato entrada de página = hex

15 3399
38 1EC9
A7 1604
162 0424
1DF 3271
3D6 0432
3F0 1A08
```

#### Formatos Soportados

- **hex**: Hexadecimal (base 16)
- **dec**: Decimal (base 10)
- **bin**: Binario (base 2)

## 🚀 Instalación y Uso

### Requisitos

- Python 3.6 o superior
- No se requieren librerías externas adicionales

### Ejecución

1. **Clonar o descargar** los archivos del proyecto
2. **Configurar** los archivos `configuracion.txt` y `tabla_paginas.txt`
3. **Ejecutar** el programa:

```bash
python index.py
```

### Ejemplo de Uso

```bash
> 3F9A hex

--- ✅ Traducción Exitosa ---
  Dirección Virtual  : 0011111110011010 (DEC: 16282)
    - Página Virtual : 00111111 (DEC: 63)
    - Desplazamiento : 1110011010 (DEC: 922)
----------------------------------------
  Dirección Física   : 0111001110011010 (DEC: 29658) (HEX: 73DA)
    - Marco Físico   : 011100111 (DEC: 231)
    - Desplazamiento : 1110011010 (DEC: 922)
-----------------------------
```

## 🔧 API de la Clase Traductor

### Constructor

```python
Traductor(tam_pag, marcos_fisicos=None, pag_virtuales=None, memoria_fisica=None, memoria_virtual=None)
```

### Métodos Principales

#### `traduccion_direccion_decimal(direccion_virtual, tabla_paginas)`

Traduce una dirección virtual (entero) a dirección física.

**Parámetros:**
- `direccion_virtual` (int): Dirección virtual en decimal
- `tabla_paginas` (dict): Diccionario con mapeo de páginas

**Retorna:**
- `dict`: Resultado detallado de la traducción

#### `traduccion_direccion_hex(direccion_virtual_hex, tabla_paginas)`

Traduce una dirección virtual en formato hexadecimal.

**Parámetros:**
- `direccion_virtual_hex` (str): Dirección en hexadecimal
- `tabla_paginas` (dict): Diccionario con mapeo de páginas

### Métodos de Información

```python
# Obtener tamaños de direcciones
traductor.tamano_direccion_virtual()  # bits para dirección virtual
traductor.tamano_direccion_fisica()   # bits para dirección física

# Obtener bits por componente
traductor.bits_pagina_virtual()       # bits para número de página
traductor.bits_marco_fisico()         # bits para número de marco
traductor.bits_desplazamiento()       # bits para desplazamiento

# Conversores de formato
traductor.decimal_a_binario(numero)
traductor.hexa_a_binario(numero_hex)
traductor.decimal_a_hexa(numero)
```

## 📊 Formato de Resultado

El método de traducción retorna un diccionario con información completa:

```python
{
    "pagina_virtual_dec": 63,
    "desplazamiento_dec": 922,
    "marco_fisico_dec": 231,
    "direccion_fisica_dec": 29658,
    "pagina_virtual_bin": "00111111",
    "desplazamiento_bin": "1110011010",
    "marco_fisico_bin": "011100111",
    "direccion_virtual_bin": "0011111110011010",
    "direccion_fisica_bin": "0111001110011010",
    "flags": {"presente": 1}  # Flags adicionales de la tabla
}
```

## ⚠️ Manejo de Errores

### Excepciones Personalizadas

- **`PageFault`**: Se lanza cuando una página no está presente en memoria
- **`InvalidConfig`**: Se lanza por configuraciones inválidas

### Errores Comunes

1. **Fallo de Página**: La página virtual no está mapeada en la tabla
2. **Dirección fuera de rango**: La dirección excede el espacio virtual
3. **Configuración inválida**: Parámetros inconsistentes o no válidos
4. **Archivo no encontrado**: Faltan archivos de configuración

## 🧮 Ejemplos de Cálculos

### Ejemplo 1: Sistema con 4KiB por página

```
Configuración:
- Memoria física: 32 KiB
- Memoria virtual: 64 KiB  
- Tamaño de página: 4 KiB

Cálculos:
- Marcos físicos: 32 KiB ÷ 4 KiB = 8 marcos
- Páginas virtuales: 64 KiB ÷ 4 KiB = 16 páginas
- Bits desplazamiento: log₂(4 KiB) = 12 bits
- Bits página virtual: log₂(16) = 4 bits
- Bits marco físico: log₂(8) = 3 bits
```

### Ejemplo 2: Traducción de dirección

```
Dirección virtual: 0x3F9A (16282 decimal)

Descomposición:
- Página: 0x3F9A >> 12 = 0x03 = 3
- Offset: 0x3F9A & 0xFFF = 0x9A = 154

Traducción:
- Marco físico: 231 (de tabla de páginas)
- Dirección física: (231 << 12) | 154 = 946458
```

### Ejemplo 3: Ejemplos de Traducción con Datos Reales

| Dirección Virtual (hex) | Dirección Física (hex) | Dirección Física (dec) |
|-------------------------|------------------------|------------------------|
| 00A8D6                  | 19CC8D6                | 27,052,246             |
| 0B1007                  | 212007                 | 2,170,887              |
| 1EB055                  | 219055                 | 2,199,637              |
| 1F819D                  | D0419D                 | 13,648,285             |

Estos ejemplos muestran traducciones reales realizadas por el programa con diferentes direcciones virtuales y sus correspondientes direcciones físicas resultantes.

## 🔍 Casos de Uso

### 1. Simulación de Sistemas Operativos

- Estudiar algoritmos de paginación
- Entender el funcionamiento de la memoria virtual
- Analizar el rendimiento de diferentes configuraciones

### 2. Desarrollo de Software de Sistema

- Prototipado de gestores de memoria
- Pruebas de algoritmos de reemplazo de páginas
- Simulación de arquitecturas de hardware

### 3. Educación en Sistemas Operativos

- Visualización de conceptos de memoria virtual
- Ejercicios prácticos de traducción de direcciones
- Comprensión de fallos de página

## 🛠️ Extensibilidad

### Agregar Nuevos Formatos

Para soportar nuevos formatos de entrada, modifica las funciones de parsing en `index.py`.

### Implementar Nuevos Algoritmos

Extiende la clase `Traductor` para implementar:
- Algoritmos de reemplazo de páginas (LRU, FIFO, etc.)
- Simulación de TLB (Translation Lookaside Buffer)
- Gestión de memoria con segmentación

### Personalizar la Interfaz

Modifica `index.py` para:
- Agregar comandos adicionales
- Implementar modo batch para procesar archivos
- Crear interfaz gráfica con tkinter o similar

## 📚 Conceptos Teóricos

### Paginación

La paginación es una técnica de gestión de memoria que divide la memoria virtual y física en bloques de tamaño fijo llamados **páginas** (virtual) y **marcos** (físico).

### Tabla de Páginas

Una estructura de datos que mapea páginas virtuales a marcos físicos, incluyendo bits de control como:
- **Presente**: Indica si la página está en memoria
- **Modificado**: Indica si la página ha sido escrita
- **Referenciado**: Indica si la página ha sido accedida

### Fallo de Página

Ocurre cuando se intenta acceder a una página que no está presente en memoria física, requiriendo cargarla desde almacenamiento secundario.

## 🤝 Contribuciones

Este proyecto está diseñado para fines educativos. Las contribuciones son bienvenidas:

1. **Fork** del repositorio
2. **Crear** una rama para tu feature
3. **Commit** de tus cambios
4. **Push** a la rama
5. **Abrir** un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia educativa para uso académico y de investigación.

## 👨‍💻 Autor

Desarrollado como parte del curso de Sistemas Operativos 2.

---

*Para más información sobre sistemas de memoria virtual, consulta los libros de texto de sistemas operativos o la documentación de arquitecturas específicas.*
