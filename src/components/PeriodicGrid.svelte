<script lang="ts">
  import { createEventDispatcher, onMount, tick } from 'svelte';
  import type { ElementWithLines } from '../lib/atomicTypes';

  type TableLayout = 'short' | 'opening' | 'long';
  type LayoutAnimationStage = 'spread' | 'series-in' | 'series-out' | 'collapse';

  interface RectSnapshot {
    left: number;
    top: number;
    width: number;
    height: number;
  }

  interface GridPosition {
    column: number;
    row: number;
  }

  export let elements: ElementWithLines[] = [];
  export let selectedSymbol = '';
  export let layoutMode: TableLayout = 'short';

  const MIN_ZOOM = 0.18;
  const MAX_ZOOM = 14;
  const DRAG_THRESHOLD_PX = 5;
  const CAMERA_TAU_MS = 82;

  let viewportElement: HTMLDivElement;
  let panElement: HTMLDivElement;
  let gridElement: HTMLDivElement;

  let zoom = 1;
  let targetZoom = 1;
  let offsetX = 0;
  let offsetY = 0;
  let targetOffsetX = 0;
  let targetOffsetY = 0;
  let committedZoom = 1;

  let cameraFrame = 0;
  let lastFrameTime = 0;
  let cameraResolvers: Array<() => void> = [];

  let isPointerDown = false;
  let dragActivated = false;
  let activePointerId = -1;
  let dragStartX = 0;
  let dragStartY = 0;
  let dragOriginX = 0;
  let dragOriginY = 0;
  let suppressClickUntil = 0;

  $: zoomClass =
    committedZoom >= 7.5
      ? 'zoom-inspect'
      : committedZoom >= 3.2
        ? 'zoom-deep'
        : committedZoom >= 1.6
          ? 'zoom-medium'
          : 'zoom-base';

  const dispatch = createEventDispatcher<{
    select: string;
    zoomchange: { zoom: number; percent: number; level: string };
  }>();

  function clamp(value: number, min: number, max: number): number {
    return Math.min(max, Math.max(min, value));
  }

  function categoryClass(category: string): string {
    const normalized = category
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .trim();

    const classes: Record<string, string> = {
      'no metal': 'no-metal',
      'gas noble': 'gas-noble',
      'metal alcalino': 'metal-alcalino',
      'metal alcalinoterreo': 'metal-alcalinoterreo',
      'metal de transicion': 'metal-transicion',
      metaloide: 'metaloide',
      halogeno: 'halogeno',
      'metal post-transicion': 'metal-post-transicion',
      lantanido: 'lantanido',
      actinido: 'actinido',
      desconocido: 'desconocido'
    };

    return classes[normalized] ?? normalized.replace(/\s+/g, '-');
  }

  function zoomLabel(value = zoom): string {
    if (value >= 7.5) return 'Inspección';
    if (value >= 3.2) return 'Ficha ampliada';
    if (value >= 1.6) return 'Datos intermedios';
    return 'Vista general';
  }

  function publishZoom(): void {
    dispatch('zoomchange', {
      zoom,
      percent: Math.round(zoom * 100),
      level: zoomLabel()
    });
  }

  function updateCommittedDetailLevel(): void {
    committedZoom = zoom;
    gridElement?.style.setProperty('--zoom', committedZoom.toFixed(4));
    gridElement?.style.setProperty(
      '--content-scale',
      Math.pow(Math.max(committedZoom, 1), 0.36).toFixed(4)
    );
  }

  function applyCamera(): void {
    if (!panElement) return;
    panElement.style.transform =
      `translate3d(calc(-50% + ${offsetX.toFixed(2)}px), ` +
      `calc(-50% + ${offsetY.toFixed(2)}px), 0) ` +
      `scale3d(${zoom.toFixed(5)}, ${zoom.toFixed(5)}, 1)`;
  }

  function resolveCameraPromises(): void {
    const resolvers = cameraResolvers;
    cameraResolvers = [];
    resolvers.forEach((resolve) => resolve());
  }

  function waitForCamera(): Promise<void> {
    if (!cameraFrame) return Promise.resolve();
    return new Promise((resolve) => cameraResolvers.push(resolve));
  }

  function stopCamera(): void {
    if (cameraFrame) cancelAnimationFrame(cameraFrame);
    cameraFrame = 0;
    lastFrameTime = 0;
    viewportElement?.classList.remove('camera-moving');
    resolveCameraPromises();
  }

  function cameraStep(timestamp: number): void {
    if (!lastFrameTime) lastFrameTime = timestamp;
    const delta = Math.min(40, Math.max(1, timestamp - lastFrameTime));
    lastFrameTime = timestamp;
    const alpha = 1 - Math.exp(-delta / CAMERA_TAU_MS);

    zoom += (targetZoom - zoom) * alpha;
    offsetX += (targetOffsetX - offsetX) * alpha;
    offsetY += (targetOffsetY - offsetY) * alpha;
    applyCamera();

    const settled =
      Math.abs(targetZoom - zoom) < Math.max(0.0005, targetZoom * 0.00035) &&
      Math.abs(targetOffsetX - offsetX) < 0.08 &&
      Math.abs(targetOffsetY - offsetY) < 0.08;

    if (settled) {
      zoom = targetZoom;
      offsetX = targetOffsetX;
      offsetY = targetOffsetY;
      applyCamera();
      updateCommittedDetailLevel();
      publishZoom();
      cameraFrame = 0;
      lastFrameTime = 0;
      viewportElement?.classList.remove('camera-moving');
      resolveCameraPromises();
      return;
    }

    publishZoom();
    cameraFrame = requestAnimationFrame(cameraStep);
  }

  function ensureCamera(): void {
    if (cameraFrame) return;
    viewportElement?.classList.add('camera-moving');
    lastFrameTime = 0;
    cameraFrame = requestAnimationFrame(cameraStep);
  }

  function setCameraTarget(nextZoom: number, anchorX = 0, anchorY = 0): void {
    const clamped = clamp(nextZoom, MIN_ZOOM, MAX_ZOOM);
    const previous = targetZoom;
    if (Math.abs(clamped - previous) < 0.00001) return;

    const ratio = clamped / previous;
    targetOffsetX = anchorX - (anchorX - targetOffsetX) * ratio;
    targetOffsetY = anchorY - (anchorY - targetOffsetY) * ratio;
    targetZoom = clamped;
    ensureCamera();
  }

  function setCameraImmediate(nextZoom: number, nextX = 0, nextY = 0): void {
    stopCamera();
    zoom = clamp(nextZoom, MIN_ZOOM, MAX_ZOOM);
    targetZoom = zoom;
    offsetX = nextX;
    offsetY = nextY;
    targetOffsetX = nextX;
    targetOffsetY = nextY;
    applyCamera();
    updateCommittedDetailLevel();
    publishZoom();
  }

  function normalizedWheelDelta(event: WheelEvent): number {
    if (event.deltaMode === WheelEvent.DOM_DELTA_LINE) return event.deltaY * 16;
    if (event.deltaMode === WheelEvent.DOM_DELTA_PAGE) return event.deltaY * innerHeight;
    return event.deltaY;
  }

  function handleWheel(event: WheelEvent): void {
    event.preventDefault();
    const rect = viewportElement.getBoundingClientRect();
    const anchorX = event.clientX - rect.left - rect.width / 2;
    const anchorY = event.clientY - rect.top - rect.height / 2;
    const factor = clamp(Math.exp(-normalizedWheelDelta(event) * 0.00125), 0.82, 1.22);
    setCameraTarget(targetZoom * factor, anchorX, anchorY);
  }

  function startDrag(event: PointerEvent): void {
    if (event.pointerType === 'mouse' && event.button !== 0) return;

    stopCamera();
    isPointerDown = true;
    dragActivated = false;
    activePointerId = event.pointerId;
    dragStartX = event.clientX;
    dragStartY = event.clientY;
    dragOriginX = offsetX;
    dragOriginY = offsetY;
    viewportElement.setPointerCapture(event.pointerId);
  }

  function dragCanvas(event: PointerEvent): void {
    if (!isPointerDown || event.pointerId !== activePointerId) return;

    const deltaX = event.clientX - dragStartX;
    const deltaY = event.clientY - dragStartY;

    if (!dragActivated && Math.hypot(deltaX, deltaY) < DRAG_THRESHOLD_PX) return;

    if (!dragActivated) {
      dragActivated = true;
      viewportElement.classList.add('dragging');
    }

    event.preventDefault();
    offsetX = dragOriginX + deltaX;
    offsetY = dragOriginY + deltaY;
    targetOffsetX = offsetX;
    targetOffsetY = offsetY;
    applyCamera();
  }

  function finishDrag(event: PointerEvent): void {
    if (!isPointerDown || event.pointerId !== activePointerId) return;

    if (dragActivated) suppressClickUntil = performance.now() + 500;
    if (viewportElement.hasPointerCapture(event.pointerId)) {
      viewportElement.releasePointerCapture(event.pointerId);
    }

    viewportElement.classList.remove('dragging');
    isPointerDown = false;
    dragActivated = false;
    activePointerId = -1;
  }

  function cancelDrag(event: PointerEvent): void {
    if (event.pointerId !== activePointerId) return;
    suppressClickUntil = performance.now() + 500;
    finishDrag(event);
  }

  function openFromClick(event: MouseEvent, symbol: string): void {
    if (performance.now() < suppressClickUntil) {
      event.preventDefault();
      event.stopPropagation();
      return;
    }
    dispatch('select', symbol);
  }

  function handleDoubleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (target.closest('[data-element-symbol]')) return;
    resetView();
  }

  function shortPosition(element: ElementWithLines): GridPosition {
    const z = element.atomic_number;
    if (z >= 57 && z <= 71) return { column: z - 54, row: 8 };
    if (z >= 89 && z <= 103) return { column: z - 86, row: 9 };
    return { column: Math.max(1, element.group), row: element.period };
  }

  function openingPosition(element: ElementWithLines): GridPosition {
    const z = element.atomic_number;
    if (z >= 57 && z <= 71) return { column: z - 54, row: 8 };
    if (z >= 89 && z <= 103) return { column: z - 86, row: 9 };
    const group = Math.max(1, element.group);
    return { column: group <= 2 ? group : group + 14, row: element.period };
  }

  function longPosition(element: ElementWithLines): GridPosition {
    const z = element.atomic_number;
    if (z >= 57 && z <= 71) return { column: z - 54, row: 6 };
    if (z >= 89 && z <= 103) return { column: z - 86, row: 7 };
    const group = Math.max(1, element.group);
    return { column: group <= 2 ? group : group + 14, row: element.period };
  }

  function positionFor(element: ElementWithLines): GridPosition {
    if (layoutMode === 'long') return longPosition(element);
    if (layoutMode === 'opening') return openingPosition(element);
    return shortPosition(element);
  }

  function fitScale(): number {
    if (!viewportElement || !gridElement) return 1;
    const availableWidth = Math.max(240, viewportElement.clientWidth - 56);
    const availableHeight = Math.max(220, viewportElement.clientHeight - 56);
    const width = Math.max(1, gridElement.offsetWidth);
    const height = Math.max(1, gridElement.offsetHeight);
    return clamp(Math.min(availableWidth / width, availableHeight / height, 1) * 0.97, MIN_ZOOM, 1);
  }

  export async function fitToViewport(animated = true): Promise<void> {
    await tick();
    const nextZoom = fitScale();
    targetOffsetX = 0;
    targetOffsetY = 0;

    if (!animated) {
      setCameraImmediate(nextZoom, 0, 0);
      return;
    }

    targetZoom = nextZoom;
    ensureCamera();
    await waitForCamera();
  }

  export function zoomIn(): void {
    setCameraTarget(targetZoom * 1.18);
  }

  export function zoomOut(): void {
    setCameraTarget(targetZoom / 1.18);
  }

  export function resetView(): void {
    void fitToViewport(true);
  }

  export function captureElementRects(): Record<string, RectSnapshot> {
    const snapshots: Record<string, RectSnapshot> = {};
    gridElement
      ?.querySelectorAll<HTMLElement>('[data-element-symbol]')
      .forEach((cell) => {
        const symbol = cell.dataset.elementSymbol;
        if (!symbol) return;
        const rect = cell.getBoundingClientRect();
        snapshots[symbol] = {
          left: rect.left,
          top: rect.top,
          width: rect.width,
          height: rect.height
        };
      });
    return snapshots;
  }

  export async function animateLayoutFrom(
    previous: Record<string, RectSnapshot>,
    stage: LayoutAnimationStage
  ): Promise<void> {
    if (!gridElement || matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const animations: Animation[] = [];
    viewportElement.classList.add('layout-animating');

    gridElement
      .querySelectorAll<HTMLElement>('[data-element-symbol]')
      .forEach((cell) => {
        const symbol = cell.dataset.elementSymbol;
        const before = symbol ? previous[symbol] : undefined;
        if (!before) return;

        const atomicNumber = Number(cell.dataset.atomicNumber ?? 0);
        const innerSeries =
          (atomicNumber >= 57 && atomicNumber <= 71) ||
          (atomicNumber >= 89 && atomicNumber <= 103);

        if ((stage === 'spread' || stage === 'collapse') && innerSeries) return;
        if ((stage === 'series-in' || stage === 'series-out') && !innerSeries) return;

        const after = cell.getBoundingClientRect();
        const deltaX = (before.left - after.left) / Math.max(zoom, 0.0001);
        const deltaY = (before.top - after.top) / Math.max(zoom, 0.0001);
        const deltaScaleX = before.width / Math.max(after.width, 0.0001);
        const deltaScaleY = before.height / Math.max(after.height, 0.0001);

        if (Math.hypot(deltaX, deltaY) < 0.5) return;

        const seriesIndex =
          atomicNumber >= 57 && atomicNumber <= 71
            ? atomicNumber - 57
            : atomicNumber >= 89 && atomicNumber <= 103
              ? atomicNumber - 89
              : 0;

        const animation = cell.animate(
          [
            {
              transform: `translate3d(${deltaX}px, ${deltaY}px, 0) scale(${deltaScaleX}, ${deltaScaleY})`,
              opacity: 0.88
            },
            { transform: 'translate3d(0, 0, 0) scale(1, 1)', opacity: 1 }
          ],
          {
            duration: innerSeries ? 820 : 680,
            delay: innerSeries ? Math.min(180, seriesIndex * 12) : 0,
            easing: 'cubic-bezier(0.22, 1, 0.36, 1)',
            fill: 'both'
          }
        );

        animations.push(animation);
      });

    await Promise.allSettled(animations.map((animation) => animation.finished));
    viewportElement.classList.remove('layout-animating');
  }

  onMount(() => {
    const observer = new ResizeObserver(() => {
      if (!isPointerDown) void fitToViewport(false);
    });
    observer.observe(viewportElement);

    requestAnimationFrame(() => {
      void fitToViewport(false);
    });

    return () => {
      observer.disconnect();
      stopCamera();
    };
  });
</script>

<div
  bind:this={viewportElement}
  class={`periodic-viewport ${zoomClass}`}
  role="application"
  aria-label="Tabla periódica interactiva. Arrastra para desplazarte y usa la rueda para ampliar."
  on:wheel={handleWheel}
  on:pointerdown={startDrag}
  on:pointermove={dragCanvas}
  on:pointerup={finishDrag}
  on:pointercancel={cancelDrag}
  on:dblclick={handleDoubleClick}
>
  <div bind:this={panElement} class="periodic-pan">
    <div bind:this={gridElement} class={`periodic-grid mode-${layoutMode}`}>
      {#if layoutMode !== 'long'}
        <div
          class="series-placeholder lanthanide-placeholder"
          style="grid-column:3;grid-row:6;"
          aria-hidden="true"
        >
          <span class="series-tree-mark"></span>
          <strong>57–71</strong>
          <span>La–Lu</span>
          <small>Fila inferior</small>
        </div>
        <div
          class="series-placeholder actinide-placeholder"
          style="grid-column:3;grid-row:7;"
          aria-hidden="true"
        >
          <span class="series-tree-mark"></span>
          <strong>89–103</strong>
          <span>Ac–Lr</span>
          <small>Fila inferior</small>
        </div>
      {/if}

      {#each elements as element (element.symbol)}
        {@const position = positionFor(element)}
        <article
          class={`element-cell ${categoryClass(element.category)}`}
          class:active={selectedSymbol === element.symbol}
          data-element-symbol={element.symbol}
          data-atomic-number={element.atomic_number}
          style={`grid-column:${position.column};grid-row:${position.row};`}
        >
          <button
            class="element-open-button"
            type="button"
            aria-label={`Abrir ficha de ${element.name_es}`}
            on:click={(event) => openFromClick(event, element.symbol)}
            on:dragstart|preventDefault
          >
            <div class="cell-topline">
              <span class="atomic-number">{element.atomic_number}</span>
              <span class="cell-data-state">{element.dataIndex?.available_file_count ?? 0}</span>
            </div>
            <div class="element-core"><strong>{element.symbol}</strong></div>
            <span class="element-name">{element.name_es}</span>
            <span class="element-detail detail-medium">Grupo {element.group || '—'} · Periodo {element.period}</span>
            <span class="element-detail detail-deep">{element.category} · {element.lines.length} líneas</span>
            <span class="element-detail detail-inspect">{element.summary}</span>
          </button>
        </article>
      {/each}
    </div>
  </div>
</div>
