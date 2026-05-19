"""
Load Knowledge Base articles into Azure AI Search with vector embeddings.

Prerequisites:
    pip install azure-search-documents azure-identity openai

Usage:
    python scripts/load_knowledge_base.py
"""

import os
import re
import glob
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
INDEX_NAME = "helpdesk-knowledge"
EMBEDDING_DIMENSIONS = 1536

# Knowledge base directory
SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent / "KB"


def get_credential():
    """Get Azure credential for authentication."""
    return DefaultAzureCredential()


def create_openai_client(credential):
    """Create Azure OpenAI client with managed identity."""
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        azure_ad_token_provider=token_provider,
        api_version="2024-06-01"
    )


def create_or_update_index(credential):
    """Create or update the search index with vector support."""
    index_client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=credential
    )
    
    # Define vector search configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(name="hnsw-config")
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )
    
    # Define index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SimpleField(name="article_number", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="product", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="url_name", type=SearchFieldDataType.String),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBEDDING_DIMENSIONS,
            vector_search_profile_name="vector-profile"
        )
    ]
    
    # Define semantic configuration (required for Foundry IQ)
    semantic_config = SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            content_fields=[SemanticField(field_name="content")]
        )
    )
    
    semantic_search = SemanticSearch(configurations=[semantic_config])
    
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search,
        semantic_search=semantic_search
    )
    
    print(f"Creating/updating index '{INDEX_NAME}'...")
    index_client.create_or_update_index(index)
    print(f"Index '{INDEX_NAME}' ready.")


def parse_markdown_file(file_path: Path) -> dict:
    """Parse a markdown knowledge base file and extract metadata."""
    content = file_path.read_text(encoding="utf-8")
    
    # Extract title (first H1)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else file_path.stem
    
    # Extract article number (handles KB001 and KB-001 formats)
    article_match = re.search(r'\*\*Article Number:\*\*\s*(KB-?\d+)', content)
    article_number = article_match.group(1) if article_match else file_path.stem[:6].upper()
    
    # Extract product
    product_match = re.search(r'\*\*Product:\*\*\s*(.+?)(?:\s{2}|\n)', content)
    product = product_match.group(1).strip() if product_match else "ZavaCloud"
    
    # Extract category
    category_match = re.search(r'\*\*Category:\*\*\s*(.+?)(?:\s{2}|\n)', content)
    category = category_match.group(1).strip() if category_match else "General"
    
    # Generate URL-friendly name
    url_name = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
    
    return {
        "id": article_number.lower().replace(" ", "-"),
        "title": title,
        "content": content,
        "article_number": article_number,
        "product": product,
        "category": category,
        "url_name": url_name
    }


def generate_embedding(client: AzureOpenAI, text: str) -> list[float]:
    """Generate embedding for text using Azure OpenAI."""
    # Truncate if too long (max 8191 tokens, ~32000 chars to be safe)
    if len(text) > 30000:
        text = text[:30000]
    
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def load_documents(credential, openai_client):
    """Load all markdown files into the search index."""
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential
    )
    
    # Find all markdown files
    md_files = sorted(KB_DIR.glob("*.md"))
    print(f"Found {len(md_files)} knowledge base articles.")
    
    documents = []
    for i, file_path in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Processing: {file_path.name}")
        
        # Parse the markdown file
        doc = parse_markdown_file(file_path)
        
        # Generate embedding for the content
        embedding_text = f"{doc['title']}\n\n{doc['content']}"
        doc["content_vector"] = generate_embedding(openai_client, embedding_text)
        
        documents.append(doc)
    
    # Upload documents in batch
    print(f"\nUploading {len(documents)} documents to index...")
    result = search_client.upload_documents(documents)
    
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Successfully uploaded {succeeded}/{len(documents)} documents.")
    
    return succeeded


def main():
    print("=" * 60)
    print("ZavaCloud Knowledge Base Loader")
    print("=" * 60)
    print(f"OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Search Endpoint: {AZURE_SEARCH_ENDPOINT}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Index Name: {INDEX_NAME}")
    print(f"Knowledge Base: {KB_DIR}")
    print("=" * 60)
    
    # Authenticate
    print("\nAuthenticating with Azure...")
    credential = get_credential()
    
    # Create OpenAI client
    print("Initializing OpenAI client...")
    openai_client = create_openai_client(credential)
    
    # Create/update the search index
    create_or_update_index(credential)
    
    # Load documents
    print("\nLoading knowledge base articles...")
    count = load_documents(credential, openai_client)
    
    print("\n" + "=" * 60)
    print(f"Done! {count} articles loaded into '{INDEX_NAME}' index.")
    print("=" * 60)


if __name__ == "__main__":
    main()
