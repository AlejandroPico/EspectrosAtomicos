#!/usr/bin/env python3
"""Enriquece cada carpeta de elemento con estructura electrónica, radios y cristales.

El script respeta la arquitectura ``data/elements/<elemento>/`` y nunca crea una
base paralela. Funciona en tres capas:

1. Deriva datos documentados desde los CSV locales: configuración abreviada,
   capa exterior, configuración de valencia, conteo formal y valencias comunes.
2. Intenta descargar en una sola consulta las energías de ionización sucesivas
   desde NIST ASD. Si la red falla, conserva los datos locales existentes.
3. Si existe ``MP_API_KEY``, importa fases elementales de Materials Project a
   ``materials.csv``. Sin clave, conserva los materiales ya almacenados.

Las derivaciones se etiquetan explícitamente como tales; no sustituyen valores
experimentales ni se presentan como una definición universal.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
ELEMENTS_ROOT = ROOT / "data" / "elements"
MANIFEST_PATH = ELEMENTS_ROOT / "elements.manifest.csv"

PROPERTY_FIELDS = ["property", "value", "unit", "source", "source_url", "retrieved_at", "notes"]
MATERIAL_FIELDS = PROPERTY_FIELDS + [
    "material_id", "phase", "structure", "space_group",
    "lattice_a", "lattice_b", "lattice_c",
    "lattice_alpha", "lattice_beta", "lattice_gamma",
]

NIST_URL = "https://physics.nist.gov/cgi-bin/ASD/ie.pl"
PUBCHEM_ELEMENT_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/element/{atomic_number}/JSON/"
MATERIALS_PROJECT_URL = "https://api.materialsproject.org/materials/summary/"
NOW = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
ORBITAL_RE = re.compile(r"(\d+)([spdf])(?:\^?([0-9]+))?", re.IGNORECASE)
NUMBER_RE = re.compile(r"[-+]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][-+]?\d+)?")


def clean(value: Any) -> str:
    return "" if value is None else str(value).replace("\ufeff", "").strip()


def read_manifest() -> list[dict[str, str]]:
    with MANIFEST_PATH.open(encoding="utf-8-sig", newline="") as handle:
        return [{key: clean(value) for key, value in row.items()} for row in csv.DictReader(handle)]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", errors="replace", newline="") as handle:
        return [{clean(k): clean(v) for k, v in row.items() if k} for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    extras = sorted({key for row in rows for key in row if key not in fields})
    columns = fields + extras
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: clean(row.get(column)) for column in columns})


def property_map(rows: Iterable[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {clean(row.get("property")): row for row in rows if clean(row.get("property"))}


def upsert(rows: list[dict[str, str]], record: dict[str, Any]) -> None:
    property_id = clean(record.get("property"))
    for index, row in enumerate(rows):
        if clean(row.get("property")) == property_id:
            rows[index] = {**row, **{key: clean(value) for key, value in record.items()}}
            return
    rows.append({key: clean(value) for key, value in record.items()})


def source_record(property_id: str, value: Any, unit: str, source: str, url: str, notes: str) -> dict[str, str]:
    return {
        "property": property_id,
        "value": clean(value),
        "unit": unit,
        "source": source,
        "source_url": url,
        "retrieved_at": NOW,
        "notes": notes,
    }


def parse_orbitals(configuration: str) -> list[tuple[int, str, int]]:
    result: list[tuple[int, str, int]] = []
    for n, orbital, count in ORBITAL_RE.findall(configuration):
        result.append((int(n), orbital.lower(), int(count or "1")))
    return result


def valence_configuration(configuration: str, block: str) -> str:
    orbitals = parse_orbitals(configuration)
    if not orbitals:
        return ""
    max_n = max(n for n, _, _ in orbitals)
    if block == "d":
        selected = [item for item in orbitals if item[0] in {max_n, max_n - 1} and item[1] in {"s", "d"}]
    elif block == "f":
        selected = [item for item in orbitals if item[0] in {max_n, max_n - 1, max_n - 2} and item[1] in {"s", "d", "f"}]
    else:
        selected = [item for item in orbitals if item[0] == max_n]
    return " ".join(f"{n}{orbital}{count}" for n, orbital, count in selected)


def outer_shell_count(configuration: str) -> int | None:
    orbitals = parse_orbitals(configuration)
    if not orbitals:
        return None
    max_n = max(n for n, _, _ in orbitals)
    return sum(count for n, _, count in orbitals if n == max_n)


def formal_valence_count(group: int, block: str, outer_count: int | None) -> tuple[int | None, str]:
    if block in {"s", "p"}:
        if group == 18:
            return (2 if group == 18 and outer_count == 2 else 8), "Conteo de capa exterior para elemento representativo."
        if group <= 2:
            return group, "Conteo periódico del bloque s."
        return group - 10, "Conteo periódico del bloque p."
    if block == "d" and 3 <= group <= 12:
        return group, "Convención formal n s + (n−1) d; la participación real depende del compuesto."
    if block == "f":
        return outer_count, "Capa exterior únicamente; los electrones 5f/4f y 6d/5d pueden participar según el estado químico."
    return outer_count, "Derivado de la capa electrónica exterior."


def oxidation_values(rows: list[dict[str, str]]) -> str:
    for row in rows:
        if clean(row.get("property")) in {"oxidation_states", "oxidation_state"}:
            return clean(row.get("value"))
    return ""


def enrich_electronic_structure(element: dict[str, str]) -> None:
    folder = ELEMENTS_ROOT / element["folder"]
    atomic_path = folder / "atomic_properties.csv"
    chemical_path = folder / "chemical_properties.csv"
    atomic_rows = read_csv(atomic_path)
    chemical_rows = read_csv(chemical_path)
    props = property_map(atomic_rows)
    configuration = clean(props.get("electron_configuration", {}).get("value"))
    if not configuration:
        return

    block = clean(element.get("block")).lower()
    group = int(element.get("group") or 0)
    outer = outer_shell_count(configuration)
    valence_count, method = formal_valence_count(group, block, outer)
    valence_config = valence_configuration(configuration, block)
    oxidation = oxidation_values(chemical_rows)

    if configuration.startswith("["):
        upsert(atomic_rows, source_record(
            "electron_configuration_abbreviated", configuration, "", "PubChem Periodic Table",
            props.get("electron_configuration", {}).get("source_url", ""),
            "Configuración abreviada conservada desde el registro local de PubChem.",
        ))

    if outer is not None:
        upsert(atomic_rows, source_record(
            "outer_shell_electron_count", outer, "electrones", "TablaElementos · derivación",
            "", "Suma de ocupaciones con el mayor número cuántico principal n.",
        ))

    if valence_config:
        upsert(atomic_rows, source_record(
            "valence_shell_configuration", valence_config, "", "TablaElementos · derivación",
            "", f"Subconjunto de la configuración electrónica según el bloque {block or 'no indicado'}.",
        ))

    if valence_count is not None:
        upsert(atomic_rows, source_record(
            "valence_electron_count", valence_count, "electrones", "TablaElementos · convención documentada",
            "", method,
        ))

    if oxidation:
        upsert(atomic_rows, source_record(
            "common_valences", oxidation, "", "PubChem Periodic Table / interpretación histórica",
            props.get("electron_configuration", {}).get("source_url", ""),
            "Presentación provisional basada en estados de oxidación publicados. No equivale estrictamente a valencia IUPAC.",
        ))

    atomic_radius = props.get("atomic_radius")
    if atomic_radius and clean(atomic_radius.get("value")):
        upsert(atomic_rows, {
            **source_record(
                "van_der_waals_radius", atomic_radius.get("value"), atomic_radius.get("unit") or "pm",
                atomic_radius.get("source") or "PubChem Periodic Table",
                atomic_radius.get("source_url") or "https://pubchem.ncbi.nlm.nih.gov/ptable/",
                "El campo AtomicRadius de la tabla periódica PubChem se conserva explícitamente como radio de Van der Waals; revisar la definición de la fuente para cada versión.",
            )
        })

    write_csv(atomic_path, atomic_rows, PROPERTY_FIELDS)


def fetch_url(url: str, *, headers: dict[str, str] | None = None, timeout: int = 90) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "TablaElementos/0.2 scientific-data-import", **(headers or {})})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def parse_nist_csv(data: bytes) -> dict[str, list[dict[str, str]]]:
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    result: dict[str, list[dict[str, str]]] = {}
    if not reader.fieldnames:
        return result

    normalized = {field: re.sub(r"\s+", " ", clean(field)).lower() for field in reader.fieldnames}
    spectrum_col = next((field for field, label in normalized.items() if "spectrum" in label), "")
    charge_col = next((field for field, label in normalized.items() if "ion charge" in label), "")
    energy_col = next((field for field, label in normalized.items() if "ionization" in label and "energy" in label), "")
    uncertainty_col = next((field for field, label in normalized.items() if "uncertainty" in label), "")
    shells_col = next((field for field, label in normalized.items() if "ground shells" in label), "")
    config_col = next((field for field, label in normalized.items() if "ground configuration" in label), "")
    level_col = next((field for field, label in normalized.items() if "ground level" in label), "")
    if not spectrum_col or not energy_col:
        return result

    for row in reader:
        spectrum = clean(row.get(spectrum_col))
        symbol_match = re.match(r"([A-Z][a-z]?)", spectrum)
        if not symbol_match:
            continue
        symbol = symbol_match.group(1)
        charge_text = clean(row.get(charge_col))
        charge_match = NUMBER_RE.search(charge_text)
        charge = int(float(charge_match.group(0))) if charge_match else len(result.get(symbol, []))
        energy_raw = clean(row.get(energy_col))
        number_match = NUMBER_RE.search(energy_raw.replace(" ", ""))
        if not number_match:
            continue
        result.setdefault(symbol, []).append({
            "stage": str(charge + 1),
            "value": number_match.group(0).replace(",", "."),
            "raw": energy_raw,
            "uncertainty": clean(row.get(uncertainty_col)),
            "shells": clean(row.get(shells_col)),
            "configuration": clean(row.get(config_col)),
            "level": clean(row.get(level_col)),
        })
    return result


def download_nist_ionizations() -> dict[str, list[dict[str, str]]]:
    params = {
        "spectra": "H-Og",
        "units": "1",
        "format": "2",
        "order": "0",
        "at_num_out": "on",
        "sp_name_out": "on",
        "ion_charge_out": "on",
        "el_name_out": "on",
        "seq_out": "on",
        "shells_out": "on",
        "level_out": "on",
        "ion_conf_out": "on",
        "e_out": "0",
        "unc_out": "on",
        "biblio": "on",
    }
    url = f"{NIST_URL}?{urllib.parse.urlencode(params)}"
    return parse_nist_csv(fetch_url(url, timeout=120))


def apply_nist_ionizations(element: dict[str, str], records: list[dict[str, str]]) -> None:
    if not records:
        return
    path = ELEMENTS_ROOT / element["folder"] / "atomic_properties.csv"
    rows = read_csv(path)
    rows = [row for row in rows if not clean(row.get("property")).startswith("ionization_energy_")]
    for record in sorted(records, key=lambda item: int(item["stage"])):
        stage = int(record["stage"])
        quality = "evaluado"
        if "[" in record["raw"]:
            quality = "semiempírico"
        elif "(" in record["raw"]:
            quality = "teórico"
        upsert(rows, source_record(
            f"ionization_energy_{stage}", record["value"], "eV", "NIST Atomic Spectra Database",
            NIST_URL,
            f"Etapa {stage}; calidad {quality}; incertidumbre {record['uncertainty'] or 'no indicada'}; configuración {record['configuration'] or record['shells']}; nivel {record['level']}.",
        ))
    write_csv(path, rows, PROPERTY_FIELDS)


def extract_pubchem_sections(node: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    result: list[tuple[tuple[str, ...], str]] = []
    if isinstance(node, dict):
        heading = clean(node.get("TOCHeading"))
        next_path = path + ((heading,) if heading else ())
        information = node.get("Information")
        if isinstance(information, list):
            for item in information:
                value = item.get("Value", {}) if isinstance(item, dict) else {}
                strings = value.get("StringWithMarkup") if isinstance(value, dict) else None
                if isinstance(strings, list):
                    for entry in strings:
                        text = clean(entry.get("String")) if isinstance(entry, dict) else ""
                        if text:
                            result.append((next_path, text))
        for value in node.values():
            result.extend(extract_pubchem_sections(value, next_path))
    elif isinstance(node, list):
        for value in node:
            result.extend(extract_pubchem_sections(value, path))
    return result


def enrich_pubchem_annotations(element: dict[str, str]) -> None:
    atomic_number = int(element["atomic_number"])
    url = PUBCHEM_ELEMENT_URL.format(atomic_number=atomic_number)
    try:
        payload = json.loads(fetch_url(url, timeout=45))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return

    entries = extract_pubchem_sections(payload)
    atomic_path = ELEMENTS_ROOT / element["folder"] / "atomic_properties.csv"
    materials_path = ELEMENTS_ROOT / element["folder"] / "materials.csv"
    atomic_rows = read_csv(atomic_path)
    material_rows = read_csv(materials_path)

    for headings, text in entries:
        joined = " / ".join(headings).lower()
        if "covalent radius" in joined:
            match = NUMBER_RE.search(text)
            if match:
                upsert(atomic_rows, source_record("covalent_radius", match.group(0), "pm", "PubChem PUG View", url, text))
        elif "van der waals radius" in joined:
            match = NUMBER_RE.search(text)
            if match:
                upsert(atomic_rows, source_record("van_der_waals_radius", match.group(0), "pm", "PubChem PUG View", url, text))
        elif "crystal structure" in joined:
            upsert(material_rows, {
                **source_record("crystal_structure", text, "", "PubChem PUG View", url, "Anotación textual del registro de elemento."),
                "structure": text,
                "phase": "referencia PubChem",
            })
        elif "allotrope" in joined or "allotrop" in joined:
            key = f"allotrope_{len([row for row in material_rows if clean(row.get('property')).startswith('allotrope_')]) + 1}"
            upsert(material_rows, {
                **source_record(key, text, "", "PubChem PUG View", url, "Anotación textual de alótropo."),
                "phase": text[:120],
            })

    write_csv(atomic_path, atomic_rows, PROPERTY_FIELDS)
    write_csv(materials_path, material_rows, MATERIAL_FIELDS)


def import_materials_project(element: dict[str, str], api_key: str) -> None:
    symbol = element["symbol"]
    params = urllib.parse.urlencode({
        "elements": symbol,
        "num_elements": "1",
        "_fields": "material_id,formula_pretty,symmetry,structure,energy_above_hull,is_stable",
        "_limit": "12",
    })
    url = f"{MATERIALS_PROJECT_URL}?{params}"
    try:
        payload = json.loads(fetch_url(url, headers={"X-API-KEY": api_key}, timeout=60))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return

    records = payload.get("data", []) if isinstance(payload, dict) else []
    path = ELEMENTS_ROOT / element["folder"] / "materials.csv"
    rows = [row for row in read_csv(path) if clean(row.get("source")) != "Materials Project"]

    for record in records:
        structure = record.get("structure") or {}
        lattice = structure.get("lattice") or {}
        symmetry = record.get("symmetry") or {}
        material_id = clean(record.get("material_id"))
        phase = clean(record.get("formula_pretty")) or symbol
        structure_name = clean(symmetry.get("crystal_system"))
        common = {
            "source": "Materials Project",
            "source_url": f"https://materialsproject.org/materials/{material_id}",
            "retrieved_at": NOW,
            "material_id": material_id,
            "phase": phase,
            "structure": structure_name,
            "space_group": clean(symmetry.get("symbol")),
            "lattice_a": clean(lattice.get("a")),
            "lattice_b": clean(lattice.get("b")),
            "lattice_c": clean(lattice.get("c")),
            "lattice_alpha": clean(lattice.get("alpha")),
            "lattice_beta": clean(lattice.get("beta")),
            "lattice_gamma": clean(lattice.get("gamma")),
        }
        for property_id, value, unit in (
            ("crystal_structure", structure_name, ""),
            ("space_group", symmetry.get("symbol"), ""),
            ("lattice_a", lattice.get("a"), "Å"),
            ("lattice_b", lattice.get("b"), "Å"),
            ("lattice_c", lattice.get("c"), "Å"),
            ("lattice_alpha", lattice.get("alpha"), "°"),
            ("lattice_beta", lattice.get("beta"), "°"),
            ("lattice_gamma", lattice.get("gamma"), "°"),
            ("energy_above_hull", record.get("energy_above_hull"), "eV/atom"),
            ("is_stable", record.get("is_stable"), ""),
        ):
            if value in (None, ""):
                continue
            rows.append({
                **common,
                "property": property_id,
                "value": clean(value),
                "unit": unit,
                "notes": "Fase elemental calculada; seleccionar con cautela la fase física representativa.",
            })

    write_csv(path, rows, MATERIAL_FIELDS)


def append_source(folder: Path, provider: str, dataset: str, target: str, url: str, status: str, notes: str) -> None:
    path = folder / "sources.csv"
    rows = read_csv(path)
    fields = ["provider", "dataset", "target_file", "source_url", "retrieved_at", "status", "sha256", "notes"]
    key = (provider, dataset, target)
    rows = [row for row in rows if (row.get("provider"), row.get("dataset"), row.get("target_file")) != key]
    rows.append({
        "provider": provider,
        "dataset": dataset,
        "target_file": target,
        "source_url": url,
        "retrieved_at": NOW,
        "status": status,
        "sha256": "",
        "notes": notes,
    })
    write_csv(path, rows, fields)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--offline", action="store_true", help="No realiza descargas; aplica solo derivaciones locales.")
    parser.add_argument("--pubchem-annotations", action="store_true", help="Consulta PUG View para radios, cristales y alótropos.")
    parser.add_argument("--skip-nist", action="store_true", help="No consulta energías sucesivas NIST.")
    args = parser.parse_args()

    elements = read_manifest()
    for element in elements:
        enrich_electronic_structure(element)

    nist_records: dict[str, list[dict[str, str]]] = {}
    if not args.offline and not args.skip_nist:
        try:
            nist_records = download_nist_ionizations()
        except (urllib.error.URLError, TimeoutError, csv.Error) as error:
            print(f"NIST ASD no disponible; se conservarán datos locales: {error}")

    mp_api_key = clean(os.getenv("MP_API_KEY"))
    for index, element in enumerate(elements, start=1):
        folder = ELEMENTS_ROOT / element["folder"]
        if nist_records.get(element["symbol"]):
            apply_nist_ionizations(element, nist_records[element["symbol"]])
            append_source(folder, "NIST ASD", "Ground States and Ionization Energies", "atomic_properties.csv", NIST_URL, "ok", "Serie de energías de ionización sucesivas.")

        if not args.offline and args.pubchem_annotations:
            enrich_pubchem_annotations(element)
            append_source(folder, "PubChem", "PUG View Element", "atomic_properties.csv; materials.csv", PUBCHEM_ELEMENT_URL.format(atomic_number=element["atomic_number"]), "consultado", "Radios, cristales y alótropos cuando existen anotaciones.")
            time.sleep(0.22)

        if not args.offline and mp_api_key:
            import_materials_project(element, mp_api_key)
            append_source(folder, "Materials Project", "Materials Summary", "materials.csv", MATERIALS_PROJECT_URL, "consultado", "Fases elementales y parámetros de red; requiere MP_API_KEY.")
            time.sleep(0.12)

        print(f"[{index:03d}/118] {element['symbol']} · estructura electrónica y radios preparados")

    print("Enriquecimiento avanzado completado dentro de data/elements/<elemento>/.")
    if not mp_api_key:
        print("Materials Project no importado: configura MP_API_KEY para añadir fases calculadas.")


if __name__ == "__main__":
    main()
