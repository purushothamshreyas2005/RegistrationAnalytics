// =========================================================
// GLOBAL REPORT DATA
// =========================================================

let eventReport = [];


// =========================================================
// INDIAN NUMBER FORMAT
// =========================================================

function indianFormat(value) {

    value = Number(value) || 0;

    value = Math.round(value);

    return value.toLocaleString("en-IN");
}


// =========================================================
// GENERATE REPORT
// =========================================================

async function generateReport() {

    const loading =
        document.getElementById(
            "loadingOverlay"
        );

    const internalFile =
        document.getElementById(
            "internalFile"
        ).files[0];

    const externalFile =
        document.getElementById(
            "externalFile"
        ).files[0];


    // =====================================================
    // VALIDATE FILES
    // =====================================================

    if (!internalFile) {

        showMessage(
            "Please upload the Internal Registrations file.",
            true
        );

        return;
    }


    if (!externalFile) {

        showMessage(
            "Please upload the External Registrations file.",
            true
        );

        return;
    }


    // =====================================================
    // SHOW LOADING TILE
    // =====================================================

    if (loading) {

        loading.style.display = "flex";

    }


    // =====================================================
    // PREPARE FILES
    // =====================================================

    const formData =
        new FormData();


    formData.append(
        "internal_file",
        internalFile
    );


    formData.append(
        "external_file",
        externalFile
    );


    showMessage(
        "Processing files...",
        false
    );


    try {

        // =================================================
        // SEND TO FLASK
        // =================================================

        const response =
            await fetch(
                "/generate",
                {
                    method: "POST",
                    body: formData
                }
            );


        const data =
            await response.json();


        // =================================================
        // HANDLE ERROR
        // =================================================

        if (!data.success) {

            showMessage(
                data.error,
                true
            );

            return;
        }


        // =================================================
        // SAVE EVENT REPORT
        // =================================================

        eventReport =
            data.events || [];


        // =================================================
        // INTERNAL
        // =================================================

        document.getElementById(
            "internalTotal"
        ).innerText =
            indianFormat(
                data.internal.total
            );


        document.getElementById(
            "internalPaid"
        ).innerText =
            indianFormat(
                data.internal.paid
            );


        document.getElementById(
            "internalFree"
        ).innerText =
            indianFormat(
                data.internal.free
            );


        document.getElementById(
            "internalRevenue"
        ).innerText =
            indianFormat(
                data.internal.revenue
            );


        // =================================================
        // EXTERNAL
        // =================================================

        document.getElementById(
            "externalTotal"
        ).innerText =
            indianFormat(
                data.external.total
            );


        document.getElementById(
            "externalPaid"
        ).innerText =
            indianFormat(
                data.external.paid
            );


        document.getElementById(
            "externalFree"
        ).innerText =
            indianFormat(
                data.external.free
            );


        document.getElementById(
            "externalRevenue"
        ).innerText =
            indianFormat(
                data.external.revenue
            );


        // =================================================
        // OVERALL
        // =================================================

        document.getElementById(
            "overallTotal"
        ).innerText =
            indianFormat(
                data.overall.total
            );


        document.getElementById(
            "overallPaid"
        ).innerText =
            indianFormat(
                data.overall.paid
            );


        document.getElementById(
            "overallFree"
        ).innerText =
            indianFormat(
                data.overall.free
            );


        document.getElementById(
            "overallRevenue"
        ).innerText =
            indianFormat(
                data.overall.revenue
            );


        // =================================================
        // COPY SUMMARY
        // =================================================

        document.getElementById(
            "summaryText"
        ).value =
            data.summary_text;


        // =================================================
        // EVENT TABLE
        // =================================================

        populateEventTable(
            eventReport
        );


        // =================================================
        // SHOW DASHBOARD
        // =================================================

        document.getElementById(
            "dashboard"
        ).style.display =
            "block";


        showMessage(
            "Files processed successfully.",
            false
        );


    } catch (error) {

        showMessage(
            "Something went wrong while processing the files.",
            true
        );

        console.error(error);

    } finally {

        // =================================================
        // ALWAYS HIDE LOADING TILE
        // =================================================

        if (loading) {

            loading.style.display = "none";

        }

    }
}


// =========================================================
// GET REGISTRATION HIGHLIGHT CLASS
// =========================================================

function getRegistrationClass(
    totalRegs
) {

    totalRegs =
        Number(totalRegs) || 0;


    // 0 - 30
    if (totalRegs <= 30) {

        return "regs-red";

    }


    // 31 - 50
    if (
        totalRegs >= 31 &&
        totalRegs <= 50
    ) {

        return "regs-yellow";

    }


    // 51 - 90
    if (
        totalRegs >= 51 &&
        totalRegs <= 90
    ) {

        return "regs-orange";

    }


    // 91+
    return "regs-green";
}


// =========================================================
// EVENT TABLE
// =========================================================

