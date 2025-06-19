# Binance Volume Monitor Bot

这是一个使用 Telegram Bot 实现的 Binance 期货成交量放量监控工具。

## 功能
- 用户通过 /add 添加交易对
- 每分钟监控成交量是否超前一分钟 150%
- 放量时主动推送 Telegram 消息

## 部署
1. clone 仓库
2. 设置环境变量 `BOT_TOKEN`
3. 本地运行：`python bot.py`；
   或使用 Docker：`docker build -t volume-bot . && docker run -d -e BOT_TOKEN=xxx volume-bot`

## Render 云平台部署
- 创建 Web Service，运行命令：
  - Build: `pip install -r requirements.txt`
  - Start: `python bot.py`
- 添加环境变量： `BOT_TOKEN`

