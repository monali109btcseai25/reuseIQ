"""
ReUseIQ: Intelligent E-Waste Reuse and Recycling Advisor
Main Streamlit Application Dashboard

A complete symbolic AI decision-support system featuring:
- Knowledge representation & predicate logic
- Forward & backward chaining inference engines
- W3C OWL/RDF domain ontology
- Fuzzy logic membership & inference
- Probabilistic Bayesian uncertainty reasoning
- Decision theory & multi-criteria expected utility
- Transparent explanation & rule firing traces
"""

import os
import sys
from pathlib import Path

# Ensure src/ is in sys.path so reuseiq package is importable
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import json
import pandas as pd
import streamlit as st

from reuseiq.data.database import DatabaseManager
from reuseiq.data.models import (
    ActionOption,
    BatteryCondition,
    ComponentInfo,
    DeviceRecord,
    DeviceType,
    OverallCondition,
    PartsAvailability,
    SafetyStatus,
)
from reuseiq.knowledge.backward_chaining import BackwardChainingEngine
from reuseiq.knowledge.predicates import Predicate
from reuseiq.knowledge.rules import device_to_facts
from reuseiq.ontology.ontology_manager import OntologyManager
from reuseiq.services.advisory_service import AdvisoryService
from reuseiq_theme import inject_global_css, render_home_hero, render_top_nav
from reuseiq.ui.components import (
    ACTION_COLORS,
    ACTION_ICONS,
    render_action_distribution_chart,
    render_fuzzy_curve_chart,
    render_radar_chart,
    render_utility_comparison_chart,
)

