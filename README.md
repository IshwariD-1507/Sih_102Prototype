# MPLADS Project Monitoring & Risk Intelligence System

**Problem Statement ID:** SIH26102  
**Problem Statement:** AI-powered MPLADS Fraud / Anomaly Detection  
**Theme:** Smart Automation  
**Category:** Software  
**Hackathon:** Smart India Hackathon (SIH) 2026

> **Detect unusual project patterns → explain why they were flagged → prioritize projects for human review.**

---

## 1. Executive Summary & Presentation Pitch

The **MPLADS Project Monitoring & Risk Intelligence System** is a prototype decision-support platform for analysing project records under the **Members of Parliament Local Area Development Scheme (MPLADS)**.

The prototype combines official project datasets with statistical feature engineering, semantic similarity analysis, rule-based risk scoring, explainable risk reasons, district-scoped access control, and an interactive Streamlit dashboard.

The system is designed to help an authorized officer move from thousands of project records to a smaller set of projects that deserve closer verification.

The platform does **not** declare that a project is fraudulent or establish wrongdoing. A risk category is a screening signal that indicates that the project contains one or more unusual, inconsistent, overlapping, delayed, or incomplete-data patterns that may warrant human investigation.

### Core idea

1. Ingest MPLADS project records from the available datasets.
2. Clean and unify recommended, sanctioned, and completed work records.
3. Engineer financial, lifecycle, progress, evidence, cost, overlap, and data-quality features.
4. Detect semantically similar projects using a Sentence Transformer embedding model.
5. Convert project-level signals into an explainable 0–100 risk score.
6. Assign each project to Low, Medium, High, or Critical risk categories.
7. Generate human-readable reasons explaining why a project was flagged.
8. Create a review queue containing Medium, High, and Critical projects.
9. Present the results through role-aware Streamlit dashboards.

---

## 2. Core Operational Workflow

```text
                MPLADS Source Datasets
                         │
                         ▼
              Data Cleaning & Normalization
                         │
                         ▼
               Unified Project Dataset
                         │
                         ▼
                  Feature Engineering
        ┌────────────────┼─────────────────┐
        ▼                ▼                 ▼
   Financial        Lifecycle /       Evidence /
    Features        Progress          Data Quality
        │                │                 │
        └────────────────┼─────────────────┘
                         ▼
                   Cost Benchmarking
                         │
                         ▼
              Semantic Duplicate Detection
                         │
              Sentence Transformer Embeddings
                         │
                         ▼
                Overlap Candidate Pairs
                         │
                         ▼
                Multi-Signal Risk Engine
                         │
       ┌─────────────────┼────────────────────┐
       ▼                 ▼                    ▼
 Financial / Cost     Delay / Progress    Overlap / Quality
       │                 │                    │
       └─────────────────┼────────────────────┘
                         ▼
                Explainable Risk Score
                         │
                         ▼
              Low / Medium / High / Critical
                         │
                         ▼
                 Review Queue (CSV)
                         │
                         ▼
              Streamlit Monitoring Portal
                         │
       ┌─────────┬───────┼────────┬──────────────┐
       ▼         ▼       ▼        ▼              ▼
   Overview  Risk Alerts Project  Duplicate   Delay / Cost /
                      Investigation Overlap    GIS Views
```

---

## 3. Data Sources

The prototype currently works with the following raw MPLADS CSV datasets:

| Dataset | Records in prototype | Purpose |
|---|---:|---|
| `Works Recommended.csv` | 8,001 | Recommended works and recommendation details |
| `Works Sanctioned.csv` | 27,001 | Sanctioned project master records and sanctioned amounts/status |
| `Works Completed.csv` | 8,001 | Completion dates, disbursed amounts and completion-image information |
| `Allocated Limit for Honble MPs.csv` | 544 | MPLADS allocation-limit reference data |
| `Amount consented for Calamity.csv` | 13 | Calamity-related consented-amount reference data |

The active project-unification pipeline currently uses **Works Recommended, Works Sanctioned, and Works Completed** to construct the main project table. The other raw datasets are retained as available source/reference data.

### Current prototype scale

- Unified projects: **27,001**
- Engineered project features: **56 columns**
- Potential semantic-overlap candidate pairs: **129,117**
- Review queue projects: **5,393**

The figures above describe the dataset included with the current prototype snapshot and may change when the source data is replaced or refreshed.

---

## 4. Data Processing & Feature Engineering

### 4.1 Data unification

The data pipeline standardizes column names, cleans text and dates, converts financial amounts, normalizes work IDs, removes duplicate work IDs before merging, and combines recommended, sanctioned, and completed records using `Work_ID`.

