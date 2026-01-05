"""PII Shield - Interactive Demo Application with Human-in-the-Loop Workflow."""

import logging
import os

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

from demo.components import build_highlighted_html
from demo.sample_texts import SAMPLES
from demo.styles import PII_COLORS, PII_ICONS, inject_custom_css

# Configure logging to show LLM prompts/responses
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
API_TIMEOUT = 60  # Increased for LLM validation (multiple API calls)
DEFAULT_CONFIDENCE_THRESHOLD = 0.85

# Detection reasons for explainability
DETECTION_REASONS = {
    "email": "Matched email pattern (RFC 5322)",
    "phone": "German phone format (+49/0xxx)",
    "iban": "Valid IBAN with checksum",
    "german_id": "Personalausweis format verified",
    "credit_card": "Luhn algorithm validated",
    "ip_address": "IPv4/IPv6 pattern match",
    "presidio": "ML model (spaCy German NER)",
}

# Page configuration
st.set_page_config(
    page_title="SAP PII SHIELD [OMAR]",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject custom styles
inject_custom_css()


def calculate_metrics(expected: list[dict], detected: list[dict]) -> dict | None:
    """Calculate Precision, Recall, F1 with smart text matching.

    Matching strategies (in order):
    1. Exact match (case-insensitive)
    2. Containment: expected in detected or vice versa (with length ratio check)
    3. Fuzzy match: 85%+ similarity for typos/variations
    """
    if not expected:
        return None

    from difflib import SequenceMatcher

    def normalize(text: str) -> str:
        return text.lower().strip()

    def texts_match(exp_text: str, det_text: str) -> bool:
        """Check if texts match using multiple strategies."""
        exp = normalize(exp_text)
        det = normalize(det_text)

        # 1. Exact match
        if exp == det:
            return True

        # 2. Containment: expected in detected (e.g., "Hans Müller" in "Dr. Hans Müller")
        #    But detected shouldn't be too much longer (max 1.5x length)
        if exp in det and len(det) <= len(exp) * 1.5:
            return True

        # 3. Containment: detected in expected (e.g., "München" in "80331 München")
        if det in exp and len(exp) <= len(det) * 1.5:
            return True

        # 4. Fuzzy match for similar strings (typos, slight variations)
        if SequenceMatcher(None, exp, det).ratio() >= 0.85:
            return True

        return False

    # Greedy 1-to-1 matching: each expected matches at most one detected
    expected_matched = [False] * len(expected)
    detected_matched = [False] * len(detected)
    tp_pairs = []

    for i, exp in enumerate(expected):
        for j, det in enumerate(detected):
            if detected_matched[j]:
                continue
            if exp["type"].upper() == det["type"].upper():
                if texts_match(exp["text"], det["text"]):
                    expected_matched[i] = True
                    detected_matched[j] = True
                    tp_pairs.append((exp["type"].upper(), normalize(exp["text"])))
                    break

    tp = sum(expected_matched)
    fn = len(expected) - tp
    fp = len(detected) - sum(detected_matched)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    # Build detail lists
    fp_details = [
        (det["type"].upper(), normalize(det["text"]))
        for j, det in enumerate(detected)
        if not detected_matched[j]
    ]
    fn_details = [
        (exp["type"].upper(), normalize(exp["text"]))
        for i, exp in enumerate(expected)
        if not expected_matched[i]
    ]

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp_details": tp_pairs,
        "fp_details": fp_details,
        "fn_details": fn_details,
    }


