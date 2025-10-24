# Simulador de Paginación - Algoritmos FIFO vs LRU

Este proyecto incluye dos implementaciones de simuladores de paginación con diferentes algoritmos de reemplazo de páginas:

## 📁 Archivos del Proyecto

- **`index.py`** - Simulador con algoritmo **FIFO** (First In, First Out)
- **`index_lru.py`** - Simulador con algoritmo **LRU** (Least Recently Used)
- **`traductor.py`** - Clase base para traducción de direcciones
- **`configuracion.txt`** - Configuración del sistema
- **`tabla_paginas.txt`** - Tabla de páginas inicial
- **`direcciones_virtuales.txt`** - Lista de direcciones a traducir

## 🔄 Algoritmos de Reemplazo

### FIFO (First In, First Out)
**Archivo:** `index.py`

**¿Cómo funciona?**
- Mantiene una cola (queue) de páginas en memoria
- Cuando se necesita liberar un marco, saca la página que entró **primero**
- Es como una cola de supermercado: el primero en llegar es el primero en salir

**Ventajas:**
- ✅ Implementación muy simple
- ✅ Bajo overhead computacional
- ✅ Fácil de entender

**Desventajas:**
- ❌ No considera el patrón de uso de las páginas
- ❌ Puede sacar páginas que se usan frecuentemente
- ❌ Menor eficiencia en casos reales

**Estructura de datos:**
```python
from collections import deque
cola_fifo = deque()  # Cola simple
```

### LRU (Least Recently Used)
**Archivo:** `index_lru.py`

**¿Cómo funciona?**
- Mantiene un registro del **orden de acceso** a las páginas
- Cuando se necesita liberar un marco, saca la página que fue usada hace **más tiempo**
- Cada vez que se accede a una página, se actualiza su posición (se vuelve "más reciente")

**Ventajas:**
- ✅ Considera el patrón de uso real
- ✅ Mejor rendimiento en la mayoría de casos
- ✅ Las páginas frecuentemente usadas tienden a permanecer en memoria
- ✅ Más eficiente que FIFO

**Desventajas:**
- ❌ Implementación más compleja
- ❌ Mayor overhead computacional
- ❌ Requiere más memoria para mantener el orden

**Estructura de datos:**
```python
from collections import OrderedDict
lru_cache = OrderedDict()  # Mantiene orden de acceso
```

## 🚀 Cómo Ejecutar

### Ejecutar con FIFO:
```bash
python index.py
```

### Ejecutar con LRU:
```bash
python index_lru.py
```

## 📊 Comparación Visual

### FIFO - Ejemplo de Funcionamiento:
```
Memoria: [Página A] [Página B] [Página C]
Cola:    A → B → C (A entró primero)

Nuevo acceso a Página D (memoria llena):
1. Sacar Página A (primera en la cola)
2. Cargar Página D
3. Nueva cola: B → C → D
```

### LRU - Ejemplo de Funcionamiento:
```
Memoria: [Página A] [Página B] [Página C]
Orden LRU: A → B → C (A menos reciente, C más reciente)

Acceso a Página B (HIT):
1. Mover B al final (más reciente)
2. Nuevo orden: A → C → B

Nuevo acceso a Página D (memoria llena):
1. Sacar Página A (menos recientemente usada)
2. Cargar Página D al final
3. Nuevo orden: C → B → D
```

## 🔍 Salida del Programa

### FIFO muestra:
```
[FIFO] Sacando página X del marco Y.
```

### LRU muestra:
```
🔄 EJECUTANDO ALGORITMO LRU:
📋 Paso 1: Identificando página a reemplazar...
   - Página menos reciente: X
   - Marco a liberar: Y
📋 Paso 2: Actualizando tabla de páginas...
📋 Paso 3: Reemplazo completado
```

## 🎯 Cuándo Usar Cada Algoritmo

### Usa FIFO cuando:
- Necesitas simplicidad máxima
- El overhead computacional es crítico
- Las páginas tienen patrones de acceso impredecibles
- Es un sistema embebido con recursos limitados

### Usa LRU cuando:
- Quieres mejor rendimiento general
- Las páginas tienen patrones de acceso predecibles
- Tienes recursos computacionales suficientes
- Es un sistema de propósito general

## 📈 Rendimiento Esperado

En la mayoría de casos reales, **LRU supera a FIFO** porque:
- Las páginas accedidas recientemente tienen mayor probabilidad de ser accedidas nuevamente
- Reduce el número de page faults
- Mejora el tiempo de respuesta del sistema

## 🛠️ Personalización

Ambos simuladores usan los mismos archivos de configuración:
- `configuracion.txt` - Parámetros del sistema
- `tabla_paginas.txt` - Estado inicial de la memoria
- `direcciones_virtuales.txt` - Secuencia de accesos a simular

Puedes modificar estos archivos para probar diferentes escenarios y comparar el rendimiento de ambos algoritmos.
