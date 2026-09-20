from pathlib import Path

dirs = """configs
data/raw data/synthetic data/external data/interim data/processed
notebooks
src/mplads/data src/mplads/features src/mplads/models src/mplads/risk src/mplads/geo src/mplads/assistant
pipelines models
app/pages app/components
tests reports/figures docs""".split()

files = """README.md requirements.txt .env.example .gitignore Makefile
configs/config.yaml configs/risk_weights.yaml
src/mplads/__init__.py src/mplads/config.py
src/mplads/data/__init__.py src/mplads/data/schema.py src/mplads/data/loaders.py src/mplads/data/cleaning.py src/mplads/data/unify.py src/mplads/data/synthetic.py
src/mplads/features/__init__.py src/mplads/features/financial.py src/mplads/features/progress.py src/mplads/features/cost.py src/mplads/features/agency.py src/mplads/features/delay_features.py src/mplads/features/quality.py
src/mplads/models/__init__.py src/mplads/models/anomaly.py src/mplads/models/delay.py src/mplads/models/duplicates.py src/mplads/models/registry.py
src/mplads/risk/__init__.py src/mplads/risk/engine.py src/mplads/risk/explain.py src/mplads/risk/priority.py
src/mplads/geo/__init__.py src/mplads/geo/geocode.py src/mplads/geo/weather.py
src/mplads/assistant/__init__.py src/mplads/assistant/tools.py src/mplads/assistant/prompts.py src/mplads/assistant/chat.py
pipelines/build_dataset.py pipelines/train_models.py pipelines/score_all.py pipelines/evaluate.py
app/main.py app/pages/1_Overview.py app/pages/2_Risk_Alerts.py app/pages/3_Project_Investigation.py app/pages/4_Duplicate_Overlap.py app/pages/5_Delay_Prediction.py app/pages/6_Cost_Financial.py app/pages/7_GIS_Risk_Map.py app/pages/8_AI_Assistant.py
docs/data_dictionary.md docs/methodology.md docs/assumptions.md docs/architecture.md""".split()

for d in dirs:
    Path(d).mkdir(parents=True, exist_ok=True)
    Path(d, ".gitkeep").touch()          # lets Git track empty folders
for f in files:
    Path(f).touch()
print("Done")
