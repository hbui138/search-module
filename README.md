# search-module
search-module for searching for relevant laws

# Search module

```bash
git submodule add git@github.com:cold-berry/data-process-module.git submodules/data-process-module
```

```bash
pip install -e submodules/data-process-module
pip install -e .
```

```bash
# Read this file first
python -m search_module.flow.hybrid_search
```

## `.env`
```ini
ES_HOST=...
ES_USER=...
ES_PASSWORD=...

QDRANT_HOST=...

JINA_ENDPOINT=...
JINA_API_KEY=...
```
