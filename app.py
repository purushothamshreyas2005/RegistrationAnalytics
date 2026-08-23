import streamlit as st
import pandas as pd
import io
import re
import html
import streamlit.components.v1 as components


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Registration Analytics",
    page_icon="📊",
    layout="wide"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.main {
    background-color: #f7f8fa;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

.title {
    font-size: 32px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 5px;
}

.subtitle {
    text-align: center;
    color: #666;
    margin-bottom: 30px;
}

.section-title {
    font-size: 21px;
    font-weight: 650;
    margin-top: 28px;
    margin-bottom: 15px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

.copy-box {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DEFAULT PREMIUM EVENTS
# =========================================================

DEFAULT_PREMIUM_EVENTS = [
    "VINHACK",
    "DevJams'26",
    "CADEX",
    "Hackbattle",
    "Code Cortex 3.0",
    "Cicada 2067",
    "The Grand GraVITas Quiz",
    "Dream Team 8.0",
    "WE Hack 5.0",
    "Code2Create 7.0",
    "Startup Street 11",
    "SENSORA 2.0",
    "SAE GRAND PRIX",
    "Quadcopter",
    "BlockPitch 2026 – Blockchain Innovation Challenge",
    "SAE-Drone Racing League (DRL)"
]


# =========================================================
# DEFAULT PRO EVENTS
# =========================================================

DEFAULT_PRO_EVENTS = [
    "Capital Hunt 2.0",
    "Capital Hunt 2.0 - Freshminds"
]


# =========================================================
# SESSION STATE
# =========================================================

if "premium_events_list" not in st.session_state:
    st.session_state.premium_events_list = (
        DEFAULT_PREMIUM_EVENTS.copy()
    )

if "pro_events_list" not in st.session_state:
    st.session_state.pro_events_list = (
        DEFAULT_PRO_EVENTS.copy()
    )


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    # Normalize different dash characters
    value = (
        value
        .replace("–", "-")
        .replace("—", "-")
    )

    # Normalize multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value


# =========================================================
# NORMALIZE COLUMN NAME
# =========================================================

def normalize_column_name(column):

    column = str(column).strip().lower()

    column = re.sub(
        r"[^a-z0-9]+",
        " ",
        column
    )

    column = re.sub(
        r"\s+",
        " ",
        column
    ).strip()

    return column


# =========================================================
# FIND COLUMN
# =========================================================

def find_column(df, possible_names):

    normalized_columns = {
        normalize_column_name(col): col
        for col in df.columns
    }

    # Exact normalized match
    for name in possible_names:

        normalized_name = normalize_column_name(name)

        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    # Flexible matching
    for normalized_col, original_col in normalized_columns.items():

        for name in possible_names:

            normalized_name = normalize_column_name(name)

            if normalized_name in normalized_col:
                return original_col

    return None


# =========================================================
# LOAD FILE
# =========================================================

def load_file(uploaded_file):

    if uploaded_file is None:
        return None

    filename = uploaded_file.name.lower()

    try:

        if filename.endswith(".csv"):

            return pd.read_csv(uploaded_file)

        elif filename.endswith(".xlsx"):

            return pd.read_excel(uploaded_file)

        elif filename.endswith(".xls"):

            return pd.read_excel(uploaded_file)

        else:

            st.error(
                "Unsupported file format."
            )

            return None

    except Exception as e:

        st.error(
            f"Could not read file: {e}"
        )

        return None


# =========================================================
# PREPARE REGISTRATION DATA
# =========================================================

def prepare_data(df, source):

    if df is None:
        return None

    df = df.copy()

    # =====================================================
    # FIND REQUIRED COLUMNS
    # =====================================================

    event_col = find_column(
        df,
        [
            "Event Name",
            "Event",
            "EventName"
        ]
    )

    participant_col = find_column(
        df,
        [
            "No. of Participants",
            "No of Participants",
            "Number of Participants",
            "Participants",
            "Participant Count",
            "No Participants"
        ]
    )

    payment_col = find_column(
        df,
        [
            "Payment Status",
            "PaymentStatus",
            "Payment",
            "Status"
        ]
    )

    amount_col = find_column(
        df,
        [
            "Amount",
            "Payment Amount",
            "Registration Amount",
            "Fee"
        ]
    )

    # =====================================================
    # VALIDATE
    # =====================================================

    missing = []

    if event_col is None:
        missing.append("Event Name")

    if participant_col is None:
        missing.append("No. of Participants")

    if payment_col is None:
        missing.append("Payment Status")

    if amount_col is None:
        missing.append("Amount")

    if missing:

        st.error(
            f"{source} file is missing required "
            f"column(s): " + ", ".join(missing)
        )

        st.info(
            "Required fields: Event Name, "
            "No. of Participants, Payment Status "
            "and Amount."
        )

        return None

    # =====================================================
    # STANDARDIZE DATA
    # =====================================================

    data = pd.DataFrame()

    # Normalized event name for matching
    data["Event Name"] = (
        df[event_col]
        .apply(normalize_text)
    )

    # Original event name for display
    data["Display Event Name"] = (
        df[event_col]
        .astype(str)
        .str.strip()
    )

    # Participant count
    data["Participants"] = pd.to_numeric(
        df[participant_col],
        errors="coerce"
    ).fillna(0)

    # Amount
    data["Amount"] = (
        df[amount_col]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.strip()
    )

    data["Amount"] = pd.to_numeric(
        data["Amount"],
        errors="coerce"
    ).fillna(0)

    # Payment status
    data["Payment Status"] = (
        df[payment_col]
        .apply(normalize_text)
    )

    # Source
    data["Source"] = source

    # Remove blank event rows
    data = data[
        data["Event Name"].str.strip() != ""
    ].copy()

    return data


# =========================================================
# CALCULATE SUMMARY
# =========================================================

def calculate_summary(data):

    if data is None or data.empty:

        return {
            "total": 0,
            "paid": 0,
            "free": 0,
            "revenue": 0
        }

    # Total registrations
    total = data["Participants"].sum()

    # Paid registrations
    paid = data.loc[
        data["Payment Status"] == "paid",
        "Participants"
    ].sum()

    # Free registrations
    free = data.loc[
        data["Amount"] == 0,
        "Participants"
    ].sum()

    # Revenue
    revenue = data.loc[
        data["Payment Status"] == "paid",
        "Amount"
    ].sum()

    return {
        "total": int(total),
        "paid": int(paid),
        "free": int(free),
        "revenue": float(revenue)
    }


# =========================================================
# CLEAN EVENT LIST
# =========================================================

def clean_event_list(values):

    cleaned = []

    for value in values:

        normalized = normalize_text(value)

        if (
            normalized
            and normalized not in cleaned
        ):
            cleaned.append(normalized)

    return cleaned


# =========================================================
# GET EVENT CATEGORY
# =========================================================

def get_event_category(event_name):

    event = normalize_text(event_name)

    premium_events = clean_event_list(
        st.session_state["premium_events_list"]
    )

    pro_events = clean_event_list(
        st.session_state["pro_events_list"]
    )

    # Pro gets highest priority
    if event in pro_events:
        return "Pro Event"

    # Premium
    if event in premium_events:
        return "Premium Event"

    # Everything else
    return "Event"


# =========================================================
# GENERATE EVENT REPORT
# =========================================================

def generate_event_report(
    internal_data,
    external_data
):

    # -----------------------------------------------------
    # GET ALL UNIQUE EVENTS
    # -----------------------------------------------------

    all_events = set()

    if internal_data is not None:

        all_events.update(
            internal_data["Event Name"].unique()
        )

    if external_data is not None:

        all_events.update(
            external_data["Event Name"].unique()
        )

    rows = []

    # =====================================================
    # PROCESS EVERY EVENT
    # =====================================================

    for event in sorted(all_events):

        # =================================================
        # INTERNAL
        # =================================================

        if internal_data is not None:

            internal_event = internal_data[
                internal_data["Event Name"] == event
            ]

            internal_total = internal_event[
                "Participants"
            ].sum()

            internal_paid = internal_event.loc[
                internal_event["Payment Status"] == "paid",
                "Participants"
            ].sum()

            display_name = (
                internal_event[
                    "Display Event Name"
                ].iloc[0]
                if not internal_event.empty
                else None
            )

        else:

            internal_event = pd.DataFrame()

            internal_total = 0

            internal_paid = 0

            display_name = None

        # =================================================
        # EXTERNAL
        # =================================================

        if external_data is not None:

            external_event = external_data[
                external_data["Event Name"] == event
            ]

            external_total = external_event[
                "Participants"
            ].sum()

            external_paid = external_event.loc[
                external_event["Payment Status"] == "paid",
                "Participants"
            ].sum()

            if (
                display_name is None
                and not external_event.empty
            ):

                display_name = (
                    external_event[
                        "Display Event Name"
                    ].iloc[0]
                )

        else:

            external_event = pd.DataFrame()

            external_total = 0

            external_paid = 0

        # =================================================
        # EVENT TYPE: PAID / FREE
        # =================================================

        internal_amount = (
            internal_event["Amount"].sum()
            if not internal_event.empty
            else 0
        )

        external_amount = (
            external_event["Amount"].sum()
            if not external_event.empty
            else 0
        )

        total_event_amount = (
            internal_amount
            + external_amount
        )

        if total_event_amount == 0:
            event_type = "Free"
        else:
            event_type = "Paid"

        # =================================================
        # EVENT CATEGORY
        # =================================================

        event_category = get_event_category(
            display_name
        )

        # =================================================
        # TOTALS
        # =================================================

        total_paid = (
            internal_paid
            + external_paid
        )

        total_regs = (
            internal_total
            + external_total
        )

        rows.append({

            "Event Name":
                display_name,

            "Category":
                event_category,

            "Type of Event":
                event_type,

            "Internal Paid":
                int(internal_paid),

            "Internal Regs":
                int(internal_total),

            "External Paid":
                int(external_paid),

            "External Regs":
                int(external_total),

            "Total Paid":
                int(total_paid),

            "Total Regs":
                int(total_regs)
        })

    return pd.DataFrame(rows)


# =========================================================
# COPY TEXT BUTTON
# =========================================================

def copy_text_button(text):

    # Escape text so it is safe inside the HTML textarea
    escaped_text = html.escape(text)

    html_code = """
    <div style="
        font-family: Arial, sans-serif;
        width: 100%;
    ">

        <textarea
            id="copyText"
            style="
                width: 100%;
                height: 230px;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
                resize: vertical;
                box-sizing: border-box;
            "
        >TEXT_PLACEHOLDER</textarea>

        <button
            onclick="copyText()"
            style="
                margin-top: 10px;
                width: 100%;
                padding: 11px;
                border: none;
                border-radius: 8px;
                background: #0066ff;
                color: white;
                font-size: 15px;
                font-weight: 600;
                cursor: pointer;
            "
        >
            📋 Copy Summary Text
        </button>

        <div
            id="message"
            style="
                text-align: center;
                margin-top: 8px;
                color: #16a34a;
                font-size: 13px;
            "
        ></div>

        <script>

        function copyText() {

            const textarea =
                document.getElementById("copyText");

            navigator.clipboard.writeText(
                textarea.value
            ).then(function() {

                document.getElementById(
                    "message"
                ).innerText =
                    "Copied to clipboard!";

            }).catch(function() {

                textarea.select();

                document.execCommand("copy");

                document.getElementById(
                    "message"
                ).innerText =
                    "Copied to clipboard!";

            });
        }

        </script>

    </div>
    """

    html_code = html_code.replace(
        "TEXT_PLACEHOLDER",
        escaped_text
    )

    components.html(
        html_code,
        height=330
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="title">'
    'Registration Analytics'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Internal + External Event Registration Report'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# EVENT CATEGORY MANAGEMENT
# =========================================================

with st.expander(
    "⚙️ Manage Event Categories"
):

    st.write(
        "Edit the Premium and Pro event lists below. "
        "Enter one event per line. Matching is "
        "case-insensitive. Anything not present in "
        "either list automatically becomes a normal Event."
    )

    cat1, cat2 = st.columns(2)

    # =====================================================
    # PREMIUM EVENTS
    # =====================================================

    with cat1:

        premium_text = st.text_area(
            "Premium Events",
            value="\n".join(
                st.session_state[
                    "premium_events_list"
                ]
            ),
            height=320,
            key="premium_editor"
        )

    # =====================================================
    # PRO EVENTS
    # =====================================================

    with cat2:

        pro_text = st.text_area(
            "Pro Events",
            value="\n".join(
                st.session_state[
                    "pro_events_list"
                ]
            ),
            height=320,
            key="pro_editor"
        )

    if st.button(
        "Save Event Lists",
        type="primary"
    ):

        st.session_state[
            "premium_events_list"
        ] = [
            x.strip()
            for x in premium_text.splitlines()
            if x.strip()
        ]

        st.session_state[
            "pro_events_list"
        ] = [
            x.strip()
            for x in pro_text.splitlines()
            if x.strip()
        ]

        st.success(
            "Event category lists updated."
        )


# =========================================================
# FILE UPLOAD
# =========================================================

st.markdown(
    '<div class="section-title">'
    'Upload Registration Files'
    '</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)


# =========================================================
# INTERNAL FILE
# =========================================================

with col1:

    st.subheader(
        "Internal Registrations"
    )

    internal_file = st.file_uploader(
        "Upload Internal Excel / CSV",
        type=[
            "xlsx",
            "xls",
            "csv"
        ],
        key="internal"
    )


# =========================================================
# EXTERNAL FILE
# =========================================================

with col2:

    st.subheader(
        "External Registrations"
    )

    external_file = st.file_uploader(
        "Upload External Excel / CSV",
        type=[
            "xlsx",
            "xls",
            "csv"
        ],
        key="external"
    )


# =========================================================
# GENERATE REPORT BUTTON
# =========================================================

st.write("")

generate = st.button(
    "Generate Report",
    type="primary",
    use_container_width=True
)


# =========================================================
# PROCESS FILES
# =========================================================

if generate:

    if internal_file is None:

        st.error(
            "Please upload the Internal Registrations file."
        )

    elif external_file is None:

        st.error(
            "Please upload the External Registrations file."
        )

    else:

        internal_raw = load_file(
            internal_file
        )

        external_raw = load_file(
            external_file
        )

        internal_data = prepare_data(
            internal_raw,
            "Internal"
        )

        external_data = prepare_data(
            external_raw,
            "External"
        )

        if (
            internal_data is not None
            and external_data is not None
        ):

            st.session_state[
                "internal_data"
            ] = internal_data

            st.session_state[
                "external_data"
            ] = external_data

            st.success(
                "Files processed successfully."
            )


# =========================================================
# DISPLAY REPORT
# =========================================================

if (
    "internal_data" in st.session_state
    and "external_data" in st.session_state
):

    internal_data = st.session_state[
        "internal_data"
    ]

    external_data = st.session_state[
        "external_data"
    ]


    # =====================================================
    # INTERNAL SUMMARY
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Internal Registrations'
        '</div>',
        unsafe_allow_html=True
    )

    internal_summary = calculate_summary(
        internal_data
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Registrations",
        f"{internal_summary['total']:,}"
    )

    c2.metric(
        "Paid Registrations",
        f"{internal_summary['paid']:,}"
    )

    c3.metric(
        "Free Registrations",
        f"{internal_summary['free']:,}"
    )

    c4.metric(
        "Revenue Generated",
        f"₹{internal_summary['revenue']:,.2f}"
    )


    # =====================================================
    # EXTERNAL SUMMARY
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'External Registrations'
        '</div>',
        unsafe_allow_html=True
    )

    external_summary = calculate_summary(
        external_data
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Registrations",
        f"{external_summary['total']:,}"
    )

    c2.metric(
        "Paid Registrations",
        f"{external_summary['paid']:,}"
    )

    c3.metric(
        "Free Registrations",
        f"{external_summary['free']:,}"
    )

    c4.metric(
        "Revenue Generated",
        f"₹{external_summary['revenue']:,.2f}"
    )


    # =====================================================
    # OVERALL SUMMARY
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Overall'
        '</div>',
        unsafe_allow_html=True
    )

    overall_total = (
        internal_summary["total"]
        + external_summary["total"]
    )

    overall_paid = (
        internal_summary["paid"]
        + external_summary["paid"]
    )

    overall_free = (
        internal_summary["free"]
        + external_summary["free"]
    )

    overall_revenue = (
        internal_summary["revenue"]
        + external_summary["revenue"]
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Registrations",
        f"{overall_total:,}"
    )

    c2.metric(
        "Paid Registrations",
        f"{overall_paid:,}"
    )

    c3.metric(
        "Free Registrations",
        f"{overall_free:,}"
    )

    c4.metric(
        "Revenue Generated",
        f"₹{overall_revenue:,.2f}"
    )


    # =====================================================
    # COPY SUMMARY TEXT
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Copy Summary'
        '</div>',
        unsafe_allow_html=True
    )

    # EVERY FIELD IS ON A NEW LINE

    summary_text = (
        "INTERNAL EVENT\n"
        f"Total regs = {internal_summary['total']:,}\n"
        f"Paid regs = {internal_summary['paid']:,}\n"
        f"Free regs = {internal_summary['free']:,}\n"
        f"Revenue = ₹{internal_summary['revenue']:,.2f}\n"
        "\n"
        "EXTERNAL EVENT\n"
        f"Total regs = {external_summary['total']:,}\n"
        f"Paid regs = {external_summary['paid']:,}\n"
        f"Free regs = {external_summary['free']:,}\n"
        f"Revenue = ₹{external_summary['revenue']:,.2f}\n"
        "\n"
        "TOTAL\n"
        f"Total regs = {overall_total:,}\n"
        f"Paid regs = {overall_paid:,}\n"
        f"Free regs = {overall_free:,}\n"
        f"Revenue = ₹{overall_revenue:,.2f}"
    )

    copy_text_button(
        summary_text
    )


    # =====================================================
    # EVENT-WISE REPORT
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Event-wise Report'
        '</div>',
        unsafe_allow_html=True
    )

    event_report = generate_event_report(
        internal_data,
        external_data
    )

    st.dataframe(
        event_report,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # EVENT SEARCH
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Search Event'
        '</div>',
        unsafe_allow_html=True
    )

    search_col, button_col = st.columns(
        [5, 1]
    )

    with search_col:

        search_event = st.text_input(
            "Search",
            placeholder="Enter event name...",
            label_visibility="collapsed"
        )

    with button_col:

        search_clicked = st.button(
            "Search",
            use_container_width=True
        )


    # =====================================================
    # SEARCH RESULT
    # =====================================================

    if search_clicked:

        search_value = normalize_text(
            search_event
        )

        if search_value == "":

            st.warning(
                "Please enter an event name."
            )

        else:

            result = event_report[
                event_report[
                    "Event Name"
                ]
                .apply(normalize_text)
                .str.contains(
                    re.escape(search_value),
                    na=False
                )
            ]

            if result.empty:

                st.error(
                    f"No event found for "
                    f"'{search_event}'."
                )

            else:

                for _, row in result.iterrows():

                    st.markdown(
                        '<div class="copy-box">',
                        unsafe_allow_html=True
                    )

                    st.subheader(
                        row["Event Name"]
                    )

                    # -------------------------------------
                    # ROW 1
                    # -------------------------------------

                    r1, r2, r3 = st.columns(3)

                    r1.metric(
                        "Category",
                        row["Category"]
                    )

                    r2.metric(
                        "Type of Event",
                        row["Type of Event"]
                    )

                    r3.metric(
                        "Internal Paid",
                        f"{row['Internal Paid']:,}"
                    )

                    # -------------------------------------
                    # ROW 2
                    # -------------------------------------

                    r1, r2, r3 = st.columns(3)

                    r1.metric(
                        "Internal Registrations",
                        f"{row['Internal Regs']:,}"
                    )

                    r2.metric(
                        "External Paid",
                        f"{row['External Paid']:,}"
                    )

                    r3.metric(
                        "External Registrations",
                        f"{row['External Regs']:,}"
                    )

                    # -------------------------------------
                    # ROW 3
                    # -------------------------------------

                    r1, r2, r3 = st.columns(3)

                    r1.metric(
                        "Total Paid",
                        f"{row['Total Paid']:,}"
                    )

                    r2.metric(
                        "Total Registrations",
                        f"{row['Total Regs']:,}"
                    )

                    st.markdown(
                        '</div>',
                        unsafe_allow_html=True
                    )


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.markdown(
        '<div class="section-title">'
        'Download Report'
        '</div>',
        unsafe_allow_html=True
    )

    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(
        excel_buffer,
        engine="openpyxl"
    ) as writer:

        # =================================================
        # SUMMARY SHEET
        # =================================================

        summary_df = pd.DataFrame({

            "Category": [
                "Internal",
                "External",
                "Overall"
            ],

            "Total Registrations": [
                internal_summary["total"],
                external_summary["total"],
                overall_total
            ],

            "Paid Registrations": [
                internal_summary["paid"],
                external_summary["paid"],
                overall_paid
            ],

            "Free Registrations": [
                internal_summary["free"],
                external_summary["free"],
                overall_free
            ],

            "Revenue Generated": [
                internal_summary["revenue"],
                external_summary["revenue"],
                overall_revenue
            ]
        })

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )


        # =================================================
        # EVENT REPORT SHEET
        # =================================================

        download_event_report = event_report[
            [
                "Event Name",
                "Category",
                "Type of Event",
                "Internal Paid",
                "Internal Regs",
                "External Paid",
                "External Regs",
                "Total Paid",
                "Total Regs"
            ]
        ].copy()

        download_event_report.to_excel(
            writer,
            sheet_name="Event Report",
            index=False
        )


    excel_buffer.seek(0)


    # =====================================================
    # DOWNLOAD BUTTON
    # =====================================================

    st.download_button(
        label="⬇️ Download Report",
        data=excel_buffer,
        file_name="Registration_Report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        type="primary",
        use_container_width=True
    )