// glossary.js
// Filters the glossary table by:
// - Type buttons (All / Term / Acronym / Metric)
// - Domain dropdown (auto-built from the Domain column)
// - Free-text search (searches across the whole row)

(function () {
  function normalise(s) {
    return (s ?? "")
      .toString()
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function getText(el) {
    return (el?.textContent ?? "").replace(/\s+/g, " ").trim();
  }

  function findGlossaryTable() {
    // Prefer a table that contains a "Name" header (glossary table)
    const tables = Array.from(document.querySelectorAll(".md-typeset table"));
    for (const t of tables) {
      const ths = Array.from(t.querySelectorAll("thead th")).map((th) =>
        normalise(getText(th))
      );
      if (ths.includes("name") && ths.includes("definition")) return t;
    }
    return tables[0] || null;
  }

  function getColumnIndexByHeader(table, headerName) {
    const headers = Array.from(table.querySelectorAll("thead th"));
    const target = normalise(headerName);
    for (let i = 0; i < headers.length; i++) {
      if (normalise(getText(headers[i])) === target) return i;
    }
    return -1;
  }

  function buildDomainDropdown(controlsEl, domains) {
    // Avoid duplicating if user hot-reloads / MkDocs live reload
    if (document.getElementById("domain-filter")) return;

    const wrapper = document.createElement("span");
    wrapper.className = "domain-filter-wrap";

    const select = document.createElement("select");
    select.id = "domain-filter";
    select.setAttribute("aria-label", "Filter by Domain");

    const optAll = document.createElement("option");
    optAll.value = "all";
    optAll.textContent = "All domains";
    select.appendChild(optAll);

    domains.forEach((d) => {
      const opt = document.createElement("option");
      opt.value = d;
      opt.textContent = d;
      select.appendChild(opt);
    });

    wrapper.appendChild(select);

    // Insert AFTER buttons, before search input (nice layout)
    const searchInput = controlsEl.querySelector("#glossary-search");
    if (searchInput) {
      controlsEl.insertBefore(wrapper, searchInput);
    } else {
      controlsEl.appendChild(wrapper);
    }
  }

  function init() {
    const controls = document.querySelector(".glossary-controls");
    const table = findGlossaryTable();
    if (!controls || !table) return;

    // Add class for your CSS table styling hook (optional)
    table.classList.add("tm-glossary");

    // Identify columns by header name (robust even if column order changes)
    const typeCol = getColumnIndexByHeader(table, "Type");
    const domainCol = getColumnIndexByHeader(table, "Domain");

    const rows = Array.from(table.querySelectorAll("tbody tr"));

    // Build domain list from table rows
    const domainSet = new Set();
    if (domainCol !== -1) {
      for (const r of rows) {
        const tds = r.querySelectorAll("td");
        const domain = getText(tds[domainCol]);
        if (domain) domainSet.add(domain);
      }
    }
    const domains = Array.from(domainSet).sort((a, b) =>
      a.localeCompare(b, undefined, { sensitivity: "base" })
    );

    // Create and insert the dropdown
    buildDomainDropdown(controls, domains);

    const domainSelect = document.getElementById("domain-filter");
    const search = document.getElementById("glossary-search");
    const buttons = Array.from(controls.querySelectorAll(".tm-btn"));

    let activeType = "all";

    function applyFilters() {
      const q = normalise(search?.value || "");
      const domainChosen = normalise(domainSelect?.value || "all");

      for (const r of rows) {
        const cells = Array.from(r.querySelectorAll("td"));
        const rowText = normalise(getText(r));

        // Type match
        let typeOk = true;
        if (activeType !== "all" && typeCol !== -1) {
          const rowType = normalise(getText(cells[typeCol]));
          typeOk = rowType === activeType;
        }

        // Domain match
        let domainOk = true;
        if (domainChosen !== "all" && domainCol !== -1) {
          const rowDomain = normalise(getText(cells[domainCol]));
          domainOk = rowDomain === domainChosen;
        }

        // Search match
        const searchOk = !q || rowText.includes(q);

        r.style.display = typeOk && domainOk && searchOk ? "" : "none";
      }
    }

    // Button wiring
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        buttons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");
        activeType = normalise(btn.getAttribute("data-type") || "all");
        applyFilters();
      });
    });

    // Default active state (All)
    const allBtn = buttons.find(
      (b) => normalise(b.getAttribute("data-type")) === "all"
    );
    if (allBtn) allBtn.classList.add("active");

    // Search + domain change wiring
    if (search) search.addEventListener("input", applyFilters);
    if (domainSelect) domainSelect.addEventListener("change", applyFilters);

    // Initial pass
    applyFilters();
  }

  document.addEventListener("DOMContentLoaded", init);
})();
