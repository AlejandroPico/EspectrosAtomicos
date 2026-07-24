# Auditoría de propiedades científicas

Fecha de revisión: 24 de julio de 2026.

Este documento define qué propiedades de los elementos están disponibles actualmente en TablaElementos, cuáles se muestran en la interfaz, qué datos faltan y qué visualizaciones deberían incorporarse para convertir el proyecto en una tabla periódica científica de cobertura máxima.

## Principio de modelado

Una propiedad no siempre puede representarse mediante un único número. Muchos valores dependen de:

- temperatura y presión;
- fase o alótropo;
- isótopo;
- carga o estado de ionización;
- estado de oxidación;
- número de coordinación;
- estructura cristalina;
- orientación de la muestra;
- método experimental o computacional.

Los nuevos datasets deberán conservar, cuando sea aplicable:

```text
property_id
value
unit
uncertainty
lower_bound
upper_bound
temperature_K
pressure_Pa
phase
allotrope
isotope
charge_state
oxidation_state
coordination_number
crystal_phase
method
quality
source
source_url
retrieved_at
notes
```

## Valencia, electrones de valencia y estado de oxidación

Estos conceptos no deben fusionarse:

- **Valencia:** capacidad de combinación; concepto histórico relacionado con el número máximo de átomos monovalentes que pueden combinarse con el átomo.
- **Electrones de valencia:** electrones que pueden participar en enlaces. Su identificación es sencilla en elementos representativos, pero puede ser dependiente del contexto en metales de transición, lantánidos y actínidos.
- **Estado de oxidación:** carga formal obtenida mediante una aproximación iónica de los enlaces de un compuesto.

El proyecto ya almacena `oxidation_states`, pero no almacena de forma separada:

- `common_valences`;
- `valence_electron_count`;
- `valence_shell_configuration`;
- estados de oxidación habituales frente a raros o predichos.

## Cobertura actual

### Disponible y visible

#### Identidad y posición

- nombre español e inglés;
- símbolo;
- número atómico;
- grupo;
- periodo;
- bloque;
- categoría química;
- estado estándar;
- clasificación PubChem.

#### Propiedades atómicas

- masa atómica;
- peso atómico estándar CIAAW;
- configuración electrónica;
- electronegatividad de Pauling;
- radio publicado por PubChem;
- primera energía de ionización;
- afinidad electrónica.

> Pendiente: confirmar y renombrar el campo `atomic_radius` según la definición exacta de PubChem. Su tabla periódica describe su tendencia como radio de van der Waals; no debe presentarse como un radio atómico universal sin aclaración.

#### Propiedades químicas

- estados de oxidación publicados;
- grupo o clasificación química.

#### Propiedades físicas

- estado estándar;
- punto de fusión;
- punto de ebullición;
- densidad.

#### Historia y color convencional

- año de descubrimiento;
- color CPK convencional.

#### Isótopos y física nuclear

Los CSV de IAEA LiveChart ya contienen, según el nucleído:

- Z y N;
- radio nuclear;
- abundancia;
- espín y paridad;
- vida media y vida media en segundos;
- modos y probabilidades de desintegración;
- isospín;
- dipolo magnético nuclear;
- cuadrupolo eléctrico;
- energías Q;
- energías de separación neutrónica y protónica;
- energía de enlace;
- masa atómica;
- exceso de masa;
- año de descubrimiento;
- referencias ENSDF.

Actualmente se presentan como tabla técnica, sin visualizaciones nucleares especializadas.

#### Espectroscopia atómica

- líneas NIST ASD;
- longitudes de onda observadas y Ritz;
- intensidades y probabilidades cuando están disponibles;
- configuraciones, términos y valores J;
- niveles de energía NIST;
- incertidumbres y referencias bibliográficas;
- espectro gráfico de emisión y absorción.

### Dominios preparados pero generalmente vacíos

La interfaz ya puede mostrar automáticamente registros añadidos a:

- `materials.csv`;
- `thermodynamics.csv`;
- `compounds.csv`;
- `computational.csv`;
- `geochemistry.csv`;
- `astrophysics.csv`;
- `biology_medicine.csv`;
- `environment_safety.csv`;
- `industry_economy.csv`;
- `analytical_methods.csv`;
- `radiation_interaction.csv`.

## Propiedades pendientes por categoría

### 1. Identidad, historia y nomenclatura

- nombre IUPAC oficial y variantes lingüísticas;
- etimología completa;
- descubridor o equipo;
- lugar y circunstancias del descubrimiento;
- origen natural o sintético;
- CAS RN y otros identificadores cuando sean aplicables;
- historia de la denominación y nombres provisionales.

