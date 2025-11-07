import requests

def register_work_tools(app, base_url, auth, api_version):
    """
    Register Azure DevOps Work MCP tools for managing iterations (sprints).
    """

    @app.tool()
    def list_team_iterations(project: str, team: str):
        """
        List all iterations (sprints) for a specific team within a project.
        """
        url = f"{base_url}/{project}/{team}/_apis/work/teamsettings/iterations?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        iterations = [
            {
                "id": i["id"],
                "name": i["name"],
                "path": i.get("path"),
                "attributes": i.get("attributes", {}),
            }
            for i in resp.json().get("value", [])
        ]
        return {"iterations": iterations}

    @app.tool()
    def create_iteration(project: str, name: str, path: str = None):
        """
        Create a new iteration (sprint) under the specified project.
        Example: create_iteration("MyProject", "Sprint 10", "Project\\Iteration")
        """
        url = f"{base_url}/{project}/_apis/wit/classificationnodes/iterations?api-version={api_version}"
        payload = {"name": name}
        if path:
            payload["path"] = path

        resp = requests.post(url, json=payload, auth=auth)
        resp.raise_for_status()
        return {"iteration": resp.json()}

    @app.tool()
    def assign_iteration(project: str, team: str, iteration_id: str):
        """
        Assign an existing iteration (by ID) to a specific team.
        """
        url = f"{base_url}/{project}/{team}/_apis/work/teamsettings/iterations/{iteration_id}?api-version={api_version}"
        payload = {"id": iteration_id}
        resp = requests.post(url, json=payload, auth=auth)
        resp.raise_for_status()
        return {"assigned_iteration": resp.json()}

  