# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fastmcp>=2.0.0,<3.0.0",
#     "toon-format>=0.9.0b1",
#     "unipressed>=1.4.0,<2.0.0",
# ]
# ///
"""UniProt MCP Server - FastMCP server providing UniProt search and fetch tools."""

from typing import Any

from fastmcp import FastMCP
from toon_format import encode

from uniprot_mcp.clients import get_client, validate_database, VALID_DATABASES
from uniprot_mcp.pagination import decode_cursor, paginate_results


def _format_response(data: dict[str, Any], format: str) -> str | dict[str, Any]:
    """
    Format response data based on the requested format.
    
    Args:
        data: The response data dictionary
        format: The format to use ('toon' or 'json')
    
    Returns:
        TOON-formatted string if format='toon', otherwise the original dict
    """
    if format == "toon":
        return encode(data)
    return data


# Create the FastMCP server instance
mcp = FastMCP(
    name="UniProt MCP Server",
    instructions="""
    This MCP server provides tools for querying the UniProt protein database.
    
    Available databases:
    - uniprotkb: UniProt Knowledgebase (default) - curated protein sequences and annotations
    - uniparc: UniProt Archive - comprehensive protein sequence archive
    - uniref: UniProt Reference Clusters - clustered protein sequences
    
    For query syntax, see: https://www.uniprot.org/help/query-fields
    """,
)


