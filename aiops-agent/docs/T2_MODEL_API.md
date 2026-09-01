# T2：确认模型接口可用

本任务只验证 deepseek 兼容的聊天接口，不修改 FreeAiOps 源码，也不把 API Key 写入文件。

需要准备四项信息：

- `MODEL_BASE_URL`：服务地址，例如 `https://api.deepseek.com`
- `MODEL_API_PATH`：接口路径，默认 `/chat/completions`
- `MODEL_API_KEY`：你的 API Key，只在本机环境变量中设置
- `MODEL_NAME`：模型名称，例如 `deepseek-chat`

运行 `scripts/test_model_api.py` 后，预期看到 HTTP 200、模型名称、响应时间和一段返回内容。