# Page configuration
st.set_page_config(
    page_title="ReUseIQ — Intelligent E-Waste Advisor",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize singletons in session state
@st.cache_resource
def get_database_manager():
    return DatabaseManager()

@st.cache_resource
def get_advisory_service():
    db = get_database_manager()
    return AdvisoryService(db_manager=db)

@st.cache_resource
def get_ontology_manager():
    try:
        return OntologyManager()
    except Exception as e:
        st.warning(f"Ontology could not be loaded: {e}")
        return None

db = get_database_manager()
advisor = get_advisory_service()
ontology_mgr = get_ontology_manager()

# -----------------------------------------------------------------------------
# THEME + TOP GLASS NAVIGATION (sidebar removed, highlights live on Home page)
# -----------------------------------------------------------------------------
inject_global_css()

PAGES = [
    "Home & Overview",
    "Register Device",
    "Device Inventory",
    "AI Recommendation",
    "Decision Comparison",
    "Rule Trace & Proof",
    "Reports & Analytics",
]

nav_page = render_top_nav(PAGES)

# -----------------------------------------------------------------------------
# PAGE 1: HOME & OVERVIEW
# -----------------------------------------------------------------------------
if nav_page == "Home & Overview":
    render_home_hero()

    st.divider()
    st.markdown("### 👥 Project Division of Work")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        st.info(
            """
            **Branch 1 — Person 1: AI Reasoning & Decision Engine**
            - Fuzzy logic membership functions (`fuzzy_engine.py`)
            - Probabilistic reasoning and Bayesian risk (`probability_engine.py`)
            - Multi-criteria expected utility engine (`utility_engine.py`)
            - Safety-first decision ranking (`decision_engine.py`)
            - Human-readable explanation generation (`explanation.py`)
            """
        )
    with d_col2:
        st.success(
            """
            **Branch 2 — Person 2: Knowledge Representation & Application**
            - Relational persistence in SQLite (`database.py`, `models.py`)
            - Predicate logic facts and IF-THEN rules (`predicates.py`, `rules.py`)
            - Forward chaining engine & trace logging (`forward_chaining.py`)
            - Backward chaining goal-driven proof solver (`backward_chaining.py`)
            - W3C OWL 2 Domain Ontology in RDF/XML (`ewaste_ontology.owl`, `ontology_manager.py`)
            - Interactive Streamlit Dashboard (`app.py`, `components.py`)
            """
        )

    st.divider()
    if ontology_mgr:
        st.markdown("### 🌐 Formal Domain Ontology Statistics")
        stats = ontology_mgr.get_ontology_statistics()
        o1, o2, o3, o4 = st.columns(4)
        o1.metric("OWL Classes", stats["classes"])
        o2.metric("Object Properties", stats["object_properties"])
        o3.metric("Data Properties", stats["data_properties"])
        o4.metric("RDF Triples", stats["total_triples"])

    st.markdown("---")
    st.caption("Developed with Python, Streamlit, SQLite, RDFLib, and Plotly.")

# -----------------------------------------------------------------------------
# PAGE 2: REGISTER DEVICE
# -----------------------------------------------------------------------------
elif nav_page == "Register Device":
    st.title("📝 Register & Assess Electronic Device")
    st.markdown("Enter device specifications. You can explicitly distinguish known, estimated, and unknown values.")

    with st.form("register_device_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 1. Identification & Type")
            dev_id = st.text_input("Device ID *", value="", placeholder="e.g. LAP104, MOB305").strip().upper()
            dev_type = st.selectbox(
                "Device Type",
                [t.value for t in DeviceType],
                format_func=lambda x: x.replace("_", " ").title()
            )
            age_years = st.number_input("Device Age (Years)", min_value=0.0, max_value=30.0, value=3.0, step=0.5)
            overall_condition = st.selectbox(
                "Overall Cosmetic Condition",
                [c.value for c in OverallCondition],
                index=2,
                format_func=lambda x: x.title()
            )

            st.markdown("##### 2. Damage & Safety Inspection")
            damage_severity = st.slider(
                "Damage Severity (0 = Mint, 100 = Destroyed)",
                min_value=0.0, max_value=100.0, value=35.0, step=1.0
            )

            battery_cond = st.selectbox(
                "Battery Condition",
                [b.value for b in BatteryCondition],
                format_func=lambda x: x.replace("_", " ").title()
            )

            safety_opt = st.radio(
                "Safety Inspection Status",
                ["Passed (Safe)", "Failed (Unsafe / Hazard)", "Unknown / Not Tested"],
                index=0
            )
            safety_passed = True if "Passed" in safety_opt else (False if "Failed" in safety_opt else None)

            parts_avail = st.selectbox(
                "Spare Parts Availability",
                [p.value for p in PartsAvailability],
                format_func=lambda x: x.title()
            )

        with col2:
            st.markdown("##### 3. Economics & Valuation (INR / Currency Units)")
            replacement_cost = st.number_input(
                "Estimated Replacement Cost *", min_value=100.0, max_value=1000000.0, value=30000.0, step=500.0
            )

            repair_cost_unknown = st.checkbox("Repair cost is unknown / unquoted")
            if repair_cost_unknown:
                repair_cost = None
                st.caption("Will use fallback estimate based on damage severity.")
            else:
                repair_cost = st.number_input("Estimated Repair Cost", min_value=0.0, max_value=500000.0, value=2500.0, step=100.0)

            resale_value = st.number_input("Estimated Resale / Salvage Value", min_value=0.0, value=6000.0, step=500.0)

            st.markdown("##### 4. Uncertainty & Data Privacy")
            prob_unknown = st.checkbox("Repair success probability is unknown")
            if prob_unknown:
                repair_prob = None
                st.caption("Will use Bayesian illustrative fallback estimate.")
            else:
                repair_prob = st.slider("Estimated Repair Success Probability", min_value=0.0, max_value=1.0, value=0.75, step=0.05)

            personal_data_present = st.checkbox("Device contains personal / sensitive user data", value=True)
            data_erased = st.checkbox("Certified data sanitization has already been completed", value=False)

            notes = st.text_area("Diagnostic Notes / Remarks", placeholder="e.g. Broken screen hinge, motherboard and RAM functional.")

        st.markdown("##### 5. Component Breakdown")
        comp_col1, comp_col2 = st.columns(2)
        with comp_col1:
            working_comps = st.multiselect(
                "Working Components",
                ["RAM", "storage", "motherboard", "screen", "keyboard", "battery", "camera", "power_supply", "chassis", "wifi_card"],
                default=["RAM", "storage"]
            )
        with comp_col2:
            damaged_comps = st.multiselect(
                "Damaged / Defective Components",
                ["RAM", "storage", "motherboard", "screen", "keyboard", "battery", "camera", "power_supply", "chassis", "wifi_card"],
                default=["screen"]
            )

        submitted = st.form_submit_button("💾 Save Device & Compute Advisory", use_container_width=True)

    if submitted:
        if not dev_id:
            st.error("Please enter a valid Device ID.")
        else:
            components_list = []
            for wc in working_comps:
                components_list.append(ComponentInfo(name=wc, is_working=True, estimated_value=2000.0))
            for dc in damaged_comps:
                if dc not in working_comps:
                    components_list.append(ComponentInfo(name=dc, is_working=False, estimated_value=0.0))

            field_meta = {}
            if repair_cost_unknown:
                field_meta["repair_cost"] = "unknown"
            if prob_unknown:
                field_meta["repair_success_probability"] = "unknown"
            if safety_passed is None:
                field_meta["safety_check_passed"] = "unknown"

            device = DeviceRecord(
                device_id=dev_id,
                device_type=dev_type,
                age_years=age_years,
                overall_condition=overall_condition,
                damage_severity=damage_severity,
                repair_cost=repair_cost,
                replacement_cost=replacement_cost,
                repair_success_probability=repair_prob,
                battery_condition=battery_cond,
                safety_check_passed=safety_passed,
                spare_parts_availability=parts_avail,
                resale_value=resale_value,
                personal_data_present=personal_data_present,
                data_erased=data_erased,
                components=components_list,
                field_metadata=field_meta,
                notes=notes
            )

            try:
                db.save_device(device)
                result = advisor.evaluate_device(device, save_result=True)
                st.success(f"Device **{dev_id}** saved and evaluated successfully!")
                st.session_state["selected_device_id"] = dev_id
                st.info("Navigate to the **AI Recommendation** page in the top navigation bar to inspect the detailed advice.")
            except Exception as e:
                st.error(f"Error saving device: {e}")

# -----------------------------------------------------------------------------
# PAGE 3: DEVICE INVENTORY
# -----------------------------------------------------------------------------
elif nav_page == "Device Inventory":
    st.title("📦 Electronic Device Inventory")
    st.markdown("View, filter, manage, and inspect registered electronic devices stored in SQLite.")

    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🌱 Load Standard Seed Devices (8 Scenarios)", use_container_width=True):
            db.seed_default_devices()
            st.success("Loaded standard test devices (LAP104, DSK201, MOB305, TAB402, LAP550, MOB611, PRN708, DEV812)!")
            st.rerun()

    devices = db.list_devices()

    if not devices:
        st.info("No devices registered in database. Click 'Load Standard Seed Devices' above to populate sample scenarios.")
    else:
        # Search & Filter bar
        s_col1, s_col2 = st.columns([2, 1])
        with s_col1:
            search_query = st.text_input("Search by Device ID or notes", placeholder="e.g. LAP104")
        with s_col2:
            filter_type = st.selectbox(
                "Filter by Type",
                ["All"] + [t.value for t in DeviceType],
                format_func=lambda x: x.replace("_", " ").title()
            )

        filtered_devices = devices
        if filter_type != "All":
            filtered_devices = [d for d in filtered_devices if d.device_type == filter_type]
        if search_query:
            filtered_devices = [
                d for d in filtered_devices
                if search_query.lower() in d.device_id.lower() or search_query.lower() in d.notes.lower()
            ]

        # Display table
        table_data = []
        for d in filtered_devices:
            table_data.append({
                "Device ID": d.device_id,
                "Type": d.device_type.replace("_", " ").title(),
                "Age (Yrs)": d.age_years,
                "Damage": f"{d.damage_severity:.0f}%",
                "Repair Cost": f"₹{d.repair_cost:,.0f}" if d.repair_cost is not None else "Unknown",
                "Replacement": f"₹{d.replacement_cost:,.0f}",
                "Safety": d.safety_status_str.title(),
                "Working Comps": ", ".join(d.working_components) if d.working_components else "None",
                "Battery": d.battery_condition.replace("_", " ").title(),
                "Personal Data": "Yes" if d.personal_data_present else "No"
            })

        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        st.divider()
        st.markdown("##### Quick Actions")
        q_col1, q_col2, q_col3 = st.columns([2, 1, 1])
        with q_col1:
            selected_dev_id = st.selectbox("Select Device for Action", [d.device_id for d in filtered_devices])
        with q_col2:
            if st.button("🔍 View Recommendation", use_container_width=True):
                st.session_state["selected_device_id"] = selected_dev_id
                st.info(f"Selected {selected_dev_id}. Please click on 'AI Recommendation' in the top navigation bar.")
        with q_col3:
            if st.button("🗑️ Delete Device", type="secondary", use_container_width=True):
                db.delete_device(selected_dev_id)
                st.warning(f"Deleted {selected_dev_id}.")
                st.rerun()

# -----------------------------------------------------------------------------
# PAGE 4: AI RECOMMENDATION
# -----------------------------------------------------------------------------
elif nav_page == "AI Recommendation":
    st.title("🎯 AI Recommendation & Decision Reasoning")
    st.markdown("Detailed symbolic inference, uncertainty analysis, and explanation for an individual device.")

    devices = db.list_devices()
    if not devices:
        st.warning("No devices available. Please register or seed devices first.")
    else:
        # Device Selector
        default_index = 0
        if "selected_device_id" in st.session_state:
            ids = [d.device_id for d in devices]
            if st.session_state["selected_device_id"] in ids:
                default_index = ids.index(st.session_state["selected_device_id"])

        selected_id = st.selectbox("Select Device to Evaluate", [d.device_id for d in devices], index=default_index)
        device = db.get_device(selected_id)

        if device:
            result = advisor.evaluate_device(device, save_result=True)
            action = result["recommended_action"]
            color = ACTION_COLORS.get(action, "#2563EB")
            icon = ACTION_ICONS.get(action, "💡")

            # Main Recommendation Banner
            st.markdown(
                f"""
                <div style="background-color: {color}15; border-left: 8px solid {color}; padding: 18px; border-radius: 6px; margin-bottom: 20px;">
                    <h2 style="color: {color}; margin: 0; font-size: 28px;">
                        {icon} Recommended Action: {action.replace('_', ' ').upper()}
                    </h2>
                    <p style="margin-top: 8px; font-size: 16px; color: #334155;">
                        <b>Device:</b> {device.device_id} ({device.device_type.replace('_', ' ').title()}) &nbsp;|&nbsp;
                        <b>Condition:</b> {device.overall_condition.title()} &nbsp;|&nbsp;
                        <b>Damage Severity:</b> {device.damage_severity:.0f}/100 &nbsp;|&nbsp;
                        <b>Cost Ratio:</b> {f"{device.repair_cost_ratio*100:.1f}%" if device.repair_cost_ratio is not None else "Unknown"}
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # Metric Cards
            m1, m2, m3, m4 = st.columns(4)
            top_util = result["expected_utility"].get(action, "N/A")
            m1.metric("Expected Utility Score", f"{top_util}/100" if isinstance(top_util, (int, float)) else str(top_util))
            m2.metric("Fuzzy Repairability", f"{result['fuzzy_scores']['repairability']}/100")
            succ_prob = result["probability_estimates"]["success_probability"]
            m3.metric("Estimated Success Prob", f"{succ_prob*100:.1f}%")
            m4.metric("Risk Classification", result["probability_estimates"]["risk_classification"])

            # Warnings Section
            if result["safety_warnings"]:
                for w in result["safety_warnings"]:
                    st.error(f"⚠️ **Safety Constraint**: {w}")

            if result["missing_information"]:
                with st.expander("ℹ️ Missing / Estimated Information Alerts", expanded=False):
                    for m in result["missing_information"]:
                        st.warning(f"• {m}")

            # Feasible vs Disqualified Options
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown("##### ✅ Feasible Alternative Options")
                for opt in result["feasible_options"]:
                    if opt != action:
                        u = result["expected_utility"].get(opt, "N/A")
                        st.markdown(f"- **{opt.replace('_', ' ').title()}** — Utility: `{u}/100`")
                if len(result["feasible_options"]) <= 1:
                    st.caption("No other options satisfied all safety and economic criteria.")

            with f_col2:
                st.markdown("##### ❌ Prohibited / Disqualified Options")
                all_opts = ["repair", "refurbish", "component_recovery", "donate_reuse", "recycle"]
                disqualified = [o for o in all_opts if o not in result["feasible_options"]]
                for dis in disqualified:
                    st.markdown(f"- <span style='color: #94A3B8; text-decoration: line-through;'>{dis.replace('_', ' ').title()}</span> *(Prohibited by domain rules or safety constraints)*", unsafe_allow_html=True)

            st.divider()

            # Natural Language Symbolic Explanation
            st.markdown("### 💬 Understandable Symbolic Explanation")
            st.caption("Generated directly from predicate logic rules, fuzzy evaluations, and expected utility calculations (No NLP / LLM).")
            for para in result["explanation"]:
                st.markdown(f"- {para}")

            st.divider()

            # Fuzzy Membership Breakdown
            st.markdown("### 📐 Fuzzy Logic & Membership Breakdown")
            f_tab1, f_tab2 = st.columns([1, 1])
            with f_tab1:
                st.write("**Damage Severity Memberships (Scale 0-100)**")
                dm = result["fuzzy_scores"]["damage_membership"]
                st.json(dm)
            with f_tab2:
                st.write("**Cost Ratio Memberships (Repair / Replacement)**")
                cm = result["fuzzy_scores"]["cost_ratio_membership"]
                st.json(cm)

# -----------------------------------------------------------------------------
# PAGE 5: DECISION COMPARISON
# -----------------------------------------------------------------------------
elif nav_page == "Decision Comparison":
    st.title("📊 Decision Comparison & Multi-Criteria Trade-offs")
    st.markdown("Compare Repair, Refurbishment, Component Recovery, Direct Reuse, and Recycling across multi-criteria objectives.")

    devices = db.list_devices()
    if not devices:
        st.warning("No devices available.")
    else:
        selected_id = st.selectbox("Select Device for Trade-off Analysis", [d.device_id for d in devices])
        device = db.get_device(selected_id)
        if device:
            result = advisor.evaluate_device(device, save_result=False)

            chart1 = render_utility_comparison_chart(
                all_utilities=result["all_option_utilities"],
                feasible_options=result["feasible_options"]
            )
            st.plotly_chart(chart1, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                chart2 = render_radar_chart(
                    all_utilities=result["all_option_utilities"],
                    feasible_options=result["feasible_options"]
                )
                st.plotly_chart(chart2, use_container_width=True)

            with col2:
                fuzzy_chart = render_fuzzy_curve_chart(
                    damage_severity=device.damage_severity,
                    damage_memberships=result["fuzzy_scores"]["damage_membership"]
                )
                st.plotly_chart(fuzzy_chart, use_container_width=True)

            # Tabular Comparison
            st.markdown("##### Criteria Weightings & Option Matrix")
            st.caption("Formula: Expected Utility = (0.40 × Economic) + (0.35 × Environmental) + (0.25 × Life Extension)")

            matrix_rows = []
            for opt, scores in result["all_option_utilities"].items():
                is_fe = opt in result["feasible_options"]
                util = round(0.40 * scores["economic"] + 0.35 * scores["environmental"] + 0.25 * scores["life_extension"], 2)
                matrix_rows.append({
                    "Candidate Action": opt.replace("_", " ").title(),
                    "Status": "Eligible" if is_fe else "Blocked / Prohibited",
                    "Economic (40%)": scores["economic"],
                    "Environmental (35%)": scores["environmental"],
                    "Life Extension (25%)": scores["life_extension"],
                    "Weighted Utility Score": util
                })

            st.dataframe(pd.DataFrame(matrix_rows), use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 6: RULE TRACE & PROOF
# -----------------------------------------------------------------------------
elif nav_page == "Rule Trace & Proof":
    st.title("🔍 Inference Engine Rule Trace & Backward Proofs")
    st.markdown("Inspect forward-chaining rule firings and query why specific decisions were made using backward chaining.")

    devices = db.list_devices()
    if not devices:
        st.warning("No devices available.")
    else:
        selected_id = st.selectbox("Select Device for Audit", [d.device_id for d in devices])
        device = db.get_device(selected_id)

        if device:
            result = advisor.evaluate_device(device, save_result=False)
            facts = device_to_facts(device)

            tab_fw, tab_bw, tab_facts = st.tabs(["⚡ Forward Chaining Trace", "🎯 Backward Chaining Proof Tool", "📚 Ground Facts Asserter"])

            with tab_fw:
                st.markdown("#### Forward Chaining Execution Audit")
                st.write(f"Inference engine evaluated domain rules against **{len(facts)}** ground facts for `{device.device_id}`.")

                traces = result["rules_fired"]
                if not traces:
                    st.info("No rules fired.")
                else:
                    for t in traces:
                        with st.expander(f"Step {t['step']}: [{t['rule_id']}] {t['rule_name']} ({t['category'].upper()})"):
                            st.write(f"**Explanation:** {t['explanation']}")
                            st.write(f"**Bindings:** `{t['bindings']}`")
                            st.write(f"**Matched Antecedents:** `{t['matched_facts']}`")
                            st.write(f"**Derived Consequents:** `{t['derived_facts']}`")

            with tab_bw:
                st.markdown("#### Backward Chaining Goal-Directed Prover")
                st.write("Ask diagnostic queries to prove or refute candidate goals via backward-chaining theorem proving:")

                query_options = [
                    f"Why is Repair feasible? [EligibleAction({device.device_id}, repair)]",
                    f"Why is Direct Reuse feasible? [EligibleAction({device.device_id}, donate_reuse)]",
                    f"Why is Direct Reuse prohibited? [ProhibitAction({device.device_id}, donate_reuse)]",
                    f"Why is Repair prohibited? [ProhibitAction({device.device_id}, repair)]",
                    f"Is Data Sanitization required? [RequiresDataSanitization({device.device_id})]",
                    f"Is Recycling mandatory? [MandatoryAction({device.device_id}, recycle)]",
                ]

                chosen_query = st.selectbox("Select Query to Prove", query_options)

                # Map selection to Predicate
                goal_pred = None
                if "EligibleAction" in chosen_query and "repair" in chosen_query:
                    goal_pred = Predicate("EligibleAction", device.device_id, "repair")
                elif "EligibleAction" in chosen_query and "donate_reuse" in chosen_query:
                    goal_pred = Predicate("EligibleAction", device.device_id, "donate_reuse")
                elif "ProhibitAction" in chosen_query and "donate_reuse" in chosen_query:
                    goal_pred = Predicate("ProhibitAction", device.device_id, "donate_reuse")
                elif "ProhibitAction" in chosen_query and "repair" in chosen_query:
                    goal_pred = Predicate("ProhibitAction", device.device_id, "repair")
                elif "RequiresDataSanitization" in chosen_query:
                    goal_pred = Predicate("RequiresDataSanitization", device.device_id)
                elif "MandatoryAction" in chosen_query:
                    goal_pred = Predicate("MandatoryAction", device.device_id, "recycle")

                if st.button("Run Backward Chaining Proof", use_container_width=True):
                    if goal_pred:
                        proof_node = advisor.backward_engine.prove(goal_pred, set(facts))
                        if proof_node.is_proved:
                            st.success(f"✓ **PROVED**: Goal `{goal_pred}` holds true in the Knowledge Base!")
                        else:
                            st.warning(f"✗ **NOT PROVED**: Goal `{goal_pred}` could not be established.")

                        st.markdown("##### Proof Tree:")
                        st.code(proof_node.format_tree(), language="text")

            with tab_facts:
                st.markdown("#### Ground Facts Extracted from Device")
                st.write("These formal first-order ground facts were asserted into the working memory:")
                fact_strings = [str(f) for f in facts]
                st.code("\n".join(fact_strings), language="prolog")

# -----------------------------------------------------------------------------
# PAGE 7: REPORTS & ANALYTICS
# -----------------------------------------------------------------------------
elif nav_page == "Reports & Analytics":
    st.title("📈 Reports & E-Waste Analytics")
    st.markdown("Aggregate metrics, economic recovery summaries, and circular economy environmental impact.")

    summary = db.get_analytics_summary()

    # KPI Top Bar
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Devices Assessed", summary["total_devices"])
    k2.metric("Total Replacement Value", f"₹{summary['total_replacement_value']:,.0f}")
    k3.metric("Total Repair Investment", f"₹{summary['total_repair_cost']:,.0f}")
    k4.metric("Harvested Working Components", summary["working_components_count"])

    st.divider()

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        dist_chart = render_action_distribution_chart(summary["recommendations_by_action"])
        st.plotly_chart(dist_chart, use_container_width=True)

    with col_chart2:
        st.markdown("##### Device Distribution by Category")
        type_data = summary["devices_by_type"]
        if type_data:
            df_type = pd.DataFrame([{"Device Type": k.replace("_", " ").title(), "Count": v} for k, v in type_data.items()])
            st.bar_chart(df_type.set_index("Device Type"))

    st.divider()
    st.markdown("##### Export Data")
    devices = db.list_devices()
    if devices:
        export_rows = [d.to_dict() for d in devices]
        df_export = pd.DataFrame(export_rows)
        csv_data = df_export.to_csv(index=False)
        st.download_button(
            label="📥 Download Device Inventory (CSV)",
            data=csv_data,
            file_name="reuseiq_inventory.csv",
            mime="text/csv"
        )