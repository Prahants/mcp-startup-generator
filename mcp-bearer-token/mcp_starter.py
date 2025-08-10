import asyncio
from typing import Annotated
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from mcp import ErrorData, McpError
from mcp.types import TextContent, ImageContent, INVALID_PARAMS, INTERNAL_ERROR
from pydantic import BaseModel, Field, AnyUrl

import markdownify
import httpx
import readabilipy

# --- Load environment variables ---
load_dotenv()

TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"

# --- Auth Provider (Simplified for deployment) ---
# Authentication temporarily disabled for Render deployment

# --- Rich Tool Description model ---
class RichToolDescription(BaseModel):
    description: str
    use_when: str
    side_effects: str | None = None

# --- Fetch Utility Class ---
class Fetch:
    USER_AGENT = "Puch/1.0 (Autonomous)"

    @classmethod
    async def fetch_url(
        cls,
        url: str,
        user_agent: str,
        force_raw: bool = False,
    ) -> tuple[str, str]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    follow_redirects=True,
                    headers={"User-Agent": user_agent},
                    timeout=30,
                )
            except httpx.HTTPError as e:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url}: {e!r}"))

            if response.status_code >= 400:
                raise McpError(ErrorData(code=INTERNAL_ERROR, message=f"Failed to fetch {url} - status code {response.status_code}"))

            page_raw = response.text

        content_type = response.headers.get("content-type", "")
        is_page_html = "text/html" in content_type

        if is_page_html and not force_raw:
            return cls.extract_content_from_html(page_raw), ""

        return (
            page_raw,
            f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
        )

    @staticmethod
    def extract_content_from_html(html: str) -> str:
        """Extract and convert HTML content to Markdown format."""
        ret = readabilipy.simple_json.simple_json_from_html_string(html, use_readability=True)
        if not ret or not ret.get("content"):
            return "<error>Page failed to be simplified from HTML</error>"
        content = markdownify.markdownify(ret["content"], heading_style=markdownify.ATX)
        return content

    @staticmethod
    async def google_search_links(query: str, num_results: int = 5) -> list[str]:
        """
        Perform a scoped DuckDuckGo search and return a list of job posting URLs.
        (Using DuckDuckGo because Google blocks most programmatic scraping.)
        """
        ddg_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        links = []

        async with httpx.AsyncClient() as client:
            resp = await client.get(ddg_url, headers={"User-Agent": Fetch.USER_AGENT})
            if resp.status_code != 200:
                return ["<error>Failed to perform search.</error>"]

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", class_="result__a", href=True):
            href = a["href"]
            if "http" in href:
                links.append(href)
            if len(links) >= num_results:
                break

        return links or ["<error>No results found.</error>"]

# --- MCP Server Setup ---
mcp = FastMCP(
    "Dynamic Startup Idea Generator MCP Server",
)

# --- Tool: validate (required by Puch) ---
@mcp.tool()
async def validate() -> str:
    return MY_NUMBER

# --- Tool: job_finder (now smart!) ---
JobFinderDescription = RichToolDescription(
    description="Smart job tool: analyze descriptions, fetch URLs, or search jobs based on free text.",
    use_when="Use this to evaluate job descriptions or search for jobs using freeform goals.",
    side_effects="Returns insights, fetched job descriptions, or relevant job links.",
)

@mcp.tool(description=JobFinderDescription.model_dump_json())
async def job_finder(
    user_goal: Annotated[str, Field(description="The user's goal (can be a description, intent, or freeform query)")],
    job_description: Annotated[str | None, Field(description="Full job description text, if available.")] = None,
    job_url: Annotated[AnyUrl | None, Field(description="A URL to fetch a job description from.")] = None,
    raw: Annotated[bool, Field(description="Return raw HTML content if True")] = False,
) -> str:
    """
    Handles multiple job discovery methods: direct description, URL fetch, or freeform search query.
    """
    if job_description:
        return (
            f"📝 **Job Description Analysis**\n\n"
            f"---\n{job_description.strip()}\n---\n\n"
            f"User Goal: **{user_goal}**\n\n"
            f"💡 Suggestions:\n- Tailor your resume.\n- Evaluate skill match.\n- Consider applying if relevant."
        )

    if job_url:
        content, _ = await Fetch.fetch_url(str(job_url), Fetch.USER_AGENT, force_raw=raw)
        return (
            f"🔗 **Fetched Job Posting from URL**: {job_url}\n\n"
            f"---\n{content.strip()}\n---\n\n"
            f"User Goal: **{user_goal}**"
        )

    if "look for" in user_goal.lower() or "find" in user_goal.lower():
        links = await Fetch.google_search_links(user_goal)
        return (
            f"🔍 **Search Results for**: _{user_goal}_\n\n" +
            "\n".join(f"- {link}" for link in links)
        )

    raise McpError(ErrorData(code=INVALID_PARAMS, message="Please provide either a job description, a job URL, or a search query in user_goal."))


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

# Image inputs and sending images

MAKE_IMG_BLACK_AND_WHITE_DESCRIPTION = RichToolDescription(
    description="Convert an image to black and white and save it.",
    use_when="Use this tool when the user provides an image URL and requests it to be converted to black and white.",
    side_effects="The image will be processed and saved in a black and white format.",
)

@mcp.tool(description=MAKE_IMG_BLACK_AND_WHITE_DESCRIPTION.model_dump_json())
async def make_img_black_and_white(
    puch_image_data: Annotated[str, Field(description="Base64-encoded image data to convert to black and white")] = None,
) -> list[TextContent | ImageContent]:
    import base64
    import io

    from PIL import Image

    try:
        image_bytes = base64.b64decode(puch_image_data)
        image = Image.open(io.BytesIO(image_bytes))

        bw_image = image.convert("L")

        buf = io.BytesIO()
        bw_image.save(buf, format="PNG")
        bw_bytes = buf.getvalue()
        bw_base64 = base64.b64encode(bw_bytes).decode("utf-8")

        return [ImageContent(type="image", mimeType="image/png", data=bw_base64)]
    except Exception as e:
        raise McpError(ErrorData(code=INTERNAL_ERROR, message=str(e)))

# --- Health Check Endpoint (Removed - FastMCP doesn't support @mcp.get) ---
# Health check functionality built into FastMCP by default

# --- Run MCP Server ---
async def main():
    port = int(os.environ.get("PORT", 8086))
    print(f"🚀 Starting MCP server on http://0.0.0.0:{port}")
    await mcp.run_sse_async()

if __name__ == "__main__":
    asyncio.run(main())
