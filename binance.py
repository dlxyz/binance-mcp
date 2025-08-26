import time
import hmac
import hashlib
import time
import requests
from functools import lru_cache
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Binance MCP Server")

import argparse

# 初始化参数解析器
parser = argparse.ArgumentParser()
parser.add_argument("--binance-api-key", type=str, default="",
                    help="币安API Key")
parser.add_argument("--binance-secret-key", type=str, default="",
                    help="币安秘钥")
args = parser.parse_args()

BINANCE_SECRET_KEY = args.binance_secret_key
BINANCE_API_KEY = args.binance_api_key


@mcp.tool()
@lru_cache(maxsize=100)
def get_symbol_price(symbol: str) -> Any:
    """
    Get the current price of a cryptocurrency pair.

    Args:
        symbol: The cryptocurrency pair, e.g., BTCUSDT.

    Returns:
        Price information from Binance.
    """
    url = "https://api.binance.com/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return {"price": data['price'], "symbol": symbol}
    return {"error": response.text}


@mcp.tool()
def get_account_balance(asset: str) -> Any:
    """
    Get the balance of a specific cryptocurrency asset.

    Args:
        asset: The cryptocurrency symbol, e.g., BTC.

    Returns:
        Asset balance info.
    """
    url = "https://api.binance.com/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        balances = response.json().get("balances", [])
        for balance in balances:
            if balance["asset"] == asset:
                return {"asset": asset, "balance": balance["free"]}
        return {"error": f"No balance found for {asset}"}
    return {"error": response.text}


@mcp.tool()
def place_market_order(symbol: str, side: str, quantity: str) -> Any:
    """
    Place a market order to buy or sell.

    Args:
        symbol: The trading pair, e.g., BTCUSDT.
        side: BUY or SELL.
        quantity: Amount to trade.

    Returns:
        Order placement result.
    """
    url = "https://api.binance.com/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return {"message": f"{side} {quantity} {symbol} order placed"}
    return {"error": response.text}


@mcp.tool()
def get_trade_history(symbol: str, limit: int = 10) -> Any:
    """
    Get recent trade history for a pair.

    Args:
        symbol: The trading pair.
        limit: Number of trades to fetch.

    Returns:
        List of trade summaries.
    """
    url = "https://api.binance.com/api/v3/myTrades"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "limit": limit,
        "timestamp": timestamp
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return [
            {
                "time": trade["time"],
                "side": "BUY" if trade["isBuyer"] else "SELL",
                "qty": trade["qty"],
                "price": trade["price"]
            } for trade in response.json()
        ]
    return {"error": response.text}


@mcp.tool()
def get_open_orders(symbol: str) -> Any:
    """
    Get open orders for a symbol.

    Args:
        symbol: The trading pair.

    Returns:
        List of open orders.
    """
    url = "https://api.binance.com/api/v3/openOrders"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "timestamp": timestamp
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return [
            {
                "side": order["side"],
                "quantity": order["origQty"],
                "price": order["price"]
            } for order in response.json()
        ]
    return {"error": response.text}


@mcp.tool()
def cancel_order(symbol: str, order_id: str) -> Any:
    """
    Cancel a specific order.

    Args:
        symbol: The trading pair.
        order_id: Order ID to cancel.

    Returns:
        Cancellation result.
    """
    url = "https://api.binance.com/api/v3/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "orderId": order_id,
        "timestamp": timestamp
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.delete(url, headers=headers, params=params)
    if response.status_code == 200:
        return {"message": f"Order {order_id} canceled"}
    return {"error": response.text}


@mcp.tool()
def get_historical_klines(symbol: str, interval: str = "1h", start_time: str = None, end_time: str = None, limit: int = 500) -> Any:
    """
    Get historical kline/candlestick data for a symbol.

    Args:
        symbol: The trading pair, e.g., BTCUSDT.
        interval: Kline interval (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M).
        start_time: Start time in milliseconds or ISO format (e.g., "2025-08-09 21:28:00").
        end_time: End time in milliseconds or ISO format.
        limit: Number of klines to return (max 1000, default 500).

    Returns:
        Historical kline data with OHLCV information.
    """
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    
    # Convert time formats if provided
    if start_time:
        if isinstance(start_time, str) and not start_time.isdigit():
            # Convert ISO format to timestamp
            from datetime import datetime
            try:
                dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                start_time = int(dt.timestamp() * 1000)
            except ValueError:
                try:
                    dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
                    start_time = int(dt.timestamp() * 1000)
                except ValueError:
                    return {"error": "Invalid start_time format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'"}
        params["startTime"] = start_time
    
    if end_time:
        if isinstance(end_time, str) and not end_time.isdigit():
            from datetime import datetime
            try:
                dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
                end_time = int(dt.timestamp() * 1000)
            except ValueError:
                try:
                    dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M")
                    end_time = int(dt.timestamp() * 1000)
                except ValueError:
                    return {"error": "Invalid end_time format. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'"}
        params["endTime"] = end_time
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        klines = response.json()
        formatted_data = []
        for kline in klines:
            formatted_data.append({
                "open_time": kline[0],
                "open_price": float(kline[1]),
                "high_price": float(kline[2]),
                "low_price": float(kline[3]),
                "close_price": float(kline[4]),
                "volume": float(kline[5]),
                "close_time": kline[6],
                "quote_asset_volume": float(kline[7]),
                "number_of_trades": kline[8],
                "taker_buy_base_asset_volume": float(kline[9]),
                "taker_buy_quote_asset_volume": float(kline[10])
            })
        return {"symbol": symbol, "interval": interval, "data": formatted_data}
    return {"error": response.text}


@mcp.tool()
def get_price_at_time(symbol: str, target_time: str) -> Any:
    """
    Get the price of a cryptocurrency at a specific time.

    Args:
        symbol: The trading pair, e.g., BTCUSDT.
        target_time: Target time in format 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'.

    Returns:
        Price information at the specified time.
    """
    from datetime import datetime, timedelta
    
    try:
        # Parse target time
        try:
            target_dt = datetime.strptime(target_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            target_dt = datetime.strptime(target_time, "%Y-%m-%d %H:%M")
        
        # Get kline data around the target time
        start_time = target_dt - timedelta(hours=1)
        end_time = target_dt + timedelta(hours=1)
        
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Get 1-minute klines for more precision
        klines_result = get_historical_klines(symbol, "1m", start_time_str, end_time_str, 120)
        
        if "error" in klines_result:
            return klines_result
        
        klines = klines_result["data"]
        if not klines:
            return {"error": "No data found for the specified time"}
        
        # Find the closest kline to target time
        target_timestamp = int(target_dt.timestamp() * 1000)
        closest_kline = None
        min_diff = float('inf')
        
        for kline in klines:
            open_time = kline["open_time"]
            close_time = kline["close_time"]
            
            # Check if target time falls within this kline period
            if open_time <= target_timestamp <= close_time:
                closest_kline = kline
                break
            
            # Find closest kline if exact match not found
            diff = min(abs(open_time - target_timestamp), abs(close_time - target_timestamp))
            if diff < min_diff:
                min_diff = diff
                closest_kline = kline
        
        if closest_kline:
            return {
                "symbol": symbol,
                "target_time": target_time,
                "price_data": {
                    "open_price": closest_kline["open_price"],
                    "high_price": closest_kline["high_price"],
                    "low_price": closest_kline["low_price"],
                    "close_price": closest_kline["close_price"],
                    "volume": closest_kline["volume"]
                },
                "kline_period": {
                    "start": datetime.fromtimestamp(closest_kline["open_time"] / 1000).strftime("%Y-%m-%d %H:%M:%S"),
                    "end": datetime.fromtimestamp(closest_kline["close_time"] / 1000).strftime("%Y-%m-%d %H:%M:%S")
                },
                "note": "Price data from the closest available 1-minute kline period"
            }
        
        return {"error": "No suitable price data found for the specified time"}
        
    except ValueError as e:
        return {"error": f"Invalid time format: {str(e)}. Use 'YYYY-MM-DD HH:MM:SS' or 'YYYY-MM-DD HH:MM'"}
    except Exception as e:
        return {"error": f"Error retrieving price data: {str(e)}"}


@mcp.tool()
def get_funding_rate_history(symbol: str, limit: int = 100) -> Any:
    """
    Get funding rate history.

    Args:
        symbol: Perpetual contract symbol.
        limit: Number of records to return (default 100).

    Returns:
        Funding rate data list.
    """
    url = "https://fapi.binance.com/fapi/v1/fundingRate"
    params = {"symbol": symbol, "limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return {"error": response.text}


@mcp.tool()
def execute_hedge_arbitrage_strategy(symbol: str, quantity: str) -> Any:
    """
    Execute hedge arbitrage based on funding rate.

    Args:
        symbol: The trading pair.
        quantity: Amount to trade.

    Returns:
        Summary of the arbitrage result.
    """
    asset = symbol.replace("USDT", "")
    balance_result = mcp.use_tool("get_account_balance", asset)
    try:
        available_balance = float(balance_result.get("balance", 0))
    except:
        available_balance = 0

    actual_quantity = min(float(quantity), available_balance) if available_balance > 0 else 0
    if actual_quantity <= 0:
        return {"error": f"Insufficient {asset} balance."}

    funding_rate_data = mcp.use_tool("get_funding_rate_history", symbol)
    funding_rate = float(funding_rate_data[0]['fundingRate'])
    spot_price_data = mcp.use_tool("get_symbol_price", symbol)
    spot_price = float(spot_price_data["price"])

    if funding_rate > 0:
        mcp.use_tool("place_market_order", symbol, "BUY", actual_quantity)
        place_futures_order(symbol, "SELL", actual_quantity)
    else:
        mcp.use_tool("place_market_order", symbol, "SELL", actual_quantity)
        place_futures_order(symbol, "BUY", actual_quantity)

    time.sleep(10)

    if funding_rate > 0:
        place_futures_order(symbol, "BUY", actual_quantity)
        mcp.use_tool("place_market_order", symbol, "SELL", actual_quantity)
    else:
        place_futures_order(symbol, "SELL", actual_quantity)
        mcp.use_tool("place_market_order", symbol, "BUY", actual_quantity)

    SPOT_FEE = 0.001
    FUTURES_FEE = 0.0002
    fee = (spot_price * actual_quantity * SPOT_FEE * 2) + (spot_price * actual_quantity * FUTURES_FEE * 2)
    profit = abs(funding_rate) * spot_price * actual_quantity
    net_profit = profit - fee

    return {
        "net_profit": round(net_profit, 4),
        "fees": round(fee, 4),
        "message": f"Arbitrage executed. Estimated net profit: {net_profit:.4f} USDT"
    }


def place_futures_order(symbol: str, side: str, quantity: str) -> Any:
    """
    Place a perpetual futures market order.

    Args:
        symbol: Futures pair.
        side: BUY or SELL.
        quantity: Amount.

    Returns:
        Order placement result.
    """
    url = "https://fapi.binance.com/fapi/v1/order"
    timestamp = int(time.time() * 1000)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp
    }
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    signature = hmac.new(BINANCE_SECRET_KEY.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    response = requests.post(url, headers=headers, params=params)
    return response.json() if response.status_code == 200 else {"error": response.text}


@mcp.tool()
def find_arbitrage_pairs(
        min_funding_rate: float = 0.0005,
        min_avg_volume: float = 1_000_000,
        history_days: int = 7,
        stability_threshold: float = 0.8
) -> list[dict[str, Any]]:
    """
    Find arbitrage pairs based on funding rate, volume, and rate direction stability.

    Args:
        min_funding_rate: Minimum funding rate to qualify.
        min_avg_volume: Minimum 24hr volume in USDT.
        history_days: How many days of history to analyze.
        stability_threshold: Minimum proportion of funding rates in same direction.

    Returns:
        List of qualifying arbitrage opportunities.
    """
    current_url = "https://fapi.binance.com/fapi/v1/premiumIndex"
    history_url = "https://fapi.binance.com/fapi/v1/fundingRate"
    candidates = []

    response = requests.get(current_url)
    if response.status_code != 200:
        return [{"error": "Failed to fetch current funding data"}]

    for pair in response.json():
        try:
            symbol = pair["symbol"]
            current_rate = float(pair["lastFundingRate"])

            if abs(current_rate) < min_funding_rate:
                continue

            history_params = {
                "symbol": symbol,
                "limit": history_days * 3
            }
            history_resp = requests.get(history_url, params=history_params)
            if history_resp.status_code != 200:
                continue

            rates = [float(x["fundingRate"]) for x in history_resp.json()]
            same_dir = sum(1 for r in rates if (r > 0 and current_rate > 0) or (r < 0 and current_rate < 0))
            stability = same_dir / len(rates) if rates else 0

            ticker_url = f"https://fapi.binance.com/fapi/v1/ticker/24hr?symbol={symbol}"
            ticker_resp = requests.get(ticker_url)
            if ticker_resp.status_code != 200:
                continue

            volume = float(ticker_resp.json().get("quoteVolume", 0))
            if volume > min_avg_volume and stability >= stability_threshold:
                candidates.append({
                    "symbol": symbol,
                    "current_funding_rate": current_rate,
                    "avg_volume": volume,
                    "stability": round(stability, 2)
                })

        except Exception:
            continue

    return sorted(candidates, key=lambda x: -abs(x["current_funding_rate"]))


if __name__ == "__main__":
    mcp.run(transport="stdio")
