"""
Script to create a Salesforce Case via REST API.

Usage:
    python create_case.py --subject "Login issue" --description "User cannot log in"

Requires:
    - .env file with SFDC_CLIENT_ID and SFDC_CLIENT_SECRET
    - pip install httpx python-dotenv
"""

import asyncio
import argparse
import json
import os
import httpx
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Configuration
SALESFORCE_TOKEN_ENDPOINT = os.getenv(
    "SALESFORCE_TOKEN_ENDPOINT",
    "https://login.salesforce.com/services/oauth2/token"
)
SALESFORCE_API_VERSION = os.getenv("SALESFORCE_API_VERSION", "v62.0")


def get_salesforce_credentials() -> tuple[str, str]:
    """Retrieve Salesforce credentials from environment variables."""
    client_id = os.getenv("SFDC_CLIENT_ID")
    client_secret = os.getenv("SFDC_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise ValueError("SFDC_CLIENT_ID and SFDC_CLIENT_SECRET must be set in .env")
    
    print("Credentials loaded from environment")
    return client_id, client_secret


async def get_salesforce_token(client_id: str, client_secret: str) -> tuple[str, str]:
    """Authenticate with Salesforce using OAuth 2.0 Client Credentials."""
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


async def create_case(
    access_token: str,
    instance_url: str,
    subject: str,
    description: str = "",
    status: str = "New",
    priority: str = "Medium",
    origin: str = "Web",
    case_type: str = None,
) -> dict:
    """Create a Case in Salesforce."""
    
    case_data = {
        "Subject": subject,
        "Status": status,
        "Priority": priority,
        "Origin": origin,
    }
    
    if description:
        case_data["Description"] = description
    if case_type:
        case_data["Type"] = case_type
    
    print(f"\nCreating Case:")
    print(json.dumps(case_data, indent=2))
    
    async with httpx.AsyncClient() as http_client:
        response = await http_client.post(
            f"{instance_url}/services/data/{SALESFORCE_API_VERSION}/sobjects/Case",
            json=case_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )
        
        result = response.json()
        
        if response.status_code == 201:
            print(f"\nCase created successfully!")
            print(f"Case ID: {result['id']}")
            return {"success": True, "id": result["id"], "data": case_data}
        else:
            print(f"\nFailed to create case: {response.status_code}")
            print(json.dumps(result, indent=2))
            return {"success": False, "error": result, "status_code": response.status_code}


async def main():
    parser = argparse.ArgumentParser(description="Create a Salesforce Case")
    parser.add_argument("--subject", "-s", required=True, help="Case subject (required)")
    parser.add_argument("--description", "-d", default="", help="Case description")
    parser.add_argument("--status", default="New", choices=["New", "Working", "Escalated", "Closed"])
    parser.add_argument("--priority", "-p", default="Medium", choices=["Low", "Medium", "High"])
    parser.add_argument("--origin", "-o", default="Web", choices=["Web", "Phone", "Email"])
    parser.add_argument("--type", "-t", dest="case_type", help="Case type (Question, Problem, Feature Request)")
    
    args = parser.parse_args()
    
    # Get credentials and authenticate
    client_id, client_secret = get_salesforce_credentials()
    access_token, instance_url = await get_salesforce_token(client_id, client_secret)
    
    # Create the case
    result = await create_case(
        access_token=access_token,
        instance_url=instance_url,
        subject=args.subject,
        description=args.description,
        status=args.status,
        priority=args.priority,
        origin=args.origin,
        case_type=args.case_type,
    )
    
    print(f"\nResult:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
