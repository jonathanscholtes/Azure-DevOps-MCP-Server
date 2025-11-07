# src/MCP/ADO/tools/core.py
import requests

def register_core_tools(app, base_url, auth, api_version):
    """
    Register all core Azure DevOps MCP tools (projects, teams, identities).
    """

    @app.tool()
    def list_projects():
        """List all Azure DevOps projects in the organization."""
        url = f"{base_url}/_apis/projects?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        projects = [p["name"] for p in resp.json().get("value", [])]
        return {"projects": projects}

    @app.tool()
    def list_project_teams(project: str):
        """List all teams within a specific Azure DevOps project."""
        url = f"{base_url}/{project}/_apis/teams?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        teams = [{"id": t["id"], "name": t["name"]} for t in resp.json().get("value", [])]
        return {"teams": teams}

    @app.tool()
    def get_identity_ids(display_name: str):
        """Search for identity IDs by display name (user or group)."""
        url = (
            f"{base_url}/_apis/identities"
            f"?searchFilter=General&filterValue={display_name}"
            f"&queryMembership=None&api-version={api_version}"
        )
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        identities = [
            {
                "id": i["id"],
                "displayName": i["displayName"],
                "uniqueName": i.get("uniqueName"),
            }
            for i in resp.json().get("value", [])
        ]
        return {"identities": identities}
