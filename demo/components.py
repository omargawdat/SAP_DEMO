"""Reusable UI components for the Streamlit demo."""

import html

import pandas as pd
import plotly.express as px
import streamlit as st

from demo.styles import PII_COLORS, PII_ICONS

# Detector metadata for info cards
DETECTOR_INFO = {
    "email": {
        "name": "EmailDetector",
        "type": "Rule-based (Regex)",
        "confidence": "Always 1.0",
        "description": "Detects email addresses using RFC 5322 pattern matching",
    },
    "phone": {
        "name": "PhoneDetector",
        "type": "Rule-based (Regex)",
        "confidence": "0.7 - 1.0",
        "description": "Detects German phone formats (mobile, landline, international)",
    },
    "iban": {
        "name": "IBANDetector",
        "type": "Rule-based + Validation",
        "confidence": "0.7 - 1.0",
        "description": "Detects IBANs with mod-97 checksum validation",
    },
    "german_id": {
        "name": "GermanIDDetector",
        "type": "Rule-based + Validation",
        "confidence": "0.6 - 1.0",
        "description": "Detects Personalausweis numbers with check digit validation",
    },
    "credit_card": {
        "name": "CreditCardDetector",
        "type": "Rule-based + Luhn",
        "confidence": "Always 1.0",
        "description": "Detects credit cards (Visa, MC, Amex) with Luhn validation",
    },
    "ip_address": {
        "name": "IPAddressDetector",
        "type": "Rule-based",
        "confidence": "Always 1.0",
        "description": "Detects IPv4 and IPv6 addresses",
    },
    "presidio": {
        "name": "PresidioDetector",
        "type": "ML-based (spaCy NER)",
        "confidence": "Variable (0.0 - 1.0)",
        "description": "Uses German NER model for names, addresses, dates",
    },
}


def build_highlighted_html(text: str, matches: list) -> str:
    """Build HTML with highlighted PII spans."""
    if not matches:
        return f"<pre style='white-space: pre-wrap;'>{html.escape(text)}</pre>"

    # Sort matches by start position (reverse for replacement)
    sorted_matches = sorted(matches, key=lambda m: m["start"])

    result = []
    last_end = 0

    for match in sorted_matches:
        # Add text before this match
        if match["start"] > last_end:
            result.append(html.escape(text[last_end : match["start"]]))

        # Add highlighted match (underline style, no icon)
        pii_type = match["type"]
        confidence = match["confidence"]
        detector = match["detector"]

        tooltip = f"{pii_type} | Confidence: {confidence:.0%} | Detector: {detector}"
        result.append(
            f'<span class="pii-highlight pii-{pii_type}" title="{tooltip}">'
            f"{html.escape(match['text'])}</span>"
        )
        last_end = match["end"]

    # Add remaining text
    if last_end < len(text):
        result.append(html.escape(text[last_end:]))

    return f"<pre style='white-space: pre-wrap; line-height: 1.8;'>{''.join(result)}</pre>"


def render_highlighted_text(text: str, matches: list) -> None:
    """Render text with colored PII highlights."""
    html_content = build_highlighted_html(text, matches)
    st.markdown(html_content, unsafe_allow_html=True)


def render_legend() -> None:
    """Render compact color legend for PII types."""
    legend_html = "<div style='margin: 8px 0; line-height: 1.8;'>"
    for pii_type, color in PII_COLORS.items():
        legend_html += (
            f"<span class='legend-item'>"
            f"<span class='legend-color' style='background-color: {color};'></span>"
            f"{pii_type}</span>"
        )
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)


def render_metrics_row(summary: dict, processing_time: float, matches: list) -> None:
    """Render metrics cards row."""
    high_conf = sum(1 for m in matches if m["confidence"] >= 0.85)
    review_needed = sum(1 for m in matches if m["confidence"] < 0.85)

    cols = st.columns(4)
    with cols[0]:
        st.metric("Total PII Found", summary["total_count"])
    with cols[1]:
        st.metric("Processing Time", f"{processing_time:.1f}ms")
    with cols[2]:
        st.metric("High Confidence", high_conf, help="Confidence >= 85%")
    with cols[3]:
        st.metric("Needs Review", review_needed, help="Confidence < 85%")


def render_matches_table(matches: list) -> None:
    """Render matches as an interactive table."""
    if not matches:
        st.info("No PII detected in the text.")
        return

    # Prepare data for table
    table_data = []
    for m in matches:
        conf = m["confidence"]
        if conf >= 0.85:
            conf_badge = f"🟢 {conf:.0%}"
        elif conf >= 0.7:
            conf_badge = f"🟡 {conf:.0%}"
        else:
            conf_badge = f"🔴 {conf:.0%}"

        icon = PII_ICONS.get(m["type"], "")
        table_data.append(
            {
                "Type": f"{icon} {m['type']}",
                "Detected Text": m["text"],
                "Confidence": conf_badge,
                "Detector": m["detector"],
                "Position": f"{m['start']}-{m['end']}",
            }
        )

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)


