# SFD Sistema Jurídico - AI Coding Agent Instructions

## Project Overview
**SFD** (Sistema Jurídico) is a Streamlit-based legal case management system tracking client cases from intake through litigation. The system automates case creation, track milestones, and manages legal document workflows.

**Tech Stack:** Streamlit (UI), SQLAlchemy (ORM), SQLite (database)

---

## Architecture & Module Structure

### Three Core Modules
Each module is self-contained with its own `service.py` containing business logic:

1. **`modules/captacion/`** - Case Intake
   - `formulario1.py`, `formulario2.py` - Multi-step Streamlit forms
   - `service.py` - `crear_caso()` function orchestrates client + case creation
   - Flow: Role selection → client data → case registration → radicado generation

2. **`modules/produccion/`** - Case Management Dashboard
   - `dashboard.py` - Analytics & case status views
   - `service.py` - Dashboard data aggregation

3. **`modules/seguimiento/`** - Case Tracking & External Data
   - `scraper.py` - External data collection (web scraping)
   - `service.py` - Follow-up milestone management

### Database Layer (`core/`)
- **`database.py`** - SQLAlchemy engine/sessionmaker setup (SQLite)
- **`models.py`** - ORM models with emoji comments (👤 Cliente, ⚖️ Caso, 📍 Hito)
  - FK relationships: `Caso` → `Cliente` (many-to-one), `Hito` → `Caso` (many-to-one)
  - State field tracks workflow: default state = `"captacion"`

### Services & Utilities
- **`services/radicado.py`** - Case reference number generation (format: `SFD-YEAR-ROLCODE-NUMBER`)
- **`services/validation.py`** - *Empty placeholder* for validators (cedula, phone, email)
- **`services/storage.py`** - *Empty placeholder* for file/document handling

---

## Key Patterns & Conventions

### Database Access Pattern
```python
# Directly import SessionLocal from core.database
from core.database import SessionLocal
from core.models import Cliente, Caso

db = SessionLocal()
cliente = Cliente(...)
db.add(cliente)
db.commit()  # Always commit after write operations
db.refresh(cliente)  # Refresh to get generated IDs
```

### Role Mapping Convention
Roles are mapped to 3-letter codes used in radicado generation:
- "Demandante" → `"DTE"` (plaintiff)
- "Demandado" → `"DDO"` (defendant)
- Other → `"TRA"` (other)

Located in [modules/captacion/service.py](modules/captacion/service.py) as `mapear_rol()` utility.

### Streamlit Form Pattern
Forms in [modules/captacion/formulario1.py](modules/captacion/formulario1.py) follow:
1. **Conditional workflows** - `flujo_documentos` flag determines if prior documentation required
2. **Multi-column layouts** - `st.columns(2)` for name/cedula, phone/email pairs
3. **Input validation** - Real-time formatting feedback:
   - Cedula: numeric only, formatted with dots (e.g., `1.234.567`)
   - Celular: 57+prefix+8digits minimum (Colombian format)
4. **Radio selection** - Role choice determines case type and document requirements

### Radicado Generation
`generar_radicado(rol_codigo)` in [services/radicado.py](services/radicado.py):
- Uses **global counter** (non-persistent, resets on app restart)
- Format: `SFD-{YEAR}-{ROLCODE}-{PADDED_NUMBER}` (e.g., `SFD-2026-DTE-0001`)
- ⚠️ **Known limitation:** Counter not persisted to DB - requires refactoring for production

---

## Common Workflows

### Adding a New Field to Case Intake
1. Add column to `Caso` or `Cliente` model in [core/models.py](core/models.py)
2. Update form in [modules/captacion/formulario1.py](modules/captacion/formulario1.py) to collect input
3. Update `crear_caso(data)` in [modules/captacion/service.py](modules/captacion/service.py) to pass data to ORM

### Adding Case Lifecycle State
- Case states stored in `Caso.estado` field (default: `"captacion"`)
- Expected states: `"captacion"` → `"produccion"` → `"sentencia"` (or similar)
- Update state transitions in appropriate module service layer

### Extending Validations
- Create validators in [services/validation.py](services/validation.py)
- Call from Streamlit form before `crear_caso()` call
- Example: cedula format `\d{6,12}`, phone: `57\d{10}`

---

## Important File Locations
| Purpose | File |
|---------|------|
| DB connection & session | [core/database.py](core/database.py) |
| ORM models | [core/models.py](core/models.py) |
| Case intake logic | [modules/captacion/service.py](modules/captacion/service.py) |
| Intake forms | [modules/captacion/formulario1.py](modules/captacion/formulario1.py), formulario2.py |
| Role/case reference generation | [services/radicado.py](services/radicado.py) |
| Entry point | [main.py](main.py) |

---

## Development Notes

**⚠️ Technical Debt:**
- `config.py` is empty - environment variables (DB path, feature flags) not externalized
- `session.py` unused - session management not implemented
- Global counter in radicado.py not database-backed (app restart loses count)
- No explicit transaction management or error handling in database operations
- Direct `SessionLocal()` calls in services (consider dependency injection)

**Default Conventions:**
- Emoji comments in models (👤, ⚖️, 📍) - maintain for scannability
- Streamlit session_state for form persistence across reruns (if implemented)
- Markdown for section headers with `st.markdown("## Title")`
