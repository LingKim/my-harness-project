SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := dev

ENV_FILE ?= .env

.PHONY: help preflight dev frontend backend

help:
	@echo "AIWorkSpace 本地开发命令"
	@echo ""
	@echo "  make              同时启动前端和后端（等同于 make dev）"
	@echo "  make dev          同时启动前端和后端，Ctrl+C 一并停止"
	@echo "  make frontend     只启动前端"
	@echo "  make backend      只启动后端"
	@echo "  make preflight    检查启动所需命令和 submodule 状态"
	@echo ""
	@echo "可选：ENV_FILE=.env.local make dev（默认读取 .env，文件不存在时跳过）"

preflight:
	@command -v git >/dev/null 2>&1 || { echo "失败：未找到 git" >&2; exit 1; }
	@command -v pnpm >/dev/null 2>&1 || { echo "失败：未找到 pnpm" >&2; exit 1; }
	@command -v java >/dev/null 2>&1 || { echo "失败：未找到 Java" >&2; exit 1; }
	@test -f frontend/package.json || { echo "失败：frontend submodule 尚未初始化" >&2; echo "请先执行：git submodule update --init --recursive" >&2; exit 1; }
	@test -x backend/mvnw || { echo "失败：backend submodule 尚未初始化或 mvnw 不可执行" >&2; echo "请先执行：git submodule update --init --recursive" >&2; exit 1; }
	@submodule_status="$$(git submodule status -- frontend backend)"; \
	if printf '%s\n' "$$submodule_status" | grep -Eq '^[-+U]'; then \
		echo "失败：submodule 未初始化、存在冲突或未处于主仓库固定提交" >&2; \
		printf '%s\n' "$$submodule_status" >&2; \
		exit 1; \
	fi
	@echo "通过：启动环境与 submodule 状态正常"

frontend: preflight
	@set -a; \
	if [[ -f "$(ENV_FILE)" ]]; then source "$(ENV_FILE)"; fi; \
	set +a; \
	cd frontend; \
	exec pnpm dev --port "$${FRONTEND_PORT:-3000}"

backend: preflight
	@set -a; \
	if [[ -f "$(ENV_FILE)" ]]; then source "$(ENV_FILE)"; fi; \
	set +a; \
	cd backend; \
	exec ./mvnw spring-boot:run

dev: preflight
	@set -a; \
	if [[ -f "$(ENV_FILE)" ]]; then \
		echo "加载环境变量：$(ENV_FILE)"; \
		source "$(ENV_FILE)"; \
	else \
		echo "未找到 $(ENV_FILE)，使用前后端默认配置"; \
	fi; \
	set +a; \
	frontend_pid=""; \
	backend_pid=""; \
	interrupted=0; \
	cleanup() { \
		trap - INT TERM EXIT; \
		if [[ -n "$$frontend_pid" ]] && kill -0 "$$frontend_pid" 2>/dev/null; then kill "$$frontend_pid" 2>/dev/null || true; fi; \
		if [[ -n "$$backend_pid" ]] && kill -0 "$$backend_pid" 2>/dev/null; then kill "$$backend_pid" 2>/dev/null || true; fi; \
		if [[ -n "$$frontend_pid" ]]; then wait "$$frontend_pid" 2>/dev/null || true; fi; \
		if [[ -n "$$backend_pid" ]]; then wait "$$backend_pid" 2>/dev/null || true; fi; \
	}; \
	handle_interrupt() { interrupted=1; cleanup; }; \
	trap handle_interrupt INT TERM; \
	trap cleanup EXIT; \
	(cd frontend && exec pnpm dev --port "$${FRONTEND_PORT:-3000}") & frontend_pid=$$!; \
	(cd backend && exec ./mvnw spring-boot:run) & backend_pid=$$!; \
	echo "前端启动中：http://localhost:$${FRONTEND_PORT:-3000}"; \
	echo "后端启动中：http://localhost:$${BACKEND_PORT:-8080}"; \
	echo "按 Ctrl+C 同时停止前端和后端"; \
	exit_status=0; \
	while kill -0 "$$frontend_pid" 2>/dev/null && kill -0 "$$backend_pid" 2>/dev/null; do sleep 1; done; \
	if ! kill -0 "$$frontend_pid" 2>/dev/null; then wait "$$frontend_pid" || exit_status=$$?; echo "前端进程已退出"; fi; \
	if ! kill -0 "$$backend_pid" 2>/dev/null; then wait "$$backend_pid" || exit_status=$$?; echo "后端进程已退出"; fi; \
	if [[ "$$interrupted" -eq 1 ]]; then echo "前端和后端已停止"; exit 0; fi; \
	exit "$$exit_status"