The sanctioned dataset acts as the master project table so that sanctioned works are retained even when recommendation or completion information is unavailable.

### 4.2 Financial features

The system derives:

- Recommendation → sanction amount gap
- Recommendation → sanction percentage gap
- Disbursement utilisation percentage
- Amount remaining
- Disbursement exceeding sanction flag
- Sanction exceeding recommendation flag
- Missing disbursement information
- Missing recommendation information

### 4.3 Lifecycle and progress features

The system derives:

- Recommendation → sanction duration
- Sanction → completion duration
- Recommendation → completion duration
- Completion status
- Missing completion information
- Completed / In Progress status
- Completion-image availability
- Completion-evidence missing flag

The current source data does **not** contain a reliable numerical physical-progress percentage. The prototype therefore does not invent one.

### 4.4 Cost benchmarking

Cost anomaly detection is currently **statistical and formula-based**, not an ML prediction.

Each project is assigned a peer group based primarily on:

```text
State + Work Category
```

For each peer group, the system calculates the median sanctioned amount and then calculates:

```text
Cost Deviation = Sanction Amount - Peer Median

Cost Deviation % =
    (Sanction Amount - Peer Median)
    / Peer Median × 100
```

A project is marked as having a high cost deviation when the deviation exceeds **50% above its peer-group median**.

This 50% threshold is a prototype screening threshold and is **not an official MPLADS statutory threshold**.

---

## 5. AI / ML Components

The current prototype contains one active ML-based detection path and an additional AI/NLP utility module that is present in the codebase but is not currently wired into the main duplicate-detection pipeline.

### 5.1 Active ML component: semantic duplicate / overlap detection

The duplicate detector uses the **Sentence Transformers** library with the `all-MiniLM-L6-v2` model.

The workflow is:

```text
Work Description
      ↓
Text cleaning
      ↓
Sentence Transformer embedding
      ↓
384-dimensional semantic representation
      ↓
Cosine-distance nearest-neighbour search
      ↓
Potentially similar project pairs
```

Projects are first blocked by **State + Work Category** so that comparisons are made within a more relevant project context.

Candidate pairs are identified using a semantic similarity threshold of **0.80**.

The final overlap score combines available signals:

- Semantic similarity: **60%**
- Cost similarity: **25%**
- Sanction-date similarity: **15%**

When secondary signals are missing, the available weights are renormalized instead of artificially reducing the score.

The resulting score is a **screening signal**. It does not prove that two projects are duplicates or that funds were improperly used.

### 5.2 Multilingual AI utility present in the codebase

The repository also contains `src/mplads/features/text_normalization.py`, which defines an AI-based text-normalization pipeline using:

- AI4Bharat IndicXlit for transliteration
- AI4Bharat IndicTrans2 for Indic-language → English translation
- PyTorch / Transformers

The intended flow is:

```text
Romanized Indic text
        ↓
IndicXlit transliteration
        ↓
Native Indic script
        ↓
IndicTrans2 translation
        ↓
English representation
```

However, this utility is **not currently called by the active duplicate-detection pipeline** in the supplied prototype. The active `DuplicateDetector` directly embeds the cleaned work descriptions with `all-MiniLM-L6-v2`.

### 5.3 What is NOT currently an ML model

Despite the dashboard page being named **Delay Prediction**, the supplied prototype does not currently contain an active Random Forest, Isolation Forest, regression model, or other trained delay-prediction model.

The current delay signal is statistical:

```text
Sanction → Completion duration
        ↓
90th percentile of available completed durations
        ↓
Projects above that threshold → Delay Risk Signal
```

Likewise, cost anomaly detection is peer-median / percentage-deviation based, and the final risk score is a deterministic rule-based scoring engine.

This distinction is important for accurately presenting the prototype to judges.

---

## 6. Mathematical Risk Scoring Formula

The prototype uses a multi-signal, explainable score rather than a black-box risk prediction model.

The maximum conceptual contributions are based on:

| Signal | Risk contribution |
|---|---:|
| Financial anomaly | Up to 20 points |
| Progress mismatch | 20 points |
| Delay risk | 20 points |
| Cost anomaly | Up to 25 points |
| Duplicate / overlap | Up to 35 points, clipped within the final score |
| Data quality | 10 points |

The final score is calculated as the sum of the generated risk-point components and then clipped to the range **0–100**.

### Risk bands

| Risk Score | Category |
|---:|---|
| 0–30 | Low |
| 31–60 | Medium |
| 61–80 | High |
| 81–100 | Critical |

### Severity-based signals

#### Financial anomaly

The recommendation/sanction percentage gap contributes progressively:

