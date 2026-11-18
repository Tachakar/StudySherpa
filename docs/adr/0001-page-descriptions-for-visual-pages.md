# Describe whole rendered pages, and only visual ones

Lecture slides carry key information in diagrams, and many of those are vector drawings that `Page.get_images()` cannot see. We render a page and have a vision model write a Page description only when the page has significant images, significant drawings, or almost no text; text-heavy pages use the text layer alone. Scanned pages take the same path, so they need no separate OCR step.

## Considered Options

- **Caption each extracted image**: misses vector diagrams entirely and describes images without the slide title and surrounding text.
- **Multimodal embeddings (CLIP, SigLIP)**: no captioning step, but trained mostly on photos with short English captions, so weak on Polish and on dense technical diagrams.
- **Render every page**: simplest routing, but pays a vision-model call for every text-only page.

## Consequences

The routing thresholds live in `ImageFilteringConfig` and are tuned by inspecting real decks; each page's routing decision is logged. Changing the routing or the vision prompt changes what gets embedded, so it bumps the `index_version` and requires a reindex.
