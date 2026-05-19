"""
Load Knowledge Base articles into Salesforce as Knowledge__kav records.

This script reads the KB/ markdown files, parses them into structured article data,
and creates Knowledge article records in Salesforce via the REST API (sObject: Knowledge__kav).

Salesforce Knowledge API Reference:
  - sObject: Knowledge__kav (Lightning Knowledge)
  - Create:  POST /services/data/v62.0/sobjects/Knowledge__kav
  - Publish: PATCH /services/data/v62.0/knowledgeManagement/articleVersions/masterVersions/{knowledgeArticleId}
  - Required fields: Title, UrlName, Language
  - Channel visibility: IsVisibleInApp, IsVisibleInCsp, IsVisibleInPkb, IsVisibleInPrm

Prerequisites:
    pip install httpx python-dotenv

Usage:
    # Load all KB articles (create as drafts)
    python scripts/load_knowledge_articles.py

    # Load and publish articles
    python scripts/load_knowledge_articles.py --publish

    # Load a single article
    python scripts/load_knowledge_articles.py --file KB/KB-001-grade-submission-sis-sync.md

    # Dry run — parse and display without creating
    python scripts/load_knowledge_articles.py --dry-run

    # Describe the Knowledge__kav sObject to discover custom fields
    python scripts/load_knowledge_articles.py --describe
"""

import asyncio
import argparse
import glob
import json
import os
import re
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------
SALESFORCE_TOKEN_ENDPOINT = os.getenv(
    "SALESFORCE_TOKEN_ENDPOINT",
    "https://login.salesforce.com/services/oauth2/token",
)
SALESFORCE_API_VERSION = os.getenv("SALESFORCE_API_VERSION", "v62.0")

# The sObject API name for Knowledge articles.
# Default is "Knowledge__kav" (Lightning Knowledge).
# Override via env var if your org uses a custom prefix.
KNOWLEDGE_SOBJECT = os.getenv("KNOWLEDGE_SOBJECT", "Knowledge__kav")

# Default language for articles (must match a language enabled in your org)
DEFAULT_LANGUAGE = os.getenv("KNOWLEDGE_LANGUAGE", "en_US")

# Paths
SCRIPT_DIR = Path(__file__).parent
KB_DIR = SCRIPT_DIR.parent / "KB"


# -------------------------------------------------------------------
# Salesforce Authentication (OAuth 2.0 Client Credentials)
# -------------------------------------------------------------------
def get_salesforce_credentials() -> tuple[str, str]:
    """Retrieve Salesforce credentials from environment variables."""
    client_id = os.getenv("SFDC_CLIENT_ID")
    client_secret = os.getenv("SFDC_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "SFDC_CLIENT_ID and SFDC_CLIENT_SECRET must be set in environment or .env file"
        )
    return client_id, client_secret


async def get_salesforce_token(client_id: str, client_secret: str) -> tuple[str, str]:
    """Authenticate with Salesforce using OAuth 2.0 Client Credentials flow."""
    print(f"Authenticating with Salesforce at: {SALESFORCE_TOKEN_ENDPOINT}")

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            SALESFORCE_TOKEN_ENDPOINT,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        if response.status_code != 200:
            print(f"Auth failed: {response.status_code}")
            print(response.text)
            raise Exception(f"Salesforce auth failed: {response.text}")

        token_data = response.json()
        print(f"Authenticated. Instance URL: {token_data['instance_url']}")

    return token_data["access_token"], token_data["instance_url"]


# -------------------------------------------------------------------
# Markdown Parsing
# -------------------------------------------------------------------
def parse_kb_markdown(file_path: str) -> dict:
    """
    Parse a KB markdown file into structured article data.

    Expected format:
        # Title
        **Article Number:** KB-001
        **Product:** ZavaCloud
        **Category:** Grading & Integration
        **Last Updated:** January 2026

        ## Overview
        ...body content...
    """
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")

    # Extract title (first heading)
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    # Extract metadata fields
    article_number = _extract_field(content, "Article Number")
    product = _extract_field(content, "Product")
    category = _extract_field(content, "Category")

    # Extract summary (first paragraph after ## Overview, or first paragraph after metadata)
    summary = _extract_summary(content)

    # Build URL-friendly name from article number or title
    url_name = _build_url_name(article_number, title)

    # Full content body (everything after the metadata block)
    body = _extract_body(content)

    return {
        "file": str(path),
        "title": title,
        "article_number": article_number or "",
        "product": product or "",
        "category": category or "",
        "summary": summary[:1000] if summary else "",  # Salesforce Summary max 1000 chars
        "url_name": url_name,
        "body": body,
    }


