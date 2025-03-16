"""Parse API Docs and Talk to NinjaRMM API."""

import pprint
import json
import ninja_api_auth

api = ninja_api_auth.NinjaRMMAPI()

# Example of how to use the API to get a list of organizations.
sorted_docs = api.get_sorted_docs()
pprint.pprint(
    api.request("get", sorted_docs["paths"]["system"]["methods"]["get"]["getOrganizations"]["path"])
    )

# Write the API documentation to a file.
with open("ninja_api_docs.json", "w", encoding="utf-8") as file:
    json.dump(sorted_docs, file, indent=4)
