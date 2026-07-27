#!/usr/bin/env bash

set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$project_root"

required_files=(
  "AGENTS.md"
  ".codex/agents/README.md"
  ".codex/agents/product_manager.toml"
  ".codex/agents/interaction_designer.toml"
  ".codex/agents/frontend_engineer.toml"
  ".codex/agents/backend_engineer.toml"
  ".codex/agents/qa_engineer.toml"
  ".codex/agents/spec_reviewer.toml"
  ".codex/agents/experience_reviewer.toml"
  ".codex/rules/README.md"
  ".codex/rules/workflow.md"
  ".codex/rules/repository-boundaries.md"
  ".codex/rules/git-safety.md"
  ".codex/rules/quality-gates.md"
  ".codex/rules/documentation.md"
  ".codex/rules/frontend-conventions.md"
  ".codex/rules/backend-conventions.md"
  ".codex/rules/database-conventions.md"
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
  ".codex/skills/chinamate-fullstack-delivery/scripts/check_delivery_environment.py"
  ".codex/skills/chinamate-fullstack-delivery/scripts/check_delivery_cleanup.py"
  ".codex/skills-lock.json"
  ".codex/manifest.json"
  "docs/architecture/system-map.md"
  "docs/standards/domain-glossary.md"
  "docs/templates/openspec-change-evidence.md"
  "scripts/test-ai-delivery-governance.py"
  "scripts/test-verification-collector.py"
  "scripts/test-delivery-safety.py"
  "frontend/scripts/check-agent-governance.sh"
  "backend/scripts/check-agent-governance.sh"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "失败：AI 治理结构缺少文件：$file" >&2
    exit 1
  fi
done

if ! grep -Fq '.codex/agents/' AGENTS.md || ! grep -Fq '.codex/rules/README.md' AGENTS.md || ! grep -Fq '.codex/skills/' AGENTS.md; then
  echo "失败：根 AGENTS.md 必须路由到根 .codex Agents、Rules 和 Skills" >&2
  exit 1
fi

if ! grep -Fq 'frontend/AGENTS.md' AGENTS.md || ! grep -Fq 'backend/AGENTS.md' AGENTS.md; then
  echo "失败：根 AGENTS.md 必须路由到前端和后端局部入口" >&2
  exit 1
fi

if ! grep -Fq 'evidence.md' AGENTS.md || ! grep -Fq 'docs/templates/openspec-change-evidence.md' AGENTS.md; then
  echo "失败：根 AGENTS.md 必须路由 OpenSpec change 交付证据与模板" >&2
  exit 1
fi

if ! grep -Fq '.codex/skills/chinamate-fullstack-delivery/SKILL.md' AGENTS.md; then
  echo "失败：根 AGENTS.md 必须路由到单人全栈编排 Skill" >&2
  exit 1
fi

node -e '
const fs = require("fs");
const path = require("path");
const files = [
  "AGENTS.md",
  ...fs.readdirSync(".codex/rules").filter((name) => name.endsWith(".md")).map((name) => `.codex/rules/${name}`),
  "frontend/AGENTS.md",
  "backend/AGENTS.md",
  ".codex/skills/chinamate-fullstack-delivery/SKILL.md",
  ...fs.readdirSync(".codex/skills/chinamate-fullstack-delivery/references").filter((name) => name.endsWith(".md")).map((name) => `.codex/skills/chinamate-fullstack-delivery/references/${name}`),
  "docs/architecture/system-map.md",
  "docs/standards/domain-glossary.md",
];
const missing = [];
for (const file of files) {
  const text = fs.readFileSync(file, "utf8");
  for (const match of text.matchAll(/\[[^\]]+\]\(([^)]+)\)/g)) {
    const target = match[1];
    if (/^(https?:|#)/.test(target)) continue;
    const resolved = path.resolve(path.dirname(file), target);
    if (!fs.existsSync(resolved)) missing.push(`${file} -> ${target}`);
  }
}
if (missing.length > 0) {
  console.error(`失效文档引用：${missing.join(", ")}`);
  process.exit(1);
}
' || {
  echo "失败：根入口或 Rules 包含失效引用" >&2
  exit 1
}

rule_ids="$(rg --no-filename -o 'RULE-[A-Z]+-[0-9]{3}' .codex/rules 2>/dev/null || true)"
if [[ -z "$rule_ids" ]]; then
  echo "失败：Rules 必须包含稳定 Rule ID" >&2
  exit 1
fi

duplicate_rule_ids="$(printf '%s\n' "$rule_ids" | sort | uniq -d)"
if [[ -n "$duplicate_rule_ids" ]]; then
  echo "失败：Rule ID 重复：$duplicate_rule_ids" >&2
  exit 1
fi

python3 scripts/validate-custom-agents.py
python3 scripts/test-ai-delivery-governance.py
python3 scripts/test-verification-collector.py
python3 scripts/test-delivery-safety.py

for forbidden in .agents .claude CLAUDE.md rules skills-lock.json; do
  if [[ -e "$forbidden" ]]; then
    echo "失败：根集中治理不允许路径：$forbidden" >&2
    exit 1
  fi
done

for repository in frontend backend; do
  for forbidden in .codex .agents .claude CLAUDE.md rules skills-lock.json; do
    if [[ -e "${repository}/${forbidden}" ]]; then
      echo "失败：子仓库不得保存局部治理路径：${repository}/${forbidden}" >&2
      exit 1
    fi
  done
done

node -e '
const fs = require("fs");
const manifest = JSON.parse(fs.readFileSync(".codex/manifest.json", "utf8"));
if (manifest.version !== 1 || manifest.platform !== "codex" || manifest.generator?.command !== "openspec update --force") {
  process.exit(1);
}
if (JSON.stringify(manifest.generatedPaths) !== JSON.stringify([".codex/skills/openspec-*"])) {
  process.exit(1);
}
const expectedProjectSkills = [{
  name: "chinamate-fullstack-delivery",
  path: ".codex/skills/chinamate-fullstack-delivery/SKILL.md",
  source: "skill-creator",
}, {
  name: "java-springboot",
  path: ".codex/skills/java-springboot/SKILL.md",
  source: "project-maintained",
}];
if (JSON.stringify(manifest.projectSkills ?? []) !== JSON.stringify(expectedProjectSkills)) {
  process.exit(1);
}
const expectedAgents = ["product_manager", "interaction_designer", "frontend_engineer", "backend_engineer", "qa_engineer", "spec_reviewer", "experience_reviewer"];
if (JSON.stringify((manifest.customAgents ?? []).map((agent) => agent.name)) !== JSON.stringify(expectedAgents)) {
  process.exit(1);
}
if ((manifest.prohibitedPaths ?? []).includes(".codex/agents")) {
  process.exit(1);
}
' || {
  echo "失败：.codex/manifest.json 必须登记 Codex-only 生成范围和七个 custom agents" >&2
  exit 1
}

bash frontend/scripts/check-agent-governance.sh
bash backend/scripts/check-agent-governance.sh

echo "通过：AGENTS.md 入口、单人全栈编排与集中 Agents、Rules、Skills 治理结构有效"
