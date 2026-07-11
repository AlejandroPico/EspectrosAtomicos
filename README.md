# TablaElementos

Tabla periódica científica, interactiva y completamente estática para explorar los 118 elementos químicos mediante zoom progresivo, filtros combinables, fichas documentales, espectros atómicos, niveles electrónicos, isótopos, propiedades físicas y químicas, contexto histórico y comparación entre elementos.

> **Estado:** versión funcional completa · `0.2.0`  
> **Tecnologías:** Svelte 5 · TypeScript · Vite · D3 · Python  
> **Despliegue:** GitHub Pages mediante GitHub Actions  
> **Ejecución:** sin backend y sin peticiones a servicios científicos durante el uso

## Demostración

La versión pública se despliega en:

**https://alejandropico.github.io/TablaElementos/**

## Objetivo

TablaElementos busca convertir la tabla periódica en una herramienta de exploración científica y educativa, no solamente en una cuadrícula de símbolos.

La posición periódica sigue siendo el punto de partida, pero cada elemento puede ampliarse hasta convertirse en una ficha resumida y abrirse después como un espacio documental completo. El proyecto está pensado para estudiantes, docentes, divulgadores y cualquier persona interesada en química, física atómica, espectroscopia, materiales o ciencias nucleares.

## Funcionalidades principales

### Tabla periódica completa

- 118 elementos.
- Distribución corta de 18 columnas.
- Distribución larga de 32 columnas.
- Lantánidos y actínidos integrables en el cuerpo principal.
- Animación en dos fases entre ambas distribuciones.
- Casillas-resumen de las series `57 - 71` y `89 - 103`.
- Resaltado completo de cada serie desde su casilla-resumen.
- Geometría cuadrada y coherente en toda la interfaz.

### Zoom científico progresivo

La rueda del ratón amplía la tabla alrededor de la posición del cursor. Las fichas incorporan información de forma gradual:

1. **Vista general:** número atómico, símbolo y nombre.
2. **Datos intermedios:** masa atómica y estado estándar.
3. **Ficha ampliada:** configuración electrónica, electronegatividad, radio y densidad.
4. **Inspección:** ionización, afinidad electrónica, temperaturas, familia y posición periódica.

El motor combina interpolación GPU, escalones de renderizado y repintado al finalizar el gesto para conservar fluidez y nitidez.

### Navegación

- Rueda: ampliar o reducir.
- Arrastre: desplazar la tabla desde el fondo o desde una ficha.
- Clic limpio: abrir el elemento.
- Doble clic sobre el fondo: restablecer y encajar.
- Clic sobre el indicador de porcentaje: restablecer y encajar.
- Zoom máximo de inspección para estudiar una sola casilla a gran tamaño.

### Filtros científicos

El botón de embudo abre un panel independiente sin ocupar espacio permanente en la mesa principal.

Los criterios del mismo grupo se combinan mediante **O** y los grupos diferentes mediante **Y**. Se pueden mantener tantos filtros simultáneos como sean necesarios.

Filtros disponibles:

- categoría química;
- bloque electrónico;
- metal, metaloide o no metal;
- estado estándar;
- grupo y periodo;
- estados de oxidación;
- número atómico;
- masa atómica;
- electronegatividad;
- primera energía de ionización;
- afinidad electrónica;
- radio atómico;
- punto de fusión;
- punto de ebullición;
- densidad;
- calor específico;
- año de descubrimiento;
- cantidad de líneas espectrales;
- cantidad de isótopos;
- niveles NIST;
- dominios científicos disponibles en el dataset.

Los filtros numéricos incluyen:

- intervalo con dos tiradores;
- mínimo y máximo editables manualmente;
- unidad normalizada;
- opción para incluir elementos sin dato;
- restablecimiento individual.

Los resultados coincidentes se realzan y los demás elementos se atenúan sin destruir el contexto periódico.

### Ficha maestra de cada elemento

Al pulsar una casilla se abre una ventana documental con pestañas rectas de estilo navegador:

- **Resumen**
- **Átomo 3D**
- **Propiedades**
- **Isótopos**
- **Espectro**
- **Líneas**
- **Niveles**
- **Química**
- **Contexto**
- **Fuentes**

El resumen presenta las propiedades esenciales como una hoja técnica continua. Los dominios extensos se cargan de forma diferida mediante un JSON independiente por elemento.

