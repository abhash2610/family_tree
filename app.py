import json
from datetime import datetime, date
from difflib import SequenceMatcher

import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="Family Tree",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown(
    """
    <style>
        .main { padding-top: 0rem; }
        .metric-card { padding: 0.25rem 0; }
        .tree-info {
            background: #eef7fb;
            padding: 12px 15px;
            border-radius: 8px;
            margin-bottom: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================================
# AUTHENTICATION
# ============================================================================


def check_password():
    """Return True only after the configured password has been entered."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return

    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                "<h1 style='text-align:center;'>🌳 Family Tree</h1>",
                unsafe_allow_html=True,
            )
            st.markdown("---")
            password = st.text_input(
                "🔐 Enter password:",
                type="password",
                key="pwd_input",
            )

            if st.button("Login", use_container_width=True, type="primary"):
                correct_password = st.secrets.get("FAMILY_TREE_PASSWORD", "")
                if not correct_password:
                    st.error("⚠️ Password not configured in secrets")
                elif password == correct_password:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Please try again.")

    st.stop()


check_password()


# ============================================================================
# GOOGLE SHEETS CONNECTION
# ============================================================================


@st.cache_resource
def get_google_sheets_connection():
    """Establish a read-only Google Sheets connection."""
    try:
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets.readonly",
                "https://www.googleapis.com/auth/drive.readonly",
            ],
        )
        return gspread.authorize(credentials)
    except Exception as exc:
        st.error(f"❌ Failed to connect to Google Sheets: {exc}")
        st.stop()


# ============================================================================
# DATA HELPERS
# ============================================================================

REQUIRED_COLUMNS = [
    "Name",
    "Generation",
    "Gender",
    "Date of Birth",
    "Father Name",
    "Mother Name",
    "Spouse Name",
    "Age",
]

OPTIONAL_COLUMNS = ["Date of Death"]


def is_blank(value) -> bool:
    return pd.isna(value) or str(value).strip() == ""


def clean_name(value):
    if is_blank(value):
        return None
    return " ".join(str(value).strip().lower().split())


def display_value(value) -> str:
    if is_blank(value):
        return ""
    return str(value).strip()


def parse_date(value):
    """Parse common spreadsheet date formats, including DD/MM/YYYY."""
    if is_blank(value):
        return pd.NaT

    if isinstance(value, (pd.Timestamp, datetime, date)):
        return pd.Timestamp(value)

    text = str(value).strip()
    for day_first in (True, False):
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=day_first)
        if not pd.isna(parsed):
            return parsed
    return pd.NaT


def format_date(value) -> str:
    if pd.isna(value):
        return ""
    try:
        return pd.Timestamp(value).strftime("%d/%m/%Y")
    except Exception:
        return ""


def normalize_gender(value) -> str:
    text = display_value(value).lower()
    if text in {"m", "male", "man", "boy"}:
        return "Male"
    if text in {"f", "female", "woman", "girl"}:
        return "Female"
    return "Other"


def fuzzy_name_match(search_name, candidates, threshold=0.90):
    """Return a unique strong fuzzy match, otherwise None."""
    if not search_name or not candidates:
        return None

    best = None
    best_score = 0.0
    for candidate_name, candidate_idx in candidates:
        score = SequenceMatcher(None, search_name, candidate_name).ratio()
        if score > best_score:
            best_score = score
            best = candidate_idx

    return best if best_score >= threshold else None


def find_person_by_name(df, search_name, exact_only=False, exclude_idx=None):
    """Find a row index by normalized name; fuzzy matching is only a fallback."""
    wanted = clean_name(search_name)
    if not wanted:
        return None

    exact = []
    candidates = []
    for idx, row in df.iterrows():
        if exclude_idx is not None and idx == exclude_idx:
            continue
        name = clean_name(row.get("Name"))
        if not name:
            continue
        candidates.append((name, idx))
        if name == wanted:
            exact.append(idx)

    # Exact matching wins. If names are duplicated, report the first deterministic row.
    if exact:
        return exact[0]

    if exact_only:
        return None

    return fuzzy_name_match(wanted, candidates)


def calculate_generation(df, person_idx, generation_data, visiting=None):
    """Infer a missing generation from the person's parents."""
    if generation_data.get(person_idx) is not None:
        return generation_data[person_idx]

    visiting = set() if visiting is None else visiting
    if person_idx in visiting:
        return 1
    visiting.add(person_idx)

    father_idx = find_person_by_name(
        df, df.loc[person_idx, "Father Name"], exact_only=False, exclude_idx=person_idx
    )
    mother_idx = find_person_by_name(
        df, df.loc[person_idx, "Mother Name"], exact_only=False, exclude_idx=person_idx
    )

    parent_gens = []
    if father_idx is not None:
        parent_gens.append(calculate_generation(df, father_idx, generation_data, visiting))
    if mother_idx is not None:
        parent_gens.append(calculate_generation(df, mother_idx, generation_data, visiting))

    if parent_gens:
        generation_data[person_idx] = max(parent_gens) - 1
        # Avoid returning zero/negative values for incomplete data.
        generation_data[person_idx] = max(1, generation_data[person_idx])
    else:
        generation_data[person_idx] = 1

    visiting.remove(person_idx)
    return generation_data[person_idx]


