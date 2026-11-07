(() => {
  document.addEventListener("error", (event) => {
    const image = event.target;
    if (image instanceof HTMLImageElement && image.dataset.fallback && !image.dataset.fallbackApplied) {
      image.dataset.fallbackApplied = "true";
      image.src = image.dataset.fallback;
    }
  }, true);

  const storageKey = "cinescope-watchlist:v1";
  const dialog = document.querySelector("#cine-watchlist");
  const list = document.querySelector("#cine-watchlist-items");
  const empty = document.querySelector("#cine-watchlist-empty");
  const count = document.querySelector("#cine-watchlist-count");
  const pickButton = document.querySelector("#cine-watchlist-pick");
  const pickResult = document.querySelector("#cine-watchlist-pick-result");
  const searchInput = document.querySelector("#cine-watchlist-search");
  const sortSelect = document.querySelector("#cine-watchlist-sort");
  const exportButton = document.querySelector("#cine-watchlist-export");
  const results = document.querySelector("#cine-watchlist-results");
  const noMatches = document.querySelector("#cine-watchlist-no-matches");
  if (!dialog || !list || !empty || !count || !pickButton || !pickResult || !searchInput || !sortSelect || !exportButton || !results || !noMatches) return;
  let memoryItems;

  function readItems() {
    try {
      const parsed = JSON.parse(localStorage.getItem(storageKey) || "[]");
      if (!Array.isArray(parsed)) return [];
      return parsed.filter((item) => item && /^\d+$/.test(String(item.id)) && typeof item.title === "string");
    } catch {
      return memoryItems || [];
    }
  }

  function saveItems(items) {
    memoryItems = items.slice(0, 100);
    try {
      localStorage.setItem(storageKey, JSON.stringify(memoryItems));
    } catch {
      // Keep the interface usable if browser storage is disabled or full.
    }
  }

  function visibleItems(items) {
    const query = searchInput.value.trim().toLowerCase();
    const filtered = items.filter((item) => `${item.title} ${item.year} ${item.genre}`.toLowerCase().includes(query));
    if (sortSelect.value === "title") filtered.sort((a, b) => a.title.localeCompare(b.title));
    if (sortSelect.value === "rating") filtered.sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));
    return filtered;
  }

  function posterFor(button) {
    const source = button.closest(".cine-card")?.querySelector("img")?.currentSrc
      || button.closest(".cine-detail")?.querySelector("img")?.currentSrc;
    if (!source) return "";
    try {
      const url = new URL(source, location.origin);
      return url.protocol === "https:" && (url.hostname === "image.tmdb.org" || url.origin === location.origin)
        ? url.href
        : "";
    } catch {
      return "";
    }
  }

  function updateButtons(items) {
    const saved = new Set(items.map((item) => String(item.id)));
    document.querySelectorAll(".cine-watchlist-save").forEach((button) => {
      const isSaved = saved.has(button.dataset.movieId);
      button.setAttribute("aria-pressed", String(isSaved));
      button.setAttribute("aria-label", `${isSaved ? "Remove" : "Save"} ${button.dataset.title} ${isSaved ? "from" : "to"} watchlist`);
      const icon = button.querySelector("[aria-hidden]");
      if (icon) icon.textContent = isSaved ? "✓" : "＋";
      if (button.classList.contains("cine-watchlist-detail")) {
        button.lastChild.textContent = isSaved ? " In your watchlist" : " Add to watchlist";
      }
    });
    count.textContent = String(items.length);
  }

  function renderList() {
    const allItems = readItems();
    const items = visibleItems(allItems);
    list.replaceChildren();
    empty.hidden = allItems.length > 0;
    noMatches.hidden = allItems.length === 0 || items.length > 0;
    pickButton.disabled = items.length === 0;
    searchInput.disabled = allItems.length === 0;
    sortSelect.disabled = allItems.length === 0;
    exportButton.disabled = allItems.length === 0;
    results.hidden = allItems.length === 0;
    results.textContent = `${items.length} of ${allItems.length} saved films`;
    pickResult.replaceChildren();
    pickResult.hidden = true;
    items.forEach((item) => {
      const row = document.createElement("li");
      const link = document.createElement("a");
      link.className = "cine-watchlist-item";
      link.href = /^\/movie\/\d+\/$/.test(item.href) ? item.href : "#";
      if (item.poster) {
        const image = document.createElement("img");
        image.src = item.poster;
        image.alt = "";
        image.loading = "lazy";
        image.width = 48;
        image.height = 72;
        link.append(image);
      }
      const detail = document.createElement("span");
      detail.className = "cine-watchlist-copy";
      const title = document.createElement("strong");
      title.textContent = item.title.slice(0, 200);
      const meta = document.createElement("small");
      meta.textContent = [item.year, item.genre, item.rating ? `★ ${item.rating}` : ""].filter(Boolean).join(" · ");
      detail.append(title, meta);
      link.append(detail);
      const remove = document.createElement("button");
      remove.className = "cine-watchlist-remove";
      remove.type = "button";
      remove.dataset.removeId = String(item.id);
      remove.setAttribute("aria-label", `Remove ${item.title.slice(0, 200)} from watchlist`);
      remove.textContent = "×";
      row.append(link, remove);
      list.append(row);
    });
    updateButtons(items);
  }

  document.addEventListener("click", (event) => {
    const saveButton = event.target.closest(".cine-watchlist-save");
    if (saveButton) {
      const items = readItems();
      const id = saveButton.dataset.movieId;
      const existing = items.findIndex((item) => String(item.id) === id);
      if (existing >= 0) items.splice(existing, 1);
      else {
        const href = saveButton.closest(".cine-card")?.querySelector("a[href*='/movie/']")?.getAttribute("href")
          || location.pathname;
        items.unshift({
          id,
          title: saveButton.dataset.title || "Untitled film",
          year: saveButton.dataset.year || "",
          genre: saveButton.dataset.genre || "",
          rating: saveButton.dataset.rating || "",
          href: /^\/movie\/\d+\/$/.test(href) ? href : `/movie/${id}/`,
          poster: posterFor(saveButton),
        });
      }
      saveItems(items);
      renderList();
      return;
    }
    const removeButton = event.target.closest("[data-remove-id]");
    if (removeButton) {
      saveItems(readItems().filter((item) => String(item.id) !== removeButton.dataset.removeId));
      renderList();
    }
  });

  document.querySelector("#cine-watchlist-toggle").addEventListener("click", () => {
    renderList();
    dialog.showModal();
  });
  pickButton.addEventListener("click", () => {
    const items = visibleItems(readItems());
    if (!items.length) return;
    const item = items[Math.floor(Math.random() * items.length)];
    const link = document.createElement("a");
    link.href = /^\/movie\/\d+\/$/.test(item.href) ? item.href : `/movie/${item.id}/`;
    link.textContent = item.title.slice(0, 200);
    pickResult.replaceChildren(document.createTextNode("Your next watch: "), link);
    pickResult.hidden = false;
  });
  dialog.querySelector(".cine-watchlist-close").addEventListener("click", () => dialog.close());
  searchInput.addEventListener("input", renderList);
  sortSelect.addEventListener("change", renderList);
  exportButton.addEventListener("click", () => {
    const blob = new Blob([`${JSON.stringify(readItems(), null, 2)}\n`], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "cinescope-watchlist.json";
    link.click();
    window.setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  renderList();
})();
