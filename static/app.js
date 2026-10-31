"use strict";

const state = {
    cases: [],
};

document.addEventListener("DOMContentLoaded", () => {
    configureTabs();
    configureAssistant();
    configureCaseRegistration();
    configureComplaintGenerator();
    configureCases();
    loadAwareness();
    loadCases();
    loadStatistics();
});

function configureTabs() {
    document.querySelectorAll(".tab").forEach((button) => {
        button.addEventListener("click", () => {
            document.querySelectorAll(".tab").forEach((tab) => {
                tab.classList.remove("active");
            });

            document.querySelectorAll(".section").forEach((section) => {
                section.classList.remove("active");
            });

            button.classList.add("active");

            const section = document.getElementById(button.dataset.section);
            section.classList.add("active");

            if (button.dataset.section === "cases-section") {
                loadCases();
                loadStatistics();
            }
        });
    });
}

async function apiRequest(url, options = {}) {
    const response = await fetch(url, options);

    let data;

    try {
        data = await response.json();
    } catch {
        throw new Error("The server returned an unreadable response.");
    }

    if (!response.ok || data.success === false) {
        throw new Error(data.message || "The request failed.");
    }

    return data;
}

function jsonOptions(method, body) {
    return {
        method,
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
    };
}

function configureAssistant() {
    const form = document.getElementById("assistant-form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector("button[type='submit']");
        const result = document.getElementById("assistant-result");
        const question = document.getElementById("question").value.trim();

        setLoading(button, true, "Analyzing...");

        try {
            const data = await apiRequest(
                "/api/assistant",
                jsonOptions("POST", { question }),
            );

            result.className = data.urgent
                ? "result urgent"
                : "result";

            replaceChildren(result, [
                createResultGrid([
                    ["Category", data.category],
                    ["Priority", data.priority],
                    ["Confidence", `${data.confidence}%`],
                ]),
                element("h3", {}, data.issue),
                element("p", {}, data.guidance),
                element("p", {}, data.safety_message),
            ]);
        } catch (error) {
            showResultError(result, error.message);
        } finally {
            setLoading(button, false, "Analyze concern");
        }
    });
}

function configureCaseRegistration() {
    const form = document.getElementById("case-form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector("button[type='submit']");
        const result = document.getElementById("case-result");

        const payload = {
            name: document.getElementById("name").value.trim(),
            email: document.getElementById("email").value.trim(),
            phone: document.getElementById("phone").value.trim(),
            location: document.getElementById("location").value.trim(),
            description: document
                .getElementById("case-description")
                .value
                .trim(),
            consent: document.getElementById("consent").checked,
        };

        setLoading(button, true, "Saving...");

        try {
            const data = await apiRequest(
                "/api/cases",
                jsonOptions("POST", payload),
            );

            result.className = "result";

            replaceChildren(result, [
                element("h3", {}, "Case registered"),
                element(
                    "p",
                    {},
                    `Reference: ${data.case.reference}`,
                ),
                element(
                    "p",
                    {},
                    `Category: ${data.case.category}`,
                ),
                element(
                    "p",
                    {},
                    `Priority: ${data.case.priority}`,
                ),
            ]);

            form.reset();
            loadCases();
            loadStatistics();
        } catch (error) {
            showResultError(result, error.message);
        } finally {
            setLoading(button, false, "Register case");
        }
    });
}

function configureComplaintGenerator() {
    const form = document.getElementById("complaint-form");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const button = form.querySelector("button[type='submit']");
        const result = document.getElementById("complaint-result");
        const complaintText = document.getElementById("complaint-text");

        const payload = {
            name: document.getElementById("complaint-name").value.trim(),
            authority: document.getElementById("authority").value.trim(),
            location: document
                .getElementById("complaint-location")
                .value
                .trim(),
            description: document
                .getElementById("complaint-description")
                .value
                .trim(),
        };

        setLoading(button, true, "Generating...");

        try {
            const data = await apiRequest(
                "/api/complaints",
                jsonOptions("POST", payload),
            );

            complaintText.textContent = data.complaint;
            result.classList.remove("hidden");
            result.classList.remove("error");
        } catch (error) {
            complaintText.textContent = error.message;
            result.classList.remove("hidden");
            result.classList.add("error");
        } finally {
            setLoading(button, false, "Generate letter");
        }
    });

    document
        .getElementById("copy-complaint")
        .addEventListener("click", async () => {
            const content =
                document.getElementById("complaint-text").textContent;

            if (!content) {
                showToast("There is no complaint text to copy.");
                return;
            }

            try {
                await navigator.clipboard.writeText(content);
                showToast("Complaint copied.");
            } catch {
                showToast("The complaint could not be copied automatically.");
            }
        });
}

