<script lang="ts">
  import * as d3 from 'd3';
  import type { ElementWithLines, SpectralLine } from '../lib/atomicTypes';
  import { formatNm } from '../lib/wavelengthColor';

  export let selected: ElementWithLines[] = [];

  const x = d3.scaleLinear().domain([320, 780]).range([0, 100]);

  $: mergedLines = selected.flatMap((element) =>
    element.lines.map((line) => ({
      ...line,
      ownerSymbol: element.symbol,
      ownerName: element.name_es
    }))
  );

  function lineLeft(wavelength: number): number {
    return x(wavelength);
  }

  function lineTitle(line: SpectralLine & { ownerSymbol?: string; ownerName?: string }): string {
    const owner = line.ownerSymbol ? `${line.ownerSymbol} · ` : '';
    return `${owner}${line.label}: ${formatNm(line.wavelength_nm)}`;
  }
</script>

<section class="compare-card">
  <div class="compare-grip" aria-hidden="true"></div>

  <div class="compare-stack">
    {#each selected as element}
      <article>
        <header>
          <strong>{element.symbol}</strong>
          <span>{element.name_es}</span>
        </header>
        <div class="mini-spectrum">
          {#each element.lines as line}
            <span
              style={`
                left:${lineLeft(line.wavelength_nm)}%;
                opacity:${0.28 + line.intensity * 0.72};
                --line-color:${line.approximate_color};
              `}
              title={lineTitle(line)}
            ></span>
          {/each}
        </div>
      </article>
    {/each}

    {#if selected.length > 1}
      <article class="fusion-row">
        <header>
          <strong>Σ</strong>
          <span>Fusión</span>
        </header>
        <div class="mini-spectrum fusion-spectrum">
          {#each mergedLines as line}
            <span
              style={`
                left:${lineLeft(line.wavelength_nm)}%;
                opacity:${0.22 + line.intensity * 0.68};
                --line-color:${line.approximate_color};
              `}
              title={lineTitle(line)}
            ></span>
          {/each}
        </div>
      </article>
    {/if}
  </div>
</section>
