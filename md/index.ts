const controls = document.querySelector<HTMLFormElement>("#paper-controls")!;
const search = document.querySelector<HTMLInputElement>("#paper-search")!;
const filterButtons = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-filter]"));
const papers = Array.from(document.querySelectorAll<HTMLDetailsElement>(".paper"));
const groups = Array.from(document.querySelectorAll<HTMLElement>(".paper-group"));
const resultCount = document.querySelector<HTMLElement>("#result-count")!;
const emptyState = document.querySelector<HTMLElement>("#empty-state")!;
const resetFilters = document.querySelector<HTMLButtonElement>("#reset-filters")!;
let selectedStatus = "all";

function updatePapers(): void {
  const words = search.value.toLocaleLowerCase("en-US").trim().split(" ").filter(Boolean);
  let visibleCount = 0;

  for (const paper of papers) {
    const matchesStatus = selectedStatus === "all" || paper.dataset.status === selectedStatus;
    const matchesSearch = words.every(word => paper.dataset.search!.includes(word));
    paper.hidden = !(matchesStatus && matchesSearch);
    if (!paper.hidden) visibleCount += 1;
  }

  for (const group of groups) {
    const groupPapers = Array.from(group.querySelectorAll<HTMLElement>(".paper"));
    group.hidden = groupPapers.every(paper => paper.hidden);
  }

  for (const button of filterButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.filter === selectedStatus));
  }

  if (visibleCount === papers.length) {
    resultCount.textContent = `${visibleCount} ${visibleCount === 1 ? "paper" : "papers"}`;
  } else {
    resultCount.textContent = `${visibleCount} / ${papers.length}`;
  }

  emptyState.hidden = visibleCount !== 0;
}

controls.hidden = false;
controls.addEventListener("submit", event => event.preventDefault());
search.addEventListener("input", updatePapers);

for (const button of filterButtons) {
  button.addEventListener("click", () => {
    selectedStatus = button.dataset.filter!;
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
