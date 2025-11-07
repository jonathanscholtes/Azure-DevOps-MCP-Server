import requests


def register_work_item_tools(app, base_url, auth, api_version):
    """
    Register Azure DevOps MCP tools for managing Work Items.
    """

    @app.tool()
    def my_work_items(project: str):
        """
        Get the authenticated user's assigned work items.
        """
        url = f"{base_url}/{project}/_apis/wit/wiql?api-version={api_version}"
        query = {
            "query": """
                SELECT [System.Id], [System.Title], [System.State]
                FROM workitems
                WHERE [System.AssignedTo] = @Me
                ORDER BY [System.ChangedDate] DESC
            """
        }
        resp = requests.post(url, json=query, auth=auth)
        resp.raise_for_status()
        work_items = [w["id"] for w in resp.json().get("workItems", [])]
        return {"work_item_ids": work_items}

    @app.tool()
    def list_backlogs(project: str):
        """
        List backlog categories (Epics, Features, Stories, etc.).
        """
        url = f"{base_url}/{project}/_apis/work/backlogconfiguration?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        categories = [c["name"] for c in resp.json().get("workItemCategories", [])]
        return {"backlogs": categories}

    @app.tool()
    def list_backlog_work_items(project: str, backlog_category: str):
        """
        List work items under a specific backlog category.
        Example: backlog_category='Microsoft.EpicCategory'
        """
        url = f"{base_url}/{project}/_apis/work/backlogs/{backlog_category}/workItems?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        items = [i["workItemId"] for i in resp.json().get("workItems", [])]
        return {"work_item_ids": items}

    @app.tool()
    def get_work_item(project: str, work_item_id: int):
        """Retrieve a single work item by ID."""
        url = f"{base_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return resp.json()

    @app.tool()
    def get_work_items_batch_by_ids(project: str, ids: list[int]):
        """Retrieve multiple work items by their IDs."""
        ids_str = ",".join(map(str, ids))
        url = f"{base_url}/{project}/_apis/wit/workitems?ids={ids_str}&api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"work_items": resp.json().get("value", [])}

    @app.tool()
    def create_work_item(project: str, work_item_type: str, fields: dict):
        """
        Create a new work item.
        Example: create_work_item("MyProject", "Task", {"System.Title": "New Task"})
        """
        url = f"{base_url}/{project}/_apis/wit/workitems/${work_item_type}?api-version={api_version}"
        patch_ops = [{"op": "add", "path": f"/fields/{k}", "value": v} for k, v in fields.items()]
        headers = {"Content-Type": "application/json-patch+json"}
        resp = requests.post(url, json=patch_ops, headers=headers, auth=auth)
        resp.raise_for_status()
        return resp.json()

    @app.tool()
    def update_work_item(project: str, work_item_id: int, fields: dict):
        """
        Update an existing work item by ID.
        Example: update_work_item("MyProject", 1234, {"System.State": "Closed"})
        """
        url = f"{base_url}/{project}/_apis/wit/workitems/{work_item_id}?api-version={api_version}"
        patch_ops = [{"op": "add", "path": f"/fields/{k}", "value": v} for k, v in fields.items()]
        headers = {"Content-Type": "application/json-patch+json"}
        resp = requests.patch(url, json=patch_ops, headers=headers, auth=auth)
        resp.raise_for_status()
        return resp.json()

    @app.tool()
    def list_work_item_comments(project: str, work_item_id: int):
        """List comments for a specific work item."""
        url = f"{base_url}/{project}/_apis/wit/workItems/{work_item_id}/comments?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        comments = [
            {"id": c["id"], "text": c["text"], "createdBy": c["createdBy"]["displayName"]}
            for c in resp.json().get("comments", [])
        ]
        return {"comments": comments}

    @app.tool()
    def add_work_item_comment(project: str, work_item_id: int, text: str):
        """Add a comment to a specific work item."""
        url = f"{base_url}/{project}/_apis/wit/workItems/{work_item_id}/comments?api-version={api_version}"
        resp = requests.post(url, json={"text": text}, auth=auth)
        resp.raise_for_status()
        return {"comment": resp.json()}

    @app.tool()
    def get_work_items_for_iteration(project: str, team: str, iteration_id: str):
        """Get all work items assigned to a specific iteration for a team."""
        url = f"{base_url}/{project}/{team}/_apis/work/teamsettings/iterations/{iteration_id}/workitems?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"work_items": resp.json().get("workItems", [])}

  
