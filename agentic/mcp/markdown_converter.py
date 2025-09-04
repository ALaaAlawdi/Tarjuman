from langchain_mcp_adapters.client import MultiServerMCPClient


class MarkdownConverterMCP:
    def __init__(self):
        self._client = MultiServerMCPClient(
            {
                "pandoc": {
                    "command": "uvx",
                    "transport": "stdio",
                    "args": ["mcp-pandoc"],
                }
            }
        )

    async def tools(self):
        return await self._client.get_tools()
