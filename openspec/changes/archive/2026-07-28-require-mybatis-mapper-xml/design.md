## Context

当前 `strengthen-engineering-practice-governance` change 已把 MyBatis-Plus 固化为默认持久化方案，但仍允许复杂 SQL 使用 Mapper XML 或注解 SQL。后端现有 `AccountMapper`、`AuthSessionMapper`、`RefreshTokenMapper` 和 `LoginFailureMapper` 已存在注解 SQL；同时 `application.yml` 已配置 `classpath:/mapper/**/*.xml`，`resources/mapper/README.md` 也已规定 XML 路径和 `namespace` 约定。

本 change 在不改变运行时依赖和业务行为的前提下，收紧未来 SQL 的治理合同。实施前必须先完成或归档 `strengthen-engineering-practice-governance`，避免两个 change 对同一 requirement 的表述和归档顺序发生冲突。

## Goals / Non-Goals

**Goals:**

- 把 Mapper XML 设为新增或实质修改自定义 SQL 的唯一允许位置。
- 明确哪些注解被禁止、哪些 MyBatis/MyBatis-Plus 能力继续允许。
- 通过治理校验防止 Rule 与 Skill 再次出现“XML 或注解 SQL”的冲突表述。

**Non-Goals:**

- 不在本 change 迁移或重构现有后端注解 SQL。
- 不禁止 `BaseMapper<T>` 自动 CRUD、`@Mapper`、`@Param` 或纯映射注解。
- 不新增 Maven 依赖，不改变 Mapper 扫描路径、数据库 schema 或 API 行为。

## Decisions

### 1. 强制 XML 的对象是“自定义 SQL”，不是全部 Mapper 方法

新增或实质修改的手写 SQL statement 必须位于 Mapper XML；Java Mapper 接口只保留方法签名及不承载 SQL 文本的注解。`BaseMapper<T>` 由 MyBatis-Plus 注入的通用 CRUD 没有项目手写 SQL，因此继续允许，避免为了形式重复实现框架已有能力。

备选方案是要求所有 CRUD 都写 XML，但这会实质放弃 MyBatis-Plus `BaseMapper` 的核心价值，并产生重复 SQL，不符合项目当前技术选型。

### 2. 禁止全部 SQL 承载注解和 Provider 变体

禁止新增 `@Select`、`@Insert`、`@Update`、`@Delete`、`@SelectProvider`、`@InsertProvider`、`@UpdateProvider` 和 `@DeleteProvider`。仅禁止四个直接 SQL 注解会留下 Provider 绕行入口，无法形成唯一 SQL 位置。

`@Mapper` 与 `@Param` 不包含 SQL 文本，继续允许。其他纯结果映射注解如果未来确有需要，应在具体 change 中证明；默认优先由 XML `resultMap` 表达复杂映射。

### 3. 采用“存量不动、触及时迁移”的兼容策略

当前注解 SQL 不因 Rule 生效立即判定为必须在本 change 内整改；后续 change 如果实质修改某个注解 statement 的 SQL、参数、结果映射或数据库行为，必须同时把该 statement 迁入 XML。只修改注释、格式或与 SQL 无关的 Java 内容不触发迁移。

备选方案是本次一次性迁移所有现有 Mapper，但那会扩大到后端业务实现、数据库集成验证和 submodule 交付，不符合用户当前只增加 Rule 的范围。

### 4. Rule、Skill、Spec 与自动治理检查同步收紧

实现同时更新 `backend-conventions.md`、`database-conventions.md` 和 `java-springboot/SKILL.md`。治理测试只检查稳定合同是否存在、冲突措辞是否消除，不伪装成能够理解全部 Java 源码语义的业务扫描器。

未来业务 change 的开发、QA 和 Spec Review 负责检查新增 SQL 的实际文件位置；是否另增源码静态扫描属于独立决策。

## Risks / Trade-offs

- [Java 接口与 SQL 跨文件维护，跳转成本增加] → 固定 `resources/mapper/<业务>/` 路径、全限定 `namespace` 和方法名一致的 statement ID。
- [“实质修改”边界可能产生争议] → 规格明确 SQL 文本、参数、结果映射或数据库行为变化触发迁移，纯格式与无关 Java 修改不触发。
- [存量注解 SQL长期残留] → 采用触及时迁移并在后续涉及相应 statement 的 change 中列出迁移任务；本 change 不虚报已完成全量统一。
- [两个治理 change 修改同一 requirement] → 先完成或归档 `strengthen-engineering-practice-governance`，再实施和归档本 change。

## Migration Plan

1. 用户确认本 change 的 XML 强制边界及存量兼容策略。
2. 确认 `strengthen-engineering-practice-governance` 的归档/同步状态，避免基线冲突。
3. 先补治理失败夹具，再更新两个 Rules 与 Java Skill，使检查转绿。
4. 同步入口说明和 `evidence.md`，运行治理检查、Harness、OpenSpec strict validate 与 `git diff --check`。
5. 本 change 不修改 backend submodule 业务 Mapper；回滚时整体恢复本 change 涉及的治理文本和校验。

## Open Questions

无。若用户要求立即迁移现有注解 SQL，应扩大本 change 的 Goals、Impact、tasks 和验证范围后再次确认。
