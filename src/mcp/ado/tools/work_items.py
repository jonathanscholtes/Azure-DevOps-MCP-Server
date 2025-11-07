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
    def get_work_item_by_title(project: str, title: str):
        """
        Find a work item ID by its title.
        """
        url = f"{base_url}/{project}/_apis/wit/wiql?api-version={api_version}"
        query = {
            "query": f"""
                SELECT [System.Id]
                FROM workitems
                WHERE [System.Title] = '{title}'
            """
        }
        resp = requests.post(url, json=query, auth=auth)
        resp.raise_for_status()
        work_items = resp.json().get("workItems", [])
        if not work_items:
            return {"error": f"No work item found with title '{title}'"}
        return {"work_item_id": work_items[0]["id"]}

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


    # ------------------------------
    # New: Summarize work item hierarchy
    # ------------------------------

    def get_child_work_items(project: str, work_item_id: int):
        """Fetch child work items (Features/Stories)"""
        url = f"{base_url}/{project}/_apis/wit/workitems/{work_item_id}?$expand=relations&api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        data = resp.json()
        children = []
        for rel in data.get("relations", []):
            if rel["rel"] == "System.LinkTypes.Hierarchy-Forward":
                child_id = int(rel["url"].split("/")[-1])
                child_item = get_work_item(project, child_id)
                children.append(child_item)
        return children

    def get_blockers(project: str, work_item_id: int):
        """Fetch items that block this work item"""
        url = f"{base_url}/{project}/_apis/wit/workitems/{work_item_id}?$expand=relations&api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        blockers = []
        for rel in resp.json().get("relations", []):
            if rel["rel"] == "System.LinkTypes.Dependency-Forward":
                blocker_id = int(rel["url"].split("/")[-1])
                blocker_item = get_work_item(project, blocker_id)
                blockers.append(blocker_item)
        return blockers

    @app.tool()
    def summarize_work_item_status(project: str, work_item_id: int):
        """
        Returns a detailed summary of a work item:
        - Title, type, state
        - Children (Features/Stories)
        - Blockers
        """
        main_item = get_work_item(project, work_item_id)

        # Get child items
        children = get_child_work_items(project, work_item_id)

        # Add blocker info for each child
        for child in children:
            child["blocked_by"] = get_blockers(project, child["id"])

        return {
            "work_item": main_item,
            "children": children
        }

  
