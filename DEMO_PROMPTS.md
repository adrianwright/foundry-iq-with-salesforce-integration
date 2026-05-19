# ZavaCloud Helpdesk Agent — Demo Prompts

Use these prompts in the Foundry Playground or the custom chat UI. Each prompt is written from the perspective of a **customer service representative** talking to the AI assistant.

---

## 1. Knowledge Base Lookup (No Customer ID Needed)

> How do I troubleshoot VPN connectivity issues when accessing ZavaCloud?

> What are the steps for setting up multi-factor authentication with ZavaID?

> How does ZavaVault file permission inheritance work after a workspace migration?

> What are the API rate limits for ZavaAPI REST endpoints?

---

## 2. KB + Forum Cross-Reference

> A user says their VPN connection keeps timing out with 504 errors when trying to reach ZavaCloud. What should I tell them?

> An admin is preparing for a Section 508 accessibility audit. What resources do we have?

> We need to do a bulk workspace clone of 200+ ZavaBoard workspaces for the new quarter. Any tips or known issues?

---

## 3. Case Lookup (Provide Customer ID)

> I'm working with customer 100030. Can you pull up their open cases?

> Customer ID 100025 is calling about an MFA issue. Do they have any existing cases?

---

## 4. Case Creation (End-to-End Flow)

> I'm helping customer 100030. They're reporting that ZavaConnect audio drops every 15-20 seconds when using Bluetooth headsets. It's affecting about 30 employees. Can we create a high priority case for this?

> Customer 100025 is having issues with their OAuth integration breaking after a JWKS certificate rotation. Slack and Jira integrations both stopped working. Please create a case.

---

## 5. Multi-Step: Research Then Escalate

> Customer 100030 is asking about ZavaDocs offline sync errors after a long flight. Can you check the knowledge base for guidance and see if they already have a case open for this?

> I'm on the phone with customer 100025. They say 40% of their users can't log in after the latest iOS update broke MFA push notifications. Check the KB and forums for known issues, then let's create a case if needed.

---

## 6. MCP Tool Test (CRM Case Creation via APIM)

> Create a test case with subject "MCP Integration Test" and priority Low.

---

## Notes

- **Customer IDs in test data**: 100025, 100030 (used in the loaded cases)
- **Knowledge base**: 15 articles covering ZavaHub, ZavaConnect, ZavaDocs, ZavaBoard, ZavaVault, ZavaID, ZavaAdmin, and ZavaAPI
- **Forum posts**: 13 community posts mirroring KB topics with real-world workarounds
- **Cases in CRM**: 13 pre-loaded cases across all topic areas
