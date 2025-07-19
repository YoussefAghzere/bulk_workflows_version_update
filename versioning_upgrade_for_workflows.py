import requests
import config_info
import json
import re
import copy


# Generate a token
token_url = f"{config_info.API_URL}/oauth/token?grant_type=client_credentials&client_id={config_info.CLIENT_ID}&client_secret={config_info.CLIENT_SECRET}"

payload = {}
headers = {
  'Accept': 'application/json',
  'Content-Type': 'x-www-form-urlencoded'
}
access_token = requests.request("POST", token_url, headers=headers, data=payload).json().get("access_token")


# GET & PATCH Workflow 
get_wf_url = f"{config_info.API_URL}/{config_info.NEW_API_VERSION}/workflows"
payload = {}
headers = {
  'Accept': 'application/json',
  'Authorization': f'Bearer {access_token}'
}
workflows = requests.request("GET", get_wf_url, headers=headers, data=payload).json()
# print(workflows)


for wf_item in workflows:
    wf = copy.deepcopy(wf_item)
    steps = wf.get("definition", {}).get("steps", {})
    wf_id = wf.get("id")
    patch_operations = []

    for key, value in steps.items():
        if value.get("actionId") == "sp:http":
            attributes = value.get("attributes", {})
            http_url = attributes.get("url")
            if http_url:
                updated_http_url = re.sub(
                    r"/(v[^/]+|beta)/",
                    f"/{config_info.NEW_API_VERSION}/",
                    http_url,
                    count=1
                )
                if updated_http_url != http_url:
                    patch_operations.append({
                        "op": "replace",
                        "path": f"/definition/steps/{key}/attributes/url",
                        "value": updated_http_url
                    })

    if patch_operations:
        update_wf_url = f"{config_info.API_URL}/{config_info.NEW_API_VERSION}/workflows/{wf_id}"

        headers = {
            'Content-Type': 'application/json-patch+json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }

        response = requests.patch(update_wf_url, headers=headers, data=json.dumps(patch_operations))

        print(f"PATCH status: {response.status_code}")
    else:
        print("No updates needed. All URLs are already up to date.")
