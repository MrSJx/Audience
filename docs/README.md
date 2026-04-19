# Docs

Project documentation for the Audience MVP and its post-MVP foundations.

## Current Implementation

- Full media analysis pipeline for `image` and `short_video`
- Local Llama 3.2-oriented audience reaction report generation
- Structured API with upload, analysis, and report persistence
- React frontend with upload form, report rendering, and history
- SQLite-backed local report storage
- Frozen Simulation 2.0 contract for future multi-agent runs
- Multi-agent persistence tables added beside the MVP report table

## API Endpoints

- `GET /` - Application status and starter report shape
- `GET /health` - Health check
- `GET /contract` - MVP upload contract and schema examples
- `GET /report-schema` - Report and analysis schema examples
- `GET /simulation-schema` - Phase 11 Simulation 2.0 schema snapshot
- `POST /analyze` - Upload media and receive a structured audience reaction report
- `GET /report/{id}` - Retrieve a previously generated report
- `GET /reports` - List recent reports

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
cd backend
pytest tests/ -v
```
