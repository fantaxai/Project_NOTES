 .PHONY: help lint fix test clean

help:
	@echo "Доступные команды:"
	@echo "  make lint    - Запустить статический анализ"
	@echo "  make fix     - Автоматически исправить форматирование"
	@echo "  make test    - Запустить тесты"
	@echo "  make check   - Запустить всё (lint + test)"
	@echo "  make clean   - Очистить временные файлы"

lint:
	python lint.py

fix:
	python lint.py --fix

test:
	python -m pytest notes/tests/ -v --cov=note

check:
	make lint
	make test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage coverage.xml
