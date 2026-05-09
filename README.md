# VRP Lab

## 一键本地运行

```bash
bash scripts/run_local.sh
```

- Backend: `http://0.0.0.0:8082`
- Frontend: `http://0.0.0.0:7998`

## 手动启动

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


## 本地调试求解（不启动前端/后端）

直接在 `local_run.py` 顶部修改 `DATASET` / `INSTANCE` / `TIME_LIMIT_S` / `POPULATION_SIZE`，然后运行：

```bash
python local_run.py
```