- >20% → 10 points
- >50% → 15 points
- >100% → 20 points

A disbursement exceeding the sanctioned amount is also treated as a financial anomaly signal.

#### Progress mismatch

A project marked as completed while completion information is incomplete creates a progress/data-consistency signal.

#### Delay risk

Projects whose sanction-to-completion duration is above the dataset's 90th percentile are flagged as unusually long-duration projects.

#### Cost anomaly

Peer-group cost deviation contributes progressively:

- >50% → 10 points
- >100% → 15 points
- >200% → 20 points
- >300% → 25 points

#### Duplicate / overlap

Overlap points increase with semantic overlap score and the number of related candidate projects.

#### Data quality

Missing core project information or missing completion evidence contributes a data-quality signal.

---

## 7. Explainable Risk Alerts

Every scored project receives a `Risk_Reasons` field generated from the triggered signals.

Example reasons include:

- Recommendation/sanction amount deviation
- Project completion duration unusually high compared with the dataset
- Sanction amount above the peer-group benchmark
- Potential overlap with related projects
- Missing project or monitoring information

For example, a project can be shown as **Critical** because several independent screening signals occur together, rather than because the system makes a direct allegation of fraud.

This makes the risk engine auditable: an officer can inspect the underlying feature and the reason that contributed to the alert.

---

## 8. Key System Features

| Module | Purpose |
|---|---|
| **Executive Dashboard / Overview** | Displays total works, recommended amount, completed and active works, project status distribution and risk distribution. |
| **Risk Alerts & Review Queue** | Shows Medium, High and Critical projects sorted by risk score, with rank, score, category, reasons and project information. |
| **Project Investigation** | Provides a searchable project-level audit table. Search is performed across all available project fields, including Work ID, description, MP, constituency, state, amounts, dates, status and risk information. |
| **Duplicate & Overlap Detection** | Displays potential candidate pairs, semantic similarity, cost similarity, date similarity, overlap score and review category. |
| **Delay Prediction & Risk Matrix** | Presents project execution timelines and the current duration-based delay-risk signals. |
| **Financial & Cost Breakdown** | Provides access to the engineered financial and cost fields for project-level analysis. |
| **GIS Risk Map** | Provides a geographic risk view when reliable latitude/longitude fields are available; otherwise it explicitly refuses to fabricate coordinates and shows the filtered project table. |
| **Authentication & District Scoping** | Provides mock role-based login and limits district officers to their assigned district while central administrators can access all districts. |

---

## 9. Project Search

The **Project Investigation** module contains a dedicated search bar.

Search is performed across the complete row rather than being restricted to only `Work_ID`.

This allows an officer to search using information such as:

- Work ID
- Work description
- State
- MP
- Constituency
- Work category
- Amount values
- Dates
- Project status
- Risk score
- Risk category
- Risk reasons

The search uses literal, case-insensitive matching and reports the number of matching projects.

---

## 10. Authentication & Role-Based District Access

The prototype includes a demonstration authentication layer.

### Central Admin

- Can access all districts.
- Intended for central-level monitoring.

### District Officer

- Assigned to a specific district.
- Project tables are filtered to the assigned district.
- The filter fails closed if district information cannot be determined, preventing accidental exposure of the full dataset to a district-scoped user.

### Current prototype users

The authentication database is currently a **mock in-code user database for demonstration purposes**, not a production identity-management system.

Production deployment should replace this with secure authentication, password hashing, role-based authorization, secret management and an audit trail.

---

## 11. Duplicate / Overlap Detection Method

The duplicate detector follows a multi-stage approach.

```text
All unified projects
        │
        ▼
Clean work descriptions
        │
        ▼
Block by State + Work Category
        │
        ▼
Sentence Transformer embeddings
        │
        ▼
Cosine nearest-neighbour search
        │
        ▼
Similarity threshold ≥ 0.80
        │
        ▼
Candidate project pairs
        │
        ▼
Overlap score
        │
        ├── Semantic similarity 60%
        ├── Cost similarity 25%
        └── Date similarity 15%
        │
        ▼
Low / Medium / High / Critical review category
```

The prototype currently contains **129,117 candidate pairs** in its generated `duplicate_candidates.csv` snapshot.

The system deliberately labels these as **potential overlaps**, because semantic similarity alone cannot establish that two physical works are the same project.

---

## 12. Review Queue

The review queue is generated from `project_features.csv` and contains projects whose risk category is:

- Medium
- High
- Critical

Low-risk projects are excluded from the review queue.

The queue is sorted by:

1. `Risk_Score` descending
2. `Max_Overlap_Score` descending

