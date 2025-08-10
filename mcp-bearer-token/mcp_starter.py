import asyncio
from typing import Annotated
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
from mcp import ErrorData, McpError
from mcp.server.auth.provider import AccessToken
from mcp.types import INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field

# --- Load environment variables ---
load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# --- Auth Provider ---
class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None

# --- Rich Tool Description model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None



# --- MCP Server Setup ---
mcp = FastMCP(
    "Dynamic Startup Idea Generator MCP Server",
    auth=SimpleBearerAuthProvider(TOKEN),
)

# --- Tool: validate (required by Puch) ---
@mcp.tool()
async def validate() -> str:
    return MY_NUMBER




# --- Tool: startup_idea_generator ---
STARTUP_IDEA_DESCRIPTION = RichToolDescription(
    description="Generate a comprehensive startup idea and execution plan based on a given noun or concept.",
    use_when="Use this tool when the user provides a noun or concept and wants a startup idea with execution plan.",
    side_effects="Returns a detailed startup idea with market analysis, execution plan, and growth strategy.",
)

@mcp.tool(description=STARTUP_IDEA_DESCRIPTION.model_dump_json())
async def startup_idea_generator(
    concept: Annotated[str, Field(description="The noun or concept to base the startup idea on (e.g., 'coffee', 'books', 'fitness')")],
) -> str:
    """
    Generate a comprehensive startup idea and execution plan based on a given noun or concept.
    """
    
    try:
        concept_lower = concept.lower().strip()
        concept_title = concept.title().strip()
        
        # Dynamic startup name generation based on concept
        def generate_startup_name(concept):
            name_patterns = [
                f"{concept_title}AI",
                f"{concept_title}Hub",
                f"{concept_title}Connect",
                f"Smart{concept_title}",
                f"{concept_title}Pro",
                f"{concept_title}Sync",
                f"{concept_title}Flow",
                f"{concept_title}Verse"
            ]
            # Use hash to consistently pick same name for same concept
            import hashlib
            hash_val = int(hashlib.md5(concept.encode()).hexdigest(), 16)
            return name_patterns[hash_val % len(name_patterns)]
        
        # Dynamic problem identification based on concept type
        def generate_problem(concept):
            common_problems = [
                f"People struggle to find quality {concept_lower} products and services",
                f"The {concept_lower} industry lacks personalization and modern technology",
                f"Consumers can't easily discover and connect with {concept_lower} communities",
                f"Traditional {concept_lower} solutions are fragmented and inefficient",
                f"There's no centralized platform for {concept_lower} enthusiasts to collaborate",
                f"Quality {concept_lower} experiences are expensive and hard to access"
            ]
            import hashlib
            hash_val = int(hashlib.md5(concept.encode()).hexdigest(), 16)
            return common_problems[hash_val % len(common_problems)]
        
        # Dynamic solution generation
        def generate_solution(concept):
            solutions = [
                f"AI-powered platform that personalizes {concept_lower} recommendations using machine learning",
                f"Community marketplace connecting {concept_lower} enthusiasts with experts and products",
                f"Smart {concept_lower} management system with real-time analytics and optimization",
                f"Social platform for {concept_lower} discovery with user-generated content and reviews",
                f"On-demand {concept_lower} services platform with quality verification",
                f"Subscription-based {concept_lower} curation service with expert recommendations"
            ]
            import hashlib
            hash_val = int(hashlib.md5(concept.encode()).hexdigest(), 16)
            return solutions[hash_val % len(solutions)]
        
        # Dynamic tech stack based on concept
        def generate_tech_stack(concept):
            base_tech = "React/Next.js, Python/FastAPI, PostgreSQL, Redis"
            specialized_tech = [
                "AI/ML, Computer Vision, IoT sensors",
                "Blockchain, Smart Contracts, Mobile SDK",
                "Real-time messaging, Video streaming, AR/VR",
                "Payment processing, Geolocation, Push notifications",
                "Analytics, Recommendation engine, Cloud infrastructure",
                "API integrations, Microservices, Docker/Kubernetes"
            ]
            import hashlib
            hash_val = int(hashlib.md5(concept.encode()).hexdigest(), 16)
            return f"{base_tech}, {specialized_tech[hash_val % len(specialized_tech)]}"
        
        # Dynamic revenue model
        def generate_revenue_model(concept):
            models = [
                f"Freemium subscriptions, {concept_lower} marketplace commissions, premium features",
                f"Subscription boxes, affiliate partnerships, enterprise solutions",
                f"Transaction fees, advertising revenue, premium memberships",
                f"Service commissions, certification programs, B2B licensing",
                f"Monthly subscriptions, pay-per-use services, corporate packages",
                f"Marketplace fees, premium listings, consultation services"
            ]
            import hashlib
            hash_val = int(hashlib.md5(concept.encode()).hexdigest(), 16)
            return models[hash_val % len(models)]
        
        # Generate dynamic startup idea
        startup_name = generate_startup_name(concept)
        problem = generate_problem(concept)
        solution = generate_solution(concept)
        tech_stack = generate_tech_stack(concept)
        revenue_model = generate_revenue_model(concept)
        
        # Create comprehensive startup response
        startup_response = f"""🚀 **STARTUP IDEA: {startup_name.upper()}**

💡 **Tagline**: Revolutionizing {concept_lower} through AI and community

🎯 **Problem**: {problem}

🔧 **Solution**: {solution}

⭐ **Unique Value**: First AI-powered {concept_lower} platform combining personalization with community engagement

🛠️ **Tech Stack**: {tech_stack}

💰 **Revenue Model**: {revenue_model}

📈 **3-Phase Execution Plan**:
**Phase 1 (Months 1-4)**: Build MVP, validate with 100+ users, gather feedback
**Phase 2 (Months 5-12)**: Scale platform, add premium features, mobile app launch
**Phase 3 (Months 13-24)**: Market expansion, enterprise solutions, Series A funding

🎯 **Target Market**: {concept_title} enthusiasts, professionals, and businesses

🚀 **Next Steps**:
1. Survey 50+ potential users about {concept_lower} pain points
2. Build prototype and test core features
3. Find co-founder with {concept_lower} industry expertise
4. Apply to accelerators and seek seed funding
5. Launch beta with early adopters

💡 **Innovation Opportunities**:
- AI-powered {concept_lower} recommendations
- Community-driven content and reviews
- Mobile-first user experience
- Integration with existing {concept_lower} tools

Ready to disrupt the {concept_lower} industry! 🎉"""
        
        return startup_response
        
    except Exception as e:
        return f"Error generating startup idea for '{concept}': {str(e)}"



# --- Health Check Endpoint (Removed - FastMCP doesn't support @mcp.get) ---
# Health check functionality built into FastMCP by default

# --- Run MCP Server ---
async def main():
    print("🚀 Starting MCP server on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())
