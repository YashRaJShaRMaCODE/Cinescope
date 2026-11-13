const validId = /^\d{1,20}$/;

export function visibleWatchlistItems(items, query, sort) {
  const normalizedQuery = query.trim().toLowerCase();
  const visible = items.filter((item) => `${item.title} ${item.year} ${item.genre}`.toLowerCase().includes(normalizedQuery));
  if (sort === "title") visible.sort((a, b) => a.title.localeCompare(b.title));
  if (sort === "rating") visible.sort((a, b) => Number(b.rating || 0) - Number(a.rating || 0));
  return visible;
}

export function persistWatchlist(storage, key, items) {
  try {
    storage.setItem(key, JSON.stringify(items));
    return true;
  } catch {
    return false;
  }
}

export function safePoster(value, origin) {
  if (typeof value !== "string" || !value) return "";
  try {
    const url = new URL(value, origin);
    return url.origin === origin || (url.protocol === "https:" && url.hostname === "image.tmdb.org")
      ? url.href
      : "";
  } catch {
    return "";
  }
}

export function normalizeWatchlistItem(item, origin) {
  if (!item || !validId.test(String(item.id)) || typeof item.title !== "string") return null;
  return {
    id: String(item.id),
    title: item.title.slice(0, 200),
    year: typeof item.year === "string" || typeof item.year === "number" ? String(item.year).slice(0, 4) : "",
    genre: typeof item.genre === "string" ? item.genre.slice(0, 80) : "",
    rating: item.rating !== "" && item.rating != null && Number.isFinite(Number(item.rating))
      ? String(item.rating).slice(0, 5)
      : "",
    href: `/movie/${String(item.id)}/`,
    poster: safePoster(item.poster, origin),
  };
}

export function normalizeWatchlistItems(items, origin, limit = 100) {
  if (!Array.isArray(items)) return [];
  return items.map((item) => normalizeWatchlistItem(item, origin)).filter(Boolean).slice(0, limit);
}

export function mergeWatchlistItems(existing, incoming, origin, limit = 100) {
  const merged = normalizeWatchlistItems(existing, origin, limit);
  const ids = new Set(merged.map((item) => item.id));
  if (!Array.isArray(incoming)) return merged;
  for (const candidate of incoming) {
    if (merged.length >= limit) break;
    const item = normalizeWatchlistItem(candidate, origin);
    if (item && !ids.has(item.id)) {
      ids.add(item.id);
      merged.push(item);
    }
  }
  return merged;
}
