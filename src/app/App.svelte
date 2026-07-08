<script lang="ts">
  import CompareElements from '../components/CompareElements.svelte';
  import ElementModal from '../components/ElementModal.svelte';
  import PeriodicGrid from '../components/PeriodicGrid.svelte';
  import type { ElementWithLines, SpectraDataset } from '../lib/atomicTypes';
  import { loadSpectraDataset, hydrateElements } from '../lib/dataLoader';

  let dataset: SpectraDataset | null = null;
  let elements: ElementWithLines[] = [];
  let selectedSymbol = '';
  let modalElement: ElementWithLines | null = null;
  let comparedSymbols: string[] = ['H', 'Na', 'Hg', 'O'];
  let loading = true;
  let errorMessage = '';

  $: comparedElements = comparedSymbols
    .map((symbol) => elements.find((element) => element.symbol === symbol))
    .filter((element): element is ElementWithLines => Boolean(element));

  async function init(): Promise<void> {
    try {
      dataset = await loadSpectraDataset();
      elements = hydrateElements(dataset);
      selectedSymbol = elements[0]?.symbol ?? '';
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : 'Error desconocido al cargar datos locales.';
    } finally {
      loading = false;
    }
  }

  function openElement(symbol: string): void {
    selectedSymbol = symbol;
    modalElement = elements.find((element) => element.symbol === symbol) ?? null;
  }

  function closeModal(): void {
    modalElement = null;
  }

  function toggleCompared(symbol: string): void {
    if (comparedSymbols.includes(symbol)) {
      comparedSymbols = comparedSymbols.filter((item) => item !== symbol);
      return;
    }

    comparedSymbols = [...comparedSymbols, symbol];
  }

  init();
</script>

<svelte:head>
  <title>Espectros Atómicos · V1.1</title>
</svelte:head>

<main class="app-shell">
  {#if loading}
    <section class="state-card">
      <h2>Cargando dataset local…</h2>
      <p>La aplicación está leyendo el JSON publicado en <code>public/data/</code>.</p>
    </section>
  {:else if errorMessage}
    <section class="state-card error">
      <h2>No se pudo iniciar la aplicación</h2>
      <p>{errorMessage}</p>
    </section>
  {:else}
    <header class="compact-header">
      <div>
        <strong>Espectros Atómicos</strong>
        <span>{elements.length} elementos de muestra · {dataset?.metadata.dataset}</span>
      </div>
      <p>Tabla periódica como punto de entrada. Pulsa un elemento para abrir su ficha espectral.</p>
    </header>

    <section class="main-grid">
      <PeriodicGrid
        {elements}
        {selectedSymbol}
        {comparedSymbols}
        on:select={(event) => openElement(event.detail)}
        on:compare={(event) => toggleCompared(event.detail)}
      />

      <CompareElements selected={comparedElements} />
    </section>

    <ElementModal
      element={modalElement}
      {comparedSymbols}
      on:close={closeModal}
      on:compare={(event) => toggleCompared(event.detail)}
    />
  {/if}
</main>
