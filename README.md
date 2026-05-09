# VRP Lab

## 启动

### Backend (0.0.0.0:8082)
```bash
pip install fastapi uvicorn pydantic
uvicorn backend.main:app --host 0.0.0.0 --port 8082 --reload
```

### Frontend (Vite, 7998)
```bash
cd frontend
npm install
npm run dev
```

## API
- `GET /healthz`
- `GET /api/datasets`
- `POST /api/runs`
- `POST /api/runs/{run_id}/stop`
- `GET /api/runs/{run_id}`
- `WS /ws/{run_id}`

## 当前能力
- 统一问题结构（CVRP/CVRPTW）。
- 多数据源加载器骨架（vrplib/Solomon/Homberger）。
- 批量运行结果落盘 CSV。
- WebSocket 推送迭代事件，前端实时收敛曲线。

## 说明
当前 `PyVRPSolver` 仍为占位循环，下一步应替换为真实 PyVRP 建模与 callback 事件上报。
