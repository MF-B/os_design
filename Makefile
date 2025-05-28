# 变量定义
PYTHON = python3
TEST_DIR = test
MAIN_DIR = .
TEST_FILE = $(TEST_DIR)/test.py

# 默认目标
.PHONY: all
all: run

# 运行主程序
.PHONY: run
run:
	$(PYTHON) $(MAIN_DIR)/main.py

.PHONY: ui
ui:
	$(PYTHON) $(MAIN_DIR)/ui.py

# 运行测试
.PHONY: test
test:
	PYTHONPATH=$(MAIN_DIR) $(PYTHON) $(TEST_FILE)

# 清理临时文件
.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type f -name ".DS_Store" -delete

# 帮助信息
.PHONY: help
help:
	@echo "可用的命令:"
	@echo "  make        - 运行主程序"
	@echo "  make run    - 运行主程序"
	@echo "  make test   - 运行测试"
	@echo "  make clean  - 清理临时文件"
	@echo "  make deps   - 安装依赖"
	@echo "  make help   - 显示此帮助信息"