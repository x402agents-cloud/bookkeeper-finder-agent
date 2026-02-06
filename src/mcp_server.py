"""
MCP Server for ContractorFinder Agent
Enables Claude, GPT, and other agents to use this tool
"""

import os
import sys
import json
import asyncio

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import agent

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not installed. Running in standalone mode.")

if MCP_AVAILABLE:
    # Create MCP server
    app = Server("contractor-finder")

    @app.list_tools()
    async def list_tools() -> list:
        """Define available tools"""
        return [
            Tool(
                name="find_contractors",
                description="Find licensed contractors by trade and location. Returns top 3 with ratings, reviews, and contact info. Charges $0.10 USDC per search.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "trade": {
                            "type": "string",
                            "description": "Type of contractor: plumber, electrician, roofer, HVAC, etc.",
                            "enum": ["plumber", "electrician", "roofer", "hvac", "painter", "landscaper", "contractor"]
                        },
                        "location": {
                            "type": "string",
                            "description": "City and state or zip code, e.g., 'Austin, TX' or '78701'"
                        },
                        "min_rating": {
                            "type": "number",
                            "description": "Minimum star rating (1-5)",
                            "minimum": 1,
                            "maximum": 5,
                            "default": 4.0
                        }
                    },
                    "required": ["trade", "location"]
                }
            )
        ]

    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list:
        """Handle tool calls"""
        
        if name == "find_contractors":
            # Call the agent
            result = agent.find_contractors(
                trade=arguments["trade"],
                location=arguments["location"],
                min_rating=arguments.get("min_rating", 4.0)
            )
            
            # Generate response
            response_text = agent.generate_response(result)
            
            return [TextContent(type="text", text=response_text)]
        
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    async def main():
        """Run the MCP server"""
        async with stdio_server() as streams:
            await app.run(
                streams[0],
                streams[1],
                app.create_initialization_options()
            )

    if __name__ == "__main__":
        asyncio.run(main())
else:
    # Standalone mode for testing
    if __name__ == "__main__":
        print("MCP Server - Standalone Test Mode")
        print("To use with Claude/GPT, install MCP: pip install mcp")
        print("\nTesting agent directly...")
        result = agent.find_contractors("plumber", "Los Angeles, CA")
        print(agent.generate_response(result))
