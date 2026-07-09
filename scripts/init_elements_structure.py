from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ELEMENTS_ROOT = ROOT / "data" / "elements"
MANIFEST_PATH = ELEMENTS_ROOT / "elements.manifest.csv"

CSV_TEMPLATES: dict[str, str] = {
    "identity.csv": "field,value,unit,source,notes\n",
    "spectra_nist_lines.csv": "wavelength_nm,intensity,species,transition,lower_level,upper_level,source,notes\n",
    "spectra_nist_levels.csv": "level_id,energy,energy_unit,configuration,term,j,source,notes\n",
    "atomic_properties.csv": "property,value,unit,source,notes\n",
    "isotopes.csv": "isotope,mass_number,atomic_mass_u,abundance_percent,half_life,decay_mode,spin,source,notes\n",
    "physical_properties.csv": "property,value,unit,phase,temperature_k,source,notes\n",
    "chemical_properties.csv": "property,value,unit,source,notes\n",
    "materials.csv": "property,value,unit,structure,temperature_k,source,notes\n",
    "thermodynamics.csv": "property,value,unit,temperature_k,pressure,source,notes\n",
    "geochemistry.csv": "property,value,unit,environment,source,notes\n",
    "astrophysics.csv": "property,value,unit,context,source,notes\n",
    "biology_medicine.csv": "property,value,unit,organism_or_use,source,notes\n",
    "environment_safety.csv": "property,value,unit,classification,source,notes\n",
    "industry_economy.csv": "property,value,unit,year,region,source,notes\n",
    "history.csv": "field,value,year,source,notes\n",
    "compounds.csv": "formula,name,compound_type,oxidation_state,source,notes\n",
    "analytical_methods.csv": "method,signal,limit_of_detection,unit,source,notes\n",
    "radiation_interaction.csv": "property,value,unit,energy,particle_or_photon,source,notes\n",
    "photonics_color.csv": "property,value,wavelength_nm,color,source,notes\n",
    "computational.csv": "property,value,unit,method,basis_or_model,source,notes\n",
    "sources.csv": "dataset,source_name,url,download_date,license,notes\n",
}

README_TEMPLATE = """# {atomic_number} · {symbol} · {name_en} / {name_es}

Carpeta de datos brutos y semiprocesados para el elemento **{name_es}** (`{symbol}`).

## Convención

- Mantener aquí CSVs específicos de este elemento.
- Guardar datos descargados de fuentes oficiales con el menor procesado posible.
- Añadir cada descarga o fuente a `sources.csv`.
- No borrar archivos originales si después se generan versiones normalizadas.

## Archivos principales

- `identity.csv`
- `spectra_nist_lines.csv`
- `spectra_nist_levels.csv`
- `atomic_properties.csv`
- `isotopes.csv`
- `physical_properties.csv`
- `chemical_properties.csv`
- `materials.csv`
- `thermodynamics.csv`
- `geochemistry.csv`
- `astrophysics.csv`
- `biology_medicine.csv`
- `environment_safety.csv`
- `industry_economy.csv`
- `history.csv`
- `compounds.csv`
- `analytical_methods.csv`
- `radiation_interaction.csv`
- `photonics_color.csv`
- `computational.csv`
- `sources.csv`
"""


def read_manifest() -> list[dict[str, str]]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"No existe el manifiesto: {MANIFEST_PATH}")

    with MANIFEST_PATH.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False

    path.write_text(content, encoding="utf-8")
    return True


def init_element_folder(element: dict[str, str]) -> tuple[int, int]:
    folder = ELEMENTS_ROOT / element["folder"]
    folder.mkdir(parents=True, exist_ok=True)

    created_files = 0
    skipped_files = 0

    readme_content = README_TEMPLATE.format(**element)
    if write_if_missing(folder / "README.md", readme_content):
        created_files += 1
    else:
        skipped_files += 1

    for filename, header in CSV_TEMPLATES.items():
        if write_if_missing(folder / filename, header):
            created_files += 1
        else:
            skipped_files += 1

    return created_files, skipped_files


def main() -> None:
    elements = read_manifest()
    created_total = 0
    skipped_total = 0

    for element in elements:
        created, skipped = init_element_folder(element)
        created_total += created
        skipped_total += skipped

    print(f"Elementos procesados: {len(elements)}")
    print(f"Archivos creados:     {created_total}")
    print(f"Archivos existentes:  {skipped_total}")
    print(f"Carpeta raíz:         {ELEMENTS_ROOT}")


if __name__ == "__main__":
    main()