The current prototype snapshot contains **5,393 projects** in the review queue:

| Category | Projects |
|---|---:|
| Medium | 5,140 |
| High | 252 |
| Critical | 1 |

---

## 13. GIS Risk Map

The GIS module uses **Folium** and **streamlit-folium** to display project markers when valid project-level latitude and longitude fields are available.

Available filters include:

- State
- Risk category
- Work category

Markers display project and risk information.

The prototype intentionally avoids fabricating geographic coordinates. If reliable coordinates are unavailable, the interface explains the limitation and provides a filtered project table instead.

---

## 14. Technology Stack

### Backend / Data Processing

- Python
- Pandas
- NumPy
- PyYAML

### Machine Learning / AI

- Sentence Transformers
- `all-MiniLM-L6-v2`
- scikit-learn `NearestNeighbors`
- PyTorch
- Hugging Face Transformers
- AI4Bharat IndicXlit / IndicTrans2 utility module

### Frontend / Dashboard

- Streamlit
- Folium
- streamlit-folium

### Storage / Data Exchange

- CSV
- YAML configuration

The current prototype is intentionally lightweight and file-based rather than database-backed.

---

## 15. Project Structure

```text
Sih_102Prototype/
│
├── app/
│   ├── main.py
│   ├── components/
│   │   └── auth_ui.py
│   └── pages/
│       ├── 1_Overview.py
│       ├── 2_Risk_Alerts.py
│       ├── 3_Project_Investigation.py
│       ├── 4_Duplicate_Overlap.py
│       ├── 5_Delay_Prediction.py
│       ├── 6_Cost_Financial.py
│       └── 7_GIS_Risk_Map.py
│
├── configs/
│   ├── config.yaml
│   └── risk_weights.yaml
│
├── data/
│   ├── raw/
│   │   ├── Works Recommended.csv
│   │   ├── Works Sanctioned.csv
│   │   ├── Works Completed.csv
│   │   ├── Allocated Limit for Honble MPs.csv
│   │   └── Amount consented for Calamity.csv
│   ├── processed/
│   │   ├── unified_projects.csv
│   │   ├── project_features.csv
│   │   ├── duplicate_candidates.csv
│   │   └── review_queue.csv
│   └── synthetic/
│
├── docs/
│   ├── architecture.md
│   ├── assumptions.md
│   ├── data_dictionary.md
│   └── methodology.md
│
├── pipelines/
│   ├── audit_raw.py
│   ├── build_dataset.py
│   ├── build_features.py
│   ├── test_duplicates.py
│   ├── build_review_queue.py
│   ├── test_risk_engine.py
│   └── other pipeline/test utilities
│
├── src/
│   └── mplads/
│       ├── auth.py
│       ├── config.py
│       ├── data/
│       ├── features/
│       ├── models/
│       ├── risk/
│       ├── verification/
│       ├── geo/
│       └── assistant/
│
├── notebooks/
│   ├── 01_data_audit.ipnyb
│   ├── 02_unified_table.ipnyb
│   ├── 03_anomaly_model.ipnyb
│   ├── 04_delay_model.ipnyb
│   ├── 05_duplicates.ipnyb
│   └── 06_progress_verificaion.ipnyb
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Some folders contain experimental or scaffolded modules that are not currently connected to the main Streamlit workflow.

---

## 16. Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd Sih_102Prototype
```
### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Prototype note:** The supplied `requirements.txt` contains the core data/ML dependencies. The Streamlit UI and GIS pages additionally require the packages imported by the application, such as `streamlit`, `folium`, `streamlit-folium`, and `pyyaml`. Before a fresh-machine deployment, make sure these are included in the environment or requirements file.

### 5. Prepare the data

The expected raw files should be placed under:

```text
data/raw/
```

Then run the data-unification pipeline:

```bash
python pipelines/build_dataset.py
```

### 6. Run semantic duplicate detection

```bash
python pipelines/test_duplicates.py
```

This generates:

```text
data/processed/duplicate_candidates.csv
```

### 7. Build project features and risk scores

```bash
python pipelines/build_features.py
```

This generates:

```text
data/processed/project_features.csv
```

### 8. Build the review queue

```bash
python pipelines/build_review_queue.py
```

This generates:

```text
data/processed/review_queue.csv
```

### 9. Start the Streamlit application

From the project root:

```bash
streamlit run app/main.py
```

The Streamlit interface will provide the dashboard and its navigation pages.

---

## 17. Processing Pipeline Commands

The recommended prototype sequence is:

```bash
python pipelines/build_dataset.py
python pipelines/test_duplicates.py
python pipelines/build_features.py
python pipelines/build_review_queue.py
streamlit run app/main.py
```

