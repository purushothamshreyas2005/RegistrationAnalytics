

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

    return value.toLocaleString(
        "en-IN"
    );
}


// =========================================================
// GENERATE REPORT
// =========================================================

async function generateReport() {

    const internalFile =
        document.getElementById(
            "internalFile"
        ).files[0];

    const externalFile =
        document.getElementById(
            "externalFile"
        ).files[0];


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


        if (!data.success) {

            showMessage(
                data.error,
                true
            );

            return;
        }


        // Save event report

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
        // COPY TEXT
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
    }
}


// =========================================================
// EVENT TABLE
// =========================================================

function populateEventTable(events) {

    const tbody =
        document.getElementById(
            "eventTableBody"
        );


    tbody.innerHTML = "";


    events.forEach(
        function(event) {

            const row =
                document.createElement(
                    "tr"
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

                <td>
                    ${indianFormat(
                        event["Total Regs"]
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


    container.innerHTML = "";


    results.forEach(
        function(row) {

            const result =
                document.createElement(
                    "div"
                );


            result.className =
                "search-result";


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

                        <div class="search-value">
                            ${indianFormat(
                                row["Total Regs"]
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


    try {

        await navigator.clipboard.writeText(
            textarea.value
        );


        document.getElementById(
            "copyMessage"
        ).innerText =
            "Copied to clipboard!";


    } catch (error) {

        textarea.select();

        document.execCommand(
            "copy"
        );


        document.getElementById(
            "copyMessage"
        ).innerText =
            "Copied to clipboard!";

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


        document.getElementById(
            "categoryMessage"
        ).innerText =
            data.message;


        // If a report already exists,
        // reload the page so the new categories
        // are reflected.

        if (data.success) {

            setTimeout(
                function() {
                    location.reload();
                },
                700
            );
        }


    } catch (error) {

        document.getElementById(
            "categoryMessage"
        ).innerText =
            "Could not save event lists.";

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

    if (value === null ||
        value === undefined) {

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