function configureCases() {
    document
        .getElementById("search-cases")
        .addEventListener("click", loadCases);

    document
        .getElementById("status-filter")
        .addEventListener("change", loadCases);

    document
        .getElementById("case-search")
        .addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                loadCases();
            }
        });

    document
        .getElementById("export-cases")
        .addEventListener("click", exportCases);
}

async function loadCases() {
    const container = document.getElementById("cases-list");
    const search = document.getElementById("case-search").value.trim();
    const status = document.getElementById("status-filter").value;

    const parameters = new URLSearchParams();

    if (search) {
        parameters.set("search", search);
    }

    if (status) {
        parameters.set("status", status);
    }

    container.replaceChildren(
        element("div", { className: "empty-state" }, "Loading cases..."),
    );

    try {
        const data = await apiRequest(
            `/api/cases?${parameters.toString()}`,
        );

        state.cases = data.cases;
        renderCases();
    } catch (error) {
        container.replaceChildren(
            element(
                "div",
                { className: "empty-state" },
                error.message,
            ),
        );
    }
}

function renderCases() {
    const container = document.getElementById("cases-list");
    container.replaceChildren();

    if (state.cases.length === 0) {
        container.append(
            element(
                "div",
                { className: "empty-state" },
                "No cases match the selected filters.",
            ),
        );
        return;
    }

    state.cases.forEach((caseData) => {
        container.append(createCaseCard(caseData));
    });
}

function createCaseCard(caseData) {
    const card = element("article", { className: "case-card" });

    const titleContainer = element("div");
    titleContainer.append(
        element(
            "div",
            { className: "case-reference" },
            caseData.reference,
        ),
        element("h3", {}, caseData.issue),
    );

    const header = element("div", { className: "case-card-header" });
    header.append(
        titleContainer,
        element("span", {}, formatDate(caseData.created_at)),
    );

    const meta = element("div", { className: "case-meta" });
    meta.append(
        badge(caseData.category),
        badge(caseData.priority, caseData.priority.toLowerCase()),
        badge(caseData.status, caseData.status.toLowerCase().replace(" ", "-")),
    );

    const description = element("p", {}, caseData.description);

    const contact = element(
        "p",
        {},
        [
            caseData.name,
            caseData.location,
            caseData.email,
            caseData.phone,
        ]
            .filter(Boolean)
            .join(" | "),
    );

    const statusSelect = createSelect(
        ["Open", "In Review", "Referred", "Resolved", "Closed"],
        caseData.status,
    );

    const prioritySelect = createSelect(
        ["Low", "Medium", "High", "Critical"],
        caseData.priority,
    );

    const notes = element("textarea", {
        rows: 3,
        maxLength: 3000,
        placeholder: "Internal case notes",
        value: caseData.notes || "",
    });

    const actions = element("div", { className: "case-actions" });

    const statusGroup = element("div");
    statusGroup.append(
        element("label", {}, "Status"),
        statusSelect,
    );

    const priorityGroup = element("div");
    priorityGroup.append(
        element("label", {}, "Priority"),
        prioritySelect,
    );

    const saveButton = element(
        "button",
        { type: "button" },
        "Save changes",
    );

    saveButton.addEventListener("click", async () => {
        setLoading(saveButton, true, "Saving...");

        try {
            await apiRequest(
                `/api/cases/${caseData.id}`,
                jsonOptions("PATCH", {
                    status: statusSelect.value,
                    priority: prioritySelect.value,
                    notes: notes.value.trim(),
                }),
            );

            showToast("Case updated.");
            await loadCases();
            await loadStatistics();
        } catch (error) {
            showToast(error.message);
        } finally {
            setLoading(saveButton, false, "Save changes");
        }
    });

    const deleteButton = element(
        "button",
        {
            type: "button",
            className: "danger",
        },
        "Delete case",
    );

    deleteButton.addEventListener("click", async () => {
        const confirmed = window.confirm(
            `Delete case ${caseData.reference}? This cannot be undone.`,
        );

        if (!confirmed) {
            return;
        }

        setLoading(deleteButton, true, "Deleting...");

        try {
            await apiRequest(`/api/cases/${caseData.id}`, {
                method: "DELETE",
            });

            showToast("Case deleted.");
            await loadCases();
            await loadStatistics();
        } catch (error) {
            showToast(error.message);
        } finally {
            setLoading(deleteButton, false, "Delete case");
        }
    });

    const buttonRow = element("div", { className: "button-row" });
    buttonRow.append(saveButton, deleteButton);

    actions.append(
        statusGroup,
        priorityGroup,
        notes,
        buttonRow,
    );

    card.append(
        header,
        meta,
        contact,
        description,
        actions,
    );

    return card;
}

