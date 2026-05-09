# VRP Lab (Scaffold)

一个面向 CVRP / CVRPTW 的实验与研究框架骨架，核心求解器定位 PyVRP，包含：

- 多源 benchmark loader（VRPLIB、Solomon、Homberger）
- 统一问题接口（`VRPProblem`）
- 批量运行器（Batch Runner）与 CSV 输出
- FastAPI REST + WebSocket 实时事件通道
- React 前端骨架（实验配置、收敛曲线、路线回放）

## Backend

```bash
pip install fastapi uvicorn pydantic
uvicorn backend.main:app --reload
```

API:
- `GET /api/datasets`
- `POST /api/runs`
- `GET /api/runs/{run_id}`
- `WS /ws/{run_id}`

## 目录

与需求一致：`backend/`、`frontend/`、`dashboard/`、`results/`。

## 后续建议

1. 将 `PyVRPSolver` 中的模拟迭代替换为真实 pyvrp 模型构建与 `solve()`。
2. 在 callback 内将 iteration 状态推送到 `EventBus`，实现前端实时动画。
3. 增加 benchmark 自动下载器（含 checksum 与缓存索引）。
4. 将 batch 管理升级为作业队列（如 Celery/RQ）并持久化任务状态。
