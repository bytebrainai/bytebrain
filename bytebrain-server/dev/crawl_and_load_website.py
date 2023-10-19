from core.document_loader import load_docs_from_site

docs = load_docs_from_site(
    doc_source_id="caliban",
    url="https://ghostdogpr.github.io/caliban/",
    max_depth=None
)

print(docs)
