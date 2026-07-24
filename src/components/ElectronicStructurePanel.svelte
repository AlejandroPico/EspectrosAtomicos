<script lang="ts">
  import type { DataRow, ElementDataPayload, ElementWithLines } from '../lib/atomicTypes';

  export let element: ElementWithLines | null = null;
  export let elementData: ElementDataPayload | null = null;
  export let loading = false;

  const ORBITAL_RE = /(\d+)([spdf])(?:\^?([0-9]+))?/gi;

  function atomicRows(): DataRow[] {
    return elementData?.domains.atomic?.rows ?? [];
  }

  function chemicalRows(): DataRow[] {
    return elementData?.domains.chemical?.rows ?? [];
  }

  function value(property: string, fallback = '—'): string {
    const row = atomicRows().find((item) => item.property === property)
      ?? chemicalRows().find((item) => item.property === property);
    if (!row?.value) return fallback;
    return `${row.value}${row.unit ? ` ${row.unit}` : ''}`;
  }

  function ionizationRows(): Array<{ stage: number; value: number; unit: string; quality: string }> {
    const rows = atomicRows().flatMap((row) => {
      const match = row.property?.match(/^ionization_energy_(\d+)$/);
      if (!match) return [];
      const parsed = Number.parseFloat(String(row.value).replace(/[\[\]()]/g, '').replace(',', '.'));
      if (!Number.isFinite(parsed)) return [];
      return [{ stage: Number(match[1]), value: parsed, unit: row.unit || 'eV', quality: row.notes || '' }];
    });

    if (!rows.length) {
      const first = atomicRows().find((row) => ['ionization_energy', 'first_ionization_energy'].includes(row.property));
      const parsed = Number.parseFloat(String(first?.value ?? '').replace(',', '.'));
      if (Number.isFinite(parsed)) rows.push({ stage: 1, value: parsed, unit: first?.unit || 'eV', quality: first?.notes || '' });
    }

    return rows.sort((a, b) => a.stage - b.stage);
  }

  function shellOccupancy(configuration: string): number[] {
    const shells = new Map<number, number>();
    for (const match of configuration.matchAll(ORBITAL_RE)) {
      const n = Number(match[1]);
      const count = Number(match[3] || 1);
      shells.set(n, (shells.get(n) ?? 0) + count);
    }
    return Array.from({ length: Math.max(0, ...shells.keys()) }, (_, index) => shells.get(index + 1) ?? 0);
  }

  function chartPoints(rows: Array<{ stage: number; value: number }>): string {
    if (!rows.length) return '';
    const max = Math.max(...rows.map((row) => row.value), 1);
    const width = 720;
    const height = 250;
    return rows.map((row, index) => {
      const x = rows.length === 1 ? width / 2 : 24 + index * ((width - 48) / (rows.length - 1));
      const y = height - 24 - (row.value / max) * (height - 48);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
  }

  $: configuration = value('electron_configuration', '');
  $: shells = shellOccupancy(configuration);
  $: ionizations = ionizationRows();
  $: points = chartPoints(ionizations);
  $: maxIonization = Math.max(...ionizations.map((row) => row.value), 1);
</script>

<div class="advanced-science-pane electronic-structure-pane">
  {#if loading}
    <div class="modal-load-state"><span></span><p>Cargando estructura electrónica…</p></div>
  {:else}
    <section class="science-hero electronic-hero">
      <div>
        <p>Estructura electrónica</p>
        <h3>Valencia, configuración e ionización</h3>
        <small>La valencia, los electrones de valencia y el estado de oxidación se presentan como conceptos distintos.</small>
      </div>
      <div class="electron-shell-badge" aria-label={`Distribución por capas: ${shells.join(', ') || 'sin datos'}`}>
        <strong>{element?.symbol}</strong>
        {#each shells as count, index}
          <span style={`--shell-index:${index + 1};--shell-total:${shells.length};`}><i>{count}</i></span>
        {/each}
      </div>
    </section>

    <section class="science-card-grid">
      <article><small>Configuración</small><strong>{configuration || '—'}</strong></article>
      <article><small>Configuración abreviada</small><strong>{value('electron_configuration_abbreviated')}</strong></article>
      <article><small>Configuración de valencia</small><strong>{value('valence_shell_configuration')}</strong></article>
      <article><small>Electrones de la capa exterior</small><strong>{value('outer_shell_electron_count')}</strong></article>
      <article><small>Electrones de valencia</small><strong>{value('valence_electron_count')}</strong></article>
      <article><small>Valencias comunes</small><strong>{value('common_valences')}</strong></article>
      <article><small>Estados de oxidación</small><strong>{value('oxidation_states')}</strong></article>
      <article><small>Término fundamental</small><strong>{value('ground_state_term')}</strong></article>
    </section>

    <section class="science-visual-card ionization-card">
      <header>
        <div><small>Energía acumulativa por extracción</small><h3>Ionizaciones sucesivas</h3></div>
        <span>{ionizations.length} etapas disponibles</span>
      </header>

      {#if ionizations.length}
        <div class="ionization-chart-wrap">
          <svg class="ionization-chart" viewBox="0 0 720 250" role="img" aria-label="Gráfico de energías de ionización sucesivas">
            <g class="chart-grid">
              {#each [0.25, 0.5, 0.75, 1] as fraction}
                <line x1="24" x2="696" y1={226 - fraction * 202} y2={226 - fraction * 202}></line>
                <text x="20" y={230 - fraction * 202} text-anchor="end">{(maxIonization * fraction).toFixed(0)}</text>
              {/each}
            </g>
            <polyline points={points}></polyline>
            {#each ionizations as row, index}
              {@const x = ionizations.length === 1 ? 360 : 24 + index * (672 / (ionizations.length - 1))}
              {@const y = 226 - (row.value / maxIonization) * 202}
              <circle cx={x} cy={y} r="5"><title>{`${row.stage}.ª: ${row.value} ${row.unit}`}</title></circle>
              <text class="stage-label" x={x} y="244" text-anchor="middle">{row.stage}</text>
            {/each}
          </svg>
        </div>
        <div class="ionization-table">
          {#each ionizations as row}
            <div><span>{row.stage}.ª ionización</span><strong>{row.value.toLocaleString('es-ES')} {row.unit}</strong></div>
          {/each}
        </div>
      {:else}
        <div class="science-empty-state"><strong>Sin serie sucesiva todavía</strong><p>El importador conserva la primera ionización disponible y puede descargar la serie completa de NIST ASD.</p></div>
      {/if}
    </section>

    <p class="science-method-note">Los valores derivados indican su método en el CSV del elemento. Para metales de transición y bloque f, “electrones de valencia” depende del criterio químico y no debe interpretarse como una constante única.</p>
  {/if}
</div>
