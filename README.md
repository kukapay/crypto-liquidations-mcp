# Crypto Liquidations MCP
[![smithery badge](https://smithery.ai/badge/@kukapay/crypto-liquidations-mcp)](https://smithery.ai/server/@kukapay/crypto-liquidations-mcp)

An MCP server that streams real-time cryptocurrency liquidation events from Binance, enabling AI agents to react instantly to high-volatility market movements.

![License](https://img.shields.io/badge/license-MIT-green)
![Python Version](https://img.shields.io/badge/python-3.10-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)


## Features

- **Real-time Liquidation Streaming**: Connects to [Binance WebSocket](wss://fstream.binance.com/ws/!forceOrder@arr`) to capture liquidation events.
- **Liquidation Data Storage**: Maintains an in-memory list of up to 1000 liquidation events, with no persistent storage.
- **Tool: `get_latest_liquidations`**:
  - Retrieves the latest liquidation events in a Markdown table.
  - Columns: `Symbol`, `Side`, `Price`, `Quantity`, `Time` (HH:MM:SS format).
  - Parameters: `limit` (default 10).
- **Prompt: `analyze_liquidations`**:
  - Generates a prompt to analyze liquidation trends across all symbols, leveraging the `get_latest_liquidations` tool.

## Prerequisites

- **Python 3.10**: Required for compatibility.
- **uv**: Package and dependency manager (install instructions below).
- **Internet Access**: To connect to Binance WebSocket.

## Installation

### Installing via Smithery

To install Crypto Liquidations for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@kukapay/crypto-liquidations-mcp):

```bash
npx -y @smithery/cli install @kukapay/crypto-liquidations-mcp --client claude
```

### 1. Clone the Repository
```bash
git clone https://github.com/kukapay/crypto-liquidations-mcp.git
cd crypto-liquidations-mcp
```

### 2. Install Dependencies
Install required packages using `uv`:
```bash
uv sync
```

### 3. Integrate with an MCP Client
Configure your MCP client to connect to the server. For Claude Desktop:
```json
{
 "mcpServers": {
   "crypto-liquidations": {
     "command": "uv",
     "args": ["--directory", "/path/to/crypto-liquidations-mcp", "run", "main.py"]
   }
 }
}
```
   
## Usage

To get started, launch the MCP server to begin streaming liquidation events from Binance. The server runs quietly, collecting up to 1000 recent events in memory without generating logs or saving data to disk.

### Retrieving Liquidation Events
Use the `get_latest_liquidations` tool to fetch the most recent liquidation events. You can specify how many events to retrieve (up to 1000) using the `limit` parameter. For example, you might ask:

> "Show me the 5 most recent liquidation events from Binance."

This will return a neatly formatted table showing the trading pair, buy or sell side, price, quantity, and the time of each liquidation in HH:MM:SS format.


**Example Output**:
```markdown
| Symbol   | Side | Price  | Quantity | Time     |
|----------|------|--------|----------|----------|
| BTCUSDT  | BUY  | 50000  | 1.5      | 14:30:45 |
| ETHUSDT  | SELL | 3000   | 10.0     | 14:30:40 |
| BNBUSDT  | BUY  | 500    | 20.0     | 14:30:35 |
| ADAUSDT  | SELL | 1.2    | 1000.0   | 14:30:30 |
| XRPUSDT  | BUY  | 0.8    | 5000.0   | 14:30:25 |
```

This table makes it easy to see recent market activity, such as large buy or sell liquidations on Binance.

### Analyzing Liquidation Trends
The `analyze_liquidations` prompt helps you dive deeper into the data. It generates instructions for analyzing liquidation trends across all trading pairs, focusing on frequency, volume, and market impact. The prompt suggests using the `get_latest_liquidations` tool to fetch data, ensuring you have the latest information to work with.

This is particularly useful for understanding broader market dynamics, such as whether liquidations are increasing or signaling significant price movements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
