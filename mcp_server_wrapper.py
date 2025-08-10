import asyncio
import threading
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your MCP server components
from mcp_bearer_token.mcp_starter import mcp

class MCPServerWrapper:
    def __init__(self):
        self.server_thread = None
        self.is_running = False
        
    def start_server_background(self):
        """Start MCP server in background thread for Streamlit"""
        if not self.is_running:
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.server_thread.start()
            self.is_running = True
            
    def _run_server(self):
        """Run the MCP server"""
        try:
            # Run the MCP server
            mcp.run_sse()
        except Exception as e:
            print(f"MCP Server error: {e}")
            
    def get_server_info(self):
        """Get server information"""
        return {
            "status": "running" if self.is_running else "stopped",
            "auth_token": os.environ.get("AUTH_TOKEN", "Not set"),
            "phone": os.environ.get("MY_NUMBER", "Not set"),
            "tools": ["Startup Idea Generator", "Job Finder", "Image Processing", "Validation"]
        }

# Global server instance
mcp_wrapper = MCPServerWrapper()
