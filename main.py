import asyncio
import json
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import websockets
from mcp.server.fastmcp import FastMCP, Context
from mcp.types import Prompt, PromptArgument, PromptMessage, TextContent, GetPromptResult

# Configuration
BINANCE_WS_URL = "wss://fstream.binance.com/ws/!forceOrder@arr"
MAX_LIQUIDATIONS = 1000  # Maximum number of liquidation events to store

# Data structure for liquidation events
@dataclass
class LiquidationEvent:
    symbol: str
    side: str  # BUY or SELL
    price: float
    quantity: float
    timestamp: int

# Application context for managing WebSocket and data
@dataclass
class AppContext:
    binance_ws: Optional[websockets.WebSocketClientProtocol]
    liquidations: List[LiquidationEvent]

# Lifespan management for WebSocket connection
@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle: WebSocket connection"""
    liquidations = []
    binance_ws = None
    try:
        async with websockets.connect(BINANCE_WS_URL) as binance:
            binance_ws = binance
            ctx = AppContext(
                binance_ws=binance_ws,
                liquidations=liquidations
            )
            # Start WebSocket listener
            asyncio.create_task(listen_binance_liquidations(ctx))
            yield ctx
    finally:
        if binance_ws:
            await binance_ws.close()

# WebSocket listener for Binance liquidations
async def listen_binance_liquidations(ctx: AppContext):
    """Listen for liquidation events from Binance WebSocket"""
    if not ctx.binance_ws:
        return
    try:
        async for message in ctx.binance_ws:
            data = json.loads(message)
            event_data = data.get('o', {})
            event = LiquidationEvent(
                symbol=event_data.get('s', ''),
                side=event_data.get('S', ''),
                price=float(event_data.get('p', 0)),
                quantity=float(event_data.get('q', 0)),
                timestamp=int(event_data.get('T', 0))
            )
            ctx.liquidations.append(event)
            # Maintain max 1000 events
            if len(ctx.liquidations) > MAX_LIQUIDATIONS:
                ctx.liquidations.pop(0)
    except Exception as e:
        ctx.liquidations.append(LiquidationEvent(
            symbol="ERROR",
            side="NONE",
            price=0.0,
            quantity=0.0,
            timestamp=int(asyncio.get_event_loop().time() * 1000),
        ))

# Initialize FastMCP server
mcp = FastMCP(
    name="Crypto Liquidations MCP",
    lifespan=app_lifespan,
    dependencies=["websockets"]
)

# Tool: Get latest liquidations
@mcp.tool()
def get_latest_liquidations(limit: int = 10, ctx: Context | None = None) -> str:
    """Retrieve the latest liquidation events from Binance in a table format.

    Args:
        limit (int): The maximum number of liquidation events to return (default: 10, max: 1000).
        ctx (Context, optional): The MCP context for logging and server interaction. Defaults to None.

    Returns:
        str: A Markdown table containing the latest liquidation events, sorted by timestamp in descending order.
    """
    app_ctx = ctx.request_context.lifespan_context if ctx else mcp.get_context().request_context.lifespan_context
    filtered = [vars(event) for event in app_ctx.liquidations]
    filtered = sorted(filtered, key=lambda x: x['timestamp'], reverse=True)[:min(limit, MAX_LIQUIDATIONS)]
    if ctx:
        ctx.info(f"Retrieved {len(filtered)} latest liquidation events")
    
    # Generate Markdown table
    if not filtered:
        return "No liquidation events available."
    table = "| Symbol | Side | Price | Quantity | Time |\n"
    table += "|--------|------|-------|----------|------|\n"
    for event in filtered:
        dt = datetime.fromtimestamp(event['timestamp'] / 1000.0)
        time_str = dt.strftime("%H:%M:%S")
        table += f"| {event['symbol']} | {event['side']} | {event['price']} | {event['quantity']} | {time_str} |\n"
    return table

# Prompt: Analyze liquidation trends
@mcp.prompt()
def analyze_liquidations() -> GetPromptResult:
    """Generate a prompt to analyze liquidation trends across all symbols"""
    return GetPromptResult(
        description="Analyze liquidation trends for all symbols",
        messages=[
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="Please analyze the recent liquidation events from Binance. "
                         "Provide insights on the frequency, volume, and market impact across all symbols. "
                         "Use the output of the get_latest_liquidations tool for data."
                )
            ),
            PromptMessage(
                role="user",
                content=TextContent(
                    type="text",
                    text="Use the get_latest_liquidations tool with limit=10 to retrieve recent liquidation data."
                )
            )
        ]
    )

# Run the server
if __name__ == "__main__":
    mcp.run()