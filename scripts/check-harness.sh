#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

required_files=(
  ".gitmodules"
  ".env.example"
  "AGENTS.md"
  "CLAUDE.md"
  "README.md"
  "compose.yaml"
  "frontend/package.json"
  "frontend/pnpm-lock.yaml"
  "frontend/vitest.config.ts"
  "frontend/src/app/page.test.tsx"
  "backend/pom.xml"
  "backend/mvnw"
  "backend/src/main/resources/application.yml"
  "backend/src/main/resources/db/migration/V1__baseline.sql"
  "backend/src/main/java/com/heness/project/health/HealthController.java"
  "backend/src/main/java/com/heness/project/config/ai/AiConfiguration.java"
  "backend/src/test/java/com/heness/project/config/ai/AiConfigurationTests.java"
  "openspec/config.yaml"
)

required_directories=(
  ".codex/skills"
  ".claude/commands/opsx"
  ".claude/skills"
  "frontend/src/app"
  "backend/src/main/java/com/heness/project"
  "backend/src/main/resources/mapper"
  "docs/designs"
  "docs/plans"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "失败：缺少必要文件：$file" >&2
    exit 1
  fi
done

for directory in "${required_directories[@]}"; do
  if [[ ! -d "$directory" ]]; then
    echo "失败：缺少必要目录：$directory" >&2
    exit 1
  fi
done

assert_submodule() {
  local name="$1"
  local expected_path="$2"
  local expected_url="$3"
  local actual_path
  local actual_url
  local index_mode

  actual_path="$(git config -f .gitmodules --get "submodule.${name}.path" || true)"
  actual_url="$(git config -f .gitmodules --get "submodule.${name}.url" || true)"

  if [[ "$actual_path" != "$expected_path" ]]; then
    echo "失败：submodule ${name} 的 path 应为 ${expected_path}，实际为 ${actual_path:-未配置}" >&2
    exit 1
  fi

  if [[ "$actual_url" != "$expected_url" ]]; then
    echo "失败：submodule ${name} 的 URL 应为 ${expected_url}，实际为 ${actual_url:-未配置}" >&2
    exit 1
  fi

  index_mode="$(git ls-files --stage -- "$expected_path" | awk 'NR == 1 { print $1 }')"
  if [[ "$index_mode" != "160000" ]]; then
    echo "失败：${expected_path} 必须以模式 160000 的 gitlink 记录，实际为 ${index_mode:-未跟踪}" >&2
    exit 1
  fi

  if [[ "$(git -C "$expected_path" rev-parse --is-inside-work-tree 2>/dev/null || true)" != "true" ]]; then
    echo "失败：submodule ${expected_path} 尚未初始化为可用 Git 工作树" >&2
    exit 1
  fi

  if ! git submodule status -- "$expected_path" >/dev/null 2>&1; then
    echo "失败：无法解析 submodule ${expected_path} 的状态" >&2
    exit 1
  fi
}

assert_submodule \
  "frontend" \
  "frontend" \
  "https://github.com/LingKim/my-harness-frontend"
assert_submodule \
  "backend" \
  "backend" \
  "https://github.com/LingKim/my-harness-backtend"

if ! grep -Eq '^schema:[[:space:]]+spec-driven$' openspec/config.yaml; then
  echo "失败：openspec/config.yaml 必须使用 spec-driven schema" >&2
  exit 1
fi

if [[ ! -x "backend/mvnw" ]]; then
  echo "失败：backend/mvnw 必须具有执行权限" >&2
  exit 1
fi

required_content=(
  'compose.yaml|image: mysql:8.4'
  'frontend/package.json|"next": "16.2.10"'
  'frontend/package.json|"react": "19.2.7"'
  'backend/pom.xml|<spring-ai.version>2.0.0</spring-ai.version>'
  'backend/pom.xml|<mybatis-plus.version>3.5.17</mybatis-plus.version>'
  'backend/pom.xml|<artifactId>mybatis-plus-spring-boot4-starter</artifactId>'
  'backend/src/main/resources/application.yml|mybatis-plus:'
  'backend/src/main/resources/application.yml|enabled: ${AI_ENABLED:false}'
)

for check in "${required_content[@]}"; do
  file="${check%%|*}"
  content="${check#*|}"
  if ! grep -Fq "$content" "$file"; then
    echo "失败：$file 缺少必要配置：$content" >&2
    exit 1
  fi
done

if grep -Fq '<artifactId>mybatis-spring-boot-starter</artifactId>' backend/pom.xml; then
  echo "失败：backend/pom.xml 不得继续直接依赖原生 MyBatis Spring Boot starter" >&2
  exit 1
fi

codex_skill_count="$(find .codex/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
claude_skill_count="$(find .claude/skills -mindepth 2 -maxdepth 2 -name SKILL.md | wc -l | tr -d ' ')"
claude_command_count="$(find .claude/commands/opsx -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')"

if [[ "$codex_skill_count" -lt 6 || "$claude_skill_count" -lt 6 || "$claude_command_count" -lt 6 ]]; then
  echo "失败：OpenSpec 工具集成不完整" >&2
  echo "      Codex 技能：$codex_skill_count；Claude 技能：$claude_skill_count；Claude 命令：$claude_command_count" >&2
  exit 1
fi

echo "通过：AIWorkSpace Harness、submodule 与全栈工程结构完整"
echo "      OpenSpec schema：spec-driven"
echo "      Codex 技能：$codex_skill_count"
echo "      Claude 技能：$claude_skill_count"
echo "      Claude 命令：$claude_command_count"
echo "      submodule：frontend / backend"
echo "      前端：Next.js 16.2.10 / React 19.2.7"
echo "      后端：Spring Boot 4.1.0 / Spring AI 2.0.0 / MyBatis-Plus 3.5.17"