@st.cache_data(ttl=300)
def load_family_data():
    """Load and normalize family data from Google Sheets."""
    try:
        gc = get_google_sheets_connection()
        sheet_name = st.secrets.get("SHEET_NAME", "Family Tree")
        spreadsheet = gc.open(sheet_name)
        worksheet = spreadsheet.sheet1
        data = worksheet.get_all_records()

        if not data:
            st.warning("⚠️ Google Sheet is empty. Please add family members.")
            return None

        df = pd.DataFrame(data)
        df.columns = [str(col).strip() for col in df.columns]

        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            st.error(f"❌ Missing columns in sheet: {', '.join(missing_columns)}")
            return None

        # Date of Death is optional. The old application accessed it later even when
        # the column did not exist, which could cause a KeyError.
        if "Date of Death" not in df.columns:
            df["Date of Death"] = ""

        # Remove completely blank spreadsheet rows and rows without a person name.
        df = df[df["Name"].apply(lambda value: not is_blank(value))].copy()
        df.reset_index(drop=True, inplace=True)

        if df.empty:
            st.warning("⚠️ No named family members were found in the sheet.")
            return None

        df.insert(0, "Unique_ID", [f"P{idx + 1}" for idx in range(len(df))])

        for column in ["Name", "Gender", "Father Name", "Mother Name", "Spouse Name"]:
            df[column] = df[column].apply(display_value)

        df["Gender"] = df["Gender"].apply(normalize_gender)
        df["Date of Birth"] = df["Date of Birth"].apply(parse_date)
        df["Date of Death"] = df["Date of Death"].apply(parse_date)
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
        df["Generation"] = pd.to_numeric(df["Generation"], errors="coerce")

        # Calculate missing ages from DOB.
        today = pd.Timestamp.today().normalize()
        missing_age = df["Age"].isna() & df["Date of Birth"].notna()
        df.loc[missing_age, "Age"] = df.loc[missing_age, "Date of Birth"].apply(
            lambda dob: max(0, (today - pd.Timestamp(dob)).days // 365)
        )

        # Infer missing generations. Existing spreadsheet values are preserved.
        generation_data = {
            idx: (int(value) if pd.notna(value) else None)
            for idx, value in df["Generation"].items()
        }
        for idx in df.index:
            if generation_data[idx] is None:
                calculate_generation(df, idx, generation_data)
        df["Generation"] = df.index.map(generation_data).astype(int)

        return df

    except gspread.exceptions.SpreadsheetNotFound:
        st.error(f"❌ Google Sheet '{sheet_name}' not found")
        return None
    except Exception as exc:
        st.error(f"❌ Error loading data: {exc}")
        return None


# ============================================================================
# FAMILY MODEL FOR D3
# ============================================================================


def resolve_family_model(df, validation_messages):
    """
    Build a visualization-friendly family model.

    Important behaviour:
      * People explicitly present in the sheet are real person records.
      * A spouse mentioned in `Spouse Name` but not present as a row is still
        rendered as a lightweight spouse node, so the spouse is visible.
      * Spouse records are merged if the person is later added to the sheet.
      * Parent relationships use the names in Father/Mother Name.
    """

    persons = {}
    name_to_id = {}

    # Real people from the sheet.
    for _, row in df.iterrows():
        person_id = str(row["Unique_ID"])
        person = {
            "id": person_id,
            "name": display_value(row["Name"]),
            "gender": normalize_gender(row["Gender"]),
            "dob": format_date(row["Date of Birth"]),
            "age": int(row["Age"]) if pd.notna(row["Age"]) else None,
            "death": format_date(row["Date of Death"]),
            "generation": int(row["Generation"]) if pd.notna(row["Generation"]) else 1,
            "father_name": display_value(row["Father Name"]),
            "mother_name": display_value(row["Mother Name"]),
            "spouse_name": display_value(row["Spouse Name"]),
            "source": "sheet",
        }
        persons[person_id] = person

        key = clean_name(person["name"])
        if key:
            # Keep the first exact name as canonical. Duplicate names are reported.
            if key in name_to_id and name_to_id[key] != person_id:
                validation_messages.append(
                    f"⚠️ Duplicate name found: '{person['name']}'. Relationship matching uses the first exact match."
                )
            else:
                name_to_id[key] = person_id

    def get_id_by_name(name):
        key = clean_name(name)
        if not key:
            return None
        return name_to_id.get(key)

    # Create inferred spouse nodes for names that do not have their own row.
    for person in list(persons.values()):
        spouse_name = person["spouse_name"]
        if not spouse_name:
            continue

        spouse_id = get_id_by_name(spouse_name)
        if spouse_id is None:
            synthetic_id = f"SYN-{len(persons) + 1}"
            while synthetic_id in persons:
                synthetic_id = f"SYN-{len(persons) + 1}"

            spouse = {
                "id": synthetic_id,
                "name": spouse_name,
                "gender": "Other",
                "dob": "",
                "age": None,
                "death": "",
                "generation": person["generation"],
                "father_name": "",
                "mother_name": "",
                "spouse_name": person["name"],
                "source": "inferred_spouse",
            }
            persons[synthetic_id] = spouse
            name_to_id[clean_name(spouse_name)] = synthetic_id
            validation_messages.append(
                f"ℹ️ Spouse '{spouse_name}' is displayed, but no separate spreadsheet row exists for them."
            )

    # Resolve spouse IDs for every person, including inferred spouse nodes.
    for person in persons.values():
        spouse_id = get_id_by_name(person["spouse_name"])
        person["spouse_id"] = spouse_id

    # Also resolve one-sided spouse data. For example, if Abhash lists Arpita
    # as spouse but Arpita's own row leaves Spouse Name blank, both still form
    # one couple in the visualization.
    for person_id, person in persons.items():
        if person.get("spouse_id"):
            continue
        referring_spouses = [
            other_id
            for other_id, other in persons.items()
            if other.get("spouse_id") == person_id and other_id != person_id
        ]
        if referring_spouses:
            person["spouse_id"] = referring_spouses[0]
            if not person.get("spouse_name"):
                person["spouse_name"] = persons[referring_spouses[0]]["name"]

    # Resolve parent IDs. Parent lookup is exact-first, fuzzy fallback only when needed.
    for person in persons.values():
        father_id = get_id_by_name(person["father_name"])
        mother_id = get_id_by_name(person["mother_name"])
        person["father_id"] = father_id
        person["mother_id"] = mother_id

        if person["father_name"] and father_id is None:
            validation_messages.append(
                f"⚠️ Father '{person['father_name']}' not found for {person['name']}"
            )
        if person["mother_name"] and mother_id is None:
            validation_messages.append(
                f"⚠️ Mother '{person['mother_name']}' not found for {person['name']}"
            )

    # Build unique couple/single units.
    unit_by_person = {}
    units = {}
    synthetic_counter = 1

    def make_unit_id(a_id, b_id=None):
        if b_id:
            return f"C-{min(a_id, b_id)}-{max(a_id, b_id)}"
        return f"P-{a_id}"

    for person_id, person in persons.items():
        spouse_id = person.get("spouse_id")
        if spouse_id and spouse_id in persons and spouse_id != person_id:
            unit_id = make_unit_id(person_id, spouse_id)
        else:
            unit_id = make_unit_id(person_id)

        if unit_id not in units:
            member_ids = [person_id]
            if spouse_id and spouse_id in persons and spouse_id != person_id:
                member_ids = [person_id, spouse_id]
            units[unit_id] = {
                "id": unit_id,
                "members": member_ids,
                "children": [],
                "parents": [],
                "generation": max(persons[mid]["generation"] for mid in member_ids),
            }

        unit_by_person[person_id] = unit_id

    # Second pass merges units if a spouse relationship points from the other side.
    # This also fixes cases where one row contains spouse and the spouse row exists.
    for person_id, person in persons.items():
        spouse_id = person.get("spouse_id")
        if not spouse_id or spouse_id not in persons or person_id == spouse_id:
            continue
        unit_id = make_unit_id(person_id, spouse_id)
        unit_by_person[person_id] = unit_id
        unit_by_person[spouse_id] = unit_id

        members = units[unit_id]["members"]
        if spouse_id not in members:
            members.append(spouse_id)
        units[unit_id]["members"] = list(dict.fromkeys(members))
        units[unit_id]["generation"] = max(persons[mid]["generation"] for mid in units[unit_id]["members"])

    # Rebuild units cleanly after the spouse merge.
    rebuilt_units = {}
    for person_id, unit_id in unit_by_person.items():
        if unit_id not in rebuilt_units:
            rebuilt_units[unit_id] = {
                "id": unit_id,
                "members": [],
                "children": [],
                "parents": [],
                "generation": persons[person_id]["generation"],
            }
        rebuilt_units[unit_id]["members"].append(person_id)
        rebuilt_units[unit_id]["generation"] = max(
            rebuilt_units[unit_id]["generation"], persons[person_id]["generation"]
        )

    units = rebuilt_units

    # Add parent -> child unit relationships for both partners.
    edge_keys = set()
    for person_id, person in persons.items():
        child_unit = unit_by_person.get(person_id)
        if not child_unit:
            continue

        for parent_id in (person.get("father_id"), person.get("mother_id")):
            if not parent_id or parent_id not in unit_by_person:
                continue
            parent_unit = unit_by_person[parent_id]
            if parent_unit == child_unit:
                continue
            edge_key = (parent_unit, child_unit)
            if edge_key not in edge_keys:
                edge_keys.add(edge_key)
                units[parent_unit]["children"].append(child_unit)
                units[child_unit]["parents"].append(parent_unit)

    # Deduplicate relationship arrays.
    for unit in units.values():
        unit["children"] = list(dict.fromkeys(unit["children"]))
        unit["parents"] = list(dict.fromkeys(unit["parents"]))

    # Clean synthetic spouses into a neutral presentation unless a real row exists.
    for person in persons.values():
        if person["source"] == "inferred_spouse":
            person["gender"] = "Other"

    model = {
        "persons": list(persons.values()),
        "units": list(units.values()),
    }
    return model


# ============================================================================
# D3 VISUALIZATION
# ============================================================================


def render_family_tree(model):
    """Render a self-contained D3 family tree inside Streamlit."""
    safe_json = json.dumps(model, ensure_ascii=False).replace("</", "<\\/")

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<style>
    html, body {{
        margin: 0;
        padding: 0;
        width: 100%;
        height: 100%;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        background: #f7f9fc;
        overflow: hidden;
    }}

    * {{ box-sizing: border-box; }}

    #app {{
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}

    #toolbar {{
        min-height: 58px;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 10px 12px;
        flex-wrap: wrap;
        z-index: 5;
    }}

    #toolbar input {{
        width: 260px;
        height: 36px;
        border: 1px solid #cbd5e1;
        border-radius: 8px;
        padding: 0 10px;
        font-size: 14px;
        outline: none;
    }}

    #toolbar button {{
        height: 36px;
        border: 1px solid #cbd5e1;
        background: white;
        border-radius: 8px;
        padding: 0 11px;
        cursor: pointer;
        font-size: 13px;
    }}

    #toolbar button:hover {{ background: #f1f5f9; }}

    #searchStatus {{
        font-size: 12px;
        color: #64748b;
        margin-left: 4px;
    }}

    #legend {{
        margin-left: auto;
        display: flex;
        align-items: center;
        gap: 11px;
        font-size: 12px;
        color: #475569;
    }}

    .legend-item {{ display: flex; align-items: center; gap: 4px; white-space: nowrap; }}
    .dot {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; border: 1px solid rgba(15,23,42,.15); }}

    #content {{
        flex: 1;
        min-height: 0;
        display: flex;
    }}

    #chartWrap {{
        flex: 1;
        min-width: 0;
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 1px 1px, rgba(148,163,184,.18) 1px, transparent 1px) 0 0 / 24px 24px,
            #f8fafc;
    }}

    #chart {{ width: 100%; height: 100%; cursor: grab; }}
    #chart:active {{ cursor: grabbing; }}

    #help {{
        position: absolute;
        bottom: 10px;
        left: 12px;
        background: rgba(255,255,255,.92);
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 6px 9px;
        font-size: 11px;
        color: #64748b;
        pointer-events: none;
    }}

    #details {{
        width: 300px;
        background: white;
        border-left: 1px solid #e2e8f0;
        padding: 16px;
        overflow-y: auto;
    }}

    #details h3 {{ margin: 0 0 8px; font-size: 19px; color: #0f172a; }}
    #details .muted {{ color: #64748b; font-size: 12px; margin-bottom: 12px; }}

    .detail-row {{
        display: flex;
        justify-content: space-between;
        gap: 12px;
        padding: 7px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 13px;
    }}
    .detail-label {{ color: #64748b; }}
    .detail-value {{ color: #0f172a; text-align: right; font-weight: 500; }}

    .node-card {{ cursor: pointer; }}
    .node-card rect {{ stroke-width: 1.5; }}
    .node-card:hover rect {{ stroke: #0f172a; stroke-width: 2; }}
    .node-name {{ font-size: 13px; font-weight: 700; fill: #0f172a; pointer-events: none; }}
    .node-meta {{ font-size: 11px; fill: #475569; pointer-events: none; }}

    .unit-label {{
        font-size: 10px;
        fill: #94a3b8;
        text-anchor: middle;
        pointer-events: none;
    }}

    .parent-edge {{
        fill: none;
        stroke: #94a3b8;
        stroke-width: 2.2;
        stroke-linecap: round;
        opacity: .72;
    }}

    .spouse-edge {{
        stroke: #f59e0b;
        stroke-width: 3;
        stroke-linecap: round;
    }}

    .relationship-dot {{ fill: #f59e0b; }}

    .dimmed {{ opacity: .12 !important; }}
    .highlighted rect {{ stroke: #0f172a !important; stroke-width: 3 !important; }}
    .highlighted .node-name {{ fill: #020617; }}

    @media (max-width: 900px) {{
        #details {{ width: 250px; }}
        #legend {{ display: none; }}
        #toolbar input {{ width: 210px; }}
    }}
</style>
</head>
<body>
<div id="app">
    <div id="toolbar">
        <input id="searchInput" list="nameList" placeholder="Search a family member..." autocomplete="off">
        <datalist id="nameList"></datalist>
        <button id="searchBtn">🔎 Find</button>
        <button id="fitBtn">⛶ Fit</button>
        <button id="zoomInBtn">＋ Zoom</button>
        <button id="zoomOutBtn">− Zoom</button>
        <button id="resetBtn">↺ Reset</button>
        <span id="searchStatus"></span>
        <div id="legend">
            <span class="legend-item"><span class="dot" style="background:#dff2ff"></span>Male</span>
            <span class="legend-item"><span class="dot" style="background:#ffe1ea"></span>Female</span>
            <span class="legend-item"><span class="dot" style="background:#eef2f7"></span>Details unavailable</span>
            <span class="legend-item">🟠 Spouse</span>
        </div>
    </div>
    <div id="content">
        <div id="chartWrap">
            <div id="chart"></div>
            <div id="help">Click a person to highlight their immediate family. Drag to pan • Wheel to zoom.</div>
        </div>
        <aside id="details">
            <h3>Family Tree</h3>
            <div class="muted">Select a person to see their details.</div>
        </aside>
    </div>
</div>

<script>
const model = {safe_json};
const persons = new Map(model.persons.map(p => [p.id, p]));
const units = new Map(model.units.map(u => [u.id, u]));
const personNames = [...model.persons]
    .filter(p => p.source === 'sheet')
    .sort((a,b) => a.name.localeCompare(b.name));

const searchInput = document.getElementById('searchInput');
const searchStatus = document.getElementById('searchStatus');
const nameList = document.getElementById('nameList');
personNames.forEach(p => {{
    const option = document.createElement('option');
    option.value = p.name;
    nameList.appendChild(option);
}});

const chartWrap = document.getElementById('chartWrap');
const chartEl = document.getElementById('chart');
const detailsEl = document.getElementById('details');

const CARD_W = 174;
const CARD_H = 96;
const COUPLE_GAP = 28;
const ROW_GAP = 180;
const SIDE_PAD = 100;
const TOP_PAD = 85;
const MIN_ROW_GAP = 70;

function unitWidth(unit) {{
    return unit.members.length > 1 ? CARD_W * 2 + COUPLE_GAP : CARD_W;
}}

function unitCenterX(unit) {{
    return unit._x + unitWidth(unit) / 2;
}}

function personColor(person) {{
    if (person.gender === 'Male') return '#dff2ff';
    if (person.gender === 'Female') return '#ffe1ea';
    return '#eef2f7';
}}

function buildLayout() {{
    const groups = d3.group([...units.values()], d => d.generation);
    const generationValues = [...groups.keys()].sort((a,b) => b - a);
    const positions = new Map();
    let maxUnits = 1;

    // Position each generation on its own row. Higher generation number is
    // displayed above lower generation numbers, matching the supplied sheet.
    generationValues.forEach((generation, rowIndex) => {{
        const rowUnits = groups.get(generation);
        maxUnits = Math.max(maxUnits, rowUnits.length);

        rowUnits.sort((a,b) => a.id.localeCompare(b.id));
        const rowWidth = rowUnits.reduce((sum,u) => sum + unitWidth(u), 0)
            + Math.max(0, rowUnits.length - 1) * 90;

        let cursor = Math.max(SIDE_PAD, (maxUnits * 300 - rowWidth) / 2);
        rowUnits.forEach(u => {{
            const w = unitWidth(u);
            u._x = cursor;
            u._y = TOP_PAD + rowIndex * (CARD_H + ROW_GAP);
            positions.set(u.id, {{x: u._x, y: u._y}});
            cursor += w + 90;
        }});
    }});

    // A lightweight second pass orders each row around the average x-position
    // of its already-positioned parent units to reduce crossing lines.
    generationValues.forEach(generation => {{
        const rowUnits = groups.get(generation);
        rowUnits.forEach(u => {{
            if (!u.parents.length) return;
            const parentCenters = u.parents
                .filter(id => units.has(id))
                .map(id => unitCenterX(units.get(id)));
            if (!parentCenters.length) return;
            u._target = d3.mean(parentCenters);
        }});
        const ordered = rowUnits.slice().sort((a,b) =>
            (a._target ?? unitCenterX(a)) - (b._target ?? unitCenterX(b))
        );
        let cursor = SIDE_PAD;
        ordered.forEach(u => {{
            u._x = Math.max(cursor, (u._target ?? cursor) - unitWidth(u) / 2);
            cursor = u._x + unitWidth(u) + 90;
        }});
    }});

    const contentRight = d3.max([...units.values()].map(u => u._x + unitWidth(u))) || 1200;
    const totalW = Math.max(chartWrap.clientWidth, contentRight + SIDE_PAD, 1200);
    const totalH = Math.max(chartWrap.clientHeight, generationValues.length * (CARD_H + ROW_GAP) + TOP_PAD * 2);
    return {{width: totalW, height: totalH, generations: generationValues}};
}}

const svg = d3.select(chartEl).append('svg');
const viewport = svg.append('g').attr('class','viewport');
const edgesLayer = viewport.append('g').attr('class','edges');
const nodesLayer = viewport.append('g').attr('class','nodes');

const zoom = d3.zoom()
    .scaleExtent([0.25, 2.5])
    .on('zoom', (event) => viewport.attr('transform', event.transform));
svg.call(zoom);

function bezierPath(parent, child) {{
    const sx = unitCenterX(parent);
    const sy = parent._y + CARD_H;
    const tx = unitCenterX(child);
    const ty = child._y;
    const midY = sy + (ty - sy) * 0.5;
    return `M ${{sx}} ${{sy}} C ${{sx}} ${{midY}}, ${{tx}} ${{midY}}, ${{tx}} ${{ty}}`;
}}

function showDetails(personId) {{
    const person = persons.get(personId);
    if (!person) return;

    const spouse = person.spouse_id ? persons.get(person.spouse_id) : null;
    const unit = [...units.values()].find(u => u.members.includes(personId));
    const parents = [];
    [person.father_id, person.mother_id].forEach(id => {{
        if (id && persons.has(id)) parents.push(persons.get(id).name);
    }});

    const rows = [
        ['Gender', person.gender],
        ['Age', person.age != null ? person.age + ' years' : '—'],
        ['Date of Birth', person.dob || '—'],
        ['Date of Death', person.death || '—'],
        ['Generation', person.generation ?? '—'],
        ['Father', person.father_name || '—'],
        ['Mother', person.mother_name || '—'],
        ['Spouse', spouse ? spouse.name : (person.spouse_name || '—')],
    ];

    let extra = '';
    if (person.source === 'inferred_spouse') {{
        extra = `<div style="margin-top:12px;padding:9px;background:#fff7ed;border-left:4px solid #f59e0b;border-radius:6px;font-size:12px;color:#9a3412;">Spouse name was found in another person's row, but this person's own record is not in the spreadsheet.</div>`;
    }}

    detailsEl.innerHTML = `
        <h3>${{escapeHtml(person.name)}}</h3>
        <div class="muted">${{person.gender === 'Other' ? 'Details partially available' : 'Family member'}}</div>
        ${{rows.map(r => `<div class="detail-row"><span class="detail-label">${{escapeHtml(r[0])}}</span><span class="detail-value">${{escapeHtml(String(r[1]))}}</span></div>`).join('')}}
        ${{parents.length ? `<div style="margin-top:14px;font-size:12px;color:#64748b;">Parents</div><div style="margin-top:5px;font-size:13px;line-height:1.5;">${{parents.map(escapeHtml).join('<br>')}}</div>` : ''}}
        ${{extra}}
    `;
}}

function escapeHtml(value) {{
    return String(value)
        .replaceAll('&', '&amp;')
        .replaceAll('<', '&lt;')
        .replaceAll('>', '&gt;')
        .replaceAll('"', '&quot;')
        .replaceAll("'", '&#039;');
}}

let selectedPersonId = null;

function relatedUnitIds(personId) {{
    const related = new Set();
    const unit = [...units.values()].find(u => u.members.includes(personId));
    if (!unit) return related;
    related.add(unit.id);
    unit.parents.forEach(id => related.add(id));
    unit.children.forEach(id => related.add(id));

    // Also highlight siblings sharing a parent unit.
    unit.parents.forEach(parentId => {{
        const parent = units.get(parentId);
        if (parent) parent.children.forEach(childId => related.add(childId));
    }});

    return related;
}}

function applyHighlight(personId) {{
    selectedPersonId = personId;
    const related = relatedUnitIds(personId);

    nodesLayer.selectAll('.family-unit')
        .classed('dimmed', d => !related.has(d.id))
        .classed('highlighted', d => d.members.includes(personId));

    edgesLayer.selectAll('.parent-edge')
        .classed('dimmed', d => !related.has(d.source) || !related.has(d.target));

    edgesLayer.selectAll('.spouse-edge-group')
        .classed('dimmed', d => !related.has(d.id));

    showDetails(personId);
}}

function draw() {{
    const layout = buildLayout();
    svg.attr('width', layout.width).attr('height', layout.height);

    // Parent-child edges.
    const edgeData = [];
    units.forEach(u => {{
        u.children.forEach(childId => {{
            if (units.has(childId)) edgeData.push({{source: u.id, target: childId}});
        }});
    }});

    edgesLayer.selectAll('*').remove();

    edgesLayer.selectAll('.parent-edge')
        .data(edgeData)
        .enter()
        .append('path')
        .attr('class','parent-edge')
        .attr('d', d => bezierPath(units.get(d.source), units.get(d.target)));

    const spouseGroups = edgesLayer.selectAll('.spouse-edge-group')
        .data([...units.values()].filter(u => u.members.length > 1))
        .enter()
        .append('g')
        .attr('class','spouse-edge-group');

    spouseGroups.each(function(u) {{
        const g = d3.select(this);
        const leftX = u._x + CARD_W;
        const rightX = u._x + CARD_W + COUPLE_GAP;
        const y = u._y + CARD_H / 2;
        g.append('line')
            .attr('class','spouse-edge')
            .attr('x1', leftX)
            .attr('x2', rightX)
            .attr('y1', y)
            .attr('y2', y);
        g.append('circle').attr('class','relationship-dot')
            .attr('cx', (leftX + rightX)/2)
            .attr('cy', y)
            .attr('r', 4);
        g.append('text')
            .attr('x', (leftX + rightX)/2)
            .attr('y', y - 9)
            .attr('text-anchor','middle')
            .attr('font-size', 12)
            .text('❤');
    }});

    nodesLayer.selectAll('*').remove();

    const generationLabels = d3.group([...units.values()], d => d.generation);
    generationLabels.forEach((rowUnits, generation) => {{
        const y = rowUnits[0]?._y ?? TOP_PAD;
        nodesLayer.append('text')
            .attr('class','unit-label')
            .attr('x', 38)
            .attr('y', y + 5)
            .attr('text-anchor','start')
            .text('Gen ' + generation);
    }});

    [...units.values()].forEach(unit => {{
        const unitGroup = nodesLayer.append('g')
            .attr('class','family-unit')
            .datum(unit);

        unit.members.forEach((personId, memberIndex) => {{
            const person = persons.get(personId);
            const x = unit._x + memberIndex * (CARD_W + COUPLE_GAP);
            const y = unit._y;

            const card = unitGroup.append('g')
                .attr('class','node-card')
                .attr('transform', `translate(${{x}},${{y}})`)
                .on('click', function(event) {{
                    event.stopPropagation();
                    applyHighlight(person.id);
                    const scale = 1.0;
                    const centerX = x + CARD_W / 2;
                    const centerY = y + CARD_H / 2;
                    const w = chartWrap.clientWidth;
                    const h = chartWrap.clientHeight;
                    const tx = w / 2 - centerX * scale;
                    const ty = h / 2 - centerY * scale;
                    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
                }});

            card.append('rect')
                .attr('width', CARD_W)
                .attr('height', CARD_H)
                .attr('rx', 13)
                .attr('fill', personColor(person))
                .attr('stroke', person.source === 'inferred_spouse' ? '#cbd5e1' : '#94a3b8')
                .attr('stroke-dasharray', person.source === 'inferred_spouse' ? '5 4' : '0')
                .attr('opacity', person.death ? 0.62 : 1);

            const icon = person.gender === 'Male' ? '👨' : person.gender === 'Female' ? '👩' : '👤';
            card.append('text')
                .attr('x', 12).attr('y', 21)
                .attr('font-size', 15).text(icon);

            const nameLines = wrapText(person.name, 20);
            nameLines.slice(0,2).forEach((line, i) => {{
                card.append('text')
                    .attr('class','node-name')
                    .attr('x', 34)
                    .attr('y', 20 + i*16)
                    .text(line);
            }});

            const meta = [];
            if (person.age != null) meta.push(person.age + ' yrs');
            if (person.dob) meta.push('DOB ' + person.dob);
            if (person.death) meta.push('Deceased');
            if (person.source === 'inferred_spouse') meta.push('Details not in sheet');

            meta.slice(0,2).forEach((line, i) => {{
                card.append('text')
                    .attr('class','node-meta')
                    .attr('x', 12)
                    .attr('y', 58 + i*15)
                    .text(line);
            }});
        }});
    }});

    // Auto-fit after the chart is drawn.
    requestAnimationFrame(fitToScreen);
}}

function wrapText(text, maxChars) {{
    const words = String(text).split(/\\s+/);
    const lines = [];
    let current = '';
    words.forEach(word => {{
        const candidate = current ? current + ' ' + word : word;
        if (candidate.length <= maxChars || !current) current = candidate;
        else {{ lines.push(current); current = word; }}
    }});
    if (current) lines.push(current);
    return lines.length ? lines : [''];
}}

function fitToScreen() {{
    const bbox = viewport.node().getBBox();
    if (!bbox.width || !bbox.height) return;
    const w = chartWrap.clientWidth;
    const h = chartWrap.clientHeight;
    const scale = Math.min((w - 40) / bbox.width, (h - 40) / bbox.height, 1.15);
    const tx = (w - bbox.width * scale) / 2 - bbox.x * scale;
    const ty = (h - bbox.height * scale) / 2 - bbox.y * scale;
    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}}

function findPerson() {{
    const wanted = searchInput.value.trim().toLowerCase();
    if (!wanted) return;

    const match = personNames.find(p => p.name.toLowerCase() === wanted)
        || personNames.find(p => p.name.toLowerCase().includes(wanted));

    if (!match) {{
        searchStatus.textContent = 'No match';
        return;
    }}

    searchStatus.textContent = match.name;
    applyHighlight(match.id);

    const unit = [...units.values()].find(u => u.members.includes(match.id));
    if (!unit) return;

    const scale = 1.0;
    const centerX = unitCenterX(unit);
    const centerY = unit._y + CARD_H / 2;
    const tx = chartWrap.clientWidth / 2 - centerX * scale;
    const ty = chartWrap.clientHeight / 2 - centerY * scale;
    svg.transition().duration(600).call(zoom.transform, d3.zoomIdentity.translate(tx, ty).scale(scale));
}}

document.getElementById('searchBtn').addEventListener('click', findPerson);
searchInput.addEventListener('keydown', event => {{ if (event.key === 'Enter') findPerson(); }});
document.getElementById('fitBtn').addEventListener('click', fitToScreen);
document.getElementById('zoomInBtn').addEventListener('click', () => svg.transition().call(zoom.scaleBy, 1.25));
document.getElementById('zoomOutBtn').addEventListener('click', () => svg.transition().call(zoom.scaleBy, 0.8));
document.getElementById('resetBtn').addEventListener('click', () => {{
    selectedPersonId = null;
    nodesLayer.selectAll('.family-unit').classed('dimmed', false).classed('highlighted', false);
    edgesLayer.selectAll('.parent-edge, .spouse-edge-group').classed('dimmed', false);
    searchStatus.textContent = '';
    detailsEl.innerHTML = '<h3>Family Tree</h3><div class="muted">Select a person to see their details.</div>';
    fitToScreen();
}});

chartWrap.addEventListener('dblclick', () => fitToScreen());

window.addEventListener('resize', () => fitToScreen());

draw();
</script>
</body>
</html>
"""

    st.components.v1.html(html, height=820, scrolling=False)


# ============================================================================
# MAIN UI
# ============================================================================

st.markdown(
    "<h1 style='text-align:center;color:#1f77b4;'>🌳 Family Tree</h1>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### 🌳 Tree Controls")
    st.caption("The chart is interactive: search, click, zoom and pan.")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.rerun()

    st.markdown("---")
    st.markdown("### ℹ️ Legend")
    st.markdown("🔵 Blue card = Male")
    st.markdown("🌸 Pink card = Female")
    st.markdown("⚪ Neutral dashed card = spouse details not found as a separate row")
    st.markdown("🟠 Orange line = Spouse")
    st.markdown("⚰️ Faded card = Deceased")

    st.markdown("---")
    st.markdown("### 🔄 Data")
    st.caption("Google Sheet data is cached for 5 minutes.")
    if st.button("Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Load data.
with st.spinner("📊 Loading family data..."):
    family_data = load_family_data()

if family_data is None:
    st.stop()

# Statistics.
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("👥 Total Members", len(family_data))
with col2:
    st.metric("👨 Males", int((family_data["Gender"] == "Male").sum()))
with col3:
    st.metric("👩 Females", int((family_data["Gender"] == "Female").sum()))
with col4:
    st.metric("⚰️ Deceased", int(family_data["Date of Death"].notna().sum()))
with col5:
    generations = sorted(family_data["Generation"].dropna().astype(int).unique().tolist())
    st.metric("🌿 Generations", len(generations))

st.markdown("---")

# Generate the relationship model.
validation_messages = []
with st.spinner("🔄 Building family tree..."):
    family_model = resolve_family_model(family_data, validation_messages)

if validation_messages:
    with st.expander("⚠️ Data / Relationship Notes", expanded=False):
        for message in validation_messages:
            if message.startswith("⚠️"):
                st.warning(message)
            else:
                st.info(message)

# Inform the user about inferred spouse nodes.
inferred_spouses = [
    p for p in family_model["persons"] if p.get("source") == "inferred_spouse"
]
if inferred_spouses:
    names = ", ".join(p["name"] for p in inferred_spouses[:8])
    suffix = " ..." if len(inferred_spouses) > 8 else ""
    st.markdown(
        f"<div class='tree-info'>💡 <b>Spouses shown from the Spouse Name column:</b> {names}{suffix}. "
        "They are displayed even when their own spreadsheet row is missing.</div>",
        unsafe_allow_html=True,
    )

render_family_tree(family_model)


# ============================================================================
# DATA TABLE VIEW
# ============================================================================

st.markdown("---")
with st.expander("📋 View Family Data"):
    display_df = family_data.copy()
    display_df["Date of Birth"] = display_df["Date of Birth"].apply(format_date)
    display_df["Date of Death"] = display_df["Date of Death"].apply(format_date)
    display_df["Age"] = display_df["Age"].apply(
        lambda value: f"{int(value)}" if pd.notna(value) else ""
    )
    display_df["Generation"] = display_df["Generation"].apply(
        lambda value: int(value) if pd.notna(value) else ""
    )

    display_columns = [
        "Unique_ID",
        "Name",
        "Generation",
        "Gender",
        "Age",
        "Date of Birth",
        "Father Name",
        "Mother Name",
        "Spouse Name",
        "Date of Death",
    ]
    display_columns = [col for col in display_columns if col in display_df.columns]

    st.dataframe(
        display_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )


# ============================================================================
# FOOTER
# ============================================================================

st.markdown(
    f"""
    <div style='text-align:center;color:#64748b;font-size:12px;margin-top:16px;'>
        🌳 Family Tree App • Last page refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        Google Sheet data refreshes every 5 minutes.
    </div>
    """,
    unsafe_allow_html=True,
)
