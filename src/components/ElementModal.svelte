<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import ElementPanel from './ElementPanel.svelte';
  import EnergyLevels from './EnergyLevels.svelte';
  import SpectrumViewer from './SpectrumViewer.svelte';
  import type { ElementWithLines, NistFileStatus, SpectralLine, SpectrumMode } from '../lib/atomicTypes';
  import { formatEv, formatNm, wavelengthRegion } from '../lib/wavelengthColor';

  type TabId = 'wavelengths' | 'levels' | 'element' | 'lines' | 'nist';

  export let element: ElementWithLines | null = null;
  export let comparedSymbols: string[] = [];

  let activeTab: TabId = 'wavelengths';
  let mode: SpectrumMode = 'emission';
  let lastSymbol = '';

  const dispatch = createEventDispatcher<{
    close: void;
    compare: string;
  }>();

  $: if (element && element.symbol !== lastSymbol) {
    activeTab = 'wavelengths';
    mode = 'emission';
    lastSymbol = element.symbol;
  }

  $: isCompared = element ? comparedSymbols.includes(element.symbol) : false;
  $: nistFiles = element?.nist
    ? [
        { label: 'Espectro / líneas', item: element.nist.espectro },
        { label: 'Niveles de energía', item: element.nist.niveles }
      ]
    : [];

  function closeOnBackdrop(event: MouseEvent): void {
    if (event.currentTarget === event.target) {
      dispatch('close');
    }
  }

  function energyJump(line: SpectralLine): number {
    return line.upper_level_ev - line.lower_level_ev;
  }

  function statusLabel(file: NistFileStatus): string {
    if (!file.present) {
      return 'No encontrado';
    }

    if (file.table_like) {
      return 'CSV tabular';
    }

    if (file.status === 'invalid_single_column_script') {
      return 'No tabular: contiene JavaScript';
    }

    if (file.status === 'invalid_html_export') {
      return 'No tabular: parece HTML';
    }

    return file.status;
  }
</script>

{#if element}
  <div class="modal-backdrop" role="presentation" on:click={closeOnBackdrop}>
    <section class="element-modal" aria-modal="true" role="dialog" aria-label={`Ficha espectral de ${element.name_es}`}>
      <header class="modal-header">
        <div class="modal-identity">
          <div class="modal-symbol">
            <span>{element.atomic_number}</span>
            <strong>{element.symbol}</strong>
          </div>
          <div>
            <p class="eyebrow">{element.category}</p>
            <h2>{element.name_es}</h2>
            <small>{element.name_en} · Grupo {element.group} · Periodo {element.period}</small>
          </div>
        </div>

        <div class="modal-actions">
          <button class:active={isCompared} type="button" on:click={() => dispatch('compare', element.symbol)}>
            {isCompared ? 'En comparador' : 'Añadir al comparador'}
          </button>
          <button class="close-button" type="button" on:click={() => dispatch('close')} aria-label="Cerrar ficha">
            ×
          </button>
        </div>
      </header>

      <nav class="modal-tabs" aria-label="Pestañas de la ficha">
        <button class:active={activeTab === 'wavelengths'} type="button" on:click={() => (activeTab = 'wavelengths')}>
          Longitudes de onda
        </button>
        <button class:active={activeTab === 'levels'} type="button" on:click={() => (activeTab = 'levels')}>
          Niveles de energía
        </button>
        <button class:active={activeTab === 'nist'} type="button" on:click={() => (activeTab = 'nist')}>
          NIST
        </button>
        <button class:active={activeTab === 'element'} type="button" on:click={() => (activeTab = 'element')}>
          Elemento
        </button>
        <button class:active={activeTab === 'lines'} type="button" on:click={() => (activeTab = 'lines')}>
          Datos de líneas
        </button>
      </nav>

      <div class="modal-content">
        {#if activeTab === 'wavelengths'}
          <div class="mode-row">
            <div>
              <p class="eyebrow">Modo de visualización</p>
              <h3>Emisión / absorción</h3>
            </div>
            <div class="segmented-control small">
              <button class:active={mode === 'emission'} type="button" on:click={() => (mode = 'emission')}>Emisión</button>
              <button class:active={mode === 'absorption'} type="button" on:click={() => (mode = 'absorption')}>Absorción</button>
            </div>
          </div>

          <SpectrumViewer lines={element.lines} {mode} title={`${element.name_es} (${element.symbol})`} />
        {:else if activeTab === 'levels'}
          <EnergyLevels lines={element.lines} />
        {:else if activeTab === 'nist'}
          <section class="modal-data-card nist-panel">
            <div class="section-title-row compact">
              <div>
                <p class="eyebrow">Datos importados</p>
                <h2>Estado NIST provisional</h2>
              </div>
              <span class="range-pill">{element.nist?.imported_line_count ?? 0} líneas importadas</span>
            </div>

            <p class="empty-copy">
              Esta pestaña es provisional. Sirve para comprobar qué archivos CSV existen para el elemento y si el
              generador los reconoce como tablas científicas limpias.
            </p>

            {#if element.nist}
              <div class="nist-status-grid">
                {#each nistFiles as file}
                  <article class:problem={file.item.present && !file.item.table_like} class="nist-status-card">
                    <header>
                      <strong>{file.label}</strong>
                      <span>{statusLabel(file.item)}</span>
                    </header>

                    <dl>
                      <div>
                        <dt>Archivo</dt>
                        <dd>{file.item.file}</dd>
                      </div>
                      <div>
                        <dt>Ruta</dt>
                        <dd>{file.item.path || '—'}</dd>
                      </div>
                      <div>
                        <dt>Filas detectadas</dt>
                        <dd>{file.item.row_count}</dd>
                      </div>
                      <div>
                        <dt>Columnas</dt>
                        <dd>{file.item.columns.length ? file.item.columns.slice(0, 8).join(', ') : '—'}</dd>
                      </div>
                    </dl>

                    <p>{file.item.notes}</p>
                    {#if file.item.preview}
                      <pre>{file.item.preview}</pre>
                    {/if}
                  </article>
                {/each}
              </div>
            {:else}
              <p class="empty-copy">No hay información NIST asociada a este elemento.</p>
            {/if}
          </section>
        {:else if activeTab === 'element'}
          <ElementPanel {element} />
        {:else if activeTab === 'lines'}
          <section class="modal-data-card">
            <div class="section-title-row compact">
              <div>
                <p class="eyebrow">Tabla técnica</p>
                <h2>Líneas espectrales</h2>
              </div>
              <span class="range-pill">{element.lines.length} líneas</span>
            </div>

            <div class="technical-table modal-table">
              <table>
                <thead>
                  <tr>
                    <th>Línea</th>
                    <th>Especie</th>
                    <th>λ</th>
                    <th>Región</th>
                    <th>Intensidad</th>
                    <th>Nivel inferior</th>
                    <th>Nivel superior</th>
                    <th>ΔE</th>
                    <th>Transición</th>
                  </tr>
                </thead>
                <tbody>
                  {#each element.lines as line}
                    <tr>
                      <td>{line.label}</td>
                      <td>{line.species}</td>
                      <td>{formatNm(line.wavelength_nm)}</td>
                      <td>{wavelengthRegion(line.wavelength_nm)}</td>
                      <td>{line.intensity.toFixed(2)}</td>
                      <td>{formatEv(line.lower_level_ev)}</td>
                      <td>{formatEv(line.upper_level_ev)}</td>
                      <td>{formatEv(energyJump(line))}</td>
                      <td>{line.transition}</td>
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
          </section>
        {/if}
      </div>
    </section>
  </div>
{/if}