### Modelo atómico 3D

Cada elemento incluye una representación didáctica animada con:

- protones;
- neutrones estimados o derivados del isótopo disponible;
- electrones;
- distribución por capas;
- núcleo y trayectorias con profundidad visual;
- pausa y reanudación pulsando directamente sobre el simulador.

El modelo es una visualización educativa. No representa órbitas cuánticas literales.

### Espectros, líneas y niveles

- Espectro de emisión.
- Espectro de absorción.
- Escala común de longitud de onda.
- Líneas más intensas destacadas.
- Tabla técnica paginada.
- Niveles de energía NIST.
- Diagnóstico de integridad de los CSV importados.
- Adaptación automática del número de filas al espacio visible.

### Isótopos y datos tabulares

Las tablas de isótopos, líneas y niveles:

- ocupan el espacio útil completo;
- calculan automáticamente las filas que caben;
- utilizan paginación sin scroll vertical duplicado;
- conservan desplazamiento horizontal cuando las columnas lo requieren;
- mantienen la cabecera visible.

### Comparador total

La selección de elementos no tiene un límite impuesto por la aplicación.

El comparador admite los ámbitos:

- global;
- resumen;
- átomo;
- propiedades;
- isótopos;
- espectro;
- líneas;
- niveles;
- química;
- contexto;
- fuentes.

El botón de comparación de la ficha abre inicialmente el ámbito de la pestaña activa. Desde el comparador se puede cambiar después a cualquier sección.

### Temas

- claro;
- oscuro;
- automático según sistema y franja horaria;
- indicador dinámico del tema realmente activo;
- paleta científica desaturada;
- contraste adaptado para todos los textos de las casillas.

### Guía científica integrada

El icono de información abre una guía de 30 capítulos con índice lateral, explicaciones, tablas conceptuales y enlaces de ampliación.

Incluye, entre otros temas:

- anatomía de la tabla y de cada casilla;
- grupos, periodos y bloques;
- masa y peso atómico;
- configuración electrónica;
- electronegatividad;
- ionización y afinidad;
- radios atómicos;
- tendencias periódicas;
- apantallamiento y carga nuclear efectiva;
- isótopos y nucleídos;
- espectros y niveles;
- enlace y reactividad;
- materiales, cristales y magnetismo;
- abundancia cósmica;
- biología, toxicidad y radiación;
- comparación científica y calidad de datos.

`Alt + clic` sobre Información abre el diagnóstico interno del proyecto: elementos cargados, líneas válidas, CSV pendientes, distribución, tema y filtros activos.

## Fuentes científicas

El dataset local consolida información procedente principalmente de:

- **PubChem:** identidad y propiedades generales.
- **CIAAW:** pesos atómicos estándar.
- **NIST Atomic Spectra Database:** líneas, niveles y energías atómicas.
- **IAEA LiveChart:** información nuclear e isotópica.

Cada valor debe interpretarse junto con su unidad, condiciones, fecha y fuente. Distintas instituciones pueden utilizar convenciones, redondeos o condiciones experimentales diferentes.

## Arquitectura

```text
Python         → lee y normaliza CSV locales; genera los JSON públicos
TypeScript     → tipos, cámara, filtros, comparación e interacción
Svelte         → componentes y estado de la interfaz
D3             → escalas y visualización espectral
Vite           → aplicación estática de producción
GitHub Actions → validación, build y despliegue automático
```

La aplicación no necesita servidor de aplicación ni base de datos remota.

## Estrategia de datos

El índice principal contiene únicamente la información necesaria para:

- dibujar la tabla;
- aplicar filtros;
- mostrar la información progresiva durante el zoom;
- localizar el JSON detallado de cada elemento.

Los dominios completos se generan como archivos separados:

```text
public/data/elements/H.json
public/data/elements/He.json
public/data/elements/Li.json
...
public/data/elements/Og.json
```

Esto evita cargar simultáneamente todos los isótopos, niveles y registros científicos de los 118 elementos.

## Estructura de datos por elemento

Cada elemento se encuentra en una carpeta con la convención:

```text
NNN-Symbol-english-name
```

Ejemplos:

```text
001-H-hydrogen
026-Fe-iron
092-U-uranium
118-Og-oganesson
```

