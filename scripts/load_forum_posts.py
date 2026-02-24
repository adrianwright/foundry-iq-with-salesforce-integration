"""
Load Community Forum Posts into Azure AI Search with vector embeddings.

Prerequisites:
    pip install azure-search-documents azure-identity openai

Usage:
    python scripts/load_forum_posts.py
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
INDEX_NAME = "community-forum-posts"
EMBEDDING_DIMENSIONS = 1536

# Forum posts directory
SCRIPT_DIR = Path(__file__).parent
FORUM_DIR = SCRIPT_DIR.parent / "forums"


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
    """Create or update the search index with vector support and semantic configuration."""
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


def parse_forum_metadata(content):
    """Extract metadata from forum post markdown."""
    metadata = {
        "article_number": "",
        "category": "",
        "product": ""
    }
    
    # Extract article number
    article_match = re.search(r'\*\*Article Number\*\*:\s*(.+)', content)
    if article_match:
        metadata["article_number"] = article_match.group(1).strip()
    
    # Extract category
    category_match = re.search(r'\*\*Category\*\*:\s*(.+)', content)
    if category_match:
        metadata["category"] = category_match.group(1).strip()
    
    # Extract product
    product_match = re.search(r'\*\*Product\*\*:\s*(.+)', content)
    if product_match:
        metadata["product"] = product_match.group(1).strip()
    
    return metadata


def load_forum_posts():
    """Load all markdown files from the forum-posts directory."""
    forum_files = sorted(FORUM_DIR.glob("*.md"))
    
    posts = []
    for file_path in forum_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract title (first # heading)
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else file_path.stem
        
        # Extract metadata
        metadata = parse_forum_metadata(content)
        
        posts.append({
            "file_name": file_path.name,
            "title": title,
            "content": content,
            "article_number": metadata["article_number"],
            "category": metadata["category"],
            "product": metadata["product"]
        })
    
    return posts


def generate_embeddings(openai_client, texts):
    """Generate embeddings for a list of texts."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


def upload_documents(credential, openai_client, posts):
    """Upload forum posts with embeddings to the search index."""
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential
    )
    
    # Prepare documents for upload
    print(f"\nUploading {len(posts)} documents to index...")
    
    # Generate embeddings in batches
    batch_size = 10
    for i in range(0, len(posts), batch_size):
        batch = posts[i:i + batch_size]
        texts = [post["content"] for post in batch]
        embeddings = generate_embeddings(openai_client, texts)
        
        # Create documents with embeddings
        documents = []
        for post, embedding in zip(batch, embeddings):
            doc = {
                "id": post["article_number"].replace("-", "_").replace(" ", "_") or post["file_name"].replace("-", "_").replace(".", "_"),
                "title": post["title"],
                "content": post["content"],
                "article_number": post["article_number"],
                "product": post["product"],
                "category": post["category"],
                "url_name": post["file_name"].replace(".md", "").lower(),
                "content_vector": embedding
            }
            documents.append(doc)
        
        # Upload batch
        result = search_client.upload_documents(documents=documents)
        
    print(f"Successfully uploaded {len(posts)}/{len(posts)} documents.")


def main():
    print("=" * 60)
    print("Community Forum Posts Loader")
    print("=" * 60)
    print(f"OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    print(f"Search Endpoint: {AZURE_SEARCH_ENDPOINT}")
    print(f"Embedding Model: {EMBEDDING_MODEL}")
    print(f"Index Name: {INDEX_NAME}")
    print(f"Forum Posts: {FORUM_DIR}")
    print("=" * 60)
    print()
    
    # Initialize
    print("Authenticating with Azure...")
    credential = get_credential()
    
    print("Initializing OpenAI client...")
    openai_client = create_openai_client(credential)
    
    # Create index
    create_or_update_index(credential)
    
    # Load forum posts
    print("\nLoading forum posts...")
    posts = load_forum_posts()
    print(f"Found {len(posts)} forum posts.")
    
    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] Processing: {post['file_name']}")
    
    # Upload to index
    upload_documents(credential, openai_client, posts)
    
    print()
    print("=" * 60)
    print(f"Done! {len(posts)} posts loaded into '{INDEX_NAME}' index.")
    print("=" * 60)


if __name__ == "__main__":
    main()
