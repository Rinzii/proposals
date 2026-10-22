"use strict";
const controls = document.querySelector("#paper-controls");
const search = document.querySelector("#paper-search");
const filterButtons = Array.from(document.querySelectorAll("[data-filter]"));
const papers = Array.from(document.querySelectorAll(".paper"));
const groups = Array.from(document.querySelectorAll(".paper-group"));
const resultCount = document.querySelector("#result-count");
const emptyState = document.querySelector("#empty-state");
const resetFilters = document.querySelector("#reset-filters");
let selectedStatus = "all";
function updatePapers() {
    const words = search.value.toLocaleLowerCase("en-US").trim().split(" ").filter(Boolean);
    let visibleCount = 0;
    for (const paper of papers) {
        const matchesStatus = selectedStatus === "all" || paper.dataset.status === selectedStatus;
        const matchesSearch = words.every(word => paper.dataset.search.includes(word));
        paper.hidden = !(matchesStatus && matchesSearch);
        if (!paper.hidden)
            visibleCount += 1;
    }
    for (const group of groups) {
        const groupPapers = Array.from(group.querySelectorAll(".paper"));
        group.hidden = groupPapers.every(paper => paper.hidden);
    }
    for (const button of filterButtons) {
        button.setAttribute("aria-pressed", String(button.dataset.filter === selectedStatus));
    }
    if (visibleCount === papers.length) {
        resultCount.textContent = `${visibleCount} ${visibleCount === 1 ? "paper" : "papers"}`;
    }
    else {
        resultCount.textContent = `${visibleCount} / ${papers.length}`;
    }
    emptyState.hidden = visibleCount !== 0;
}
controls.hidden = false;
controls.addEventListener("submit", event => event.preventDefault());
search.addEventListener("input", updatePapers);
for (const button of filterButtons) {
    button.addEventListener("click", () => {
        selectedStatus = button.dataset.filter;
        updatePapers();
    });
}
resetFilters.addEventListener("click", () => {
    search.value = "";
    selectedStatus = "all";
    updatePapers();
    search.focus();
});
updatePapers();
