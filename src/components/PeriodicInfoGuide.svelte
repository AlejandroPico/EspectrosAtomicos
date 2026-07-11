<script lang="ts">
  import { createEventDispatcher, onMount } from 'svelte';

  interface GuideLink { label: string; url: string; }
  interface GuideRow { term: string; description: string; }
  interface GuideTopic {
    id: string;
    label: string;
    title: string;
    paragraphs: string[];
    rows?: GuideRow[];
    callout?: string;
    links?: GuideLink[];
  }

  export let open = false;

  const dispatch = createEventDispatcher<{ close: void }>();
  let activeId = 'vision';
  let scrollElement: HTMLDivElement;

  const topics: GuideTopic[] = [
    {
      id: 'vision',
      label: '1 · Qué estás viendo',
      title: 'Qué estás viendo',
      paragraphs: [
        'Esta aplicación representa la tabla periódica de los elementos químicos y permite ampliar cada casilla como una ficha científica progresiva. La posición de un elemento no es decorativa: resume su número atómico, su configuración electrónica y las semejanzas químicas que comparte con los elementos próximos.',
        'En la vista general aparecen únicamente el número atómico, el símbolo y el nombre. Al ampliar se incorporan propiedades fundamentales. En el nivel de inspección la casilla actúa como una ficha resumida; al pulsarla se abre la ficha maestra con todos los dominios disponibles.'
      ],
      rows: [
        { term: 'Filas', description: 'Son periodos. Indican el nivel electrónico principal que se está ocupando.' },
        { term: 'Columnas', description: 'Son grupos. Reúnen elementos con patrones de valencia y comportamiento químico relacionados.' },
        { term: 'Colores', description: 'Distinguen familias químicas como gases nobles, halógenos, metales de transición, lantánidos y actínidos.' }
      ],
      callout: 'La tabla es un mapa de regularidades atómicas: cada desplazamiento horizontal o vertical tiene significado físico y químico.',
      links: [
        { label: 'IUPAC · Tabla periódica', url: 'https://iupac.org/what-we-do/periodic-table-of-elements/' },
        { label: 'PubChem · Periodic Table', url: 'https://pubchem.ncbi.nlm.nih.gov/periodic-table/' }
      ]
    },
    {
      id: 'anatomia',
      label: '2 · Anatomía de la casilla',
      title: 'Cómo leer una casilla',
      paragraphs: [
        'La casilla mínima conserva tres referencias universales: número atómico, símbolo y nombre. El resto de campos aparece de forma progresiva para evitar que la tabla completa se convierta en una masa ilegible.',
        'En ampliaciones medias se priorizan masa atómica y estado estándar. En ampliaciones profundas aparecen configuración electrónica, electronegatividad, radio y densidad. La inspección incorpora las principales magnitudes del resumen científico.'
      ],
      rows: [
        { term: 'Esquina superior izquierda', description: 'Número atómico Z.' },
        { term: 'Centro', description: 'Símbolo químico y nombre del elemento.' },
        { term: 'Perímetro ampliado', description: 'Propiedades atómicas y físicas procedentes de los CSV locales.' }
      ]
    },
    {
      id: 'identidad',
      label: '3 · Z, símbolo y nombre',
      title: 'Número atómico, símbolo y nombre',
      paragraphs: [
        'El número atómico Z es la cantidad de protones del núcleo. Define la identidad del elemento: un átomo con un protón es hidrógeno; uno con veintiséis protones es hierro. En un átomo neutro, el número de electrones coincide con Z.',
        'El símbolo es la abreviatura internacional del elemento. Puede proceder de su nombre moderno o de una denominación histórica o latina, como Fe para ferrum o Na para natrium.'
      ],
      rows: [
        { term: 'Z', description: 'Número de protones y posición ordinal en la tabla.' },
        { term: 'Símbolo', description: 'Abreviatura química normalizada, sensible a mayúsculas y minúsculas.' },
        { term: 'Nombre', description: 'Denominación del elemento en español; la ficha conserva también el nombre inglés.' }
      ],
      links: [{ label: 'IUPAC · Nombres de elementos', url: 'https://iupac.org/what-we-do/periodic-table-of-elements/' }]
    },
    {
      id: 'organizacion',
      label: '4 · Grupo, periodo y bloque',
      title: 'Grupo, periodo y bloque electrónico',
      paragraphs: [
        'Los grupos son las columnas numeradas del 1 al 18. Los elementos de un mismo grupo suelen compartir pautas de electrones de valencia y, por ello, propiedades químicas relacionadas. Los periodos son las filas y reflejan el llenado progresivo de niveles electrónicos.',
        'El bloque indica el tipo de orbital que recibe el electrón diferenciador: s, p, d o f. El bloque no es una categoría estética; conecta la posición periódica con la configuración electrónica.'
      ],
      rows: [
        { term: 'Bloque s', description: 'Grupos 1 y 2, además de helio por configuración.' },
        { term: 'Bloque p', description: 'Zona derecha de la tabla, grupos 13 a 18.' },
        { term: 'Bloque d', description: 'Metales de transición.' },
        { term: 'Bloque f', description: 'Lantánidos y actínidos.' }
      ]
    },
    {
      id: 'familias',
      label: '5 · Familias químicas',
      title: 'Categorías y familias químicas',
      paragraphs: [
        'Las categorías coloreadas son agrupaciones prácticas. Algunas, como gases nobles, halógenos o metales alcalinos, tienen fronteras claras. Otras, como metaloides o metales postransición, dependen parcialmente del criterio de clasificación.',
        'El color ayuda a reconocer regiones, pero no sustituye los datos. Un elemento puede mostrar comportamientos distintos según estado de oxidación, presión, temperatura o compuesto.'
      ],
      rows: [
        { term: 'Gases nobles', description: 'Elementos del grupo 18, generalmente poco reactivos en condiciones ordinarias.' },
        { term: 'Halógenos', description: 'Grupo 17, con elevada tendencia a formar sales y aniones.' },
        { term: 'Metales de transición', description: 'Bloque d, con química de coordinación y estados de oxidación variados.' },
        { term: 'Lantánidos y actínidos', description: 'Series del bloque f, mostradas separadas o integradas según el modo 18/32.' }
      ]
    },
    {
      id: 'masa',
      label: '6 · Masa y peso atómico',
      title: 'Masa atómica y peso atómico estándar',
      paragraphs: [
        'La masa de un átomo concreto depende del isótopo. La masa atómica mostrada en bases de datos suele representar un valor isotópico o una media asociada a la composición natural. El peso atómico estándar es un valor recomendado para materiales terrestres normales y puede expresarse como intervalo cuando la abundancia isotópica varía.',
        'No debe confundirse número másico A con peso atómico: A es la suma entera de protones y neutrones de un isótopo; el peso atómico puede ser decimal y representar una mezcla.'
      ],
      rows: [
        { term: 'u', description: 'Unidad de masa atómica unificada.' },
        { term: 'Número másico A', description: 'Protones + neutrones de un nucleído concreto.' },
        { term: 'CIAAW', description: 'Comisión que evalúa y publica pesos atómicos estándar.' }
      ],
      links: [{ label: 'CIAAW · Standard Atomic Weights', url: 'https://ciaaw.org/atomic-weights.htm' }]
    },
    {
      id: 'configuracion',
      label: '7 · Configuración electrónica',
      title: 'Configuración electrónica y capas',
      paragraphs: [
        'La configuración electrónica describe cómo se distribuyen los electrones entre niveles, subniveles y orbitales. Una expresión como [Ar] 3d6 4s2 utiliza el gas noble argón como núcleo abreviado y especifica los electrones restantes.',
        'Las capas del simulador 3D son una representación didáctica. En mecánica cuántica los electrones no siguen órbitas planetarias rígidas: se describen mediante orbitales y distribuciones de probabilidad.'
      ],
      rows: [
        { term: 'n', description: 'Nivel principal o capa electrónica.' },
        { term: 's, p, d, f', description: 'Tipos de subnivel con distintas formas y capacidades.' },
        { term: 'Electrones de valencia', description: 'Electrones que participan con mayor frecuencia en enlaces y reacciones.' }
      ],
      links: [{ label: 'NIST · Atomic Spectra Database', url: 'https://physics.nist.gov/PhysRefData/ASD/' }]
    },
    {
      id: 'electronegatividad',
      label: '8 · Electronegatividad',
      title: 'Electronegatividad',
      paragraphs: [
        'La electronegatividad expresa la tendencia relativa de un átomo enlazado a atraer densidad electrónica. No es una energía absoluta y existen varias escalas. La escala de Pauling es la más habitual en tablas generales.',
        'Suele aumentar hacia la derecha y hacia arriba de la tabla, aunque hay excepciones y elementos para los que el valor no está definido o depende del método.'
      ],
      rows: [
        { term: 'Valor alto', description: 'Mayor capacidad relativa para atraer electrones en un enlace.' },
        { term: 'Valor bajo', description: 'Mayor carácter electropositivo y tendencia a ceder densidad electrónica.' },
        { term: 'Uso', description: 'Ayuda a interpretar polaridad, carácter iónico y tendencias de enlace.' }
      ]
    },
    {
      id: 'energias',
      label: '9 · Ionización y afinidad',
      title: 'Energía de ionización y afinidad electrónica',
      paragraphs: [
        'La primera energía de ionización es la energía necesaria para retirar el electrón más débilmente ligado de un átomo gaseoso neutro. Las ionizaciones sucesivas retiran electrones adicionales y suelen requerir cada vez más energía.',
        'La afinidad electrónica describe el cambio energético asociado a la captura de un electrón por un átomo gaseoso. El signo y la convención pueden variar entre fuentes, por lo que siempre conviene leer la unidad y la definición del dataset.'
      ],
      rows: [
        { term: 'Ionización alta', description: 'Electrones externos más difíciles de extraer.' },
        { term: 'Salto grande', description: 'Puede señalar que ya se ha eliminado la capa de valencia y se intenta romper una capa interna.' },
        { term: 'Afinidad', description: 'Relacionada con la estabilidad del anión gaseoso, no con una reacción completa en disolución.' }
      ],
      links: [{ label: 'NIST · Ionization Energies', url: 'https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html' }]
    },
    {
      id: 'radio',
      label: '10 · Radio atómico',
      title: 'Radio atómico e iónico',
      paragraphs: [
        'Un átomo no tiene una frontera rígida. El radio atómico se define mediante modelos o distancias experimentales, por ejemplo radio covalente, metálico o de van der Waals. Por eso distintas fuentes pueden publicar valores diferentes sin que una sea necesariamente errónea.',
        'Los cationes suelen ser más pequeños que el átomo neutro correspondiente y los aniones suelen ser mayores, debido al cambio en repulsión electrónica y carga nuclear efectiva.'
      ],
      rows: [
        { term: 'Covalente', description: 'Mitad de la distancia entre núcleos enlazados de forma covalente.' },
        { term: 'Metálico', description: 'Derivado de distancias entre átomos en estructuras metálicas.' },
        { term: 'van der Waals', description: 'Distancia de contacto entre átomos no enlazados.' }
      ]
    },
    {
      id: 'fisicas',
      label: '11 · Estado, densidad y temperaturas',
      title: 'Propiedades físicas principales',
      paragraphs: [
        'El estado estándar indica la forma física de referencia bajo condiciones especificadas por la fuente. No significa que el elemento permanezca siempre sólido, líquido o gas: presión y temperatura pueden cambiar su fase.',
        'Densidad, punto de fusión y punto de ebullición dependen de condiciones, pureza, estructura cristalina e isótopo. Los valores de la tabla son referencias, no sustituyen una ficha termodinámica completa.'
      ],
      rows: [
        { term: 'Densidad', description: 'Masa por unidad de volumen; debe leerse junto con temperatura y fase.' },
        { term: 'Fusión', description: 'Temperatura de equilibrio entre sólido y líquido a una presión dada.' },
        { term: 'Ebullición', description: 'Temperatura a la que la presión de vapor iguala la presión externa.' }
      ],
      links: [{ label: 'PubChem · Periodic Table', url: 'https://pubchem.ncbi.nlm.nih.gov/periodic-table/' }]
    },
    {
      id: 'isotopos',
      label: '12 · Isótopos y nucleídos',
      title: 'Isótopos, estabilidad y desintegración',
      paragraphs: [
        'Los isótopos son átomos del mismo elemento —mismo número de protones— con diferente número de neutrones. Cada combinación concreta de protones y neutrones es un nucleído.',
        'La pestaña de isótopos puede incluir masa, vida media, abundancia, espín y modos de desintegración. Un elemento puede poseer isótopos estables, radiactivos naturales y radionucleídos producidos artificialmente.'
      ],
      rows: [
        { term: 'N', description: 'Número de neutrones.' },
        { term: 'A', description: 'Número másico: Z + N.' },
        { term: 'Vida media', description: 'Tiempo en el que se desintegra estadísticamente la mitad de una población.' },
        { term: 'Abundancia', description: 'Fracción del isótopo en una muestra o reservorio definido.' }
      ],
      links: [{ label: 'IAEA · LiveChart of Nuclides', url: 'https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html' }]
    },
    {
      id: 'espectro',
      label: '13 · Espectros y líneas',
      title: 'Espectros atómicos, emisión y absorción',
      paragraphs: [
        'Cuando un átomo cambia de estado electrónico puede emitir o absorber fotones con energías concretas. Esa selección produce líneas espectrales características. La longitud de onda identifica la energía del fotón mediante la relación E = hc/λ.',
        'El espectro de emisión muestra radiación producida por transiciones hacia estados de menor energía. El de absorción muestra longitudes de onda retiradas de una radiación continua al excitar el átomo.'
      ],
      rows: [
        { term: 'λ', description: 'Longitud de onda, normalmente expresada en nanómetros.' },
        { term: 'Intensidad', description: 'Medida relativa cuya escala depende del experimento y de la fuente.' },
        { term: 'UV, visible, IR', description: 'Regiones del espectro electromagnético; el ojo solo detecta una fracción estrecha.' }
      ],
      links: [{ label: 'NIST · Atomic Spectra Database', url: 'https://physics.nist.gov/PhysRefData/ASD/' }]
    },
    {
      id: 'niveles',
      label: '14 · Niveles de energía',
      title: 'Niveles, términos y transiciones',
      paragraphs: [
        'Los niveles de energía son estados permitidos del sistema electrónico. NIST publica configuraciones, términos espectroscópicos, valores J, energías e incertidumbres evaluadas.',
        'Una línea espectral conecta un nivel inferior con uno superior. No todas las transiciones son igual de probables: las reglas de selección y las probabilidades de transición determinan qué líneas son intensas, débiles o prácticamente prohibidas.'
      ],
      rows: [
        { term: 'cm⁻¹', description: 'Número de onda, unidad muy utilizada en espectroscopia.' },
        { term: 'J', description: 'Momento angular total del estado.' },
        { term: 'Término', description: 'Notación que resume propiedades angulares y de espín del estado.' }
      ],
      links: [{ label: 'NIST ASD · Levels', url: 'https://physics.nist.gov/PhysRefData/ASD/levels_form.html' }]
    },
    {
      id: 'quimica',
      label: '15 · Química y materiales',
      title: 'Estados de oxidación, compuestos y materiales',
      paragraphs: [
        'Los estados de oxidación son una contabilidad formal de electrones en compuestos. Ayudan a organizar reacciones redox y tendencias de enlace, pero no representan siempre cargas físicas localizadas.',
        'Las pestañas de química y materiales reúnen propiedades del elemento, compuestos relevantes, comportamiento termodinámico y datos computacionales. La ausencia de una fila no implica que la propiedad sea desconocida: puede significar que el CSV todavía no la incluye.'
      ],
      rows: [
        { term: 'Estado de oxidación', description: 'Carga formal asignada según reglas de contabilidad química.' },
        { term: 'Compuesto', description: 'Sustancia formada por dos o más elementos en proporciones definidas.' },
        { term: 'Material', description: 'Forma o aplicación macroscópica cuyas propiedades dependen de estructura y procesado.' }
      ]
    },
    {
      id: 'contexto',
      label: '16 · Contexto e historia',
      title: 'Historia, geología, biología, seguridad e industria',
      paragraphs: [
        'Un elemento no se entiende solo mediante cifras atómicas. Su historia de descubrimiento, presencia geológica, papel biológico, toxicidad, impacto ambiental y uso industrial aportan el contexto necesario para interpretar su importancia.',
        'Estas secciones pueden combinar descripciones cualitativas con datos cuantitativos. Deben leerse junto a la fuente y la fecha, especialmente en apartados de seguridad, regulación, producción y economía.'
      ],
      rows: [
        { term: 'Geoquímica', description: 'Distribución y comportamiento del elemento en minerales, rocas y reservorios terrestres.' },
        { term: 'Biología', description: 'Esencialidad, metabolismo, aplicaciones médicas o toxicidad.' },
        { term: 'Industria', description: 'Producción, usos, materiales estratégicos y cadenas de suministro.' }
      ]
    },
    {
      id: 'navegacion',
      label: '17 · Navegación y zoom',
      title: 'Cómo explorar la tabla',
      paragraphs: [
        'La rueda amplía o reduce tomando como ancla la posición del cursor. Arrastrar desplaza la tabla incluso si el gesto comienza encima de una casilla. Un clic limpio abre la ficha maestra.',
        'El indicador de zoom también funciona como restablecimiento: al pulsarlo, la tabla vuelve a encajarse completa. El botón 18/32 alterna entre la forma abreviada y la forma larga con el bloque f integrado.'
      ],
      rows: [
        { term: 'Vista general', description: 'Número atómico, símbolo y nombre.' },
        { term: 'Datos intermedios', description: 'Añade propiedades esenciales sin saturar el conjunto.' },
        { term: 'Ficha ampliada', description: 'Expone estructura electrónica y propiedades físicas relevantes.' },
        { term: 'Inspección', description: 'Convierte la casilla en una ficha científica resumida.' }
      ],
      callout: 'Alt + clic sobre el icono de información abre el diagnóstico interno del proyecto en lugar de esta guía.'
    },
    {
      id: 'fuentes',
      label: '18 · Fuentes y límites',
      title: 'Procedencia, unidades y límites del dataset',
      paragraphs: [
        'La aplicación consolida datos locales procedentes de fuentes especializadas. PubChem aporta propiedades generales; CIAAW evalúa pesos atómicos; NIST aporta líneas y niveles espectroscópicos; IAEA aporta datos nucleares.',
        'Dos fuentes pueden usar condiciones, convenciones o redondeos distintos. Antes de comparar valores debe comprobarse la unidad, la definición, el estado físico y la fecha de consulta. La pestaña Fuentes de cada elemento conserva la procedencia y el diagnóstico de los archivos.'
      ],
      rows: [
        { term: 'PubChem', description: 'Identidad y propiedades químicas y físicas generales.' },
        { term: 'CIAAW', description: 'Pesos atómicos estándar y composiciones isotópicas.' },
        { term: 'NIST ASD', description: 'Espectros, líneas, niveles y energías de ionización.' },
        { term: 'IAEA LiveChart', description: 'Estados fundamentales, vidas medias y desintegraciones nucleares.' }
      ],
      links: [
        { label: 'PubChem', url: 'https://pubchem.ncbi.nlm.nih.gov/periodic-table/' },
        { label: 'CIAAW', url: 'https://ciaaw.org/atomic-weights.htm' },
        { label: 'NIST ASD', url: 'https://physics.nist.gov/PhysRefData/ASD/' },
        { label: 'IAEA LiveChart', url: 'https://www-nds.iaea.org/relnsd/vcharthtml/VChartHTML.html' }
      ]
    }
  ];

  $: activeTopic = topics.find((topic) => topic.id === activeId) ?? topics[0];

  function selectTopic(id: string): void {
    activeId = id;
    scrollElement?.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function closeFromBackdrop(event: MouseEvent): void {
    if (event.currentTarget === event.target) dispatch('close');
  }

  onMount(() => {
    const handleKey = (event: KeyboardEvent): void => {
      if (open && event.key === 'Escape') dispatch('close');
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  });
</script>

{#if open}
  <div class="periodic-guide-backdrop" role="presentation" on:click={closeFromBackdrop}>
    <article class="periodic-guide" role="dialog" aria-modal="true" aria-label="Guía completa de la tabla periódica">
      <header class="periodic-guide-head">
        <div>
          <p>Guía científica</p>
          <h2>Tabla periódica de los elementos</h2>
          <small>Conceptos, propiedades, espectros, isótopos, navegación y fuentes.</small>
        </div>
        <button type="button" aria-label="Cerrar guía" title="Cerrar" on:click={() => dispatch('close')}>
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 5l14 14M19 5 5 19"></path></svg>
        </button>
      </header>

      <nav class="periodic-guide-tabs" aria-label="Temas de la guía">
        {#each topics as topic}
          <button class:active={activeId === topic.id} type="button" on:click={() => selectTopic(topic.id)}>{topic.label}</button>
        {/each}
      </nav>

      <div bind:this={scrollElement} class="periodic-guide-scroll" tabindex="0">
        <section class="periodic-guide-section">
          <h3>{activeTopic.title}</h3>
          {#each activeTopic.paragraphs as paragraph}<p>{paragraph}</p>{/each}

          {#if activeTopic.rows?.length}
            <div class="periodic-guide-table">
              {#each activeTopic.rows as row}
                <div><b>{row.term}</b><span>{row.description}</span></div>
              {/each}
            </div>
          {/if}

          {#if activeTopic.callout}<div class="periodic-guide-callout">{activeTopic.callout}</div>{/if}

          {#if activeTopic.links?.length}
            <div class="periodic-guide-links">
              <span>Fuentes y ampliación:</span>
              {#each activeTopic.links as link}<a href={link.url} target="_blank" rel="noreferrer">{link.label}</a>{/each}
            </div>
          {/if}
        </section>
      </div>
    </article>
  </div>
{/if}
