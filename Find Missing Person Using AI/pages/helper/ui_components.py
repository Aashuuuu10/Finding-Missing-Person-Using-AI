import os
import streamlit as st


def load_css():
    """Inject the global custom CSS into the Streamlit app."""
    css_path = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "style.css")
    css_path = os.path.normpath(css_path)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def status_badge(status: str) -> str:
    """Return an HTML status badge string."""
    dot_map = {"F": "🟢", "NF": "🔴", "matched": "🔵"}
    dot = dot_map.get(status, "🟡")
    if status == "F":
        return f'<span class="badge badge-found">{dot} Found</span>'
    elif status == "NF":
        return f'<span class="badge badge-not-found">{dot} Not Found</span>'
    elif status == "matched":
        return f'<span class="badge badge-matched">{dot} Matched</span>'
    else:
        return f'<span class="badge badge-pending">{dot} Pending</span>'


def stat_card(icon: str, value, label: str) -> str:
    """Return HTML for a dashboard stat card."""
    return f"""
    <div class="stat-card">
        <div class="stat-icon">{icon}</div>
        <div class="stat-value">{value}</div>
        <div class="stat-label">{label}</div>
    </div>
    """


def page_header(title: str, subtitle: str = ""):
    """Render a styled page header."""
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def section_header(icon: str, title: str, count: int = None) -> str:
    """Return HTML for a section header with optional count badge."""
    count_html = f'<span class="count-badge">{count}</span>' if count is not None else ""
    return f'<div class="section-header">{icon} {title} {count_html}</div>'


def empty_state(icon: str, title: str, description: str) -> str:
    """Return HTML for an empty state placeholder."""
    return f"""
    <div class="empty-state">
        <div class="empty-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """


def feature_card(icon: str, title: str, desc: str) -> str:
    """Return HTML for a quick-action / feature card."""
    return f"""
    <div class="feature-card">
        <div class="feature-icon">{icon}</div>
        <div class="feature-title">{title}</div>
        <div class="feature-desc">{desc}</div>
    </div>
    """


def step_card(number: int, icon: str, title: str, desc: str) -> str:
    """Return HTML for a numbered step card."""
    return f"""
    <div class="step-card">
        <div class="step-number">{number}</div>
        <div class="step-icon">{icon}</div>
        <div class="step-title">{title}</div>
        <div class="step-desc">{desc}</div>
    </div>
    """


def confirm_card(icon: str, title: str, desc: str) -> str:
    """Return HTML for a success / confirmation card."""
    return f"""
    <div class="confirm-card">
        <div class="confirm-icon">{icon}</div>
        <div class="confirm-title">{title}</div>
        <div class="confirm-desc">{desc}</div>
    </div>
    """


def case_card_html(fields: dict, status: str = "", title: str = "Case Details") -> str:
    """Return HTML for a styled case card with info rows."""
    rows = ""
    for label, value in fields.items():
        rows += f"""
        <div class="info-row">
            <span class="info-label">{label}</span>
            <span class="info-value">{value}</span>
        </div>"""

    badge = status_badge(status) if status else ""

    return f"""
    <div class="case-card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <h4 style="margin:0; color:#FAFAFA;">{title}</h4>
            {badge}
        </div>
        {rows}
    </div>
    """


def sidebar_profile(name: str, role: str, area: str, city: str):
    """Render a styled sidebar profile section."""
    initials = "".join([w[0].upper() for w in name.split()[:2]])
    st.sidebar.markdown(f"""
    <div class="sidebar-profile">
        <div class="profile-avatar">{initials}</div>
        <div class="profile-name">{name}</div>
        <div class="profile-role">{role}</div>
        <div class="profile-location">📍 {area}, {city}</div>
    </div>
    """, unsafe_allow_html=True)


def similarity_score_card(score: float) -> str:
    """Return HTML for a radial-style similarity score display."""
    if score >= 80:
        color = "#2ECC71"
        label = "Excellent"
    elif score >= 60:
        color = "#F1C40F"
        label = "Good"
    elif score >= 40:
        color = "#E67E22"
        label = "Moderate"
    else:
        color = "#E74C3C"
        label = "Low"

    # SVG ring gauge
    radius = 40
    circumference = 2 * 3.14159 * radius
    offset = circumference * (1 - score / 100)
    return f"""
    <div class="confirm-card" style="background:linear-gradient(135deg, rgba(26,31,46,0.95), rgba(37,43,59,0.95));
                border-color:rgba({_hex_to_rgb(color)}, 0.25); padding:24px 16px;">
        <svg width="100" height="100" viewBox="0 0 100 100" style="display:block; margin:0 auto;">
            <circle cx="50" cy="50" r="{radius}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="6"/>
            <circle cx="50" cy="50" r="{radius}" fill="none" stroke="{color}" stroke-width="6"
                    stroke-dasharray="{circumference}" stroke-dashoffset="{offset}"
                    stroke-linecap="round" transform="rotate(-90 50 50)"
                    style="transition:stroke-dashoffset 1s ease;"/>
            <text x="50" y="46" text-anchor="middle" fill="{color}" font-size="18" font-weight="800">{score}%</text>
            <text x="50" y="62" text-anchor="middle" fill="#7B8598" font-size="9" font-weight="600">{label}</text>
        </svg>
        <div style="color:#7B8598; font-size:0.78rem; text-transform:uppercase; letter-spacing:1px;
                    font-weight:600; margin-top:8px; text-align:center;">Similarity Score</div>
    </div>
    """


def timeline_event(action: str, description: str, timestamp, actor: str = "") -> str:
    """Return HTML for a single timeline event."""
    icon_map = {
        "created": "📝",
        "matched": "🎯",
        "updated": "✏️",
        "photo_added": "📷",
        "status_change": "🔄",
    }
    icon = icon_map.get(action, "📌")
    ts_str = timestamp.strftime("%b %d, %Y %I:%M %p") if hasattr(timestamp, 'strftime') else str(timestamp)
    actor_html = f'<span style="color:#4F8BF9; font-weight:600;"> by {actor}</span>' if actor else ""
    return (
        '<div style="display:flex; gap:14px; padding:12px 0; border-bottom:1px solid rgba(255,255,255,0.04);">'
        '<div style="min-width:36px; height:36px; border-radius:10px;'
        ' background:rgba(79,139,249,0.1); border:1px solid rgba(79,139,249,0.15);'
        ' display:flex; align-items:center; justify-content:center; font-size:1rem;">'
        f'{icon}</div>'
        '<div style="flex:1;">'
        f'<div style="color:#FAFAFA; font-weight:600; font-size:0.9rem;">{action.replace("_", " ").title()}{actor_html}</div>'
        f'<div style="color:#7B8598; font-size:0.82rem; margin-top:2px;">{description}</div>'
        f'<div style="color:#5A6476; font-size:0.75rem; margin-top:4px;">{ts_str}</div>'
        '</div></div>'
    )


def _hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to r,g,b string."""
    h = hex_color.lstrip("#")
    return ",".join(str(int(h[i:i+2], 16)) for i in (0, 2, 4))
