from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import io
import re
import json
import os

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/static"
)


# =========================================================
# DEFAULT EVENT LISTS
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

DEFAULT_PRO_EVENTS = [
    "Capital Hunt 2.0",
    "Capital Hunt 2.0 - Freshminds"
]


# =========================================================
# SESSION-LIKE GLOBAL DATA
# =========================================================

premium_events = DEFAULT_PREMIUM_EVENTS.copy()
pro_events = DEFAULT_PRO_EVENTS.copy()

latest_internal = None
latest_external = None
latest_report = None


# =========================================================
# INDIAN NUMBER FORMAT
# =========================================================

def indian_format(value):
    """
    1234567 -> 12,34,567
    """

    try:
        value = int(round(float(value)))
    except:
        return "0"

    negative = value < 0

    value = abs(value)

    number = str(value)

    if len(number) <= 3:
        result = number

    else:
        last_three = number[-3:]
        remaining = number[:-3]

        groups = []

        while len(remaining) > 2:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]

        if remaining:
            groups.insert(0, remaining)

        result = ",".join(groups) + "," + last_three

    if negative:
        result = "-" + result

    return result


# =========================================================
# NORMALIZE TEXT
# =========================================================

def normalize_text(value):

    if pd.isna(value):
        return ""

    value = str(value).strip().lower()

    value = (
        value
        .replace("–", "-")
        .replace("—", "-")
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

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

    # Exact match
    for name in possible_names:

        normalized_name = (
            normalize_column_name(name)
        )

        if normalized_name in normalized_columns:
            return normalized_columns[
                normalized_name
            ]

    # Flexible match
    for normalized_col, original_col in (
        normalized_columns.items()
    ):

        for name in possible_names:

            normalized_name = (
                normalize_column_name(name)
            )

            if normalized_name in normalized_col:
                return original_col

    return None


# =========================================================
# LOAD EXCEL / CSV
# =========================================================

def load_file(file):

    filename = file.filename.lower()

    if filename.endswith(".csv"):

        return pd.read_csv(file)

    elif filename.endswith(".xlsx"):

        return pd.read_excel(file)

    elif filename.endswith(".xls"):

        return pd.read_excel(file)

    else:

        raise ValueError(
            "Only CSV, XLS and XLSX files are supported."
        )


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(df, source):

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

        raise ValueError(
            f"{source} file is missing: "
            + ", ".join(missing)
        )

    data = pd.DataFrame()

    data["Event Name"] = (
        df[event_col]
        .apply(normalize_text)
    )

    data["Display Event Name"] = (
        df[event_col]
        .astype(str)
        .str.strip()
    )

    data["Participants"] = pd.to_numeric(
        df[participant_col],
        errors="coerce"
    ).fillna(0)

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

    data["Payment Status"] = (
        df[payment_col]
        .apply(normalize_text)
    )

    data["Source"] = source

    data = data[
        data["Event Name"].str.strip() != ""
    ].copy()

    return data


# =========================================================
# SUMMARY
# =========================================================

def calculate_summary(data):

    if data is None or data.empty:

        return {
            "total": 0,
            "paid": 0,
            "free": 0,
            "revenue": 0
        }

    total = data[
        "Participants"
    ].sum()

    paid = data.loc[
        data["Payment Status"] == "paid",
        "Participants"
    ].sum()

    free = data.loc[
        data["Amount"] == 0,
        "Participants"
    ].sum()

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
# EVENT CATEGORY
# =========================================================

def get_event_category(event_name):

    event = normalize_text(event_name)

    premium = [
        normalize_text(x)
        for x in premium_events
    ]

    pro = [
        normalize_text(x)
        for x in pro_events
    ]

    if event in pro:
        return "Pro Event"

    if event in premium:
        return "Premium Event"

    return "Event"


# =========================================================
# EVENT REPORT
# =========================================================

def generate_event_report(
    internal_data,
    external_data
):

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

    for event in sorted(all_events):

        # =================================================
        # INTERNAL
        # =================================================

        if internal_data is not None:

            internal_event = internal_data[
                internal_data["Event Name"] == event
            ]

            internal_total = (
                internal_event["Participants"].sum()
            )

            internal_paid = (
                internal_event.loc[
                    internal_event["Payment Status"] == "paid",
                    "Participants"
                ].sum()
            )

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

            external_total = (
                external_event["Participants"].sum()
            )

            external_paid = (
                external_event.loc[
                    external_event["Payment Status"] == "paid",
                    "Participants"
                ].sum()
            )

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
        # EVENT TYPE
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

        total_amount_inclusive_gst = (
            internal_amount
            + external_amount
        )

        event_type = (
            "Free"
            if total_amount_inclusive_gst == 0
            else "Paid"
        )


        # =================================================
        # CATEGORY
        # =================================================

        category = get_event_category(
            display_name
        )


        # =================================================
        # TOTAL PAID / TOTAL REGS
        # =================================================

        total_paid = (
            internal_paid
            + external_paid
        )

        total_regs = (
            internal_total
            + external_total
        )


        # =================================================
        # EXCLUSIVE GST CALCULATION
        #
        # Uploaded amount is GST-inclusive.
        #
        # For team events:
        # amount / number of participants
        #
        # Then remove 18% GST.
        # =================================================

        paid_amount = 0

        paid_participants = 0


        if not internal_event.empty:

            internal_paid_rows = internal_event[
                internal_event["Payment Status"] == "paid"
            ]

            for _, row in internal_paid_rows.iterrows():

                participants = float(
                    row["Participants"]
                )

                amount = float(
                    row["Amount"]
                )

                if participants > 0:

                    paid_amount += amount

                    paid_participants += participants


        if not external_event.empty:

            external_paid_rows = external_event[
                external_event["Payment Status"] == "paid"
            ]

            for _, row in external_paid_rows.iterrows():

                participants = float(
                    row["Participants"]
                )

                amount = float(
                    row["Amount"]
                )

                if participants > 0:

                    paid_amount += amount

                    paid_participants += participants


        # =================================================
        # PER-PERSON COST EXCLUDING GST
        # =================================================

        if paid_participants > 0:

            amount_excl_gst = (
                paid_amount
                / paid_participants
                / 1.18
            )

        else:

            amount_excl_gst = 0


        # =================================================
        # REVENUE GENERATED
        #
        # Total paid participants ×
        # exclusive-GST per-person cost
        # =================================================

        revenue_generated = (
            total_paid
            * amount_excl_gst
        )


        # =================================================
        # ADD ROW
        # =================================================

        rows.append({

            "Event Name":
                display_name,

            "Category":
                category,

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
                int(total_regs),

            "Amount (Excl. GST)":
                round(amount_excl_gst, 2),

            "Revenue Generated":
                round(revenue_generated, 2)

        })

    return pd.DataFrame(rows)

# =========================================================
# COPY SUMMARY TEXT
# =========================================================

def create_summary_text(
    internal_summary,
    external_summary
):

    total = (
        internal_summary["total"]
        + external_summary["total"]
    )

    paid = (
        internal_summary["paid"]
        + external_summary["paid"]
    )

    free = (
        internal_summary["free"]
        + external_summary["free"]
    )

    revenue = (
        internal_summary["revenue"]
        + external_summary["revenue"]
    )

    return (
        "INTERNAL EVENT\n"
        f"Total regs = "
        f"{indian_format(internal_summary['total'])}\n"
        f"Paid regs = "
        f"{indian_format(internal_summary['paid'])}\n"
        f"Free regs = "
        f"{indian_format(internal_summary['free'])}\n"
        f"Revenue = "
        f"{indian_format(internal_summary['revenue'])}\n"
        "\n"
        "EXTERNAL EVENT\n"
        f"Total regs = "
        f"{indian_format(external_summary['total'])}\n"
        f"Paid regs = "
        f"{indian_format(external_summary['paid'])}\n"
        f"Free regs = "
        f"{indian_format(external_summary['free'])}\n"
        f"Revenue = "
        f"{indian_format(external_summary['revenue'])}\n"
        "\n"
        "TOTAL\n"
        f"Total regs = "
        f"{indian_format(total)}\n"
        f"Paid regs = "
        f"{indian_format(paid)}\n"
        f"Free regs = "
        f"{indian_format(free)}\n"
        f"Revenue = "
        f"{indian_format(revenue)}"
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/", methods=["GET"])
def index():

    return render_template(
        "index.html",
        premium_events=premium_events,
        pro_events=pro_events
    )


# =========================================================
# GENERATE REPORT
# =========================================================

@app.route(
    "/generate",
    methods=["POST"]
)
def generate():

    global latest_internal
    global latest_external
    global latest_report

    internal_file = request.files.get(
        "internal_file"
    )

    external_file = request.files.get(
        "external_file"
    )

    if (
        internal_file is None
        or external_file is None
    ):

        return jsonify({
            "success": False,
            "error":
                "Please upload both Internal "
                "and External files."
        })

    try:

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

        internal_summary = (
            calculate_summary(
                internal_data
            )
        )

        external_summary = (
            calculate_summary(
                external_data
            )
        )

        overall = {

            "total":
                internal_summary["total"]
                + external_summary["total"],

            "paid":
                internal_summary["paid"]
                + external_summary["paid"],

            "free":
                internal_summary["free"]
                + external_summary["free"],

            "revenue":
                internal_summary["revenue"]
                + external_summary["revenue"]
        }

        event_report = (
            generate_event_report(
                internal_data,
                external_data
            )
        )

        latest_internal = internal_data
        latest_external = external_data
        latest_report = event_report

        report_records = (
            event_report
            .fillna("")
            .to_dict(
                orient="records"
            )
        )

        return jsonify({

            "success": True,

            "internal": internal_summary,

            "external": external_summary,

            "overall": overall,

            "summary_text":
                create_summary_text(
                    internal_summary,
                    external_summary
                ),

            "events":
                report_records
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        })


# =========================================================
# SEARCH EVENT
# =========================================================

@app.route(
    "/search",
    methods=["POST"]
)
def search():

    global latest_report

    data = request.get_json()

    query = normalize_text(
        data.get("event", "")
    )

    if not query:

        return jsonify({
            "success": False,
            "error":
                "Please enter an event name."
        })

    if latest_report is None:

        return jsonify({
            "success": False,
            "error":
                "Generate a report first."
        })

    matches = latest_report[
        latest_report[
            "Event Name"
        ]
        .apply(normalize_text)
        .str.contains(
            re.escape(query),
            na=False
        )
    ]

    if matches.empty:

        return jsonify({
            "success": False,
            "error":
                f"No event found for '{query}'."
        })

    results = (
        matches
        .fillna("")
        .to_dict(
            orient="records"
        )
    )

    return jsonify({
        "success": True,
        "results": results
    })


# =========================================================
# UPDATE EVENT LISTS
# =========================================================

@app.route(
    "/update_categories",
    methods=["POST"]
)
def update_categories():

    global premium_events
    global pro_events

    data = request.get_json()

    premium_text = data.get(
        "premium",
        ""
    )

    pro_text = data.get(
        "pro",
        ""
    )

    premium_events = [
        x.strip()
        for x in premium_text.splitlines()
        if x.strip()
    ]

    pro_events = [
        x.strip()
        for x in pro_text.splitlines()
        if x.strip()
    ]

    return jsonify({
        "success": True,
        "message":
            "Event category lists updated."
    })


# =========================================================
# DOWNLOAD EXCEL REPORT
# =========================================================

@app.route(
    "/download",
    methods=["GET"]
)
def download():

    if latest_report is None:

        return (
            "Please generate a report first.",
            400
        )

    internal_summary = (
        calculate_summary(
            latest_internal
        )
    )

    external_summary = (
        calculate_summary(
            latest_external
        )
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

    # =====================================================
    # SUMMARY
    # =====================================================

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

    # =====================================================
    # EVENT REPORT
    # =====================================================

    download_event_report = latest_report[
    [
        "Event Name",
        "Category",
        "Type of Event",
        "Internal Paid",
        "Internal Regs",
        "External Paid",
        "External Regs",
        "Total Paid",
        "Total Regs",
        "Amount (Excl. GST)",
        "Revenue Generated"
    ]
].copy()

    # =====================================================
    # CREATE EXCEL
    # =====================================================

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

        download_event_report.to_excel(
            writer,
            sheet_name="Event Report",
            index=False
        )

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=(
            "Registration_Report.xlsx"
        ),
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )
