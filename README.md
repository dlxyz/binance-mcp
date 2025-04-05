# Binance MCP Server

这是一个基于MCP (Model Control Protocol) 的币安交易接口服务器起点代码。它提供了一系列基础的币安交易所交互能力，可以作为你开发更复杂交易策略和功能的基础。

## 功能特性

当前实现的基础功能包括：
- 实时获取加密货币价格
- 查询账户资产余额
- 下单交易（市价单）
- 查询交易历史
- 查询当前未完成订单
- 取消订单
- 获取资金费率历史
- 执行对冲套利策略
- 自动寻找套利机会

这些功能为你开发更高级的交易策略和自动化系统提供了基础构建块。你可以基于这些接口：
- 开发更复杂的交易策略
- 添加风险管理系统
- 实现更多类型的订单支持
- 扩展数据分析能力
- 添加自定义的套利策略

## 安装要求

- Python >= 3.13
- mcp[cli] >= 1.6.0
- requests >= 2.32.3

## 安装和配置

1. 克隆仓库：
```bash
git clone [repository-url]
cd binance-mcp-server
```

2. 创建并激活虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
pip install -e .
```

4. 配置MCP：
在你的MCP配置文件中（通常位于 `~/.cursor/mcp.json`）添加以下配置：

```json
{
  "binance-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/binance-mcp-server",
      "run",
      "binance.py",
      "--binance-api-key",
      "YOUR_API_KEY",
      "--binance-secret-key",
      "YOUR_SECRET_KEY"
    ]
  }
}
```

## 使用方法

1. 确保你已经在币安创建了API密钥，并在MCP配置文件中正确配置。

2. 通过MCP客户端调用服务提供的功能：

- `get_symbol_price`: 获取某个交易对的当前价格
- `get_account_balance`: 查询特定加密货币的账户余额
- `place_market_order`: 下市价单
- `get_trade_history`: 获取交易历史
- `get_open_orders`: 查询未完成订单
- `cancel_order`: 取消订单
- `get_funding_rate_history`: 获取资金费率历史
- `execute_hedge_arbitrage_strategy`: 执行对冲套利策略
- `find_arbitrage_pairs`: 寻找套利机会

## 开发和扩展

这个项目提供了基础的交易功能框架，你可以：
1. 添加新的交易策略
2. 扩展现有功能
3. 添加更多的错误处理和日志
4. 实现更复杂的套利逻辑
5. 集成其他交易所的API

## 安全提示

- 请妥善保管你的API密钥和密钥
- 建议在使用时设置适当的API权限限制
- 在进行实际交易前，建议先在测试网络上进行测试

## 贡献

欢迎提交问题和合并请求。这个项目处于积极开发中，我们欢迎任何形式的贡献。

## 许可证

MIT
