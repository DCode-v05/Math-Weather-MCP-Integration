from mcp.server.fastmcp import FastMCP

mcp=FastMCP("Math")

@mcp.tool()
def calculate(expr: str) -> float:
    """Evaluate math expression like '(3+5)*12'."""
    return eval(expr)

if __name__=="__main__":
    mcp.run(transport="stdio")