# Scripts Directory

Helper scripts for Retail Branch Management System.

## Setup Scripts

### 1. `setup_local.sh` - Local Development Setup

**Purpose:** Setup local development environment with all dependencies.

**Usage:**
```bash
./scripts/setup_local.sh
```

**What it does:**
- Installs UV package manager (if needed)
- Creates Python virtual environment
- Installs Python dependencies
- Installs Node.js dependencies (Tailwind CSS)
- Builds Tailwind CSS
- Creates `.env` file from template

**Requirements:**
- Python 3.12+
- Node.js 18+ (optional, for Tailwind CSS)

---

### 2. `run_local.sh` - Run Development Server

**Purpose:** Start FastAPI development server with Tailwind CSS watcher.

**Usage:**
```bash
./scripts/run_local.sh
```

**What it does:**
- Activates virtual environment
- Starts Tailwind CSS in watch mode (background)
- Starts FastAPI server with auto-reload
- Server runs at `http://localhost:8000`

**Stop:** Press `Ctrl+C`

---

## Google Cloud Platform Scripts

### 3. `test_service_account.py` - Test GCP Permissions

**Purpose:** Verify service account has correct permissions.

**Usage:**
```bash
python scripts/test_service_account.py
```

**What it tests:**
- ✅ BigQuery connection
- ✅ Dataset existence
- ✅ Table listing
- ✅ Query execution
- ✅ Cloud Storage access
- ✅ Bucket access

**Requirements:**
- `.env` configured with:
  - `GOOGLE_APPLICATION_CREDENTIALS`
  - `PROJECT_ID`
  - `GCS_BUCKET` (optional)

**Example output:**
```
✅ BigQuery: Connected as project 'your-project'
✅ BigQuery: Can list datasets (2 found)
✅ Dataset: 'retail_branches' exists
✅ Dataset: Contains 10 table(s)
✅ Storage: Can access bucket 'retail-branch-documents'
```

---

### 4. `setup_bigquery.py` - Create BigQuery Tables

**Purpose:** Create dataset and all required tables.

**Usage:**
```bash
python scripts/setup_bigquery.py
```

**What it creates:**
- Dataset: `retail_branches`
- Tables:
  - `branches` - Branch information
  - `documents` - Document metadata
  - `users` - User accounts
  - `user_teams` - User team permissions
  - `legal_ppp09` - Legal ภ.พ.09 data
  - `audit_logs` - Activity logs (partitioned)
  - `dc_changes` - DC change history
  - `provinces` - Province master data
  - `districts` - District master data
  - `subdistricts` - Subdistrict master data

**Requirements:**
- `.env` configured
- Service account with:
  - `roles/bigquery.dataEditor`
  - `roles/bigquery.jobUser`

**Run only once** per project/environment.

---

### 5. `create_test_user.py` - Create Test User

**Purpose:** Add test user to database for login testing.

**Usage:**
```bash
python scripts/create_test_user.py
```

**Interactive prompts:**
1. Email address (e.g., `your-email@gmail.com`)
2. Full name
3. User level (admin/manager/editor/viewer)
4. Team(s) (for non-admin)
5. Role in team(s)

**Example:**
```
Email: john@example.com
Name: John Doe
User Level: admin
Teams: (none - admin has access to all)

✅ User created with ID: abc-123-def
✅ Test user created successfully!
```

**Requirements:**
- BigQuery tables created (`setup_bigquery.py`)
- Email must match Google account for OAuth login

---

## Setup Workflow

**First Time Setup:**

```bash
# 1. Setup local environment
./scripts/setup_local.sh

# 2. Configure .env file
cp .env.example .env
nano .env  # Add your credentials

# 3. Test service account
python scripts/test_service_account.py

# 4. Create BigQuery tables
python scripts/setup_bigquery.py

# 5. Create test user
python scripts/create_test_user.py

# 6. Start development server
./scripts/run_local.sh

# 7. Visit http://localhost:8000/login
```

---

## Troubleshooting

### Error: `PROJECT_ID not set`
**Solution:** Add `PROJECT_ID=your-project-id` to `.env`

### Error: `Failed to connect to BigQuery`
**Solution:**
1. Check `GOOGLE_APPLICATION_CREDENTIALS` in `.env`
2. Verify service account key file exists
3. Run `python scripts/test_service_account.py`

### Error: `Dataset does not exist`
**Solution:** Run `python scripts/setup_bigquery.py`

### OAuth Error: `redirect_uri_mismatch`
**Solution:**
1. Check `OAUTH_REDIRECT_URI` in `.env`
2. Add to Google OAuth Authorized redirect URIs:
   - `http://localhost:8000/auth/callback`

### Tailwind CSS not compiling
**Solution:**
```bash
npm install
npm run build
```

---

## Environment Variables Required

**Minimal `.env` for development:**
```bash
# Required for BigQuery/Storage
PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json

# Required for OAuth
GOOGLE_CLIENT_ID=xxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=xxx

# Optional (has defaults)
DATASET_ID=retail_branches
GCS_BUCKET=retail-branch-documents
SESSION_SECRET=your-random-secret-min-32-chars
```

---

## Script Dependencies

| Script | Requires |
|--------|----------|
| `setup_local.sh` | bash, curl |
| `run_local.sh` | bash, Python venv |
| `test_service_account.py` | google-cloud-bigquery, google-cloud-storage |
| `setup_bigquery.py` | google-cloud-bigquery |
| `create_test_user.py` | google-cloud-bigquery |

All Python dependencies are installed via `setup_local.sh`.