### 2. Estructura electrónica

- configuración electrónica completa y abreviada por separado;
- distribución por capas;
- electrones de valencia;
- configuración de valencia;
- valencias comunes;
- estados de oxidación comunes, raros, predichos y máximos;
- término fundamental, J y factor de Landé;
- energías de ionización sucesivas;
- energía electrónica total de enlace;
- carga nuclear efectiva por orbital o método;
- constante de apantallamiento y modelo utilizado;
- polarizabilidad estática y dinámica.

### 3. Radios y tamaños

- radio covalente, indicando orden de enlace o parametrización;
- radio de van der Waals;
- radio metálico;
- radio iónico por carga, coordinación y estado de espín;
- radio cristalino;
- volumen atómico y volumen molar;
- radio nuclear de carga por isótopo.

### 4. Reactividad y electroquímica

- electronegatividad de Mulliken;
- electronegatividad de Allred–Rochow;
- electronegatividad de Allen;
- dureza y blandura química;
- potencial químico;
- potenciales estándar de reducción por semirreacción;
- comportamiento frente a agua, aire, ácidos, bases y halógenos;
- trabajo de extracción por superficie cristalográfica;
- energía cohesiva y energía de atomización.

### 5. Termodinámica y fases

- capacidad calorífica Cp y Cv;
- entropía molar estándar;
- entalpía de fusión;
- entalpía de vaporización;
- entalpía de sublimación;
- entalpía de atomización;
- energía libre de Gibbs;
- presión de vapor y parámetros de Antoine;
- punto triple;
- punto crítico;
- viscosidad y tensión superficial en fase líquida;
- velocidad del sonido;
- temperatura de Debye;
- diagrama de fases presión–temperatura;
- transiciones sólido–sólido.

### 6. Cristalografía, alótropos y materiales

- estructuras cristalinas por fase;
- grupo espacial;
- parámetros y ángulos de red;
- volumen de celda;
- densidad calculada y experimental;
- posiciones atómicas;
- fichero CIF o estructura equivalente;
- alótropos y polimorfos;
- estabilidad relativa de fases;
- ecuación de estado;
- fonones y estabilidad dinámica;
- energía superficial por plano;
- diagramas de bandas y densidad de estados;
- energía de Fermi y banda prohibida, cuando tengan sentido.

### 7. Propiedades eléctricas, magnéticas, térmicas y mecánicas

- conductividad y resistividad eléctrica;
- coeficiente térmico de resistividad;
- efecto Hall;
- coeficiente Seebeck;
- temperatura crítica de superconductividad;
- conductividad y difusividad térmica;
- coeficiente de expansión térmica;
- tipo y orden magnético;
- momento magnético;
- susceptibilidad y permeabilidad;
- temperaturas de Curie y Néel;
- tensor elástico;
- módulos de Young, cizallamiento y compresibilidad;
- coeficiente de Poisson;
- anisotropía elástica;
- durezas Mohs, Vickers, Brinell y Rockwell;
- resistencia a tracción, límite elástico y tenacidad, siempre ligados a pureza y procesado.

### 8. Óptica, rayos X y electrones

- índice de refracción complejo por longitud de onda;
- reflectividad, absorción y transmitancia;
- constantes dieléctricas;
- color real por fase y condiciones;
- color de llama y líneas responsables;
- bordes de absorción;
- líneas características K, L y M;
- energías XPS y líneas Auger;
- rendimientos de fluorescencia;
- coeficientes de atenuación másica;
- secciones eficaces fotoeléctrica, Compton, Rayleigh y creación de pares;
- secciones eficaces de dispersión de electrones.

### 9. Nuclear y neutrónica

- número resumido de isótopos conocidos y estables;
- isótopos primordiales, cosmogénicos y artificiales;
- cadenas de desintegración;
- abundancias CIAAW separadas de abundancias IAEA;
- longitudes de dispersión neutrónica coherente e incoherente;
- secciones eficaces de dispersión y absorción;
- captura neutrónica dependiente de energía;
- integrales de resonancia;
- secciones de fisión;
- niveles nucleares y transiciones gamma;
- rendimientos de fisión y productos de activación.

### 10. Geoquímica, cosmos, biología y medioambiente

