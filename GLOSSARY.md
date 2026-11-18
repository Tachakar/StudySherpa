# StudySherpa

A study assistant that lets a student upload their course materials and then search and ask questions over them.

## Language

**Document**:
A single piece of study material a user uploaded (e.g. lecture slides, a textbook chapter), regardless of its file format. Visible only to the user who uploaded it.
_Avoid_: File, Material, Source, Note

**Position**:
The place inside a Document that a search result or citation points to: a page for PDFs, a slide for presentations.
_Avoid_: Location, page (when speaking format-independently)

**Document status**:
Where a Document is in its lifecycle as the user sees it: pending, processing, ready, failed, or deleting. Only ready Documents can be searched.
_Avoid_: State, stage, progress

**Page description**:
A text account of a Position's visual content (diagrams, charts, photos, or a scanned page) produced by a vision model, so that visual content becomes searchable.
_Avoid_: Caption, alt text, summary

**Search**:
Finding the passages in a Search scope most relevant to a user's query, returned as ranked Positions without a generated answer.
_Avoid_: Query, lookup, retrieval (in user-facing language)

**Question**:
A single natural-language request over a Search scope that produces an Answer. Questions are kept in the user's history.
_Avoid_: Prompt, chat, query

**Answer**:
Generated text responding to a Question, grounded only in the user's Documents and carrying Citations, or an explicit statement that the Documents don't contain it.
_Avoid_: Response, completion, reply

**Citation**:
A reference inside an answer to the Position in a Document that supports a claim.
_Avoid_: Source, reference, footnote

**Search scope**:
The set of a user's Documents that a single search or question is run against, chosen by the user; empty means all of their Documents.
_Avoid_: Filter, selection, collection
