"""
Load sample support cases into the 'service-cases' AI Search index.

Creates the index if it doesn't exist (matching the schema used by the
Logic App), then pre-loads demo case data so the agent has cases to
search before any Salesforce cases flow through the Logic App.

Reads case .md files from the cases/ folder, parses metadata and
description, generates embeddings, and uploads documents.

Usage:
    python scripts/load_cases.py              # Load all cases
    python scripts/load_cases.py --dry-run    # Preview without uploading

Requires:
    - .env file with AZURE_OPENAI_ENDPOINT and AZURE_SEARCH_ENDPOINT
    - pip install azure-search-documents azure-identity openai python-dotenv
"""

import argparse
import re
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SearchableField,
    SimpleField,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch,
)
from openai import AzureOpenAI

# Configuration
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"]
AZURE_SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]
EMBEDDING_MODEL = "text-embedding-3-small"
INDEX_NAME = "service-cases"
EMBEDDING_DIMENSIONS = 1536

# Cases directory
SCRIPT_DIR = Path(__file__).parent
CASES_DIR = SCRIPT_DIR.parent / "cases"


def get_credential():
    """Get Azure credential for authentication."""
    return DefaultAzureCredential()


def create_openai_client(credential):
    """Create Azure OpenAI client with managed identity."""
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-06-01",
    )


