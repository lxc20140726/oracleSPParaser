#!/bin/bash
# 激活Oracle SP Parser虚拟环境
source venv/bin/activate
echo "✅ Oracle SP Parser 虚拟环境已激活"
echo "📖 使用方法:"
echo "  - oracle-sp-parser --help"
echo "  - oracle-sp-backend"
echo "  - oracle-sp-test --smoke"
exec "$SHELL"
