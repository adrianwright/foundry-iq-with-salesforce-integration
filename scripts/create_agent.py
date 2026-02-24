"""
Create the NimbusCloud IT Helpdesk agent in Azure AI Foundry.

Uses the Azure AI Projects SDK v2 (azure-ai-projects 2.x) with the new
Foundry Agents API (create_version / PromptAgentDefinition).

Usage:
    python scripts/create_agent.py

Environment variables (from .env):
    AZURE_AI_PROJECT_ENDPOINT  - AI Foundry project endpoint
    AZURE_OPENAI_DEPLOYMENT    - Model deployment name (e.g. gpt-5.2)
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

PROJECT_ENDPOINT = os.environ.get("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-5.2")
SEARCH_ENDPOINT = os.environ.get("AZURE_SEARCH_ENDPOINT", "")
KB_NAME = os.environ.get("AZURE_KB_NAME", "knowledgebase314")
KB_CONNECTION_NAME = os.environ.get("AZURE_KB_CONNECTION", "kb-knowledgebase314-56yau")
AGENT_NAME = "nimbuscloud-it-support-agent"

INSTRUCTIONS_FILE = Path(__file__).resolve().parent.parent / "AGENT_INSTRUCTIONS.md"

# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate():
    errors = []
    if not PROJECT_ENDPOINT:
        errors.append("AZURE_AI_PROJECT_ENDPOINT is not set")
    if not SEARCH_ENDPOINT:
        errors.append("AZURE_SEARCH_ENDPOINT is not set")
    if not INSTRUCTIONS_FILE.exists():
        errors.append(f"Instructions file not found: {INSTRUCTIONS_FILE}")
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    validate()

    print("=" * 60)
    print("NimbusCloud Agent Creator (Foundry Agents API v2)")
    print("=" * 60)
    print(f"Project Endpoint: {PROJECT_ENDPOINT}")
    print(f"Model Deployment: {MODEL_DEPLOYMENT}")
    print(f"Search Endpoint:  {SEARCH_ENDPOINT}")
    print(f"KB Name:          {KB_NAME}")
    print(f"KB Connection:    {KB_CONNECTION_NAME}")
    print(f"Agent Name:       {AGENT_NAME}")
    print("=" * 60)
    print()

    # --- Authenticate ---
    print("Authenticating with Azure...")
    credential = DefaultAzureCredential()

    # --- Create project client (v2 preview) ---
    project_client = AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential,
    )

    # --- Load system prompt ---
    print("Loading agent instructions...")
    instructions = INSTRUCTIONS_FILE.read_text(encoding="utf-8")
    print(f"  Loaded {len(instructions)} characters from AGENT_INSTRUCTIONS.md")

    # --- Configure MCP tool for Foundry IQ knowledge base ---
    mcp_endpoint = f"{SEARCH_ENDPOINT}/knowledgebases/{KB_NAME}/mcp?api-version=2025-11-01-preview"
    print(f"\nConfiguring KB MCP tool...")
    print(f"  MCP Endpoint: {mcp_endpoint}")

    mcp_kb_tool = MCPTool(
        server_label="knowledge-base",
        server_url=mcp_endpoint,
        require_approval="never",
        allowed_tools=["knowledge_base_retrieve"],
        project_connection_id=KB_CONNECTION_NAME,
    )

    # --- Create agent version (new Foundry Agents API) ---
    print("Creating agent...")
    agent = project_client.agents.create_version(
        agent_name=AGENT_NAME,
        definition=PromptAgentDefinition(
            model=MODEL_DEPLOYMENT,
            instructions=instructions,
            tools=[mcp_kb_tool],
        ),
    )
    print(f"  Agent created successfully!")
    print(f"  Agent ID:      {agent.id}")
    print(f"  Agent Name:    {agent.name}")
    print(f"  Agent Version: {agent.version}")

    # --- Summary ---
    print()
    print("=" * 60)
    print("Agent created. Next steps:")
    print("=" * 60)
    print()
    print("1. Open the Azure AI Foundry portal: https://ai.azure.com")
    print("2. Navigate to your project → Agents")
    print(f"3. Select '{AGENT_NAME}'")
    print("4. KB MCP tool is already attached with require_approval=never")
    print("5. Under Tools → MCP Server, add the APIM MCP endpoint URL")
    print("   from Step 5 of SETUP.md and enter the subscription key")
    print("6. Test the agent in the playground")
    print()


if __name__ == "__main__":
    main()
