# Precise print processing

Start with the same natural-language [print objective](../../references/print-direction.md). The AI chooses the source plane, substrate, ink roles, separation, dimensions and visible inspection targets, then prepares the processing backend's actual parameter card. Preserve that card with its report and inspect the output image.

## Choose a supported operation

Use [process profiles](references/print-style-presets.json) and [woven structures](references/material-library.json) to inform the visible design. The catalog includes more visual processes than the deterministic renderer implements. `scripts/suggest_print_styles.py --help` and `scripts/suggest_carrier_dye.py --help` describe available recommendations.

Native image-direction compilation needs Python's standard library. Raster processing and palette extraction use [requirements.txt](requirements.txt). Relative paths in cards resolve from the card directory; command-line file paths resolve from the working directory.

## Build the source plane before placing it

For a paper photograph, construct the complete source window, separation and border, then transform the whole plane together. The implemented photographic modes are monochrome_am, spot_duotone_am and subtractive_cmyk_am. For direct spot printing, use a source plate with real alpha and two to eight declared ink colors. Preserve substantial broad-fill coverage while using shared substrate relief and restrained edge absorption.

The AI translates that objective into the [plane-card protocol](references/preprinted-plane-card.schema.json), then runs:

```bash
python3 <skill-dir>/modules/print/scripts/compose_preprinted_planes.py --input /path/to/actual-plane-card.json --report /path/to/new-report.json
```

`scripts/extract_plate_alpha.py` can separate a bright neutral background connected to the image border. Inspect the real boundary before composition; applicability depends on the source. Save the actual extraction settings and resulting alpha.

## Process an existing scene

Bound the actual surfaces deliberately and prepare the [zone-card protocol](references/halftone-render-card.schema.json). Existing backend examples show [monochrome](examples/halftone-render-card.json), [duotone](examples/halftone-render-card-duotone.json) and [CMYK](examples/halftone-render-card-cmyk.json) controls.

```bash
python3 <skill-dir>/modules/print/scripts/render_halftone_zones.py --input /path/to/actual-render-card.json --report /path/to/new-report.json
```

Compare corners, rotated edges, protrusions and occlusions against the actual source. Outside-zone pixel equality is containment evidence; boundaries and material appearance need their own inspection. `scripts/enhance_carrier_texture.py` and `scripts/raster_probe.py` provide bounded texture treatment and raster evidence; use their current --help interfaces.

## Inspect what the operation achieved

View the whole output and 100% details. Check complete-source preservation, shared paper geometry, coverage, fiber continuity and independently readable ink roles. The shared transform is geometric evidence; visual quality and user acceptance retain separate evidence. FM, riso and gravure catalog entries guide native generation; the deterministic renderer supports the modes listed above. Numeric controls describe the implementation, with physical press and material measurements documented separately.

Use new versioned paths, preserve sources and previous outputs, and retain the [license](LICENSE). Ordinary generation uses the main natural-language direction interface and actual image tool.