Dominios admitidos:

```text
identity.csv
spectra_nist_lines.csv
spectra_nist_levels.csv
atomic_properties.csv
isotopes.csv
physical_properties.csv
chemical_properties.csv
materials.csv
thermodynamics.csv
geochemistry.csv
astrophysics.csv
biology_medicine.csv
environment_safety.csv
industry_economy.csv
history.csv
compounds.csv
analytical_methods.csv
radiation_interaction.csv
photonics_color.csv
computational.csv
sources.csv
```

Los archivos aceptados y normalizados deben terminar en `data/elements/<elemento>/`. `data/import/` se conserva como zona de entrada y material bruto.

## Estructura del repositorio

```text
.
├─ data/
│  ├─ elements/                 # 118 carpetas y manifiesto maestro
│  ├─ import/                   # descargas y material de entrada
│  ├─ processed/                # JSON generado durante el build
│  ├─ raw/                      # compatibilidad y datos históricos
│  └─ schema/                   # esquemas de validación
├─ public/
│  ├─ data/                     # dataset estático servido por la web
│  └─ favicon.svg
├─ scripts/
│  ├─ build_data.py
│  ├─ build_element_data.py
│  ├─ import_nist_exports.py
│  └─ init_elements_structure.py
├─ src/
│  ├─ app/
│  ├─ components/
│  ├─ lib/
│  ├─ styles/
│  └─ main.ts
├─ .github/workflows/deploy.yml
├─ package.json
├─ svelte.config.js
├─ tsconfig.json
├─ vite.config.ts
└─ README.md
```

## Requisitos para desarrollo

El workflow de producción utiliza:

- Node.js 24;
- Python 3.13.

Para trabajar localmente se recomienda utilizar esas versiones o versiones compatibles recientes.

## Instalación local

```bash
git clone https://github.com/AlejandroPico/TablaElementos.git
cd TablaElementos
npm install
npm run dev
```

Vite mostrará la dirección local en la terminal.

## Comandos

### Desarrollo

```bash
npm run dev
```

Genera los datos y abre el servidor de desarrollo.

### Validación

```bash
npm run check
```

Ejecuta `svelte-check` y la validación de TypeScript.

### Generar datasets

```bash
npm run build:data
```

Ejecuta:

```text
scripts/build_data.py
scripts/build_element_data.py
```

### Producción

```bash
npm run build
```

El resultado se guarda en `dist/`.

### Vista previa del build

```bash
npm run preview
```

### Inicializar las 118 carpetas

```bash
npm run init:elements
```

### Importar exportaciones NIST

Prueba sin modificar archivos:

```bash
npm run import:nist:dry
```

Importación real:

```bash
npm run import:nist
```

## Despliegue en GitHub Pages

El workflow `.github/workflows/deploy.yml` se ejecuta con cada `push` a `main` y realiza:

1. checkout del repositorio;
2. instalación de Python 3.13;
3. instalación de Node.js 24;
4. instalación de dependencias;
5. `npm run check`;
6. generación de datasets;
7. build de Vite;
8. publicación del artefacto en GitHub Pages.

La fuente de Pages debe estar configurada como:

```text
Settings → Pages → Build and deployment → GitHub Actions
```

## Principios del proyecto

- Los datos científicos utilizados por la web quedan versionados en el repositorio.
- No se consultan APIs científicas durante la navegación.
- Las ausencias de datos se muestran como ausencias, no se inventan valores.
- Las unidades se normalizan antes de construir rangos comparables.
- Las fuentes y fechas deben conservarse junto al dato.
- La tabla mantiene siempre el contexto periódico, incluso al filtrar.
- Las representaciones visuales educativas se distinguen de los modelos físicos exactos.

## Inspiración de interfaz

El sistema de filtros toma como referencia conceptual las posibilidades de exploración de herramientas periódicas modernas como [ZPeriod](https://zperiod.app/?lang=es), pero su implementación, estructura de datos, código y diseño visual son propios de TablaElementos.

La estética general mantiene coherencia con otros proyectos científicos interactivos del autor, especialmente la Tabla de Nucleídos.

## Licencia

El repositorio todavía no incluye un archivo de licencia. Hasta que se añada uno, el código y los datos no deben considerarse automáticamente reutilizables bajo una licencia abierta concreta.