def create_or_update_index(credential):
    """Create or update the service-cases index.

    Uses the same schema as the Logic App so either can populate the index.
    """
    index_client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=credential,
    )

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-algorithm",
                parameters={"metric": "cosine", "m": 4, "ef_construction": 400, "ef_search": 500},
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-algorithm",
            )
        ],
    )

    fields = [
        SearchableField(name="id", type=SearchFieldDataType.String, key=True, filterable=True, sortable=True, facetable=True),
        SearchableField(name="case_number", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="subject", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="description", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="vector-profile",
        ),
        SearchableField(name="status", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="priority", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="origin", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="case_type", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="contact_email", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="account_name", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SimpleField(name="created_date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True, facetable=True),
        SimpleField(name="closed_date", type=SearchFieldDataType.DateTimeOffset, filterable=True, sortable=True, facetable=True),
        SearchableField(name="resolution", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="owner_name", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
        SearchableField(name="salesforce_id", type=SearchFieldDataType.String, filterable=True, sortable=True, facetable=True),
    ]

    semantic_config = SemanticConfiguration(
        name="semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="subject"),
            content_fields=[
                SemanticField(field_name="description"),
                SemanticField(field_name="resolution"),
            ],
        ),
    )

    semantic_search = SemanticSearch(configurations=[semantic_config])

    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search,
    )

    print(f"Creating/updating index '{INDEX_NAME}'...")
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' ready.")


def parse_date(date_str: str) -> str | None:
    """Parse a date string like 'January 20, 2026' to ISO 8601 format for DateTimeOffset."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%B %d, %Y").replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except ValueError:
        return None


def parse_case_file(file_path: Path) -> dict:
    """Parse a case markdown file into the existing service-cases index schema.

    Existing index fields:
        id, case_number, subject, description, content_vector,
        status, priority, origin, case_type, contact_email,
        account_name, created_date (DateTimeOffset),
        closed_date (DateTimeOffset), resolution, owner_name,
        salesforce_id
    """
    content = file_path.read_text(encoding="utf-8")

    def extract(key: str) -> str:
        match = re.search(rf'\*\*{key}\*\*:\s*(.+?)(?:\s{{2,}}|\n)', content)
        return match.group(1).strip() if match else ""

    case_number = extract("Case Number")
    status = extract("Status")
    priority = extract("Priority")
    category = extract("Category")
    origin = extract("Origin")
    contact = extract("Contact")
    account = extract("Account")
    created = extract("Created")
    last_updated = extract("Last Updated")

    # Extract Subject section
    subject_match = re.search(
        r'^## Subject\s*\n(.+?)(?=\n## |\Z)', content, re.MULTILINE | re.DOTALL
    )
    subject = subject_match.group(1).strip() if subject_match else file_path.stem

    # Extract Description section (everything after ## Description until next ##)
    desc_match = re.search(
        r'^## Description\s*\n(.+?)(?=\n## |\Z)', content, re.MULTILINE | re.DOTALL
    )
    description = desc_match.group(1).strip() if desc_match else ""

    # Extract Resolution section
    res_match = re.search(
        r'^## Resolution\s*\n(.+?)(?=\n## |\Z)', content, re.MULTILINE | re.DOTALL
    )
    resolution = res_match.group(1).strip() if res_match else ""

    # Map category to case_type
    case_type = "Problem"
    if category and any(kw in category.lower() for kw in ["question", "how-to", "guidance"]):
        case_type = "Question"

    # Determine closed_date: if status is Resolved/Closed, use last_updated
    closed_date = None
    if status.lower() in ("resolved", "closed"):
        closed_date = parse_date(last_updated)

    doc = {
        "id": case_number.lower().replace("-", "") if case_number else file_path.stem.lower().replace("-", ""),
        "case_number": case_number,
        "subject": subject,
        "description": description,
        "status": status,
        "priority": priority,
        "origin": origin,
        "case_type": case_type,
        "contact_email": contact,
        "account_name": account,
        "created_date": parse_date(created),
        "closed_date": closed_date,
        "resolution": resolution,
        "owner_name": "",
        "salesforce_id": "",
    }

    return doc


def generate_embedding(client: AzureOpenAI, text: str) -> list[float]:
    """Generate embedding for text using Azure OpenAI."""
    if len(text) > 30000:
        text = text[:30000]

    response = client.embeddings.create(input=text, model=EMBEDDING_MODEL)
    return response.data[0].embedding


def load_documents(credential, openai_client):
    """Load all case markdown files into the existing search index."""
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential,
    )

    md_files = sorted(CASES_DIR.glob("CASE-*.md"))
    if not md_files:
        raise FileNotFoundError(f"No CASE-*.md files found in {CASES_DIR}")

    print(f"Found {len(md_files)} case files.")

    documents = []
    for i, file_path in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Processing: {file_path.name}")
        doc = parse_case_file(file_path)

        # Embed subject + description + resolution
        embedding_text = f"{doc['subject']}\n\n{doc['description']}\n\n{doc['resolution']}"
        doc["content_vector"] = generate_embedding(openai_client, embedding_text)

        documents.append(doc)

    print(f"\nUploading {len(documents)} documents to index '{INDEX_NAME}'...")
    result = search_client.merge_or_upload_documents(documents)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Successfully uploaded {succeeded}/{len(documents)} documents.")
    return succeeded


def main():
    parser = argparse.ArgumentParser(
        description="Pre-load sample cases into the existing service-cases AI Search index"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview cases without uploading to AI Search",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("NimbusCloud Demo — Service Case Pre-Loader")
    print("=" * 60)
    print(f"OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Search Endpoint: {AZURE_SEARCH_ENDPOINT}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Index Name: {INDEX_NAME}")
    print(f"Cases Directory: {CASES_DIR}")
    print("=" * 60)

    if args.dry_run:
        md_files = sorted(CASES_DIR.glob("CASE-*.md"))
        print(f"\n--- DRY RUN MODE: No documents will be uploaded ---\n")
        for i, fp in enumerate(md_files, 1):
            doc = parse_case_file(fp)
            print(f"[{i}/{len(md_files)}] {fp.name}")
            print(f"    Subject:  {doc['subject'][:70]}")
            print(f"    Status: {doc['status']}  Priority: {doc['priority']}  Type: {doc['case_type']}")
            print(f"    Account: {doc['account_name']}  Contact: {doc['contact_email']}")
            print()
        print(f"Total: {len(md_files)} cases would be uploaded.")
        return

    # Authenticate
    print("\nAuthenticating with Azure...")
    credential = get_credential()

    # Create OpenAI client
    print("Initializing OpenAI client...")
    openai_client = create_openai_client(credential)

    # Create/update the search index
    create_or_update_index(credential)

    # Load documents
    print("\nLoading case files...")
    count = load_documents(credential, openai_client)

    print("\n" + "=" * 60)
    print(f"Done! {count} cases pre-loaded into '{INDEX_NAME}' index.")
    print("=" * 60)


if __name__ == "__main__":
    main()
