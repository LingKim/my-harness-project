#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

required_files=(
  ".gitmodules"
  ".env.example"
  "AGENTS.md"
  "README.md"
  "Makefile"
  "compose.yaml"
  ".codex/agents/README.md"
  ".codex/agents/product_manager.toml"
  ".codex/agents/interaction_designer.toml"
  ".codex/agents/frontend_engineer.toml"
  ".codex/agents/backend_engineer.toml"
  ".codex/agents/qa_engineer.toml"
  ".codex/agents/spec_reviewer.toml"
  ".codex/agents/experience_reviewer.toml"
  ".codex/rules/README.md"
  ".codex/rules/frontend-conventions.md"
  ".codex/rules/backend-conventions.md"
  ".codex/rules/database-conventions.md"
  ".codex/skills-lock.json"
  ".codex/manifest.json"
  "scripts/check-agent-governance.sh"
  "scripts/validate-custom-agents.py"
  "scripts/test-custom-agents.py"
  "frontend/AGENTS.md"
  "frontend/README.md"
  "frontend/package.json"
  "frontend/pnpm-lock.yaml"
  "frontend/playwright.config.ts"
  "frontend/vitest.config.ts"
  "frontend/scripts/check-agent-governance.sh"
  "backend/AGENTS.md"
  "backend/README.md"
  "backend/pom.xml"
  "backend/mvnw"
  "backend/docs/architecture.md"
  "backend/scripts/check-agent-governance.sh"
  "backend/src/main/resources/application.yml"
  "backend/src/main/resources/db/migration/V1__baseline.sql"
  "backend/src/test/java/com/heness/project/architecture/ArchitectureRulesTests.java"
  "openspec/config.yaml"
  ".codex/skills/openspec-apply-change/SKILL.md"
  ".codex/skills/vercel-react-best-practices/SKILL.md"
  ".codex/skills/java-springboot/SKILL.md"
  ".codex/skills/mysql/SKILL.md"
  ".codex/skills/chinamate-fullstack-delivery/SKILL.md"
  ".codex/skills/chinamate-fullstack-delivery/agents/openai.yaml"
  ".codex/skills/chinamate-fullstack-delivery/references/stage-routing.md"
  ".codex/skills/chinamate-fullstack-delivery/references/control-matrix.md"
  ".codex/skills/chinamate-fullstack-delivery/references/knowledge-routing.md"
  ".codex/skills/chinamate-fullstack-delivery/references/verification-profiles.md"
  ".codex/skills/chinamate-fullstack-delivery/scripts/collect_verification.py"
  ".codex/skills/chinamate-fullstack-delivery/scripts/check_verification_freshness.py"
  "docs/architecture/system-map.md"
  "docs/standards/domain-glossary.md"
  "docs/templates/openspec-change-evidence.md"
  "scripts/test-ai-delivery-governance.py"
  "scripts/test-verification-collector.py"
)

required_directories=(
  ".codex/agents"
  ".codex/rules"
  "frontend/src/app"
  "frontend/e2e"
  ".codex/skills/vercel-react-best-practices/rules"
  "backend/src/main/java/com/heness/project"
  "backend/src/main/resources/mapper"
  ".codex/skills/mysql/references"
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

for executable in scripts/check-harness.sh scripts/check-agent-governance.sh frontend/scripts/check-agent-governance.sh backend/scripts/check-agent-governance.sh backend/mvnw; do
  if [[ ! -x "$executable" ]]; then
    echo "失败：文件必须具有执行权限：$executable" >&2
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

  if [[ "$actual_path" != "$expected_path" || "$actual_url" != "$expected_url" ]]; then
    echo "失败：submodule ${name} 的 path 或 URL 不符合项目契约" >&2
    exit 1
  fi

  index_mode="$(git ls-files --stage -- "$expected_path" | awk 'NR == 1 { print $1 }')"
  if [[ "$index_mode" != "160000" ]]; then
    echo "失败：${expected_path} 必须以模式 160000 的 gitlink 记录" >&2
    exit 1
  fi

  if [[ "$(git -C "$expected_path" rev-parse --is-inside-work-tree 2>/dev/null || true)" != "true" ]]; then
    echo "失败：submodule ${expected_path} 尚未初始化" >&2
    exit 1
  fi
}

assert_submodule "frontend" "frontend" "https://github.com/LingKim/my-harness-frontend"
assert_submodule "backend" "backend" "https://github.com/LingKim/my-harness-backtend"