async function loadStatistics() {
    const container = document.getElementById("statistics");

    try {
        const data = await apiRequest("/api/statistics");
        const statistics = data.statistics;

        replaceChildren(container, [
            statCard("Total cases", statistics.total),
            statCard("Active cases", statistics.open),
            statCard("Resolved", statistics.resolved),
            statCard("Critical", statistics.critical),
        ]);
    } catch {
        container.replaceChildren();
    }
}

async function loadAwareness() {
    const container = document.getElementById("awareness-content");

    try {
        const data = await apiRequest("/api/awareness");
        container.replaceChildren();

        data.content.forEach((item) => {
            const card = element("article", {
                className: "awareness-card",
            });

            const list = element("ul");

            item.actions.forEach((action) => {
                list.append(element("li", {}, action));
            });

            card.append(
                element("h3", {}, item.title),
                element("p", {}, item.summary),
                list,
            );

            container.append(card);
        });
    } catch (error) {
        container.replaceChildren(
            element(
                "div",
                { className: "empty-state" },
                error.message,
            ),
        );
    }
}

async function exportCases() {
    try {
        const data = await apiRequest("/api/export");
        const content = JSON.stringify(data.cases, null, 2);
        const blob = new Blob([content], {
            type: "application/json",
        });

        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = `human-rights-cases-${new Date()
            .toISOString()
            .slice(0, 10)}.json`;

        document.body.append(link);
        link.click();
        link.remove();

        URL.revokeObjectURL(link.href);
        showToast("Cases exported.");
    } catch (error) {
        showToast(error.message);
    }
}

function createResultGrid(items) {
    const grid = element("div", { className: "result-grid" });

    items.forEach(([label, value]) => {
        const item = element("div", { className: "result-item" });
        item.append(
            element("span", {}, label),
            element("strong", {}, String(value)),
        );
        grid.append(item);
    });

    return grid;
}

function statCard(label, value) {
    const card = element("div", { className: "stat-card" });
    card.append(
        element("span", {}, label),
        element("strong", {}, String(value)),
    );
    return card;
}

function badge(text, extraClass = "") {
    return element(
        "span",
        {
            className: `badge ${extraClass}`.trim(),
        },
        text,
    );
}

function createSelect(options, selectedValue) {
    const select = element("select");

    options.forEach((optionValue) => {
        const option = element(
            "option",
            { value: optionValue },
            optionValue,
        );

        option.selected = optionValue === selectedValue;
        select.append(option);
    });

    return select;
}

function element(tagName, properties = {}, text = "") {
    const node = document.createElement(tagName);

    Object.entries(properties).forEach(([key, value]) => {
        if (key in node) {
            node[key] = value;
        } else {
            node.setAttribute(key, value);
        }
    });

    if (text !== "") {
        node.textContent = text;
    }

    return node;
}

function replaceChildren(parent, children) {
    parent.replaceChildren(...children);
}

function showResultError(container, message) {
    container.className = "result error";
    container.replaceChildren(
        element("strong", {}, "Request failed"),
        element("p", {}, message),
    );
}

function setLoading(button, loading, label) {
    button.disabled = loading;
    button.textContent = label;
}

function showToast(message) {
    const toast = document.getElementById("toast");

    toast.textContent = message;
    toast.classList.remove("hidden");

    window.clearTimeout(showToast.timeout);

    showToast.timeout = window.setTimeout(() => {
        toast.classList.add("hidden");
    }, 3000);
}

function formatDate(value) {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleString();
}