SEARCH_DESCRIPTION = """
Search the UniProt protein database using query syntax.

Args:
    query: UniProt query string. Examples:
        - gene:BRCA1 - Search by gene name
        - organism_id:9606 - Human proteins (NCBI taxonomy ID)
        - (gene:BRCA*) AND (organism_id:10090) - Mouse BRCA genes with wildcard
        - length:[500 TO 700] - Proteins of specific length range
        - keyword:kinase - By UniProt keyword
        - family:serpin - By protein family
        - ec:3.2.1.23 - By enzyme classification
        - database:pfam - With Pfam cross-references
        - reviewed:true - Only Swiss-Prot reviewed entries
        
        Available query fields (see https://www.uniprot.org/help/query-fields):
        - accession: Primary/canonical isoform accessions (e.g., accession:P62988)
        - active: Active/obsolete status (e.g., active:false)
        - lit_author: Reference author (e.g., lit_author:ashburner)
        - protein_name: Protein name (e.g., protein_name:CD233)
        - chebi: ChEBI identifier (e.g., chebi:18420)
        - xrefcount_pdb: Cross-reference count (e.g., xref_count_pdb:[20 TO *])
        - date_created: Creation date (e.g., date_created:[2012-10-01 TO *])
        - date_modified: Last modification date (e.g., date_modified:[2012-01-01 TO 2019-03-01])
        - date_sequence_modified: Sequence modification date (e.g., date_sequence_modified:[2012-01-01 TO 2012-03-01])
        - database: Database cross-reference (e.g., database:pfam)
        - xref: Cross-reference (e.g., xref:pdb-1aut)
        - ec: Enzyme Commission number (e.g., ec:3.2.1.23)
        - existence: Protein existence level (e.g., existence:3)
        - family: Protein family (e.g., family:serpin)
        - fragment: Fragment status (e.g., fragment:true)
        - gene: Gene name (e.g., gene:HPSE)
        - gene_exact: Exact gene name (e.g., gene_exact:HPSE)
        - go: Gene Ontology term (e.g., go:0015629)
        - virus_host_name: Virus host name
        - virus_host_id: Virus host ID (e.g., virus_host_id:10090)
        - accession_id: Primary accession (e.g., accession_id:P00750)
        - inchikey: InChIKey identifier (e.g., inchikey:WQZGKKKJIJFFOK-GASJEMHNSA-N)
        - interactor: Interacting protein (e.g., interactor:P00520)
        - keyword: Keyword (e.g., keyword:toxin or keyword:KW-0800)
        - length: Sequence length range (e.g., length:[500 TO 700])
        - mass: Molecular mass range (e.g., mass:[500000 TO *])
        - cc_mass_spectrometry: Mass spectrometry method (e.g., cc_mass_spectrometry:maldi)
        - encoded_in: Gene location (e.g., encoded_in:Mitochondrion)
        - organism_name: Organism name (e.g., organism_name:"Ovis aries")
        - organism_id: Organism taxonomy ID (e.g., organism_id:9940)
        - plasmid: Plasmid name (e.g., plasmid:ColE1)
        - proteome: Proteome ID (e.g., proteome:UP000005640)
        - proteomecomponent: Proteome component (e.g., proteomecomponent:"chromosome 1")
        - sec_acc: Secondary accession (e.g., sec_acc:P02023)
        - reviewed: Reviewed status (e.g., reviewed:true)
        - scope: Reference scope (e.g., scope:mutagenesis)
        - sequence: Sequence identifier (e.g., accession:P05067-9 AND is_isoform:true)
        - strain: Organism strain (e.g., strain:wistar)
        - taxonomy_name: Taxonomy name (e.g., taxonomy_name:mammal)
        - taxonomy_id: Taxonomy ID (e.g., taxonomy_id:40674)
        - tissue: Tissue type (e.g., tissue:liver)
        - cc_webresource: Web resource (e.g., cc_webresource:wikipedia)
        
    database: UniProt database to search. One of: uniprotkb (default), uniparc, uniref
    
    limit: Maximum number of results per page (1-100, default 10)
    
    fields: Optional list of return fields to include. If not specified, all fields
        are returned. Available return fields (see https://www.uniprot.org/help/return_fields):
        
        Names & Taxonomy:
        - accession, id, gene_names, gene_primary, gene_synonym, gene_oln, gene_orf
        - organism_name, organism_id, protein_name, xref_proteomes
        - lineage, lineage_ids, virus_hosts
        
        Sequences:
        - cc_alternative_products, ft_var_seq, cc_sc_epred, fragment, encoded_in
        - length, mass, cc_mass_spectrometry, ft_variant, ft_non_cons, ft_non_std
        - ft_non_ter, cc_polymorphism, cc_rna_editing, sequence, cc_sequence_caution
        - ft_conflict, ft_unsure, sequence_version
        
        Function:
        - absorption, ft_act_site, cc_activity_regulation, ft_binding, cc_catalytic_activity
        - cc_cofactor, ft_dna_bind, ec, cc_function, kinetics, cc_pathway
        - ph_dependence, redox_potential, rhea, ft_site, temp_dependence
        
        Miscellaneous:
        - annotation_score, cc_caution, comment_count, feature_count, keywordid, keyword
        - cc_miscellaneous, protein_existence, reviewed, tools, uniparc_id
        
        Interaction:
        - cc_interaction, cc_subunit
        
        Expression:
        - cc_developmental_stage, cc_induction, cc_tissue_specificity
        
        Gene Ontology (GO):
        - go_p, go_c, go, go_f, go_id
        
        Pathology & Biotech:
        - cc_allergen, cc_biotechnology, cc_disruption_phenotype, cc_disease
        - ft_mutagen, cc_pharmaceutical, cc_toxic_dose
        
        Subcellular location:
        - ft_intramem, cc_subcellular_location, ft_topo_dom, ft_transmem
        
        PTM / Processing:
        - ft_chain, ft_crosslnk, ft_disulfid, ft_carbohyd, ft_init_met, ft_lipid
        - ft_mod_res, ft_peptide, cc_ptm, ft_propep, ft_signal, ft_transit
        
        Structure:
        - structure_3d, ft_strand, ft_helix, ft_turn
        
        Publications:
        - lit_pubmed_id
        
        Date:
        - date_created, date_modified, date_sequence_modified, version
        
        Family & Domains:
        - ft_coiled, ft_compbias, cc_domain, ft_domain, ft_motif, protein_families
        - ft_region, ft_repeat, ft_zn_fing
        
        Cross-references:
        - See https://www.uniprot.org/help/return_fields for cross-reference fields
        
    cursor: Pagination cursor from a previous search result's 'nextCursor' field.
        Pass this to retrieve the next page of results.
    
    format: Response format. One of: 'toon' (default) or 'json'.
        - 'toon': Returns response in TOON format (token-efficient compression)
        - 'json': Returns response in JSON format

Returns:
    When format='toon': TOON-formatted string with:
    - results: Array of matching protein entries
    - total: Total number of matching entries (if available)
    - nextCursor: Cursor string for retrieving the next page (if more results exist)
    
    When format='json': JSON object with:
    - results: Array of matching protein entries
    - total: Total number of matching entries (if available)
    - nextCursor: Cursor string for retrieving the next page (if more results exist)

See https://www.uniprot.org/help/query-fields for full query syntax documentation.
"""


