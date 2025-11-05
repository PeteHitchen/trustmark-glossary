(function () {
  function onReady(fn){ document.readyState!=="loading" ? fn() : document.addEventListener("DOMContentLoaded", fn); }
  function norm(s){ return (s??"").toString().trim().toLowerCase(); }
  function bucketize(typeText) {
    const t = norm(typeText);
    if (t.includes("acronym")) return "acronym";
    if (t.includes("metric"))  return "metric";
    if (t.includes("term") || t.includes("definition")) return "term";
    return "";
  }
  function findGlossaryTable() {
    const tables = document.querySelectorAll(".md-typeset table");
    for (const t of tables) {
      const thead = t.tHead || t.querySelector("thead");
      if (!thead) continue;
      const headers = Array.from(thead.querySelectorAll("th,td")).map(h => norm(h.textContent));
      if (headers.includes("name") && (headers.includes("definition") || headers.includes("type"))) return t;
    } return null;
  }
  function comparator(idx, dir) {
    return (a,b) => {
      const A = (a.cells[idx]?.textContent ?? "").trim();
      const B = (b.cells[idx]?.textContent ?? "").trim();
      const An = parseFloat(A.replace(/,/g,"")), Bn = parseFloat(B.replace(/,/g,""));
      const aNum = !isNaN(An) && /^[\d\.,]+$/.test(A);
      const bNum = !isNaN(Bn) && /^[\d\.,]+$/.test(B);
      if (aNum && bNum) return dir==="asc" ? An-Bn : Bn-An;
      return dir==="asc" ? A.localeCompare(B) : B.localeCompare(A);
    };
  }
  function enhance(table){
    const thead = table.tHead || table.querySelector("thead");
    const tbody = table.tBodies[0] || table.querySelector("tbody");
    if (!thead || !tbody) return;

    const headers = Array.from(thead.querySelectorAll("th,td"));
    const rows = Array.from(tbody.rows);
    const headerNames = headers.map(h => norm(h.textContent));
    let typeIdx = headerNames.findIndex(h => ["type","types","category","classification"].includes(h));

    // sorting
    headers.forEach((th, idx) => {
      th.style.cursor = "pointer"; th.title = "Click to sort";
      th.addEventListener("click", () => {
        const current = th.getAttribute("data-sort") || "none";
        const next = current==="asc" ? "desc" : "asc";
        headers.forEach(h=>h.removeAttribute("data-sort"));
        th.setAttribute("data-sort", next);
        const sorted = rows.slice().sort(comparator(idx, next));
        sorted.forEach(r=>tbody.appendChild(r));
        applyFilters();
      });
    });

    const btns = document.querySelectorAll(".glossary-controls .tm-btn");
    const search = document.getElementById("glossary-search");
    let active = "all";

    let badge = document.querySelector(".glossary-count");
    if (!badge) {
      badge = document.createElement("div");
      badge.className = "glossary-count";
      document.querySelector(".glossary-controls")?.appendChild(badge);
    }

    function matchesBucket(row){
      if (active==="all" || typeIdx===-1) return true;
      const val = row.cells[typeIdx]?.textContent ?? "";
      return bucketize(val) === active;
    }
    function matchesSearch(row){
      const q = norm(search?.value);
      if (!q) return true;
      for (let i=0;i<row.cells.length;i++){
        if (norm(row.cells[i].textContent).includes(q)) return true;
      }
      return false;
    }
    function applyFilters(){
      let shown=0;
      rows.forEach(r=>{
        const ok = matchesBucket(r) && matchesSearch(r);
        r.style.display = ok ? "" : "none";
        if (ok) shown++;
      });
      badge.textContent = `${shown} / ${rows.length} shown`;
    }

    btns.forEach(btn=>{
      btn.addEventListener("click", ()=>{
        btns.forEach(b=>b.classList.remove("active"));
        btn.classList.add("active");
        active = btn.getAttribute("data-type") || "all";
        applyFilters();
      });
    });
    document.querySelector('.tm-btn[data-type="all"]')?.classList.add("active");
    search?.addEventListener("input", applyFilters);
    applyFilters();
  }

  onReady(()=>{
    const t = findGlossaryTable();
    if (t) return enhance(t);
    const obs = new MutationObserver(()=>{
      const t2 = findGlossaryTable();
      if (t2){ obs.disconnect(); enhance(t2); }
    });
    obs.observe(document.body, { childList:true, subtree:true });
  });
})();
