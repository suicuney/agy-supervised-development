# Provider Boundary

AGY Supervised Development 3.0 把 **Pi Harness** 与 **模型 Provider** 明确拆开。

```text
Codex App
  ↓
Pi Harness
  ↓
Pi Provider API
  ↓
Antigravity / OpenAI / Anthropic / other
```

Provider 负责模型推理；Harness 负责工具、状态、scope、evidence；Codex 负责监督和最终验收。

---

## 1. 为什么必须拆开

v2.1.x 使用 AGY CLI 时，模型、Harness、工具循环和 conversation runtime 被绑定在同一个外部 CLI 中。v3.0 的关键改进是：

```text
Model intelligence != Worker Harness
```

因此：

- Provider 可以替换；
- Harness policy 不随模型供应商重写；
- Codex Review Contract 不随 Provider 改变；
- Provider outage 不等于 repository failure；
- credential 不进入监督协议。

---

## 2. 默认目标：Antigravity Provider

用户当前设计目标是：

```text
Pi
  ↓ Google OAuth
Antigravity
```

再由 Pi 自己提供 coding harness。

Pi 社区已经存在多种 Antigravity Provider extension，典型实现会：

- 注册 `antigravity` 或 `google-antigravity` provider；
- 使用 Google OAuth；
- 将 Gemini / Claude / GPT-OSS 等 runtime model 映射成 Pi Model；
- 使用 Pi 原生 provider streaming，而不是 shell out 到 `agy` CLI。

v3 Skill **不绑定某个第三方包名**。原因：这些扩展更新快、实现边界和风险提示不同。

---

## 3. 非官方集成风险

第三方 Pi Antigravity Provider 不是 Google 官方 AGY CLI。

必须明确：

- 某些 Provider 作者明确提示可能违反 Google Terms of Service；
- 不同实现对账号风险判断并不一致；
- endpoint/model routing/OAuth compatibility 可能随 Google 变化；
- 账号、订阅、quota、模型可用性都可能改变。

因此本 Skill 不把以下陈述当事实：

```text
"Pi Antigravity OAuth 是 Google 官方支持方式"
"使用第三方 Provider 没有账号风险"
"某个 Provider endpoint 会长期稳定"
```

Codex 在首次启用或 Provider 明显更新后，应提醒用户审查 Provider source / README / license / risk note。

---

## 4. Credential Ownership

Credential 只能由 Pi/Provider 自己的 credential store 管理。

Harness / Skill 不得：

- 读取并复制 access token；
- 读取并复制 refresh token；
- 打印 Authorization header；
- 将 credential 写进 `.pi/supervised`；
- 将 auth 文件 commit；
- 把 token 放进 Evidence Bundle；
- 模拟登录完成状态。

可以记录的仅是：

```text
auth_status = usable | missing | expired | error
provider_id
model_id
```

---

## 5. 安装与登录边界

Preflight 发现 Provider 缺失：

```text
BLOCKED: provider-missing
```

发现未登录：

```text
BLOCKED: auth-required
```

默认不执行：

```bash
pi install npm:<provider>
/login <provider>
```

除非用户明确要求安装/登录。

OAuth 浏览器授权、账号选择、条款接受由用户自己完成。

---

## 6. Provider Capability Contract

Harness 只要求 Provider 满足：

```text
model discoverable
credential usable
text/tool-capable generation
stream/result can settle
abort/error can surface
usage metadata optional
```

Provider 不需要知道：

- Task Contract；
- baseline；
- review gates；
- closeout state；
- final acceptance。

这些属于 Harness/Codex。

---

## 7. Model Selection

Model selection 可以由用户或 Codex Task Contract 指定，但 Harness 不应在失败时静默升级/降级模型。

例如：

```text
requested: antigravity/<model-A>
actual:    antigravity/<model-B>
```

只有以下情况才能发生：

- 用户明确选择；
- Task Contract 允许 fallback；
- Provider 自己的 documented internal routing 不改变公开 model contract。

所有可观察的 Provider/model transition 写入 Evidence Bundle。

---

## 8. Provider Error 分类

不要把所有 Provider error 都归成 worker failure。

### Authentication

```text
401 / invalid_grant / expired credential / login required
→ PROVIDER_AUTH_BLOCKED
```

### Quota / Rate limit

```text
429 / quota exhausted / subscription limit
→ PROVIDER_CAPACITY_BLOCKED
```

### Transport

```text
timeout / 5xx / connection reset
→ PROVIDER_TRANSIENT_FAILURE
```

### Model unavailable

```text
unknown model / removed routing / unsupported tool call
→ PROVIDER_CAPABILITY_FAILURE
```

### Harness policy block

这不是 Provider error：

```text
tool denied / path denied / one-way decision
→ HARNESS_POLICY_BLOCKED
```

分类必须进入 evidence，方便 Codex 判断是否重试、换模型还是向用户求助。

---

## 9. Retry / Failover

Provider transient error 可以有**有限、可观察** retry。

规则：

- 不无限 retry；
- 遵守 Provider retry-after；
- operation ID 不因为内部 safe retry 随意改变；
- 如果 crash/retry 可能重复 tool effect，先进入 recovery analysis；
- model/provider failover 默认需要 Task Contract 授权。

不要因为 Provider 断线就重新跑全部实现步骤。

---

## 10. Antigravity 与 `agy` CLI 的关系

v3 主链路：

```text
Pi Provider → Antigravity
```

不是：

```text
Pi → agy CLI → AGY Harness → Antigravity
```

因此 v3 主流程不需要：

- `command -v agy`；
- `agy --help`；
- `agy --conversation`；
- tty7；
- AGY conversation DB；
- AGY status hook；
- AGY permission TUI。

如果用户未来明确要求官方 AGY CLI fallback，它应被设计成**单独 Adapter**，不能偷偷混回 v3 主链路。

---

## 11. Provider 替换性

Harness 代码不要出现这种耦合：

```text
if provider == antigravity:
    task lifecycle = ...
```

应该：

```text
Harness lifecycle
  ↓
Pi Model/Provider abstraction
```

Provider-specific code只存在于 Provider extension 自己内部，或极薄 diagnostics adapter。

这样未来可以：

```text
Pi Harness + Antigravity
Pi Harness + Codex subscription
Pi Harness + Anthropic
Pi Harness + local model
```

而监督规则不变。

---

## 12. Provider Health Evidence

Harness `doctor` 可以输出：

```json
{
  "provider": "antigravity",
  "installed": true,
  "auth": "usable",
  "model": "...",
  "modelAvailable": true,
  "toolCapable": true
}
```

不得输出：

```text
accessToken
refreshToken
clientSecret
Authorization
credential path content
full OAuth response
```

---

## 13. 更新策略

第三方 Provider 更新快。v3 不在 Skill 里 hard-code 当前模型列表和 endpoint。

Preflight 读取**当前实际 Provider catalog**。

只有 Harness compatibility 需要 pin：

```text
Pi major/minor capability range
Harness extension API expectations
Evidence schema version
```

Provider/model catalog 运行时发现。

---

## 14. 推荐的安全姿势

对于 Antigravity Provider：

1. 用户自己选择并审查 Provider；
2. 用户自己安装；
3. 用户自己完成 `/login`；
4. Harness 只读取“是否可用”的能力状态；
5. Provider 只给 Pi 提供 model stream；
6. Pi Tools 执行所有 repository 操作；
7. Codex 最终独立验证。

这样可以最大程度把第三方 Provider 风险限制在**模型传输层**，而不让它接管 Harness、文件权限或最终验收。
