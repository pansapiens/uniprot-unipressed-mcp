# UniProt MCP Server

An MCP (Model Context Protocol) server that provides tools for querying the [UniProt](https://www.uniprot.org/) protein database using the [unipressed](https://github.com/multimeric/Unipressed) Python library.

## Features

- **Search proteins** using standard the  [UniProt query syntax](https://www.uniprot.org/help/query-fields) across UniProtKB, UniParc, or UniRef databases
- **Fetch specific entries** by accession ID
- **Pagination** for large result sets
- **Field selection** to control returned data
- **JSON format responses** by default - responses are returned in JSON format, with TOON format available as an option

## Installation

### Using uv (recommended)

```bash
uv sync
```

This will create a virtual environment and install all dependencies.


### Development installation

```bash
uv sync --extra dev
```

This installs the package with development dependencies (pytest, etc.).

## Usage

### Running the server

#### With uvx (recommended)

```bash
uvx uniprot-unipressed-mcp
```

Or from a git repository:

```bash
uvx --from git+https://github.com/pansapiens/uniprot-unipressed-mcp uniprot-mcp
```

#### Alternative example: with the FastMCP CLI and HTTP transport

```bash
fastmcp run src/uniprot_mcp/server.py:mcp --transport http --port 8007
```

### Configuring with MCP clients

#### Claude Code

Add the server using the Claude Code CLI:

```bash
claude mcp add uniprot-unipressed-mcp -- uvx git+https://github.com/pansapiens/uniprot-unipressed-mcp
```

#### Other MCP clients

Or manually add to your MCP configuration (Claude Code, Cursor, etc.):

```json
{
  "mcpServers": {
    "uniprot-unipressed-mcp": {
      "command": "uvx",
      "args": ["git+https://github.com/pansapiens/uniprot-unipressed-mcp"]
    }
  }
}
```

## Response Format

Tool responses are returned in JSON format by default. To receive [TOON format](https://github.com/toon-format/toon-python) responses instead, use the `response_format` parameter with value `"toon"`:

```python
# JSON format (default)
result = uniprot_search(query="gene:BRCA1")

# TOON format
result = uniprot_search(query="gene:BRCA1", response_format="toon")
```

## Tools

### uniprot_search

Search the UniProt protein database using query syntax.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| query | string | Yes | - | UniProt query string |
| database | string | No | "uniprotkb" | Database to search: uniprotkb, uniparc, uniref |
| limit | integer | No | 10 | Results per page (1-100) |
| fields | list[string] | No | None | Return fields to include |
| cursor | string | No | None | Pagination cursor from previous result |
| response_format | string | No | "json" | Response format: "json" (default) or "toon" |

**Example queries:**

```
gene:BRCA1                              # Search by gene name
organism_id:9606                        # Human proteins (NCBI taxonomy ID)
(gene:BRCA*) AND (organism_id:10090)    # Mouse BRCA genes with wildcard
length:[500 TO 700]                     # Proteins of specific length range
keyword:kinase                          # By UniProt keyword
family:serpin                           # By protein family
ec:3.2.1.23                             # By enzyme classification
reviewed:true                           # Only Swiss-Prot reviewed entries
```

**Response:**

By default, responses are returned in JSON format. When `response_format="toon"` is specified, responses are returned in TOON format (a compact string):

**JSON format (default):**
```json
{
  "results": [...],
  "total": 1234,
  "nextCursor": "eyJvZmZzZXQiOiAxMH0="
}
```

**TOON format:**
```
results[10]:
  - entryType: UniProtKB reviewed (Swiss-Prot)
    primaryAccession: P38398
    secondaryAccessions[7]: E9PFZ0,O15129,Q1RMC1,Q3LRJ0,Q3LRJ6,Q6IN79,Q7KYU9
    uniProtkbId: BRCA1_HUMAN
    ...etc...
```

### uniprot_fetch

Fetch specific protein entries by their UniProt accession IDs.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| ids | list[string] | Yes | - | UniProt accession IDs to fetch |
| database | string | No | "uniprotkb" | Database to fetch from |
| fields | list[string] | No | None | Return fields to include |
| response_format | string | No | "json" | Response format: "json" (default) or "toon" |

**Example:**

```python
uniprot_fetch(ids=["P62988", "A0A0C5B5G6"])
```

**Response:**

By default, responses are returned in JSON format. When `response_format="toon"` is specified, responses are returned in TOON format (a compact string):

**JSON format (default):**
```json
{
  "results": [...],
  "found": 2,
  "requested": 2
}
```

**TOON format:**
```
results[10]:
  - entryType: UniProtKB reviewed (Swiss-Prot)
    primaryAccession: P38398
    secondaryAccessions[7]: E9PFZ0,O15129,Q1RMC1,Q3LRJ0,Q3LRJ6,Q6IN79,Q7KYU9
    uniProtkbId: BRCA1_HUMAN
    ...etc...
```

## Pagination

The server uses cursor-based pagination for search results. When more results are available, the response includes a `nextCursor` field. Pass this cursor in subsequent requests to retrieve the next page:

```python
# First request
result1 = uniprot_search(query="organism_id:9606", limit=10)

# Get next page using cursor
if "nextCursor" in result1:
    result2 = uniprot_search(
        query="organism_id:9606",
        limit=10,
        cursor=result1["nextCursor"]
    )
```

## Databases

| Database | Description |
|----------|-------------|
| uniprotkb | UniProt Knowledgebase - curated protein sequences and annotations |
| uniparc | UniProt Archive - comprehensive protein sequence archive |
| uniref | UniProt Reference Clusters - clustered protein sequences |

## Return Fields

Common return fields include:

- `accession` - UniProt accession number
- `id` - Entry name
- `gene_names` - Gene names
- `protein_name` - Protein names
- `organism_name` - Source organism
- `organism_id` - NCBI taxonomy ID
- `length` - Sequence length
- `mass` - Molecular mass
- `sequence` - Amino acid sequence
- `cc_function` - Function annotation
- `cc_subcellular_location` - Subcellular location

See the [UniProt return fields documentation](https://www.uniprot.org/help/return_fields) for the complete list.

## Development

### Using a local copy of the repository

```json
{
  "mcpServers": {
    "uniprot-unipressed-mcp": {
      "command": "uv",
      "args": ["--directory", "/path/to/uniprot-unipressed-mcp", "run", "-m", "uniprot_mcp.server"]
    }
  }
}
```

### Testing using the MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv --directory $(pwd) run -m uniprot_mcp.server
```

### Running tests

```bash
uv run pytest
```

This runs all unit tests. Integration tests (which require network access to the UniProt API) are skipped by default.

### Running integration tests

Integration tests can be enabled using an environment variable:

```bash
RUN_INTEGRATION_TESTS=1 uv run pytest
```

Or run only integration tests:

```bash
RUN_INTEGRATION_TESTS=1 uv run pytest -m integration
```

### Running tests with coverage

```bash
uv run pytest --cov=uniprot_mcp
```

To include integration tests in coverage:

```bash
RUN_INTEGRATION_TESTS=1 uv run pytest --cov=uniprot_mcp
```

## Resources

- [UniProt](https://www.uniprot.org/)
- [UniProt Query Syntax](https://www.uniprot.org/help/query-fields)
- [UniProt Return Fields](https://www.uniprot.org/help/return_fields)
- [unipressed Documentation](https://multimeric.github.io/Unipressed/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [TOON Format](https://github.com/toon-format/toon-python) - Alternative serialization format available as an option

## Licence

MIT
