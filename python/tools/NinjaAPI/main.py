"""Parse API Docs and Talk to NinjaRMM API."""

import pprint
import json
import ninja_api_auth


api = ninja_api_auth.NinjaRMMAPI()

sorted_paths = api.get_docs_sorted_paths()
pprint.pprint(
    api.request("get", sorted_paths["system"]["methods"]["get"]["getOrganizations"]["path"])
    )

# Write the API documentation to a file.
with open("ninja_api_docs.json", "w", encoding="utf-8") as file:
    json.dump(sorted_paths, file, indent=4)
