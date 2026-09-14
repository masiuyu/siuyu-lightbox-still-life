# Material Presets

Scope: Explicit offline renderer operation or implementation. Enter through [Offline workflow](offline-workflow.md) for the local runtime contract.

## Contents

1. Geometry versus material
2. Light-table stack
3. Presets
4. Contact and transmission
5. Realism checks

## 1. Geometry Versus Material

Low poly describes geometry complexity, not material quality. Simplify props geometrically while preserving credible response to light. Do not convert detailed products, logos, or exact museum images into low-poly reconstructions.

Recommended geometry:

- paper: plane with slight thickness, optional corner curl;
- folder/envelope: folded planes with 1–3 mm implied thickness;
- metal tool: simplified extruded mesh with bevels;
- glass/acrylic: low-poly solid with real thickness;
- product cutout: exact image plane or approved 3D asset;
- lightbox frame: beveled rectangular solid.

## 2. Light-Table Stack

```text
rectangular emitter
→ diffuser layer 1
→ diffuser layer 2
→ frosted translucent surface
→ scene objects
→ weak environment/top light
→ orthographic camera
```

Expected visual cues:

- brighter center with controlled edge falloff;
- subtle frame occlusion;
- soft contact shadows near the surface;
- transmitted halos through tracing paper and film;
- hard light blocking under metal and opaque folders;
- weak top highlights on metal, acrylic, and product surfaces.

## 3. Presets

Values are normalized renderer presets for visual tuning.

| Material | Opacity | Transmission | Roughness | Shadow | Thickness cue |
|---|---:|---:|---:|---:|---:|
| `tracing_paper` | 0.72 | 0.42 | 0.90 | 0.06 | 0.15 |
| `plain_paper` | 0.96 | 0.10 | 0.86 | 0.10 | 0.25 |
| `kraft_paper` | 1.00 | 0.02 | 0.94 | 0.18 | 0.70 |
| `photo_print` | 1.00 | 0.00 | 0.55 | 0.14 | 0.35 |
| `film_sleeve` | 0.78 | 0.62 | 0.34 | 0.04 | 0.08 |
| `acrylic` | 0.35 | 0.72 | 0.22 | 0.07 | 1.20 |
| `glass_lens` | 0.20 | 0.84 | 0.10 | 0.05 | 2.00 |
| `metal_tool` | 1.00 | 0.00 | 0.30 | 0.24 | 1.50 |
| `cutout_object` | 1.00 | asset-defined | asset-defined | 0.16 | asset-defined |

Do not use one generic shadow preset for all materials.

## 4. Contact and Transmission

Render in this conceptual order:

1. backlight contribution;
2. contact shadow from object mask and height;
3. transmission through material;
4. object surface color and texture;
5. top/environment reflection;
6. restrained bloom and grain.

Avoid strong bloom. A light table is a physical translucent surface, not a luminous sci-fi interface.

## 5. Realism Checks

Fail or warn when:

- every object has the same shadow softness;
- opaque metal transmits backlight;
- tracing paper behaves like solid card;
- objects have no thickness or contact cue;
- the frame casts no edge occlusion;
- the entire surface is uniformly white;
- paper grain scales incorrectly with object size;
- low-poly facets appear on protected product images;
- background enhancement changes approved object silhouettes.
