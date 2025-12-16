// docs/glossary.js
// Filters the glossary table by Type buttons, Domain dropdown, and Search box.
// Works by finding column indexes from header names (so it won't break if columns move).

document.addEventListener("DOMContentLoaded", () => {
  const domainSelect = document.getElementById("domain-filter");
  const searchInput = document.getElementById("glossary-search");
  const typeButtons = Array.from(document.querySelectorAll(".tm-btn"));

  // Find the first table in the page content (the glossary table)
  const table = document.querySelector(".md-content .md-typeset table");
  if (!table) return;

  const thead = table.querySelector("thead");
  const tbody = table.querySelector("tbody");
  if (!thead || !tbody) return;

  const headerCells = Array.from(thead.querySelectorAll("th"));
  const headers = headerCells.map(th => (th.textContent || "").trim().toLowerCase());

  const idxType = headers.indexOf("type");
  const idxDomain = headers.indexOf("domain");

  // If we can't find expected columns, don't break the page.
  if (idxType === -1 || idxDomain === -1) {
    console.warn("Glossary filter: couldn't find Type/Domain columns in table header.", headers);
    return;
  }

  const rows = Array.from(tbody.querySelectorAll("tr"));

  // Build a list of domains from the table
  const domainSet = new Set();
  rows.forEach(tr => {
    const tds = Array.from(tr.querySelectorAll("td"));
    const domain = (tds[idxDomain]?.textContent || "").trim();
    if (domain) domainSet.add(domain);
  });

  // Populate dropdown (preserve the first option: "All domains")
  if (domainSelect) {
    // Clear all options except the first one
    while (domainSelect.options.length > 1) domainSelect.remove(1);

    Array.from(domainSet)
      .sort((a, b) => a.localeCompare(b))
      .forEach(d => {
        const opt = document.createElement("option");
        opt.value = d;
        opt.textContent = d;
        domainSelect.appendChild(opt);
      });
  }

  // State
  let activeType = "all";     // all | term | acronym | metric
  let activeDomain = "";      // "" means all
  let searchQuery = "";

  function normalize(s) {
    return (s || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  function applyFilters() {
    const q = normalize(searchQuery);

    rows.forEach(tr => {
      const tds = Array.from(tr.querySelectorAll("td"));
      const rowType = normalize(tds[idxType]?.textContent);
      const rowDomain = (tds[idxDomain]?.textContent || "").trim();

      const matchesType = (activeType === "all") || (rowType === activeType);
      const matchesDomain = (!activeDomain) || (rowDomain === activeDomain);

      // Search across all cells
      const rowText = normalize(tr.textContent);
      const matchesSearch = (!q) || rowText.includes(q);

      tr.style.display = (matchesType && matchesDomain && matchesSearch) ? "" : "none";
    });
  }

  // Button wiring
  typeButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      typeButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      activeType = (btn.getAttribute("data-type") || "all").toLowerCase();
      applyFilters();
    });
  });

  // Default active button: All
  const allBtn = typeButtons.find(b => (b.getAttribute("data-type") || "").toLowerCase() === "all");
  if (allBtn) allBtn.classList.add("active");

  // Domain dropdown wiring
  if (domainSelect) {
    domainSelect.addEventListener("change", () => {
      activeDomain = domainSelect.value || "";
      applyFilters();
    });
  }

  // Search wiring
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      searchQuery = searchInput.value || "";
      applyFilters();
    });
  }

  // Initial filter pass
  applyFilters();
});