def _extract_field(content: str, field_name: str) -> str | None:
    """Extract a **Field:** Value line from markdown content."""
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _extract_summary(content: str) -> str:
    """Extract the first paragraph after ## Overview as the summary."""
    overview_match = re.search(
        r"##\s+Overview\s*\n+(.*?)(?=\n##|\Z)", content, re.DOTALL
    )
    if overview_match:
        # Take the first paragraph
        text = overview_match.group(1).strip()
        paragraphs = text.split("\n\n")
        return paragraphs[0].replace("\n", " ").strip()

    # Fallback: first non-metadata paragraph
    lines = content.split("\n")
    body_started = False
    para_lines = []
    for line in lines:
        if line.startswith("## "):
            body_started = True
            continue
        if body_started and line.strip():
            para_lines.append(line.strip())
        elif body_started and para_lines:
            break
    return " ".join(para_lines) if para_lines else ""


def _extract_body(content: str) -> str:
    """Extract the full article body (everything after metadata block)."""
    # Find the first ## heading and take everything from there
    match = re.search(r"(##\s+.+)", content, re.DOTALL)
    return match.group(1).strip() if match else content


def _build_url_name(article_number: str | None, title: str) -> str:
    """Build a URL-friendly name for the article."""
    base = article_number if article_number else title
    # Convert to lowercase, replace spaces/special chars with hyphens
    url_name = re.sub(r"[^a-zA-Z0-9]+", "-", base.lower()).strip("-")
    return url_name[:255]  # Salesforce max 255 chars


