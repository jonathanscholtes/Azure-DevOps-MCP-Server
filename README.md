# Azure DevOps MCP Server (HTTP-Streamable)

> ⚠️ **Active Development Notice**  
> This project is currently under active development and may include breaking changes.  
> Updates are frequent and could impact stability or functionality.  
> This notice will be removed once a stable release is reached.

---

## 🧩 Overview  

The **Azure DevOps MCP Server** enables dynamic tool calling for Azure DevOps services, allowing **agentic integration with Copilot Studio MCP Tools**.  
It is deployed as a container image to **Azure Container Registry** and runs on **Azure Container Apps** for scalable, secure remote access.

---

## 🚀 Key Features  

- FastMCP-based Python server for Azure DevOps automation  
- Modular tool domains (Core, Work, Work Items, Repositories, Pipelines, etc.)  
- Secure authentication using an Azure DevOps Personal Access Token (PAT)  
- Fully compatible with **Copilot Studio** and **Azure AI Foundry Agents**  
- Designed for easy extensibility and rapid iteration  


![design](/media/design.png)

---

## 🛠️ Core Steps for Solution Implementation

Follow these key steps to deploy and configure the solution:

### 1️⃣ [**Deploy the Solution**](docs/deployment.md)
- Detailed instructions for deployment, including prerequisites and configuration steps.  

---

## ♻️ Clean-Up  

After completing the workshop or testing, delete any unused Azure resources or remove the entire Resource Group to avoid additional charges.

---

## 📜 License  

This project is licensed under the [MIT License](LICENSE.md), permitting commercial and non-commercial use with proper attribution.

---

## ⚖️ Disclaimer  

This project and related materials are provided **"as-is"** without warranties of any kind.  
They are intended for **educational and demonstration purposes**.  
Users assume all responsibility for deployment and usage in their own environments.