FETCH_DESCRIPTION = """
Fetch specific protein entries by their UniProt accession IDs.

Args:
    ids: List of UniProt accession IDs to fetch. Examples:
        - ["P62988"] - Single protein
        - ["A0A0C5B5G6", "A0A1B0GTW7"] - Multiple proteins
        
    database: UniProt database to fetch from. One of: uniprotkb (default), uniparc, uniref
    
    fields: Optional list of return fields to include. If not specified, all fields
        are returned. Available return fields (see https://www.uniprot.org/help/return_fields):
        
        Names & Taxonomy:
        - accession, id, gene_names, gene_primary, gene_synonym, gene_oln, gene_orf
        - organism_name, organism_id, protein_name, xref_proteomes
        - lineage, lineage_ids, virus_hosts
        
        Sequences:
        - cc_alternative_products, ft_var_seq, cc_sc_epred, fragment, encoded_in
        - length, mass, cc_mass_spectrometry, ft_variant, ft_non_cons, ft_non_std
        - ft_non_ter, cc_polymorphism, cc_rna_editing, sequence, cc_sequence_caution
        - ft_conflict, ft_unsure, sequence_version
        
        Function:
        - absorption, ft_act_site, cc_activity_regulation, ft_binding, cc_catalytic_activity
        - cc_cofactor, ft_dna_bind, ec, cc_function, kinetics, cc_pathway
        - ph_dependence, redox_potential, rhea, ft_site, temp_dependence
        
        Miscellaneous:
        - annotation_score, cc_caution, comment_count, feature_count, keywordid, keyword
        - cc_miscellaneous, protein_existence, reviewed, tools, uniparc_id
        
        Interaction:
        - cc_interaction, cc_subunit
        
        Expression:
        - cc_developmental_stage, cc_induction, cc_tissue_specificity
        
        Gene Ontology (GO):
        - go_p, go_c, go, go_f, go_id
        
        Pathology & Biotech:
        - cc_allergen, cc_biotechnology, cc_disruption_phenotype, cc_disease
        - ft_mutagen, cc_pharmaceutical, cc_toxic_dose
        
        Subcellular location:
        - ft_intramem, cc_subcellular_location, ft_topo_dom, ft_transmem
        
        PTM / Processing:
        - ft_chain, ft_crosslnk, ft_disulfid, ft_carbohyd, ft_init_met, ft_lipid
        - ft_mod_res, ft_peptide, cc_ptm, ft_propep, ft_signal, ft_transit
        
        Structure:
        - structure_3d, ft_strand, ft_helix, ft_turn
        
        Publications:
        - lit_pubmed_id
        
        Date:
        - date_created, date_modified, date_sequence_modified, version
        
        Family & Domains:
        - ft_coiled, ft_compbias, cc_domain, ft_domain, ft_motif, protein_families
        - ft_region, ft_repeat, ft_zn_fing
        
        Cross-references:
        - See https://www.uniprot.org/help/return_fields for cross-reference fields
    
    format: Response format. One of: 'toon' (default) or 'json'.
        - 'toon': Returns response in TOON format (token-efficient compression)
        - 'json': Returns response in JSON format

Returns:
    When format='toon': TOON-formatted string with:
    - results: Array of fetched protein entries
    - found: Number of entries successfully retrieved
    - requested: Number of IDs that were requested
    
    When format='json': JSON object with:
    - results: Array of fetched protein entries
    - found: Number of entries successfully retrieved
    - requested: Number of IDs that were requested
"""


