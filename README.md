# Tabla elementos

Tabla periódica ampliada y estática para explorar elementos químicos, espectros, niveles electrónicos, propiedades físicas, química, isótopos, materiales, usos, historia y futuros bloques de datos científicos.

> Estado: **V1.7 renombrado estructural**.  
> Tecnología: **Python + Svelte + TypeScript + Vite + D3**.  
> Despliegue: **GitHub Pages mediante GitHub Actions**.  
> Ejecución: **100% estática**, sin servidor externo y sin consultas remotas en tiempo de uso.

## Objetivo del proyecto

**Tabla elementos** nace como una tabla periódica ampliada: una interfaz visual y educativa donde cada elemento químico pueda consultarse como una ficha científica completa.

El proyecto empezó centrado en espectros atómicos, pero ahora queda preparado para crecer hacia una tabla periódica total. La V1.6 cargó los 118 elementos desde el manifiesto maestro, mantuvo la visualización espectral de muestra como respaldo y añadió un diagnóstico NIST provisional dentro de cada ficha. La V1.7 consolida el nuevo nombre del proyecto y actualiza las referencias internas principales.

Cada ficha de la tabla muestra:

- número atómico;
- símbolo;
- nombre del elemento.

Al pulsar un elemento se abre una ficha flotante con pestañas:

- longitudes de onda, con interruptor interno de emisión/absorción;
- niveles de energía;
- NIST, con diagnóstico provisional de archivos importados;
- información del elemento;
- tabla técnica de líneas espectrales.

El comparador aparece solo cuando se añaden elementos con el botón `+`. Se muestra como una bandeja inferior que ocupa parte de la pantalla sin superponerse a la tabla.

## Arquitectura

```txt
Python         → procesa datos locales CSV y genera JSON público
TypeScript     → modelado tipado de elementos, líneas, transiciones y estado NIST
Svelte         → componentes visuales de la interfaz
Vite           → build estático para GitHub Pages
D3             → escalas científicas, ejes y representación espectral
GitHub Actions → build y despliegue automático
```

## Estructura del repositorio

```txt
.
├─ data/
│  ├─ elements/
│  │  ├─ README.md
│  │  └─ elements.manifest.csv
│  ├─ import/
│  │  ├─ README.md
│  │  └─ nist/
│  │     └─ .gitkeep
│  ├─ raw/
│  │  ├─ elements.csv
│  │  └─ sample-lines.csv
│  ├─ processed/
│  │  └─ spectra.sample.json
│  └─ schema/
│     └─ spectral-line.schema.json
├─ public/
│  ├─ data/
│  │  └─ spectra.sample.json
│  └─ favicon.svg
├─ scripts/
│  ├─ build_data.py
│  ├─ import_nist_exports.py
│  └─ init_elements_structure.py
├─ src/
│  ├─ app/
│  ├─ components/
│  ├─ lib/
│  ├─ styles/
│  │  ├─ expanded.css
│  │  └─ global.css
│  └─ main.ts
├─ .github/
│  └─ workflows/
│     └─ deploy.yml
├─ package.json
├─ vite.config.ts
└─ README.md
```

## Datos

La aplicación no hace llamadas externas en tiempo de ejecución. Los datos se versionan dentro del repositorio y el build genera un JSON estático en `public/data/`.

La tabla principal se genera desde:

```txt
data/elements/elements.manifest.csv
```

La estructura ampliada vive en:

```txt
data/elements/
```

Contiene:

- `elements.manifest.csv`: manifiesto maestro con los 118 elementos y la carpeta prevista para cada uno;
- `README.md`: reglas de estructura, nombres de CSVs y dominios científicos previstos;
- `scripts/init_elements_structure.py`: generador local de las 118 carpetas de elementos y sus plantillas CSV.

Para generar localmente todas las carpetas:

```bash
npm run init:elements
```

Git no conserva carpetas vacías, por eso las subcarpetas se generan mediante script antes de empezar a cargar datos reales.

## Importar CSVs de NIST ASD

Coloca los CSV descargados de NIST en:

```txt
data/import/nist/
```

Nombres esperados:

```txt
001_H_espectro.csv
001_H_niveles.csv
002_He_espectro.csv
002_He_niveles.csv
...
118_Og_espectro.csv
118_Og_niveles.csv
```

Primero genera las carpetas si no existen:

```bash
npm run init:elements
```

Luego prueba la importación sin copiar nada:

```bash
npm run import:nist:dry
```

Si la salida es correcta, ejecuta la importación real:

```bash
npm run import:nist
```

El script copiará, por ejemplo:

```txt
data/import/nist/001_H_espectro.csv
```

a:

```txt
data/elements/001-H-hydrogen/001_H_espectro.csv
```

Por defecto copia los archivos y conserva la bandeja de entrada. Para moverlos en vez de copiarlos:

```bash
python scripts/import_nist_exports.py --move
```

## Diagnóstico NIST provisional

`scripts/build_data.py` analiza los archivos NIST en cada build y añade un bloque `nist_by_element` al JSON público. La pestaña **NIST** de cada ficha muestra:

- si existe el archivo de espectro;
- si existe el archivo de niveles;
- columnas detectadas;
- número de filas;
- ruta del archivo;
- advertencia si el CSV parece HTML, JavaScript o una sola columna no tabular.

Si los CSV no son tablas limpias, el build no falla: lo marca como diagnóstico para poder corregir la exportación.

## Instalación local

Requisitos:

- Node.js 22 o superior recomendado;
- Python 3.12 recomendado.

```bash
npm install
npm run dev
```

## Comandos útiles

Generar datos actuales de la aplicación:

```bash
npm run build:data
```

Inicializar estructura ampliada de elementos:

```bash
npm run init:elements
```

Build de producción:

```bash
npm run build
```

El resultado queda en:

```txt
dist/
```

## Publicación en GitHub Pages

El workflow `.github/workflows/deploy.yml` publica automáticamente la carpeta `dist` cuando se hace push a `main`.

En GitHub, revisa:

```txt
Settings → Pages → Build and deployment → Source → GitHub Actions
```

La base pública configurada para Vite es:

```txt
/TablaElementos/
```

## Funcionalidades V1.7

- Proyecto renombrado internamente a **Tabla elementos**.
- Título HTML y título Svelte actualizados a `Tabla elementos`.
- Base de GitHub Pages actualizada a `/TablaElementos/`.
- Favicon SVG nuevo basado en una tabla periódica estilizada.
- Tabla periódica con los 118 elementos desde `data/elements/elements.manifest.csv`.
- Lantánidos y actínidos visibles en filas separadas.
- Pantalla principal sin cabeceras, subtítulos ni textos guía.
- Tabla periódica como elemento visual dominante.
- Fichas cuadradas con ángulos de 90 grados.
- Celdas con número atómico, símbolo y nombre.
- Coloración por categoría química.
- Ficha flotante por elemento al pulsar la celda.
- Pestañas internas: longitudes de onda, niveles de energía, NIST, elemento y datos técnicos.
- Diagnóstico provisional de archivos NIST por elemento.
- Bandeja `data/import/nist/` para subir CSVs planos de NIST.
- Importador `npm run import:nist` para repartir espectros y niveles por elemento.
- Dataset local y estático.

## Licencia

Pendiente de decisión. Para proyectos abiertos y educativos, Apache-2.0 o MIT son opciones razonables.
