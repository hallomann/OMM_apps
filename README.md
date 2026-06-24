# OMM apps
To run locally: `streamlit run %appname%.py`

## Getting ready to dev

### 1. Clone repository

```bash
git clone <repo_url>
cd <repo_name>
git pull
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```
### 4. Verify imports

```bash
python -c "from voice_helper.tts import build_listen_message; from configs.sfft_fields import SFFT_FIELDS; print('ok')"
```

### 5. Run tests

```bash
python -m unittest discover -s tests -v
```

### 6. Run SFFT app

```bash
streamlit run sfft_app.py --server.port 8510
```

### 7. Run Shunt app

```bash
streamlit run shunt_app.py --server.port 8511
```