def call_api(endpoint: str, payload: dict) -> tuple[dict | None, dict]:
    """Make API call with error handling. Returns (response, request_info)."""
    request_info = {
        "method": "POST",
        "url": f"{API_URL}/api/v1/{endpoint}",
        "body": payload,
    }
    try:
        response = requests.post(
            request_info["url"],
            json=payload,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        return response.json(), request_info
    except requests.exceptions.ConnectionError:
        st.error(f"Cannot connect to API at {API_URL}. Make sure the API server is running.")
        return None, request_info
    except requests.exceptions.Timeout:
        st.error("API request timed out. Please try again.")
        return None, request_info
    except requests.exceptions.HTTPError as e:
        st.error(f"API error: {e.response.text}")
        return None, request_info


def render_step_indicator(current_step: int) -> None:
    """Render visual step progress indicator with connected circles."""
    steps = [("1", "Analyze"), ("2", "Review"), ("3", "Result")]

    def get_step_style(step_num: int) -> tuple[str, str, str]:
        """Return (circle_bg, circle_border, text_color) for step."""
        if step_num < current_step:
            return "#4CAF50", "#4CAF50", "#4CAF50"  # Completed - green
        elif step_num == current_step:
            return "#2196F3", "#2196F3", "#fff"  # Active - blue
        else:
            return "transparent", "#666", "#666"  # Pending - gray

    # Build HTML with all inline styles
    html = '<div style="display: flex; justify-content: center; align-items: center; padding: 0;">'

    for i, (num, label) in enumerate(steps):
        bg, border, text = get_step_style(i + 1)
        checkmark = "✓" if i + 1 < current_step else num

        html += f'''
        <div style="display: flex; align-items: center;">
            <div style="width: 26px; height: 26px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px; background-color: {bg}; border: 2px solid {border}; color: {text};">
                {checkmark}
            </div>
            <span style="margin-left: 6px; font-size: 13px; font-weight: 500; color: {text};">{label}</span>
        </div>
        '''

        # Add connecting line (except after last step)
        if i < len(steps) - 1:
            line_color = "#4CAF50" if i + 1 < current_step else "#444"
            html += f'<div style="width: 50px; height: 2px; margin: 0 10px; background-color: {line_color};"></div>'

    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_api_panel(title: str, request_info: dict, response: dict | None) -> None:
    """Render collapsible API request/response panel."""
    with st.expander(f"📡 API: {title}", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Request:**")
            st.code(
                f"POST {request_info['url']}\n\n{st.json(request_info['body'], expanded=False)}",
                language="json",
            )
        with col2:
            st.markdown("**Response:**")
            if response:
                st.json(response)
            else:
                st.error("No response")


def reset_workflow() -> None:
    """Reset workflow to step 1."""
    keys_to_clear = [
        "workflow_step",
        "detect_response",
        "detect_request",
        "anonymize_response",
        "anonymize_request",
        "match_selections",
        "expected_annotations",
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]


def main():
    """Main application entry point."""
    # Header with SAP logo - compact professional style
    col_logo, col_title, col_name = st.columns([0.5, 7, 2])
    with col_logo:
        st.image("demo/sap.svg", width=50)
    with col_title:
        st.markdown("### SAP PII SHIELD")
    with col_name:
        st.markdown("<div style='text-align: right; padding-top: 8px;'><b>Omar Mohamed</b></div>", unsafe_allow_html=True)

    st.divider()

    # Initialize workflow step
    if "workflow_step" not in st.session_state:
        st.session_state.workflow_step = 1

    # Step indicator
    render_step_indicator(st.session_state.workflow_step)
    st.divider()

    # ============== STEP 1: INPUT & DETECTION ==============
    if st.session_state.workflow_step == 1:
        # Sample loader at the top
        col1, col2 = st.columns([4, 1])
        with col1:
            sample_name = st.selectbox(
                "Load sample text:",
                options=list(SAMPLES.keys()),
                index=None,
                placeholder="Select a sample to load...",
                label_visibility="collapsed",
            )
        with col2:
            if st.button("Load", use_container_width=True):
                if sample_name:
                    sample = SAMPLES[sample_name]
                    st.session_state.input_text = sample["text"]
                    st.session_state.expected_annotations = sample["annotations"].copy()
                    st.rerun()

        # Text input - empty by default
        input_text = st.text_area(
            "Enter text containing PII:",
            value=st.session_state.get("input_text", ""),
            height=250,
            placeholder="Paste German text containing personal information...",
        )
        st.session_state.input_text = input_text

        # LLM model selection (None = no LLM, others = use that model)
        llm_options = ["None", "Haiku", "Sonnet", "Opus"]
        llm_selection = st.radio(
            "🤖 LLM Validation",
            options=llm_options,
            index=llm_options.index(st.session_state.get("llm_selection", "None")),
            horizontal=True,
            help="None=rule-based only, Haiku=fast/cheap, Sonnet=balanced, Opus=most capable",
        )
        st.session_state.llm_selection = llm_selection
        use_llm = llm_selection != "None"
        st.session_state.use_llm = use_llm
        if use_llm:
            st.session_state.llm_model = llm_selection.lower()
            # LLM threshold slider (only shown when LLM is selected)
            llm_threshold_pct = st.slider(
                "LLM Threshold (send detections ≤ this to LLM)",
                min_value=50,
                max_value=100,
                value=int(st.session_state.get("llm_threshold", 0.90) * 100),
                step=1,
                format="%d%%",
                help="Detections with confidence ≤ this value are validated by LLM. Higher = more LLM calls.",
            )
            st.session_state.llm_threshold = llm_threshold_pct / 100.0

        # Expected annotations section (for ML metrics)
        with st.expander("📊 Expected PII Annotations (Optional)", expanded=False):
            st.caption("Mark expected PII to calculate Precision/Recall/F1 metrics")

            if "expected_annotations" not in st.session_state:
                st.session_state.expected_annotations = []

            # Add new annotation form
            col_type, col_text, col_btn = st.columns([2, 4, 1])
            with col_type:
                new_type = st.selectbox(
                    "Type",
                    options=list(PII_COLORS.keys()),
                    key="new_annotation_type",
                    label_visibility="collapsed",
                )
            with col_text:
                new_text = st.text_input(
                    "Text",
                    key="new_annotation_text",
                    placeholder="Enter expected PII text...",
                    label_visibility="collapsed",
                )
            with col_btn:
                if st.button("Add", key="add_annotation"):
                    if new_text.strip():
                        st.session_state.expected_annotations.append({
                            "type": new_type,
                            "text": new_text.strip(),
                        })
                        st.rerun()

            # Display current annotations with delete buttons
            if st.session_state.expected_annotations:
                st.markdown("**Current Annotations:**")
                for i, ann in enumerate(st.session_state.expected_annotations):
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        color = PII_COLORS.get(ann["type"], "#888")
                        icon = PII_ICONS.get(ann["type"], "")
                        st.markdown(
                            f"<span style='color:{color};'>{icon} {ann['type']}</span>: `{ann['text']}`",
                            unsafe_allow_html=True,
                        )
                    with col2:
                        if st.button("✕", key=f"del_ann_{i}"):
                            st.session_state.expected_annotations.pop(i)
                            st.rerun()
            else:
                st.info("No annotations added. Detection will proceed without metrics calculation.")

        # Analyze button
        analyze_clicked = st.button("🔍 Analyze Text", type="primary", use_container_width=True)

        # Handle analyze button click
        if analyze_clicked:
            if input_text.strip():
                status_label = "🤖 AI Processing..." if use_llm else "🔍 Analyzing..."
                with st.status(status_label, expanded=True) as status:
                    st.write("🔍 Scanning text for PII patterns...")
                    payload = {"text": input_text, "use_llm": use_llm}
                    if use_llm:
                        payload["llm_model"] = st.session_state.get("llm_model", "haiku")
                        payload["llm_threshold"] = st.session_state.get("llm_threshold", 0.90)
                        st.write("🧠 Validating detections with LLM...")
                    response, request_info = call_api("detect", payload)

                    if response:
                        st.write("✨ Processing results...")
                        st.session_state.detect_response = response
                        st.session_state.detect_request = request_info
                        # High confidence = True (auto-approved), Low confidence = None (user must decide)
                        matches = response.get("matches", [])
                        threshold = st.session_state.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)
                        st.session_state.match_selections = {
                            i: True if m["confidence"] >= threshold else None
                            for i, m in enumerate(matches)
                        }
                        status.update(label="✅ Analysis complete!", state="complete", expanded=False)
                        st.session_state.workflow_step = 2
                        st.rerun()
                    else:
                        status.update(label="❌ Analysis failed", state="error", expanded=False)
            else:
                st.warning("Please enter some text to analyze.")

    # ============== STEP 2: REVIEW & APPROVE ==============
    elif st.session_state.workflow_step == 2:
        # Scroll to top when entering this step
        st.markdown("<script>window.parent.document.querySelector('section.main').scrollTo(0, 0);</script>", unsafe_allow_html=True)
        st.subheader("Step 2: Review & Approve Matches")

        detect_response = st.session_state.detect_response
        detect_request = st.session_state.detect_request
        matches = detect_response.get("matches", [])

        # Show API call
        with st.expander("📡 API: Detection", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Request:**")
                st.json(detect_request["body"])
            with col2:
                st.markdown("**Response:**")
                st.json(detect_response)

        if not matches:
            st.info("No PII detected in the text.")
            if st.button("← Back to Input"):
                reset_workflow()
                st.rerun()
        else:
            # Confidence threshold slider
            confidence_threshold = st.slider(
                "Auto-approve threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD),
                step=0.01,
                format="%.2f",
                help="Matches with confidence ≥ this value are auto-approved",
            )
            st.session_state.confidence_threshold = confidence_threshold

            # Summary metrics
            summary = detect_response.get("summary", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Detected", summary.get("total_count", 0))
            with col2:
                high_conf = sum(1 for m in matches if m["confidence"] >= confidence_threshold)
                st.metric("High Confidence", high_conf)
            with col3:
                needs_review = sum(1 for m in matches if m["confidence"] < confidence_threshold)
                st.metric("Needs Review", needs_review, help=f"Confidence < {confidence_threshold:.0%}")

            st.divider()

            # Split matches by confidence
            high_conf_matches = [(i, m) for i, m in enumerate(matches) if m["confidence"] >= confidence_threshold]
            review_matches = [(i, m) for i, m in enumerate(matches) if m["confidence"] < confidence_threshold]

            # Needs review matches FIRST (user must decide)
            pending_decisions = 0
            if review_matches:
                st.markdown("#### ⚠️ Needs Review (You must decide for each)")
                for idx, match in review_matches:
                    col1, col2, col3, col4 = st.columns([1.5, 1, 3, 0.8])
                    with col1:
                        # User must explicitly choose: Is PII or Not PII
                        current_decision = st.session_state.match_selections.get(idx, None)
                        # Map None -> None, True -> 0, False -> 1
                        current_index = None if current_decision is None else (0 if current_decision else 1)
                        decision_str = st.radio(
                            "Decision",
                            options=["✓ Is PII", "✗ Not PII"],
                            index=current_index,
                            key=f"review_{idx}",
                            horizontal=True,
                            label_visibility="collapsed",
                        )
                        # Map back: None -> None, "Is PII" -> True, "Not PII" -> False
                        if decision_str is None:
                            st.session_state.match_selections[idx] = None
                            pending_decisions += 1
                        else:
                            st.session_state.match_selections[idx] = decision_str == "✓ Is PII"
                    with col2:
                        color = PII_COLORS.get(match["type"], "#888")
                        st.markdown(f"<span style='color:{color};font-weight:bold;'>{match['type']}</span>", unsafe_allow_html=True)
                    with col3:
                        st.code(match["text"], language=None)
                    with col4:
                        st.markdown(f"🔴 **{match['confidence']:.0%}**")

            # High confidence matches (auto-approved, display only)
            if high_conf_matches:
                with st.expander(f"✅ High Confidence (Auto-Approved) — {len(high_conf_matches)} items", expanded=False):
                    for idx, match in high_conf_matches:
                        col1, col2, col3, col4 = st.columns([0.5, 1.5, 3, 1])
                        with col1:
                            st.checkbox("Include", value=True, disabled=True, key=f"high_{idx}", label_visibility="collapsed")
                        with col2:
                            color = PII_COLORS.get(match["type"], "#888")
                            st.markdown(f"<span style='color:{color};font-weight:bold;'>{match['type']}</span>", unsafe_allow_html=True)
                        with col3:
                            st.code(match["text"], language=None)
                        with col4:
                            st.markdown(f"**{match['confidence']:.0%}**")

            st.divider()

            # Strategy selection
            strategy = st.radio(
                "Anonymization Strategy:",
                options=["redaction", "masking", "hashing"],
                horizontal=True,
                help="Choose how to anonymize the selected PII",
            )
            st.session_state.selected_strategy = strategy

            # Action buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.workflow_step = 1
                    st.rerun()
            with col3:
                # Count selected matches (high conf = always True, review = user decision)
                selected_count = 0
                for i, match in enumerate(matches):
                    decision = st.session_state.match_selections.get(i, None)
                    if match["confidence"] >= confidence_threshold:
                        selected_count += 1  # High confidence auto-approved
                    elif decision is True:
                        selected_count += 1  # User marked as PII

                # Disable if pending decisions or no matches selected
                has_pending = pending_decisions > 0
                button_disabled = has_pending or selected_count == 0
                button_label = f"⏳ {pending_decisions} pending decisions" if has_pending else f"✓ Apply Anonymization ({selected_count} matches)"

                if st.button(
                    button_label,
                    type="primary",
                    use_container_width=True,
                    disabled=button_disabled,
                ):
                    # Build approved matches list
                    approved_matches = []
                    for i, match in enumerate(matches):
                        decision = st.session_state.match_selections.get(i, None)
                        # Include high confidence (auto-approved) and user-confirmed PII
                        if match["confidence"] >= confidence_threshold or decision is True:
                            approved_matches.append({
                                "type": match["type"],
                                "start": match["start"],
                                "end": match["end"],
                            })

                    # Call anonymize API
                    payload = {
                        "text": st.session_state.input_text,
                        "matches": approved_matches,
                        "strategy": strategy,
                    }
                    with st.spinner("Anonymizing..."):
                        response, request_info = call_api("anonymize", payload)

                        if response:
                            st.session_state.anonymize_response = response
                            st.session_state.anonymize_request = request_info
                            st.session_state.workflow_step = 3
                            st.rerun()

    # ============== STEP 3: RESULT ==============
    elif st.session_state.workflow_step == 3:
        # Scroll to top when entering this step
        st.markdown("<script>window.parent.document.querySelector('section.main').scrollTo(0, 0);</script>", unsafe_allow_html=True)

        # Header with New button inline
        header_col, btn_col = st.columns([6, 1])
        with header_col:
            st.subheader("Step 3: Anonymization Result")
        with btn_col:
            if st.button("🔄 New", type="primary", use_container_width=True):
                reset_workflow()
                st.rerun()

        anonymize_response = st.session_state.anonymize_response
        anonymize_request = st.session_state.anonymize_request
        detect_response = st.session_state.detect_response
        match_selections = st.session_state.get("match_selections", {})
        threshold = st.session_state.get("confidence_threshold", DEFAULT_CONFIDENCE_THRESHOLD)

        # ---- SECTION 1: Before/After comparison ----
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Original Text")
            st.code(anonymize_response.get("original_text", ""), language=None)
        with col2:
            st.markdown(f"#### Anonymized ({st.session_state.get('selected_strategy', 'redaction')})")
            st.code(anonymize_response.get("processed_text", ""), language=None)

        st.divider()

        # ---- SECTION 2: Protection Summary (4 metrics) ----
        summary = anonymize_response.get("summary", {})
        original_text = anonymize_response.get("original_text", "")
        processed_text = anonymize_response.get("processed_text", "")

        # Calculate text coverage (chars replaced / total chars)
        total_chars = len(original_text)
        chars_diff = abs(len(original_text) - len(processed_text))
        # Better estimate: count replacement placeholders
        pii_count = summary.get("total_count", 0)
        text_coverage = (chars_diff / total_chars * 100) if total_chars > 0 else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("PII Protected", pii_count)
        with col2:
            st.metric("Text Coverage", f"{text_coverage:.1f}%", help="Percentage of text modified")
        with col3:
            st.metric("Strategy", st.session_state.get("selected_strategy", "redaction").title())
        with col4:
            st.metric("Processing Time", f"{anonymize_response.get('processing_time_ms', 0):.1f}ms")

        st.divider()

        # ---- SECTION 3: Analytics Dashboard (Plotly Charts) ----
        st.markdown("#### Analytics Dashboard")
        matches = detect_response.get("matches", [])
        total_detected = len(matches)
        by_type = summary.get("by_type", {})

        # Calculate HITL metrics
        auto_approved = sum(1 for m in matches if m["confidence"] >= threshold)
        user_confirmed = sum(
            1 for i, m in enumerate(matches)
            if m["confidence"] < threshold and match_selections.get(i) is True
        )
        user_rejected = sum(
            1 for i, m in enumerate(matches)
            if m["confidence"] < threshold and match_selections.get(i) is False
        )
        human_correction_rate = (user_rejected / total_detected * 100) if total_detected > 0 else 0

        # Detection method counts
        rule_based_detectors = {"email", "phone", "iban", "credit_card", "ip_address", "german_id"}
        rule_based_count = sum(1 for m in matches if m.get("detector", "").lower() in rule_based_detectors)
        ml_count = sum(1 for m in matches if m.get("detector", "").lower() == "presidio")

        # Row 1: Gauge + Donut side by side
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            # Human Correction Rate Gauge
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=human_correction_rate,
                number={"suffix": "%", "font": {"size": 32, "color": "#e0e0e0"}},
                title={"text": "Human Correction Rate", "font": {"size": 14, "color": "#888"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": "#888", "tickfont": {"color": "#888"}},
                    "bar": {"color": "#00b4d8"},
                    "bgcolor": "rgba(0,0,0,0)",
                    "steps": [
                        {"range": [0, 10], "color": "#2ecc71"},
                        {"range": [10, 30], "color": "#f39c12"},
                        {"range": [30, 100], "color": "#e74c3c"},
                    ],
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font={"family": "Inter, sans-serif"},
                height=220,
                margin={"l": 20, "r": 20, "t": 50, "b": 20}
            )
            st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})

        with chart_col2:
            # Detection Methods Donut
            if rule_based_count + ml_count > 0:
                fig_donut = go.Figure(go.Pie(
                    labels=["Rule-based", "ML/NER"],
                    values=[rule_based_count, ml_count],
                    hole=0.6,
                    marker={"colors": ["#00b4d8", "#7209b7"], "line": {"color": "#1a1a2e", "width": 2}},
                    textinfo="percent+label",
                    textposition="outside",
                    textfont={"size": 11, "color": "#e0e0e0"},
                ))
                fig_donut.update_layout(
                    title={"text": "Detection Methods", "font": {"size": 14, "color": "#888"}, "x": 0.5},
                    paper_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    height=220,
                    margin={"l": 20, "r": 20, "t": 50, "b": 20},
                    annotations=[{
                        "text": f"{rule_based_count + ml_count}",
                        "x": 0.5, "y": 0.5,
                        "font": {"size": 24, "color": "#e0e0e0"},
                        "showarrow": False
                    }]
                )
                st.plotly_chart(fig_donut, use_container_width=True, config={"displayModeBar": False})
            else:
                st.info("No detection method data")

        st.divider()

        # ---- SECTION 4: HITL Summary Metrics ----
        st.markdown(f"<div style='color: #888; font-size: 12px;'>Confidence Threshold: {threshold:.0%}</div>", unsafe_allow_html=True)
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Auto-approved", auto_approved, help="High confidence detections")
        with metric_col2:
            st.metric("User Confirmed", user_confirmed, help="Reviewed and marked as PII")
        with metric_col3:
            st.metric("User Rejected", user_rejected, help="False positives caught by human review")

        # ---- SECTION 4.5: ML Performance Metrics ----
        expected_annotations = st.session_state.get("expected_annotations", [])
        if expected_annotations:
            st.divider()
            st.markdown("#### ML Performance Metrics")

            # Get approved matches only (high confidence + user confirmed)
            approved_matches = [
                m for i, m in enumerate(matches)
                if m["confidence"] >= threshold or match_selections.get(i) is True
            ]

            metrics = calculate_metrics(expected_annotations, approved_matches)

            if metrics:
                # Metrics row
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Precision",
                        f"{metrics['precision']:.1%}",
                        help="Of detected PII, how much was expected?",
                    )
                with col2:
                    st.metric(
                        "Recall",
                        f"{metrics['recall']:.1%}",
                        help="Of expected PII, how much was detected?",
                    )
                with col3:
                    st.metric(
                        "F1 Score",
                        f"{metrics['f1']:.1%}",
                        help="Harmonic mean of Precision and Recall",
                    )

                # Confusion counts
                st.markdown(
                    f"<div style='background: #1a1a2e; padding: 12px; border-radius: 8px; margin: 10px 0;'>"
                    f"<span style='color: #4CAF50;'>TP: {metrics['tp']}</span> | "
                    f"<span style='color: #FFC107;'>FP: {metrics['fp']}</span> | "
                    f"<span style='color: #F44336;'>FN: {metrics['fn']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                # Detailed breakdown in expander (only show errors)
                with st.expander("Breakdown Details", expanded=True):
                    # False Positives (wrong detections) - Yellow/Orange
                    if metrics["fp_details"]:
                        st.markdown("<span style='color: #FFC107; font-weight: bold;'>False Positives (Wrong Detections):</span>", unsafe_allow_html=True)
                        for pii_type, text in metrics["fp_details"]:
                            st.markdown(f"<span style='color: #FFC107;'>- {pii_type}: `{text}`</span>", unsafe_allow_html=True)

                    # False Negatives (missed) - Red
                    if metrics["fn_details"]:
                        st.markdown("<span style='color: #F44336; font-weight: bold;'>False Negatives (Missed):</span>", unsafe_allow_html=True)
                        for pii_type, text in metrics["fn_details"]:
                            st.markdown(f"<span style='color: #F44336;'>- {pii_type}: `{text}`</span>", unsafe_allow_html=True)

                    # Show success message if no errors
                    if not metrics["fp_details"] and not metrics["fn_details"]:
                        st.markdown("<span style='color: #4CAF50;'>✓ All detections correct!</span>", unsafe_allow_html=True)

        # ---- SECTION 5: Detection Details with Explainability ----
        with st.expander("📋 Detection Details", expanded=True):
            if matches:
                # Part 1: Annotated Text View
                st.markdown("**Annotated Text** *(hover over highlights for details)*")
                highlighted_html = build_highlighted_html(original_text, matches)
                st.markdown(highlighted_html, unsafe_allow_html=True)

                # Merged legend + counts
                if by_type:
                    legend_html = "<div style='margin: 8px 0; line-height: 2;'>"
                    for pii_type, count in by_type.items():
                        color = PII_COLORS.get(pii_type, "#888")
                        icon = PII_ICONS.get(pii_type, "")
                        legend_html += (
                            f"<span style='display: inline-flex; align-items: center; "
                            f"margin-right: 14px; background: {color}22; border: 1px solid {color}; "
                            f"padding: 4px 12px; border-radius: 16px; font-size: 12px;'>"
                            f"<span style='width: 14px; height: 3px; background: {color}; "
                            f"margin-right: 6px; border-radius: 2px;'></span>"
                            f"{icon} {pii_type}: "
                            f"<span style='font-size: 15px; font-weight: 700; color: #fff; "
                            f"margin-left: 2px;'>{count}</span></span>"
                        )
                    legend_html += "</div>"
                    st.markdown(legend_html, unsafe_allow_html=True)

                st.divider()

                # Part 2: Detection Breakdown Table with Reason column
                st.markdown("**Detection Breakdown**")
                table_data = []
                for i, m in enumerate(matches):
                    conf = m["confidence"]
                    # Confidence badge
                    if conf >= 0.85:
                        conf_display = f"🟢 {conf:.0%}"
                    elif conf >= 0.7:
                        conf_display = f"🟡 {conf:.0%}"
                    else:
                        conf_display = f"🔴 {conf:.0%}"

                    # Decision status
                    selection = match_selections.get(i)
                    if m["confidence"] >= threshold:
                        status = "✓ Auto"
                    elif selection is True:
                        status = "✓ Confirmed"
                    elif selection is False:
                        status = "✗ Rejected"
                    else:
                        status = "⏳ Pending"

                    # Get detection reason
                    detector = m.get("detector", "unknown").lower()
                    reason = DETECTION_REASONS.get(detector, "Pattern matched")

                    table_data.append({
                        "Type": m["type"],
                        "Detected Text": m["text"],
                        "Confidence": conf_display,
                        "Detector": m.get("detector", "unknown"),
                        "Reason": reason,
                        "Status": status,
                    })

                df = pd.DataFrame(table_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No detections to display")

        st.divider()

        # ---- SECTION 6: API Panel (collapsed at bottom) ----
        with st.expander("📡 API: Anonymization", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Request:**")
                st.json(anonymize_request["body"])
            with col2:
                st.markdown("**Response:**")
                st.json(anonymize_response)


if __name__ == "__main__":
    main()