function populateEventTable(events) {

    const tbody =
        document.getElementById(
            "eventTableBody"
        );


    if (!tbody) {
        return;
    }


    tbody.innerHTML = "";


    events.forEach(
        function(event) {

            const row =
                document.createElement(
                    "tr"
                );


            const totalRegs =
                Number(
                    event["Total Regs"]
                ) || 0;


            const registrationClass =
                getRegistrationClass(
                    totalRegs
                );


            row.innerHTML = `

                <td>
                    ${escapeHtml(
                        event["Event Name"]
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        event["Category"]
                    )}
                </td>

                <td>
                    ${escapeHtml(
                        event["Type of Event"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["Internal Paid"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["Internal Regs"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["External Paid"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["External Regs"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["Total Paid"]
                    )}
                </td>

                <td
                    class="${registrationClass}"
                >
                    ${indianFormat(
                        totalRegs
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["Amount (Excl. GST)"]
                    )}
                </td>

                <td>
                    ${indianFormat(
                        event["Revenue Generated"]
                    )}
                </td>

            `;


            tbody.appendChild(
                row
            );

        }
    );
}


// =========================================================
// SEARCH EVENT
// =========================================================

async function searchEvent() {

    const query =
        document.getElementById(
            "searchEvent"
        ).value.trim();


    if (!query) {

        showSearchMessage(
            "Please enter an event name."
        );

        return;
    }


    try {

        const response =
            await fetch(
                "/search",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        event: query
                    })
                }
            );


        const data =
            await response.json();


        if (!data.success) {

            showSearchMessage(
                data.error
            );

            return;
        }


        displaySearchResults(
            data.results
        );


    } catch (error) {

        showSearchMessage(
            "Search failed."
        );

        console.error(error);
    }
}


// =========================================================
// DISPLAY SEARCH RESULTS
// =========================================================

function displaySearchResults(
    results
) {

    const container =
        document.getElementById(
            "searchResults"
        );


    if (!container) {
        return;
    }


    container.innerHTML = "";


    results.forEach(
        function(row) {

            const result =
                document.createElement(
                    "div"
                );


            result.className =
                "search-result";


            const totalRegs =
                Number(
                    row["Total Regs"]
                ) || 0;


            const registrationClass =
                getRegistrationClass(
                    totalRegs
                );


            result.innerHTML = `

                <h3>
                    ${escapeHtml(
                        row["Event Name"]
                    )}
                </h3>


                <div class="search-metrics">

                    <div class="search-metric">

                        <div class="search-label">
                            Category
                        </div>

                        <div class="search-value">
                            ${escapeHtml(
                                row["Category"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Type of Event
                        </div>

                        <div class="search-value">
                            ${escapeHtml(
                                row["Type of Event"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Internal Paid
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["Internal Paid"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Internal Registrations
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["Internal Regs"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            External Paid
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["External Paid"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            External Registrations
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["External Regs"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Total Paid
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["Total Paid"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Total Registrations
                        </div>

                        <div
                            class="search-value ${registrationClass}"
                            style="
                                padding: 4px 8px;
                                border-radius: 6px;
                            "
                        >
                            ${indianFormat(
                                totalRegs
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Amount (Excl. GST)
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["Amount (Excl. GST)"]
                            )}
                        </div>

                    </div>


                    <div class="search-metric">

                        <div class="search-label">
                            Revenue Generated
                        </div>

                        <div class="search-value">
                            ${indianFormat(
                                row["Revenue Generated"]
                            )}
                        </div>

                    </div>

                </div>

            `;


            container.appendChild(
                result
            );

        }
    );
}


// =========================================================
// COPY SUMMARY
// =========================================================

async function copySummary() {

    const textarea =
        document.getElementById(
            "summaryText"
        );


    if (!textarea) {
        return;
    }


    try {

        await navigator.clipboard.writeText(
            textarea.value
        );


        const message =
            document.getElementById(
                "copyMessage"
            );


        if (message) {

            message.innerText =
                "Copied to clipboard!";

        }


    } catch (error) {

        textarea.select();

        textarea.setSelectionRange(
            0,
            99999
        );


        document.execCommand(
            "copy"
        );


        const message =
            document.getElementById(
                "copyMessage"
            );


        if (message) {

            message.innerText =
                "Copied to clipboard!";

        }

    }
}


// =========================================================
// SAVE EVENT CATEGORIES
// =========================================================

async function saveCategories() {

    const premium =
        document.getElementById(
            "premiumEvents"
        ).value;


    const pro =
        document.getElementById(
            "proEvents"
        ).value;


    try {

        const response =
            await fetch(
                "/update_categories",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        premium: premium,
                        pro: pro
                    })
                }
            );


        const data =
            await response.json();


        const message =
            document.getElementById(
                "categoryMessage"
            );


        if (message) {

            message.innerText =
                data.message;

        }


        if (data.success) {

            setTimeout(
                function() {

                    location.reload();

                },
                700
            );

        }


    } catch (error) {

        const message =
            document.getElementById(
                "categoryMessage"
            );


        if (message) {

            message.innerText =
                "Could not save event lists.";

        }

    }
}


// =========================================================
// GENERAL MESSAGE
// =========================================================

function showMessage(
    message,
    isError
) {

    const element =
        document.getElementById(
            "message"
        );


    if (!element) {
        return;
    }


    element.innerText =
        message;


    element.style.color =
        isError
            ? "#dc2626"
            : "#16a34a";
}


// =========================================================
// SEARCH MESSAGE
// =========================================================

function showSearchMessage(
    message
) {

    const container =
        document.getElementById(
            "searchResults"
        );


    if (!container) {
        return;
    }


    container.innerHTML = `

        <div class="search-result">

            <strong>
                ${escapeHtml(message)}
            </strong>

        </div>

    `;
}


// =========================================================
// HTML ESCAPE
// =========================================================

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );
}
