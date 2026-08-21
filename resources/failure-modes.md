# AGY Supervised Development Failure Modes

本文件用于把“卡住了”拆成可诊断状态。原则：**先收集证据，再采取动作；不要盲目重复 send。**

## 1. AGY binary 不存在

### 证据

```bash
command -v agy
```

无输出或退出非 0。

### 处理

- 停止监督开发；
- 告知用户本机找不到 `agy`；
- 不自行安装、升级或修改全局 PATH，除非用户明确要求。

---

## 2. tty7 不可达

### 证据

```bash
tty7 doctor
```

失败。

### 处理

- 不自行启动/重启 tty7 server；
- 不接管其他 pane；
- 向用户报告阻塞点。

---

## 3. AGY 启动后没有新输出

### 可能原因

- 仍在启动；
- 停在 trust/auth/permission；
- 进程已经退出；
- capture 读到旧输出；
- 当前 pane 不是本任务 pane。

### 检查

```bash
tty7 capture "%<id>" --plain --scrollback
tty7 procs
```

若支持 status hook，可使用 changed/wait 机制确认是否有新状态。

### 处理

根据实际状态继续，不重复发送相同 prompt 轰炸终端。

---

## 4. Trust / Auth / Permission 阻塞

### Trust

只有路径准确等于当前 `repo_root`，且确认项明确表示信任该目录时，才允许确认一次。

### Auth

账号登录、OAuth、订阅/配额相关操作属于用户控制范围，默认暂停。

### Permission

只允许 Task Contract 内、本地、低风险操作继续。出现 workspace 外访问、外部系统、破坏性命令或发布动作时停止。

---

## 5. Workspace / Context 串项目

这是监督开发的高优先级故障。

### 迹象

- AGY 提到另一个项目名；
- AGY 返回的 root 与 `repo_root` 不一致；
- AGY 无法找到当前仓库已知文件，却能描述旧项目文件；
- AGY 修改了 workspace 之外的路径；
- AGY 恢复了不属于本任务的旧 conversation。

### 处理

1. 立即停止编码；
2. capture 当前输出留证；
3. 检查 Git state，确认是否已有误改；
4. 不直接删除或回滚未知改动；
5. 关闭/放弃本 Skill 创建的错误 pane；
6. 创建新的隔离 pane；
7. 使用当前版本支持的显式 directory/project 绑定；
8. 重新做 workspace verification；
9. 确认无误后再重新委派任务。

---

## 6. AGY 声称 Done，但 Git 没有对应改动

### 检查

```bash
git status --short
git diff --stat
git diff
```

### 处理

- 不接受 `done`；
- 明确告诉 AGY：实际 repository state 没有满足 Task Contract 的改动；
- 要求它定位自己写入了哪里；
- 同时重点检查 workspace 是否串项目。

---

## 7. AGY 修改超出 Scope

### 例子

- 顺手重构无关模块；
- 大面积格式化；
- 修改配置/依赖但需求不需要；
- 删除用户已有文件；
- 改 API contract 但没有同步调用方。

### 处理

- 先记录哪些改动属于越界；
- 不用 `git reset --hard` 粗暴清理；
- 通过同一 pane 要求 AGY 只撤销**它自己本次产生的越界改动**；
- Codex 再检查 diff，确保没有误伤 baseline。

---

## 8. 测试失败

分类失败原因：

1. 本次代码真实回归；
2. 测试本身需要更新；
3. 环境/依赖问题；
4. 与本任务无关的既有失败；
5. flaky / 外部服务不可用。

### 处理

把失败命令、关键错误、涉及文件和预期行为发给 AGY。修复后由 Codex 独立重跑。

不要只把“test failed”四个字丢回去。

---

## 9. AGY 反复修不好同一个问题

当同一缺陷连续出现多轮返工时：

1. 停止重复相同 prompt；
2. Codex 重新检查根因和调用链；
3. 缩小问题为更明确的 Task Contract；
4. 必要时要求 AGY 先解释根因和修复方案，不立即改代码；
5. 如果继续失败，向用户报告当前阻塞，而不是无限循环。

---

## 10. 长任务 Timeout / 卡住

先区分：

- 模型仍在工作；
- shell/test 在长时间运行；
- 等待权限；
- 进程死锁/退出；
- tty7 capture 只是没有刷新。

通过 capture/procs 和实际子进程判断后，再决定等待状态变化、取消当前动作或重新委派。不要无证据地启动第二个 AGY 同时改同一工作区。

---

## 11. 生成物/临时文件污染

最终 Review 常见：

- build output；
- coverage；
- log；
- 临时 patch；
- debug 文件；
- IDE metadata；
- lockfile 意外变化。

处理前先确认它是否是项目应提交产物。若不是，让 AGY 清理它本次生成的文件，再 Review `git status`。

---

## 12. 外部副作用请求

AGY 若提出或准备执行：

- push；
- merge；
- deploy；
- release；
- 删除远端资源；
- 写生产数据库；
- 创建云资源；

默认停止并交由用户决定。监督开发的“完成”默认止于本地 repository 可验收状态。
