#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

approved_skill_names=(
  "java-springboot"
  "mysql"
  "vercel-react-best-practices"
)

required_files=(
  ".gitmodules"
  ".env.example"
  "AGENTS.md"
  "CLAUDE.md"
  "Makefile"
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
  ".agents/skills/java-springboot/SKILL.md"
  ".agents/skills/mysql/SKILL.md"
  ".agents/skills/mysql/references/data-types.md"
  ".agents/skills/mysql/references/explain-analysis.md"
  ".agents/skills/mysql/references/online-ddl.md"
  ".agents/skills/mysql/references/row-locking-gotchas.md"
  ".agents/skills/vercel-react-best-practices/SKILL.md"
  ".agents/skills/vercel-react-best-practices/rules/async-parallel.md"
  "skills-lock.json"
  "openspec/config.yaml"
)

required_directories=(
  ".codex/skills"
  ".claude/commands/opsx"
  ".claude/skills"
  ".agents/skills/mysql/references"
  ".agents/skills/vercel-react-best-practices/rules"
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

if ! node -e '
const fs = require("fs");
const lock = JSON.parse(fs.readFileSync(process.argv[1], "utf8"));
const approvedSkillNames = process.argv.slice(2).sort();
const skillNames = Object.keys(lock.skills ?? {}).sort();
const javaSkill = lock.skills?.["java-springboot"];
const mysqlSkill = lock.skills?.mysql;
const reactSkill = lock.skills?.["vercel-react-best-practices"];
const unapprovedSkillNames = skillNames.filter(
  (name) => !approvedSkillNames.includes(name),
);
const missingSkillNames = approvedSkillNames.filter(
  (name) => !skillNames.includes(name),
);

if (unapprovedSkillNames.length > 0) {
  console.error(`未批准 Skill：${unapprovedSkillNames.join(", ")}`);
}
if (missingSkillNames.length > 0) {
  console.error(`缺少已批准 Skill：${missingSkillNames.join(", ")}`);
}

const valid = lock.version === 1
  && unapprovedSkillNames.length === 0
  && missingSkillNames.length === 0
  && javaSkill?.source === "github/awesome-copilot"
  && javaSkill?.sourceType === "github"
  && javaSkill?.skillPath === "skills/java-springboot/SKILL.md"
  && /^[0-9a-f]{64}$/.test(javaSkill?.computedHash ?? "")
  && mysqlSkill?.source === "planetscale/database-skills"
  && mysqlSkill?.sourceType === "github"
  && mysqlSkill?.skillPath === "skills/mysql/SKILL.md"
  && /^[0-9a-f]{64}$/.test(mysqlSkill?.computedHash ?? "")
  && reactSkill?.source === "vercel-labs/agent-skills"
  && reactSkill?.sourceType === "github"
  && reactSkill?.skillPath === "skills/react-best-practices/SKILL.md"
  && /^[0-9a-f]{64}$/.test(reactSkill?.computedHash ?? "");
process.exit(valid ? 0 : 1);
' skills-lock.json "${approved_skill_names[@]}"; then
  echo "失败：skills-lock.json 必须匹配项目批准的 Skill 清单，且 Java/MySQL/React Skill 必须来自批准的官方仓库" >&2
  exit 1
fi

if ! grep -Fq '必须使用 `vercel-react-best-practices`' AGENTS.md; then
  echo "失败：AGENTS.md 必须强制 React/Next.js 任务使用 vercel-react-best-practices" >&2
  exit 1
fi

if ! grep -Fq '`frontend/node_modules/next/dist/docs/`' AGENTS.md; then
  echo "失败：AGENTS.md 必须声明当前 Next.js 本地文档的事实优先级" >&2
  exit 1
fi

if ! grep -Fq '必须使用 `java-springboot`' AGENTS.md; then
  echo "失败：AGENTS.md 必须强制后端 Java/Spring Boot 任务使用 java-springboot" >&2
  exit 1
fi

if ! grep -Fq '先完整读取 `.agents/skills/java-springboot/SKILL.md`' AGENTS.md; then
  echo "失败：AGENTS.md 必须要求完整读取 java-springboot Skill 入口" >&2
  exit 1
fi

if ! grep -Fq '`java-springboot` 中涉及 Spring Data JPA' AGENTS.md; then
  echo "失败：AGENTS.md 必须声明 java-springboot 的 Spring Data JPA 建议不适用于当前项目" >&2
  exit 1
fi

if ! grep -Fq '数据库结构继续只由 Flyway 管理' AGENTS.md; then
  echo "失败：AGENTS.md 必须保留 MyBatis-Plus 与 Flyway 的技术栈覆盖规则" >&2
  exit 1
fi

if ! grep -Fq '必须使用 `mysql`' AGENTS.md; then
  echo "失败：AGENTS.md 必须强制数据库与 SQL 任务使用 mysql Skill" >&2
  exit 1
fi

if ! grep -Fq '先完整读取 `.agents/skills/mysql/SKILL.md`' AGENTS.md; then
  echo "失败：AGENTS.md 必须要求完整读取 mysql Skill 入口" >&2
  exit 1
fi

if ! grep -Fq '数据库结构继续只由 Flyway migration 管理' AGENTS.md; then
  echo "失败：AGENTS.md 必须保留数据库结构的 Flyway-only 规则" >&2
  exit 1
fi

if ! grep -Fq '业务值必须使用 `#{}` 参数绑定' AGENTS.md; then
  echo "失败：AGENTS.md 必须要求 MyBatis 业务值使用参数绑定" >&2
  exit 1
fi

if ! grep -Fq '`${}` 只能用于 JDBC 无法参数化' AGENTS.md; then
  echo "失败：AGENTS.md 必须限制 MyBatis \${} 只接受服务端封闭白名单" >&2
  exit 1
fi

if ! grep -Fq '`EXPLAIN ANALYZE` 会实际执行 SQL' AGENTS.md; then
  echo "失败：AGENTS.md 必须声明 EXPLAIN ANALYZE 的真实执行风险" >&2
  exit 1
fi

if ! grep -Fq '破坏性数据库操作必须在执行前获得用户明确批准' AGENTS.md; then
  echo "失败：AGENTS.md 必须要求破坏性数据库操作获得人工批准" >&2
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
echo "      前端 Skill：vercel-react-best-practices（Vercel 官方）"
echo "      后端：Spring Boot 4.1.0 / Spring AI 2.0.0 / MyBatis-Plus 3.5.17"
echo "      后端 Skill：java-springboot（GitHub 官方仓库）"
echo "      数据库 Skill：mysql（PlanetScale）"