# -------------------------------------------------------------------
# Salesforce Knowledge API Operations
# -------------------------------------------------------------------
async def describe_knowledge_object(
    access_token: str, instance_url: str
) -> dict:
    """
    Describe the Knowledge__kav sObject to discover available fields.
    Useful for finding custom fields (e.g., Content__c, Body__c) in your org.

    GET /services/data/v62.0/sobjects/Knowledge__kav/describe
    """
    url = f"{instance_url}/services/data/{SALESFORCE_API_VERSION}/sobjects/{KNOWLEDGE_SOBJECT}/describe"

    async with httpx.AsyncClient() as http_client:
        response = await http_client.get(
            url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    if response.status_code != 200:
        print(f"Describe failed: {response.status_code}")
        print(response.text)
        return {}

    describe = response.json()
    return describe


def print_describe_summary(describe: dict):
    """Print a summary of Knowledge__kav fields, highlighting custom/writable fields."""
    fields = describe.get("fields", [])

    print(f"\n{'='*80}")
    print(f"sObject: {describe.get('name', 'Unknown')}")
    print(f"Label:   {describe.get('label', 'Unknown')}")
    print(f"Fields:  {len(fields)} total")
    print(f"{'='*80}\n")

    # Separate standard vs custom, show createable fields
    createable_fields = [f for f in fields if f.get("createable")]
    custom_fields = [f for f in createable_fields if f["name"].endswith("__c")]
    standard_fields = [f for f in createable_fields if not f["name"].endswith("__c")]

    print("CREATEABLE STANDARD FIELDS:")
    print(f"{'Name':<40} {'Type':<15} {'Required':<10} {'Label'}")
    print("-" * 100)
    for f in sorted(standard_fields, key=lambda x: x["name"]):
        required = "Yes" if not f.get("nillable") and not f.get("defaultedOnCreate") else ""
        print(f"{f['name']:<40} {f['type']:<15} {required:<10} {f.get('label', '')}")

    if custom_fields:
        print(f"\nCREATEABLE CUSTOM FIELDS:")
        print(f"{'Name':<40} {'Type':<15} {'Required':<10} {'Label'}")
        print("-" * 100)
        for f in sorted(custom_fields, key=lambda x: x["name"]):
            required = "Yes" if not f.get("nillable") and not f.get("defaultedOnCreate") else ""
            print(f"{f['name']:<40} {f['type']:<15} {required:<10} {f.get('label', '')}")
    else:
        print("\nNo custom fields found on this sObject.")

    # Show record types if any
    record_types = describe.get("recordTypeInfos", [])
    if record_types:
        print(f"\nRECORD TYPES:")
        for rt in record_types:
            default = " (default)" if rt.get("defaultRecordTypeMapping") else ""
            print(f"  {rt['recordTypeId']}  {rt['name']}{default}")


async def create_knowledge_article(
    access_token: str,
    instance_url: str,
    article_data: dict,
    custom_field_mapping: dict | None = None,
) -> dict:
    """
    Create a Knowledge article in Salesforce via the sObject API.

    POST /services/data/v62.0/sobjects/Knowledge__kav

    Required fields:
      - Title (str, max 255)
      - UrlName (str, max 255, unique, alphanumeric + hyphens)
      - Language (picklist, e.g. "en_US")

    Channel visibility (boolean, defaults to false):
      - IsVisibleInApp  — Articles tab
      - IsVisibleInCsp  — Customer Portal
      - IsVisibleInPkb  — Public Knowledge Base
      - IsVisibleInPrm  — Partner Portal

    Optional:
      - Summary (textarea, max 1000)
      - RecordTypeId (if multiple article types exist)

    Custom fields (org-specific, discovered via --describe):
      - Commonly: Content__c, Body__c, etc.
    """
    url = f"{instance_url}/services/data/{SALESFORCE_API_VERSION}/sobjects/{KNOWLEDGE_SOBJECT}"

    # Build the sObject payload with required + standard fields
    payload = {
        "Title": article_data["title"][:255],
        "UrlName": article_data["url_name"][:255],
        "Language": DEFAULT_LANGUAGE,
        "Summary": article_data.get("summary", "")[:1000],
        # Channel visibility — IsVisibleInApp is often read-only; set the ones the profile allows
        "IsVisibleInCsp": True,
        "IsVisibleInPkb": True,
        "IsVisibleInPrm": False,
    }

    # Map custom fields if provided (e.g., {"Content__c": "body", "Product__c": "product"})
    if custom_field_mapping:
        for sf_field, data_key in custom_field_mapping.items():
            if data_key in article_data and article_data[data_key]:
                payload[sf_field] = article_data[data_key]

    print(f"\nCreating article: {article_data['title']}")
    print(f"  UrlName:  {payload['UrlName']}")
    print(f"  Language: {payload['Language']}")

    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    result = response.json()

    if response.status_code == 201:
        article_id = result["id"]
        print(f"  ✓ Created (ID: {article_id})")
        return {"success": True, "id": article_id, "title": article_data["title"]}
    else:
        error_msg = json.dumps(result, indent=2)
        print(f"  ✗ Failed ({response.status_code}): {error_msg}")
        return {
            "success": False,
            "error": result,
            "status_code": response.status_code,
            "title": article_data["title"],
        }


async def publish_article(
    access_token: str,
    instance_url: str,
    article_version_id: str,
) -> bool:
    """
    Publish a Knowledge article by transitioning it from Draft to Online.

    To publish, we first need to get the KnowledgeArticleId from the article version,
    then use the Knowledge Management REST API:

    PATCH /services/data/v62.0/knowledgeManagement/articleVersions/masterVersions/{knowledgeArticleId}
    Body: {"publishStatus": "Online"}
    """
    # Step 1: Query the KnowledgeArticleId from the article version ID
    query = (
        f"SELECT KnowledgeArticleId FROM {KNOWLEDGE_SOBJECT} WHERE Id = '{article_version_id}'"
    )
    query_url = f"{instance_url}/services/data/{SALESFORCE_API_VERSION}/query"

    async with httpx.AsyncClient() as http_client:
        resp = await http_client.get(
            query_url,
            params={"q": query},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code != 200:
        print(f"  ✗ Failed to query KnowledgeArticleId: {resp.status_code}")
        print(f"    {resp.text}")
        return False

    records = resp.json().get("records", [])
    if not records:
        print(f"  ✗ No article found for version ID: {article_version_id}")
        return False

    knowledge_article_id = records[0]["KnowledgeArticleId"]

    # Step 2: Publish via Knowledge Management API
    publish_url = (
        f"{instance_url}/services/data/{SALESFORCE_API_VERSION}"
        f"/knowledgeManagement/articleVersions/masterVersions/{knowledge_article_id}"
    )

    async with httpx.AsyncClient() as http_client:
        resp = await http_client.patch(
            publish_url,
            json={"publishStatus": "Online"},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code in (200, 204):
        print(f"  ✓ Published (KnowledgeArticleId: {knowledge_article_id})")
        return True
    else:
        print(f"  ✗ Publish failed ({resp.status_code}): {resp.text}")
        return False


async def check_existing_articles(
    access_token: str,
    instance_url: str,
) -> list[str]:
    """Query existing Knowledge articles to avoid duplicates. Returns list of UrlNames."""
    query = f"SELECT UrlName FROM {KNOWLEDGE_SOBJECT} WHERE PublishStatus = 'Draft' OR PublishStatus = 'Online'"
    query_url = f"{instance_url}/services/data/{SALESFORCE_API_VERSION}/query"

    async with httpx.AsyncClient() as http_client:
        resp = await http_client.get(
            query_url,
            params={"q": query},
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

    if resp.status_code != 200:
        print(f"Warning: Could not check existing articles: {resp.status_code}")
        return []

    records = resp.json().get("records", [])
    return [r["UrlName"] for r in records]


# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
async def main():
    parser = argparse.ArgumentParser(
        description="Load KB markdown articles into Salesforce Knowledge (Knowledge__kav sObject)"
    )
    parser.add_argument(
        "--file", "-f",
        help="Path to a single KB markdown file to load. If omitted, loads all files from KB/.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Publish articles after creation (transition from Draft to Online).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and display articles without creating them in Salesforce.",
    )
    parser.add_argument(
        "--describe",
        action="store_true",
        help="Describe the Knowledge__kav sObject and list available fields, then exit.",
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        default=True,
        help="Skip articles whose UrlName already exists in Salesforce (default: True).",
    )
    parser.add_argument(
        "--custom-fields",
        type=str,
        default=None,
        help=(
            'JSON mapping of Salesforce custom field names to parsed data keys. '
            'Example: \'{"Content__c": "body", "Product__c": "product", "Category__c": "category"}\''
        ),
    )
    args = parser.parse_args()

    # Parse custom field mapping
    custom_field_mapping = None
    if args.custom_fields:
        try:
            custom_field_mapping = json.loads(args.custom_fields)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON for --custom-fields: {e}")
            return

    # Collect KB files to process
    if args.file:
        kb_files = [args.file]
    else:
        kb_files = sorted(glob.glob(str(KB_DIR / "KB-*.md")))

    if not kb_files:
        print(f"No KB files found in {KB_DIR}")
        return

    # Parse all markdown files
    print(f"\nParsing {len(kb_files)} KB article(s)...")
    articles = []
    for f in kb_files:
        article = parse_kb_markdown(f)
        articles.append(article)

    # Dry run: display parsed articles and exit
    if args.dry_run:
        print(f"\n{'='*80}")
        print("DRY RUN — Parsed articles (not creating in Salesforce)")
        print(f"{'='*80}")
        for i, a in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"  File:     {a['file']}")
            print(f"  Title:    {a['title']}")
            print(f"  Number:   {a['article_number']}")
            print(f"  Product:  {a['product']}")
            print(f"  Category: {a['category']}")
            print(f"  UrlName:  {a['url_name']}")
            print(f"  Summary:  {a['summary'][:120]}...")
            print(f"  Body:     {len(a['body'])} characters")
        print(f"\n{'='*80}")
        print(f"Total: {len(articles)} articles parsed. Use without --dry-run to create them.")
        return

    # Authenticate with Salesforce
    client_id, client_secret = get_salesforce_credentials()
    access_token, instance_url = await get_salesforce_token(client_id, client_secret)

    # Describe mode: show sObject fields and exit
    if args.describe:
        describe = await describe_knowledge_object(access_token, instance_url)
        if describe:
            print_describe_summary(describe)
        return

    # Check for existing articles to avoid duplicates
    existing_url_names = []
    if args.skip_existing:
        print("\nChecking for existing articles...")
        existing_url_names = await check_existing_articles(access_token, instance_url)
        if existing_url_names:
            print(f"  Found {len(existing_url_names)} existing article(s)")

    # Create articles
    print(f"\n{'='*80}")
    print(f"Creating {len(articles)} Knowledge article(s) in Salesforce")
    print(f"  sObject:  {KNOWLEDGE_SOBJECT}")
    print(f"  Language: {DEFAULT_LANGUAGE}")
    print(f"  Publish:  {'Yes' if args.publish else 'No (Draft)'}")
    if custom_field_mapping:
        print(f"  Custom fields: {json.dumps(custom_field_mapping)}")
    print(f"{'='*80}")

    results = {"created": [], "skipped": [], "failed": []}

    for article in articles:
        # Skip if already exists
        if args.skip_existing and article["url_name"] in existing_url_names:
            print(f"\n  ⊘ Skipping (already exists): {article['title']}")
            results["skipped"].append(article["title"])
            continue

        result = await create_knowledge_article(
            access_token,
            instance_url,
            article,
            custom_field_mapping=custom_field_mapping,
        )

        if result["success"]:
            results["created"].append(result)

            # Publish if requested
            if args.publish:
                published = await publish_article(
                    access_token, instance_url, result["id"]
                )
                if not published:
                    print(f"  ⚠ Article created but publish failed: {article['title']}")
        else:
            results["failed"].append(result)

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"  Created:  {len(results['created'])}")
    print(f"  Skipped:  {len(results['skipped'])}")
    print(f"  Failed:   {len(results['failed'])}")

    if results["failed"]:
        print("\nFailed articles:")
        for f in results["failed"]:
            print(f"  - {f['title']}: {json.dumps(f.get('error', {}))}")

    if results["created"]:
        print("\nCreated article IDs:")
        for c in results["created"]:
            print(f"  - {c['id']}: {c['title']}")


if __name__ == "__main__":
    asyncio.run(main())