def render_strategy_comparison(
    original: str, redacted: str, masked: str, hashed: str
) -> None:
    """Render side-by-side strategy comparison."""
    cols = st.columns(3)

    with cols[0]:
        st.markdown("### Redaction")
        st.code(redacted, language=None)
        st.caption("✓ Full removal | ✓ Shows type placeholder")

    with cols[1]:
        st.markdown("### Masking")
        st.code(masked, language=None)
        st.caption("✓ Partial visibility | ✓ Recognizable format")

    with cols[2]:
        st.markdown("### Hashing")
        st.code(hashed, language=None)
        st.caption("✓ GDPR pseudonymization | ✓ Deterministic")


def render_detector_chart(matches: list) -> None:
    """Render horizontal bar chart of matches per detector."""
    if not matches:
        st.info("No matches to visualize.")
        return

    # Count by detector
    detector_counts = {}
    for m in matches:
        detector = m["detector"]
        detector_counts[detector] = detector_counts.get(detector, 0) + 1

    df = pd.DataFrame(
        [{"Detector": k, "Matches": v} for k, v in detector_counts.items()]
    )
    df = df.sort_values("Matches", ascending=True)

    fig = px.bar(
        df,
        x="Matches",
        y="Detector",
        orientation="h",
        color="Matches",
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        height=max(200, len(detector_counts) * 40),
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        showlegend=False,
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_confidence_histogram(matches: list) -> None:
    """Render confidence distribution histogram."""
    if not matches:
        st.info("No matches to visualize.")
        return

    df = pd.DataFrame([{"confidence": m["confidence"], "type": m["type"]} for m in matches])

    fig = px.histogram(
        df,
        x="confidence",
        color="type",
        nbins=20,
        range_x=[0, 1],
        color_discrete_map=PII_COLORS,
    )
    fig.update_layout(
        xaxis_title="Confidence Score",
        yaxis_title="Count",
        height=300,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
    )

    # Add threshold line
    fig.add_vline(x=0.85, line_dash="dash", line_color="red", annotation_text="Review threshold")

    st.plotly_chart(fig, use_container_width=True)


def render_pii_type_chart(summary: dict) -> None:
    """Render pie chart of PII types."""
    by_type = summary.get("by_type", {})
    if not by_type:
        st.info("No PII types to visualize.")
        return

    df = pd.DataFrame([{"Type": k, "Count": v} for k, v in by_type.items()])

    fig = px.pie(
        df,
        values="Count",
        names="Type",
        color="Type",
        color_discrete_map=PII_COLORS,
        hole=0.4,
    )
    fig.update_layout(
        height=300,
        margin={"l": 0, "r": 0, "t": 10, "b": 0},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_detector_info_cards(matches: list) -> None:
    """Render expandable detector info cards."""
    # Get unique detectors from matches
    detectors_used = {m["detector"] for m in matches} if matches else set()

    for detector_id, info in DETECTOR_INFO.items():
        match_count = sum(1 for m in matches if m["detector"] == detector_id) if matches else 0
        status = "✅ Active" if detector_id in detectors_used else "⚪ No matches"

        with st.expander(f"{info['name']} - {status} ({match_count} matches)"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Type:** {info['type']}")
                st.markdown(f"**Confidence:** {info['confidence']}")
            with col2:
                st.markdown(f"**Description:** {info['description']}")


def render_architecture_diagram() -> None:
    """Render architecture flow diagram."""
    st.markdown(
        """
    ```
    ┌─────────────────────────────────────────────────────────────────┐
    │                        INPUT TEXT                               │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                      DETECTION PIPELINE                         │
    │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
    │  │  Email   │ │  Phone   │ │   IBAN   │ │ Presidio │  ...      │
    │  │ (Regex)  │ │ (Regex)  │ │(Checksum)│ │  (NER)   │           │
    │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘           │
    │       │            │            │            │                  │
    │       └────────────┴────────────┴────────────┘                  │
    │                         │                                       │
    │                         ▼                                       │
    │              ┌─────────────────────┐                           │
    │              │   DEDUPLICATION     │                           │
    │              │ (Merge overlapping) │                           │
    │              └─────────────────────┘                           │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                    DE-IDENTIFICATION STRATEGY                   │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
    │  │  REDACTION   │  │   MASKING    │  │   HASHING    │          │
    │  │  [EMAIL]     │  │  han***com   │  │  a7f3d2c1... │          │
    │  └──────────────┘  └──────────────┘  └──────────────┘          │
    └─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
    ┌─────────────────────────────────────────────────────────────────┐
    │                      ANONYMIZED OUTPUT                          │
    └─────────────────────────────────────────────────────────────────┘
    ```
    """
    )


def render_code_snippet(title: str, code: str, language: str = "python") -> None:
    """Render a code snippet with title."""
    st.markdown(f"**{title}**")
    st.code(code, language=language)