### Pipeline outputs

| Command | Main output |
|---|---|
| `build_dataset.py` | `unified_projects.csv` |
| `test_duplicates.py` | `duplicate_candidates.csv` |
| `build_features.py` | `project_features.csv` |
| `build_review_queue.py` | `review_queue.csv` |

---

## 18. Compliance, Explainability & Ethical Safeguards

### Screening, not accusation

The system identifies unusual patterns and generates risk signals. A risk score is **not proof of fraud, corruption, misuse of funds, or misconduct**.

### Human-in-the-loop review

The review queue is designed to help authorized officers decide which records deserve further documentary or physical verification.

### Explainability

Risk points are generated from identifiable signals such as:

- financial amount deviation
- unusual completion duration
- cost deviation from peer benchmark
- potential project overlap
- missing monitoring information

The system therefore provides a reason behind an alert instead of exposing only an opaque score.

### No fabricated geographic data

The GIS module does not create artificial coordinates when reliable latitude/longitude information is unavailable.

### District-level access control

District-scoped users are filtered to their assigned district. Central administrators can access all districts in the prototype.

---

## 19. Important Prototype Limitations

The current prototype should be presented accurately as a **risk-screening and monitoring system**, not as a complete fraud-detection model.

Current limitations include:

1. The final risk score is deterministic and rule-based.
2. Cost anomaly detection uses peer-group medians and percentage thresholds rather than ML.
3. Delay risk uses a statistical percentile threshold rather than a trained predictive model.
4. No numerical physical-progress percentage is currently available in the active source data.
5. Semantic similarity identifies potential overlaps; it does not establish actual duplication.
6. The multilingual IndicXlit / IndicTrans2 utility exists but is not currently wired into the active duplicate pipeline.
7. The authentication database is mock/in-code and is not suitable for production security.
8. The application is CSV/file based and does not yet use a production database.
9. GIS visualization depends on reliable project-level coordinates being available.
10. Several verification, assistant, anomaly-model and delay-model files are currently scaffolds/placeholders rather than active production modules.

---

## 20. Future Enhancements

Potential next-stage improvements include:

- Train and validate a dedicated anomaly-detection model using the engineered feature set.
- Add a validated delay-prediction model for active projects.
- Integrate the IndicXlit / IndicTrans2 normalization pipeline into multilingual duplicate detection.
- Add calibrated model evaluation metrics such as precision, recall, F1-score and false-positive analysis.
- Add historical project-level trend analysis.
- Add richer financial transaction-level anomaly detection when transaction data becomes available.
- Add verified GPS/project-location data for stronger geographic overlap analysis.
- Add image/evidence verification when reliable project photographs and metadata are available.
- Replace mock authentication with secure identity and role management.
- Add database-backed storage and scalable querying.
- Add audit logs and investigation status workflows.
- Add secure deployment and secret management.
- Add automated scheduled data refreshes.
- Add model monitoring and drift detection once predictive ML models are deployed.

---

## 21. Demonstration Flow

A typical judge demonstration can follow this sequence:

```text
Login
  ↓
Executive Dashboard
  ↓
Risk Alerts
  ↓
Select a high / critical project
  ↓
Explain the risk reasons
  ↓
Project Investigation
  ↓
Search the project using any available field
  ↓
Duplicate & Overlap
  ↓
Show semantic similarity and supporting signals
  ↓
Delay / Financial analysis
  ↓
GIS view when coordinates are available
```

The key demonstration point is that the system does not stop at **"this project has a high score"**. It moves from **detection → explanation → prioritization → human investigation**.

---

## 22. Current Prototype Risk Snapshot

The supplied prototype dataset currently produces:

| Risk Category | Projects |
|---|---:|
| Low | 21,608 |
| Medium | 5,140 |
| High | 252 |
| Critical | 1 |
| **Total** | **27,001** |

The current generated review queue contains all Medium, High and Critical projects, for a total of **5,393 projects**.

These figures are dataset-specific and should be regenerated after any source-data refresh.

---

## 23. Important Note

This project is a **prototype for Smart India Hackathon 2026** and is intended to demonstrate how data engineering, semantic similarity, statistical screening and explainable risk scoring can support MPLADS monitoring.

The system should be used as an **administrative decision-support tool**. Final conclusions about project compliance, duplication, expenditure, delay, or potential wrongdoing require verification using authoritative records and appropriate human review.

---

## 24. License / Usage

This prototype is intended for hackathon, educational, research and demonstration purposes.

For production use, the project should undergo appropriate security, data-governance, model-validation, privacy, authorization and infrastructure reviews.