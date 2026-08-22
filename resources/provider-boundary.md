# Provider Boundary — v3.0.1

AGY Supervised Development 3.0.1 把 **Pi Native Harness** 与 **模型 Provider** 明确拆开：

```text
Codex App
  ↓
Pi Native Harness
  ↓
Pi Provider abstraction
  ↓
Antigravity / OpenAI / Anthropic / other
```

Provider 负责模型推理；Pi 负责 agent loop/tools/session；Codex 负责监督和最终验收。

---

## 1. 核心边界

```text
Model intelligence != Coding Harness != Supervisor
```

因此：

- Provider 可以替换；
- Pi session/tool behavior 不随模型供应商重写；
- Codex Review Contract 不随 Provider 改变；
- Provider outage 不等于 repository failure；
- credential 不进入监督协议。

---

## 2. 默认目标：Antigravity Provider

目标可以是：

```text
Pi
  ↓ user-selected Provider / Google OAuth
Antigravity
```

再由 Pi 自己提供 coding harness。

v3.0.1 **不绑定具体第三方包名或模型列表**。Provider 扩展更新快，风险声明和 model routing 也可能变化。

---

## 3. 非官方集成风险

第三方 Pi Antigravity Provider 不是 Google 官方 AGY CLI。

必须明确：

- 某些实现作者可能提示 Terms of Service / account suspension 风险；
- 不同实现判断可能不同；
- endpoint/model routing/OAuth compatibility 会变化；
- quota、subscription、model availability 会变化。

Skill 不把以下说法当事实：

```text
"第三方 Pi Antigravity OAuth 是 Google 官方支持方式"
"没有账号风险"
"当前 endpoint/model 会长期稳定"
```

首次启用或 Provider 大版本变化后，应审查当前 source/README/license/risk note。

---

## 4. Credential Ownership

Credential 只由 Pi/Provider 自己的 store 管理。

Skill/Codex 不得：

- 读取并复制 access token；
- 读取并复制 refresh token；
- 打印 Authorization header；
- commit auth 文件；
- 把 token 写进 Task Contract/Review evidence；
- 模拟登录完成状态。

允许记录：

```text
auth_status = usable | missing | expired | error
provider_id
model_id
```

---

## 5. 安装 / 登录边界

Provider 缺失：

```text
BLOCKED: provider-missing
```

未登录/过期：

```text
BLOCKED: auth-required
```

默认不执行：

```bash
pi install npm:<provider>
```

也不自动完成 OAuth。

用户明确要求安装时再按当前 Provider 文档执行；OAuth 浏览器授权、账号选择、条款接受由用户完成。

---

## 6. Provider Capability

Codex/Pi 只需要确认当前 Provider 满足：

```text
provider/model discoverable
credential usable
tool-capable generation
errors can surface
```

Provider 不需要知道：

- baseline；
- Task Contract governance；
- Review Gates；
- Completeness；
- Closeout；
- final Acceptance。

---

## 7. Model Selection / Failover

Model selection 由用户、当前 Pi config 或 Task Contract 决定。

失败时不得静默：

```text
requested provider/model A
→ silently continue with B
```

只在：

- 用户明确要求；或
- Task Contract 明确允许 fallback

时切换，并记录可观察的 requested/actual transition。

Provider 自己 documented 的内部 routing 若仍保持同一个公开 model contract，不必假装知道不可观察内部细节。

---

## 8. Provider Error 分类

```text
401 / invalid auth
→ PROVIDER_AUTH_BLOCKED

429 / quota exhausted
→ PROVIDER_CAPACITY_BLOCKED

timeout / 5xx / reset
→ PROVIDER_TRANSIENT_FAILURE

unknown/removed/unsupported model
→ PROVIDER_CAPABILITY_FAILURE
```

不要把这些直接归成 code failure。

有限 transient retry 可以接受；不无限重试。

---

## 9. Antigravity 与 `agy` CLI

v3 主链路：

```text
Pi Provider → Antigravity
```

不是：

```text
Pi → agy CLI → AGY Harness → Antigravity
```

所以主流程不需要：

- `command -v agy`；
- `agy --help`；
- `agy --conversation`；
- tty7；
- AGY conversation DB/status hook/permission TUI。

未来用户若明确需要官方 AGY CLI fallback，应作为独立可选路径，不偷偷混入 Pi Native 主链路。

---

## 10. Provider Replaceability

3.0.1 不存在自研 Harness 代码，因此更简单：

```text
Codex Skill
  ↓
Pi Native Harness
  ↓
Pi configured Provider
```

Provider-specific transport/auth 只留在 Provider extension 自己内部。

未来可以替换：

```text
Pi + Antigravity
Pi + Codex/OpenAI
Pi + Anthropic
Pi + local/other Provider
```

监督规则不变。

---

## 11. Provider Health Evidence

3.0.1 不要求自定义 `doctor` JSON schema。

只记录从当前 Pi/Provider 可观察到的最小事实：

```text
provider registered/configured
provider/model selected if observable
auth usable/missing/error
actual invocation success/error class
```

不得记录：

```text
accessToken
refreshToken
clientSecret
Authorization
credential file contents
full OAuth payload
```

---

## 12. 更新策略

第三方 Provider 更新快，因此：

- 不 hard-code current model list；
- 不 hard-code internal endpoint；
- 运行时通过当前 Pi/provider capability 发现；
- 文档只保留稳定边界。

---

## 13. 推荐姿势

1. 用户选择/审查 Provider；
2. 用户安装；
3. 用户完成登录；
4. Codex 只确认“可用/不可用”；
5. Provider 只向 Pi 提供 model intelligence；
6. Pi tools 修改 repository；
7. Codex最终独立 Review/Verify。

这样第三方 Provider 风险被限制在模型/传输层，不接管文件权限、Harness lifecycle 或 Acceptance。
