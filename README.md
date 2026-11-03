# ReUseIQ — Intelligent E-Waste Reuse & Recycling Advisor

> **A Classical Symbolic AI Decision-Support System for Sustainable Electronics Lifecycle Management**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Framework Streamlit](https://img.shields.io/badge/framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Knowledge W3C OWL 2](https://img.shields.io/badge/ontology-OWL%202%20%2F%20RDFLib-darkgreen.svg)](https://www.w3.org/OWL/)
[![Tests pytest](https://img.shields.io/badge/tests-39%20passed-brightgreen.svg)](https://docs.pytest.org/)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## 1. Project Overview

**ReUseIQ** is an expert advisory system that evaluates obsolete, damaged, or unwanted electronic devices to determine whether each device should be:
1. **Repaired** (economical fixes with high success probability)
2. **Refurbished** (comprehensive overhaul and testing for extended reuse)
3. **Harvested for Usable Components** (salvaging functional RAM, SSD, screens, or motherboards)
4. **Directly Reused or Donated** (functional devices with verified safety and cleared personal data)
5. **Recycled via Authorized Facilities** (safe material extraction and hazardous waste treatment)

### Strict Symbolic AI Constraint
In strict accordance with academic AI requirements:
- **NO Machine Learning (ML)**
- **NO Deep Learning (DL)**
- **NO Natural Language Processing (NLP)**
- **NO Neural Networks, Word2Vec, GloVe, or Text Embeddings**
- **NO Black-Box Trained Models**

All reasoning is 100% deterministic, explainable, and grounded in **Predicate Logic, Forward/Backward Rule Chaining, Formal OWL Ontologies, Triangular Fuzzy Sets, Bayesian Probability, and Multi-Criteria Expected Utility Theory**.

---

## 2. System Architecture

```
                                  [ User Input / SQLite Device Record ]
                                                    │
                                                    ▼
                            [ Step 1: Fact Extractor (device_to_facts) ]
                                    Generates Ground Predicates
                                                    │
                   ┌────────────────────────────────┴────────────────────────────────┐
                   ▼                                                                 ▼
   [ Step 2: Knowledge Base & Rules ]                             [ Step 3: W3C OWL 2 Domain Ontology ]
   - Forward Chaining Engine                                      - Class & Property Taxonomy
   - Safety Constraints (Priority 100)                            - Protégé Compatible (RDF/XML)
   - Data Sanitization Rules (Priority 80)                        - SPARQL Semantic Query Engine
   - Feasibility Deducer (Priority 50)
   - Backward Chaining Theorem Prover
                   │
                   ▼
     Eligible & Prohibited Actions
                   │
                   ├────────────────────────────────┬────────────────────────────────┐
                   ▼                                ▼                                ▼
    [ Step 4: Fuzzy Logic Engine ]     [ Step 5: Probability Engine ]   [ Step 6: Multi-Criteria Utility ]
    - Triangular Membership (μ)        - Bayesian Posterior Updates      - Economic Feasibility (40%)
    - Damage & Cost Severity           - Failure Risk Classification     - Environmental Benefit (35%)
    - Defuzzified Repairability (0-100)- Uncertainty Handling           - Usable Life Extension (25%)
                   │                                │                                │
                   └────────────────────────────────┼────────────────────────────────┘
                                                    ▼
                                    [ Step 7: Decision Engine ]
                                    - Hard Safety Filters Applied First
                                    - Expected Utility Ranking
                                    - Selection of Best Eligible Action
                                                    │
                                                    ▼
                               [ Step 8: Transparent Explanation Engine ]
                               - Rules Fired Audit Trail
                               - Formal Proof Trees
                               - Human-Readable Decision Rationale
                                                    │
                                                    ▼
                                  [ Streamlit Interactive Dashboard ]
```

---

## 3. Two-Person Work Division & Branch Structure

The project is developed using a shared repository structured into two specialized branches:

| Branch | Contributor | Modules & Responsibilities |
|---|---|---|
| **`feature/ai-reasoning`** | **Person 1** | • Fuzzy logic engine (`fuzzy_engine.py`)<br>• Bayesian probability engine (`probability_engine.py`)<br>• Utility engine (`utility_engine.py`)<br>• Decision engine (`decision_engine.py`)<br>• Explanation generation (`explanation.py`) |
| **`feature/knowledge-ui`** | **Person 2** | • SQLite persistence & data models (`models.py`, `database.py`)<br>• Predicate logic & domain rules (`predicates.py`, `rules.py`)<br>• Forward & backward chaining inference (`forward_chaining.py`, `backward_chaining.py`)<br>• Formal OWL ontology & SPARQL manager (`ewaste_ontology.owl`, `ontology_manager.py`)<br>• Integration orchestrator (`advisory_service.py`)<br>• Complete 7-page Streamlit dashboard (`app.py`, `components.py`) |

---

## 4. AI Syllabus Mapping

| Syllabus Topic | Practical Implementation in ReUseIQ | File Location |
|---|---|---|
| **Intelligent Agents** | Goal-directed advisory agent evaluating environments, options, and actions | `src/reuseiq/services/advisory_service.py` |
| **Knowledge Representation** | Explicit ground facts, domain taxonomy, component attributes | `src/reuseiq/knowledge/rules.py` |
| **Predicate Logic** | First-order relations (`Device`, `HasComponent`, `Working`, `SafetyCheckPassed`, unification) | `src/reuseiq/knowledge/predicates.py` |
| **Forward Chaining** | Data-driven rule firing until fixpoint with conflict resolution and trace logging | `src/reuseiq/knowledge/forward_chaining.py` |
| **Backward Chaining** | Goal-directed theorem proving answering *"Why was repair recommended?"* with proof trees | `src/reuseiq/knowledge/backward_chaining.py` |
| **Ontologies & Semantic Web** | W3C OWL 2 XML ontology compatible with Protégé, SPARQL query interface | `src/reuseiq/ontology/ewaste_ontology.owl` |
| **Fuzzy Logic** | Triangular membership functions modeling vague concepts (damage severity, repairability) | `src/reuseiq/reasoning/fuzzy_engine.py` |
| **Probabilistic Reasoning** | Bayesian updating of repair success and failure likelihood under evidence | `src/reuseiq/reasoning/probability_engine.py` |
| **Decision Theory** | Multi-attribute expected utility ranking under safety and economic constraints | `src/reuseiq/reasoning/utility_engine.py` |
| **Expert Systems Architecture** | Knowledge base + inference engine + explanation facility + UI separation | Entire project modular architecture |
| **Ethics in AI** | Mandatory hazardous battery isolation, certified personal data sanitization blocks | Safety and Data Security Rules |

---

## 5. Standard Benchmark Scenarios (Section 11)

ReUseIQ comes pre-seeded with 8 benchmark devices representing diverse real-world edge cases:

1. **`LAP104` (Specification Benchmark)**: Laptop with cracked screen but functional 16GB RAM and NVMe SSD. Low repair cost (₹2,000 / ₹30,000) $\rightarrow$ **Repair Recommended**.
2. **`DSK201` (Mint Working Device)**: Desktop computer needing no repair $\rightarrow$ **Direct Reuse / Donation Recommended**.
3. **`MOB305` (Inexpensive Minor Repair)**: Smartphone with cracked front glass, high success probability $\rightarrow$ **Repair Recommended**.
4. **`TAB402` (Uneconomical Repair)**: Tablet with water corrosion, high repair cost, scarce parts $\rightarrow$ **Authorized Recycling Recommended**.
5. **`LAP550` (Valuable Component Harvest)**: Blown motherboard and smashed screen, but working 32GB RAM and 1TB SSD $\rightarrow$ **Component Recovery Recommended**.
6. **`MOB611` (Critical Safety Hazard)**: Swollen lithium battery $\rightarrow$ **Mandatory Hazardous Recycling Block** (repair, reuse, and refurbish strictly prohibited).
7. **`PRN708` (Data Security Block)**: Functional printer containing unerased personal print spool logs $\rightarrow$ **Donation Prohibited until Data Sanitization Cleared**.
8. **`DEV812` (Incomplete Diagnostic Data)**: Device with unmeasured repair cost and unverified safety status $\rightarrow$ **Explicit Missing Information Warnings & Safety Assessment Required**.

---

## 6. Quickstart & Installation

### Prerequisites
- Python 3.9+ (Python 3.12 recommended)
- Git

### Setup
```powershell
# 1. Clone repository
git clone https://github.com/monali109btcseai25/reuseIQ.git
cd reuseIQ

# 2. Checkout the Person 2 feature branch
git checkout feature/knowledge-ui

# 3. Install dependencies in editable mode
pip install -e .
```

### Running Unit Tests
```powershell
pytest
```
*Expected: 39 passed in ~0.9 seconds.*

### Launching the Streamlit Web Application
```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 7. Streamlit Dashboard Features

1. **🏠 Home & Overview**: Comprehensive explanation of symbolic AI architecture and ontology statistics.
2. **📝 Register Device**: Dynamic form with component checklist, input validation, and known vs. estimated vs. unknown indicators.
3. **📦 Device Inventory**: SQLite-backed table with filtering, search, deletion, and 1-click loading of the 8 benchmark scenarios.
4. **🎯 AI Recommendation**: Action banner, feasible alternatives, fuzzy score breakdown, Bayesian risk gauge, and generated explanation.
5. **📊 Decision Comparison**: Plotly grouped bar charts, radar trade-off diagrams, and fuzzy membership curves.
6. **🔍 Rule Trace & Proof**: Forward-chaining execution audit log + interactive backward-chaining theorem prover.
7. **📈 Reports & Analytics**: Inventory distribution donut charts, financial recovery metrics, and CSV export.

---

## 8. Viewing the Domain Ontology in Protégé

1. Download and launch [Protégé](https://protege.stanford.edu/) (v5.5+).
2. Go to **File $\rightarrow$ Open** and select:
   ```
   src/reuseiq/ontology/ewaste_ontology.owl
   ```
3. Navigate to **Entities $\rightarrow$ Classes** to inspect the `ElectronicDevice`, `Component`, `AdvisoryAction`, `SafetyHazard`, and `RecyclingFacility` hierarchies.
4. Open the **Individuals by class** tab to view instances such as `Device_LAP104` and `RAM_LAP104`.
