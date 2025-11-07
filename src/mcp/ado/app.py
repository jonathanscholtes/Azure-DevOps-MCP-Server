# src/mcp/ado/app.py

from mcp.server.fastmcp import FastMCP
import logging
from tools.core import register_core_tools
from tools.work import register_work_tools
from tools.work_items import register_work_item_tools
from tools.pipeline import register_pipeline_tools

from os import environ
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastMCP(
    name="Azure DevOps MCP",
    host="0.0.0.0",
     port=int(environ.get("MCP_PORT", 80))
)

MCP_ORG = environ["MCP_ORG"]
ORG_URL = environ["AZURE_DEVOPS_URL"]
ORG_URL = ORG_URL + MCP_ORG if MCP_ORG else ORG_URL # e.g. https://dev.azure.com/my-org

PAT = environ["AZURE_DEVOPS_PAT"]     # Personal Access Token
API_VERSION = "7.0"

if not ORG_URL or not PAT:
    raise EnvironmentError("AZURE_DEVOPS_URL and AZURE_DEVOPS_PAT must be set")



AUTH = ("", PAT)  # Basic auth with PAT as password, temp for quick build and testing


# Register all domain tools
register_core_tools(app, ORG_URL, AUTH, API_VERSION)
register_work_tools(app, ORG_URL, AUTH, API_VERSION)
register_work_item_tools(app, ORG_URL, AUTH, API_VERSION)
register_pipeline_tools(app, ORG_URL, AUTH, API_VERSION)
#register_repo_tools(app, ORG_URL, AUTH, API_VERSION)


if __name__ == "__main__":
    logger.info("Starting the FastMCP ADO...")
    logger.info(f"Service name: {environ.get('SERVICE_NAME', 'unknown')}")   
    app.run(transport="streamable-http")