def _uniprot_search_impl(
    query: str,
    database: str = "uniprotkb",
    limit: int = 10,
    fields: list[str] | None = None,
    cursor: str | None = None,
    format: str = "toon",
) -> dict[str, Any] | str:
    """
    Implementation of UniProt search.

    This is the underlying implementation, separated from the tool decorator
    for testability.
    """
    # Validate inputs
    db = validate_database(database)

    if not query or not query.strip():
        raise ValueError("Query string cannot be empty")

    if limit < 1 or limit > 100:
        raise ValueError("Limit must be between 1 and 100")
    
    if format not in ("toon", "json"):
        raise ValueError("Format must be 'toon' or 'json'")

    # Decode cursor to get offset
    offset = 0
    if cursor:
        offset = decode_cursor(cursor)

    # Get the appropriate client
    client = get_client(db)

    # Build search parameters
    search_kwargs: dict[str, Any] = {"query": query}
    if fields:
        search_kwargs["fields"] = fields

    # Execute search and collect results
    results: list[dict[str, Any]] = []
    search_result = client.search(**search_kwargs)

    # Skip to offset and collect up to limit results
    record_iterator = search_result.each_record()

    # Skip to offset
    for _ in range(offset):
        try:
            next(record_iterator)
        except StopIteration:
            break

    # Collect results up to limit
    for record in record_iterator:
        results.append(dict(record))
        if len(results) >= limit:
            break

    result = paginate_results(results, offset, limit)
    return _format_response(result, format)


def _uniprot_fetch_impl(
    ids: list[str],
    database: str = "uniprotkb",
    fields: list[str] | None = None,
    format: str = "toon",
) -> dict[str, Any] | str:
    """
    Implementation of UniProt fetch.

    This is the underlying implementation, separated from the tool decorator
    for testability.
    """
    # Validate inputs
    db = validate_database(database)
    
    if format not in ("toon", "json"):
        raise ValueError("Format must be 'toon' or 'json'")

    if not ids:
        raise ValueError("IDs list cannot be empty")

    # Clean and validate IDs
    clean_ids = [id_.strip() for id_ in ids if id_ and id_.strip()]
    if not clean_ids:
        raise ValueError("No valid IDs provided")

    # Get the appropriate client
    client = get_client(db)

    # Fetch entries
    results: list[dict[str, Any]] = []

    # If fields are specified, use search with accession queries since
    # fetch_one/fetch_many don't support field selection
    if fields:
        # Build query for multiple accessions: accession:(P12345 OR P67890)
        if len(clean_ids) == 1:
            query = f"accession:{clean_ids[0]}"
        else:
            accession_list = " OR ".join(clean_ids)
            query = f"accession:({accession_list})"
        
        try:
            search_result = client.search(query=query, fields=fields)
            for record in search_result.each_record():
                results.append(dict(record))
                if len(results) >= len(clean_ids):
                    break
        except Exception:
            pass  # IDs not found, will be reflected in found count
    else:
        # Use fetch methods when no field selection is needed
        if len(clean_ids) == 1:
            # Single ID fetch
            try:
                record = client.fetch_one(clean_ids[0])
                if record:
                    results.append(dict(record))
            except Exception:
                pass  # ID not found, will be reflected in found count
        else:
            # Multiple IDs fetch
            try:
                records = client.fetch_many(clean_ids)
                for record in records:
                    results.append(dict(record))
            except Exception:
                pass  # Some IDs may not be found

    result = {
        "results": results,
        "found": len(results),
        "requested": len(clean_ids),
    }
    return _format_response(result, format)


# Register tools with FastMCP
@mcp.tool(description=SEARCH_DESCRIPTION)
def uniprot_search(
    query: str,
    database: str = "uniprotkb",
    limit: int = 10,
    fields: list[str] | None = None,
    cursor: str | None = None,
    format: str = "toon",
) -> dict[str, Any] | str:
    """Search the UniProt protein database."""
    return _uniprot_search_impl(query, database, limit, fields, cursor, format)


@mcp.tool(description=FETCH_DESCRIPTION)
def uniprot_fetch(
    ids: list[str],
    database: str = "uniprotkb",
    fields: list[str] | None = None,
    format: str = "toon",
) -> dict[str, Any] | str:
    """Fetch specific protein entries by their UniProt accession IDs."""
    return _uniprot_fetch_impl(ids, database, fields, format)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