- abundancia en corteza, manto, océanos y atmósfera;
- abundancia solar, meteórica y cósmica;
- temperatura de condensación cosmológica;
- origen de nucleosíntesis;
- clasificación Goldschmidt;
- minerales y menas principales;
- abundancia y función en el cuerpo humano;
- esencialidad, deficiencia y toxicidad;
- especiación química relevante;
- LD50 con especie, vía y formulación;
- carcinogenicidad, neurotoxicidad y bioacumulación;
- destino ambiental y movilidad;
- estados de oxidación con toxicidad diferenciada.

### 11. Industria, economía y criticidad

- producción minera y refinada;
- reservas y recursos;
- principales países productores;
- reciclaje;
- usos por sector;
- sustitución;
- criticidad y riesgo de suministro;
- precio con fecha, mercado, pureza y unidad;
- inventarios estratégicos y regulación.

## Fuentes prioritarias

### Ya integradas

- PubChem PUG REST y PUG View;
- CIAAW;
- IAEA LiveChart;
- NIST Atomic Spectra Database.

### Ampliaciones recomendadas

- **NIST ASD Ground States and Ionization Energies:** configuración fundamental, términos, energías de ionización sucesivas y energía total de enlace.
- **NIST Chemistry WebBook / JANAF:** termodinámica, cambios de fase, presión de vapor, capacidades caloríficas y entropías, con cobertura desigual según elemento y especie.
- **Materials Project API:** estructuras cristalinas, elasticidad, magnetismo, estructura electrónica, fonones, dieléctricos, ecuaciones de estado, XAS y superficies. Requiere clave de API y selección explícita de fase.
- **NIST XCOM:** coeficientes de atenuación y secciones eficaces de fotones frente a energía.
- **NIST X-ray Transition Energies:** líneas características y energías de transición de rayos X.
- **NIST XPS Database:** energías de enlace, líneas Auger y desplazamientos químicos.
- **NIST NCNR / NNDC:** dispersión y absorción neutrónica.
- **EPA CompTox / PubChem PUG View:** toxicología, seguridad, exposición y bioactividad. CompTox requiere clave gratuita para su API.
- **USGS Mineral Commodity Summaries:** producción, reservas, recursos y cadenas de suministro con versión anual.

## Visualizaciones objetivo

### Estructura electrónica

- diagrama de ocupación por capas y orbitales;
- resaltado de electrones de valencia;
- diagrama de niveles y término fundamental;
- gráfico de energías de ionización sucesivas con saltos de capa.

### Radios

- comparación de radios covalente, van der Waals, metálico e iónico;
- selector de carga y coordinación para radios iónicos;
- representación concéntrica proporcional.

### Termodinámica

- curva de presión de vapor;
- diagrama de fases P–T;
- curva de calentamiento con entalpías de transición;
- Cp frente a temperatura.

### Cristalografía y materiales

- visor 3D de celda unidad;
- selector de alótropo o fase;
- parámetros de red y grupo espacial;
- bandas electrónicas y densidad de estados;
- matriz y superficies de anisotropía elástica.

### Nuclear

- franja de isótopos frente a número de neutrones;
- abundancias naturales en barras;
- vida media en escala logarítmica;
- mapa de modos de desintegración;
- cadenas de desintegración;
- momentos nucleares y energías Q.

### Radiación

- atenuación frente a energía del fotón;
- bordes de absorción;
- espectro característico de rayos X;
- tabla y gráfico XPS/Auger;
- secciones neutrónicas frente a energía.

### Abundancia y contexto

- comparación logarítmica entre Universo, corteza, océano y cuerpo humano;
- mapa de origen por proceso de nucleosíntesis;
- producción y reservas con fecha de referencia.

### Tendencias globales

Crear una vista global que permita seleccionar cualquier propiedad numérica y representar:

- propiedad frente a número atómico;
- propiedad sobre la geometría periódica mediante escala de color;
- comparación de varios elementos;
- distribución por grupo, periodo, bloque o categoría;
- incertidumbre y elementos sin dato.

Esta vista reutilizará el sistema actual de filtros y será la principal herramienta para explorar tendencias periódicas.

## Prioridad recomendada

1. Valencia, electrones de valencia, estados de oxidación y energías de ionización sucesivas.
2. Separación correcta de los distintos radios atómicos e iónicos.
3. Estructuras cristalinas, alótropos y visor 3D.
4. Termodinámica y diagramas de fase.
5. Visualización nuclear avanzada sobre los datos IAEA ya descargados.
6. Rayos X, XPS, atenuación y datos neutrónicos.
7. Propiedades eléctricas, magnéticas, térmicas y mecánicas.
8. Abundancias, biología, toxicidad, industria y economía.
9. Vista global de tendencias para cualquier propiedad numérica.