if ! grep -Eq '^schema:[[:space:]]+spec-driven$' openspec/config.yaml; then
  echo "失败：openspec/config.yaml 必须使用 spec-driven schema" >&2
  exit 1
fi

required_content=(
  'compose.yaml|image: mysql:8.4'
  'frontend/package.json|"next": "16.2.10"'
  'frontend/package.json|"react": "19.2.7"'
  'frontend/package.json|"typecheck": "next typegen && tsc --noEmit"'
  'frontend/package.json|"test:e2e": "playwright test"'
  'backend/pom.xml|<spring-ai.version>2.0.0</spring-ai.version>'
  'backend/pom.xml|<archunit.version>1.4.1</archunit.version>'
  'backend/pom.xml|<mybatis-plus.version>3.5.17</mybatis-plus.version>'
  'backend/pom.xml|<artifactId>mybatis-plus-spring-boot4-starter</artifactId>'
  '.codex/rules/backend-conventions.md|跨模块同步调用只能使用目标模块公开的 `application` 契约'
  '.codex/rules/backend-conventions.md|RULE-BE-010'
  '.codex/rules/database-conventions.md|SQL 业务值必须使用 `#{}` 参数绑定'
  '.codex/rules/database-conventions.md|新增或实质修改的自定义 SQL 必须使用 Mapper XML'
  '.codex/rules/database-conventions.md|BaseMapper<T>` 自动 CRUD'
  '.codex/skills/java-springboot/SKILL.md|自定义 SQL 必须写入 Mapper XML'
  'backend/docs/architecture.md|./mvnw -Dtest=ArchitectureRulesTests test'
  'backend/src/main/resources/application.yml|mybatis-plus:'
  'backend/src/main/resources/application.yml|enabled: ${AI_ENABLED:false}'
)

for check in "${required_content[@]}"; do
  file="${check%%|*}"
  content="${check#*|}"
  if ! grep -Fq "$content" "$file"; then
    echo "失败：$file 缺少必要契约：$content" >&2
    exit 1
  fi
done

if rg -Fq 'XML 或注解 SQL' .codex/rules .codex/skills/java-springboot; then
  echo "失败：后端 Rules 与 Java Skill 不得继续允许新增自定义 SQL 使用注解 SQL" >&2
  exit 1
fi

if grep -Fq '<artifactId>mybatis-spring-boot-starter</artifactId>' backend/pom.xml; then
  echo "失败：backend/pom.xml 不得依赖原生 MyBatis Spring Boot starter" >&2
  exit 1
fi

node -e '
const fs = require("fs");
const lock = JSON.parse(fs.readFileSync(".codex/skills-lock.json", "utf8"));
const projectSkill = lock.projectSkills?.["chinamate-fullstack-delivery"];
const javaSkill = lock.projectSkills?.["java-springboot"];
if (lock.version !== 1
  || JSON.stringify(Object.keys(lock.skills ?? {}).sort()) !== JSON.stringify(["mysql", "vercel-react-best-practices"])
  || JSON.stringify(Object.keys(lock.projectSkills ?? {}).sort()) !== JSON.stringify(["chinamate-fullstack-delivery", "java-springboot"])
  || projectSkill?.sourceType !== "project"
  || javaSkill?.sourceType !== "project"
  || !/^[0-9a-f]{64}$/.test(projectSkill?.contentHash ?? "")
  || !/^[0-9a-f]{64}$/.test(javaSkill?.contentHash ?? "")) {
  process.exit(1);
}
' || {
  echo "失败：根统一 Skills 锁必须登记两个项目 Skill 与两个第三方技术 Skill" >&2
  exit 1
}

for name in apply-change archive-change explore propose sync-specs update-change; do
  skill_file=".codex/skills/openspec-${name}/SKILL.md"
  if [[ ! -f "$skill_file" ]] || ! grep -Fq 'generatedBy: "1.6.0"' "$skill_file"; then
    echo "失败：Codex OpenSpec Skill 缺失或生成版本不正确：${name}" >&2
    exit 1
  fi
done

bash scripts/check-agent-governance.sh

echo "通过：AIWorkSpace Harness、submodule 与集中 Agents/Rules/Skills 治理结构完整"
echo "      OpenSpec schema：spec-driven"
echo "      治理平台：Codex-only（根 .codex/agents + .codex/rules + .codex/skills）"
echo "      单人全栈 Skill：.codex/skills/chinamate-fullstack-delivery"
echo "      前端 Skill：.codex/skills/vercel-react-best-practices"
echo "      后端 Skills：.codex/skills/java-springboot + mysql"
