import { mergeWatchlistItems, normalizeWatchlistItems, persistWatchlist, safePoster, visibleWatchlistItems } from "./watchlist-tools.mjs";

(() => {
  const copyViewButton = document.querySelector("#cine-copy-view");
  const copyViewStatus = document.querySelector("#cine-copy-status");
  if (copyViewButton && copyViewStatus) {
    copyViewButton.addEventListener("click", async () => {
      try {
        await navigator.clipboard.writeText(copyViewButton.dataset.copyUrl || window.location.href);
        copyViewStatus.textContent = copyViewButton.dataset.copiedMessage || "Filtered link copied.";
      } catch {
        copyViewStatus.textContent = "Could not copy. Copy the page address instead.";
      }
      copyViewStatus.hidden = false;
    });
  }

  const revealTargets = document.querySelectorAll(".cine-section-heading, .cine-genre-link, .cine-card");
  if (revealTargets.length && "IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    document.documentElement.classList.add("has-scroll-reveal");
    const revealObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-revealed");
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
    revealTargets.forEach((target) => revealObserver.observe(target));
  }

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
  const importButton = document.querySelector("#cine-watchlist-import");
  const importInput = document.querySelector("#cine-watchlist-file");
  const results = document.querySelector("#cine-watchlist-results");
  const noMatches = document.querySelector("#cine-watchlist-no-matches");
  if (!dialog || !list || !empty || !count || !pickButton || !pickResult || !searchInput || !sortSelect || !exportButton || !importButton || !importInput || !results || !noMatches) return;
  let memoryItems;
  const maxImportBytes = 256_000;

  function readItems() {
    try {
      const parsed = JSON.parse(localStorage.getItem(storageKey) || "[]");
      return normalizeWatchlistItems(parsed, location.origin);
    } catch {
      return memoryItems || [];
    }
  }

  function saveItems(items) {
    memoryItems = items.slice(0, 100);
    try {
      return persistWatchlist(localStorage, storageKey, memoryItems);
    } catch {
      return false;
    }
  }

  function visibleItems(items) {
    return visibleWatchlistItems(items, searchInput.value, sortSelect.value);
  }

  function posterFor(button) {
    const source = button.closest(".cine-card")?.querySelector("img")?.currentSrc
      || button.closest(".cine-detail")?.querySelector("img")?.currentSrc;
    return safePoster(source, location.origin);
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
    updateButtons(allItems);
  }

  document.addEventListener("click", (event) => {
    const saveButton = event.target.closest(".cine-watchlist-save");
    if (saveButton) {
      const items = readItems();
      const id = saveButton.dataset.movieId;
      const existing = items.findIndex((item) => String(item.id) === id);
      if (existing >= 0) items.splice(existing, 1);
      else {
        if (items.length >= 100) {
          const message = "Your watchlist is full. Remove a film before saving another.";
          const globalStatus = document.querySelector("#cine-watchlist-global-status");
          if (globalStatus) globalStatus.textContent = message;
          if (results) { results.textContent = message; results.hidden = false; }
          return;
        }
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
      const persisted = saveItems(items);
      renderList();
      const globalStatus = document.querySelector("#cine-watchlist-global-status");
      if (globalStatus) globalStatus.textContent = persisted
        ? existing >= 0 ? "Film removed from your watchlist." : "Film saved to your watchlist."
        : "Browser storage is unavailable. Watchlist changes are temporary and can be lost on reload.";
      return;
    }
    const removeButton = event.target.closest("[data-remove-id]");
    if (removeButton) {
      const persisted = saveItems(readItems().filter((item) => String(item.id) !== removeButton.dataset.removeId));
      renderList();
      const globalStatus = document.querySelector("#cine-watchlist-global-status");
      if (globalStatus) globalStatus.textContent = persisted
        ? "Film removed from your watchlist."
        : "Browser storage is unavailable. Watchlist changes are temporary and can be lost on reload.";
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
  importButton.addEventListener("click", () => importInput.click());
  importInput.addEventListener("change", async () => {
    const file = importInput.files?.[0];
    if (!file) return;
    try {
      if (file.size > maxImportBytes) throw new Error("This backup is larger than 256 KB.");
      const parsed = JSON.parse(await file.text());
      if (!Array.isArray(parsed)) throw new Error("Choose a CineScope watchlist JSON export.");
      const existing = readItems();
      const merged = mergeWatchlistItems(existing, parsed, location.origin);
      const persisted = saveItems(merged);
      renderList();
      results.textContent = persisted
        ? `Added ${merged.length - existing.length} films; duplicates and invalid entries were skipped.`
        : `Added ${merged.length - existing.length} films; changes are temporary because browser storage is unavailable.`;
      results.hidden = false;
    } catch (error) {
      results.textContent = error instanceof SyntaxError ? "That file is not valid JSON." : error.message;
      results.hidden = false;
    } finally {
      importInput.value = "";
    }
  });
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
  window.addEventListener("storage", (event) => {
    if (event.key === storageKey || event.key === null) renderList();
  });
  renderList();
})();
