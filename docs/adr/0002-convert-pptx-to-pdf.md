# Convert PPTX to PDF before processing

We support PDF and PPTX through a single pipeline by converting PPTX to PDF with headless LibreOffice in the worker; slide N becomes page N, so a Position means the same thing for both formats. Native extraction with `python-pptx` cannot render slides to images, which the vision path (ADR-0001) needs, so it would have meant two extractors plus LibreOffice anyway.

## Consequences

The worker image grows by a few hundred MB, and converted slides occasionally differ slightly in fonts or layout. Conversion runs with a timeout and without network access. Both the original PPTX and the converted PDF are stored, so reprocessing does not convert again.
