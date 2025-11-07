import requests

def register_pipeline_tools(app, base_url, auth, api_version):
    """
    Register Azure DevOps pipeline MCP tools.
    """

    @app.tool()
    def get_builds(definition_id: int = None):
        """Get all builds, optionally filtered by build definition ID."""
        url = f"{base_url}/_apis/build/builds"
        if definition_id:
            url += f"?definitions={definition_id}"
        url += f"&api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"builds": resp.json().get("value", [])}

    @app.tool()
    def get_build_changes(build_id: int):
        """Get all changes associated with a build."""
        url = f"{base_url}/_apis/build/builds/{build_id}/changes?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"changes": resp.json().get("value", [])}

    @app.tool()
    def get_build_definitions():
        """List all build definitions in the organization."""
        url = f"{base_url}/_apis/build/definitions?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"definitions": resp.json().get("value", [])}

    @app.tool()
    def get_build_definition_revisions(definition_id: int):
        """Get all revisions for a build definition."""
        url = f"{base_url}/_apis/build/definitions/{definition_id}/revisions?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"revisions": resp.json().get("value", [])}

    @app.tool()
    def get_build_log(build_id: int):
        """Get build logs for a specific build."""
        url = f"{base_url}/_apis/build/builds/{build_id}/logs?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"logs": resp.json().get("value", [])}

    @app.tool()
    def get_build_log_by_id(build_id: int, log_id: int):
        """Get a specific build log by log ID."""
        url = f"{base_url}/_apis/build/builds/{build_id}/logs/{log_id}?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"log": resp.json()}

    @app.tool()
    def get_build_status(build_id: int):
        """Get the current status of a build."""
        url = f"{base_url}/_apis/build/builds/{build_id}?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        build = resp.json()
        return {
            "build_id": build["id"],
            "status": build.get("status"),
            "result": build.get("result"),
            "queue_time": build.get("queueTime"),
            "start_time": build.get("startTime"),
            "finish_time": build.get("finishTime"),
        }

    @app.tool()
    def update_build_stage(build_id: int, stage_name: str, status: str):
        """Update the status of a stage in a build (if supported)."""
        url = f"{base_url}/_apis/build/builds/{build_id}?api-version={api_version}"
        payload = {"stageName": stage_name, "status": status}
        resp = requests.patch(url, json=payload, auth=auth)
        resp.raise_for_status()
        return {"message": f"Stage '{stage_name}' updated to '{status}'"}

    @app.tool()
    def get_run(run_id: int):
        """Get details for a pipeline run."""
        url = f"{base_url}/_apis/pipelines/runs/{run_id}?api-version={api_version}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"run": resp.json()}

    @app.tool()
    def list_runs(pipeline_id: int = None):
        """List all pipeline runs, optionally filtered by pipeline ID."""
        url = f"{base_url}/_apis/pipelines/runs?api-version={api_version}"
        if pipeline_id:
            url += f"&pipelineId={pipeline_id}"
        resp = requests.get(url, auth=auth)
        resp.raise_for_status()
        return {"runs": resp.json().get("value", [])}

    @app.tool()
    def run_pipeline(pipeline_id: int, branch: str = None):
        """Queue a new pipeline run."""
        url = f"{base_url}/_apis/pipelines/{pipeline_id}/runs?api-version={api_version}"
        payload = {}
        if branch:
            payload["resources"] = {"repositories": {"self": {"refName": branch}}}
        resp = requests.post(url, json=payload, auth=auth)
        resp.raise_for_status()
        return {"queued_run": resp.json()}

  
