import assert from "node:assert/strict";
import test from "node:test";
import { mergeWatchlistItems, normalizeWatchlistItem, normalizeWatchlistItems, persistWatchlist, visibleWatchlistItems } from "../static/watchlist-tools.mjs";

const origin = "https://cinescope.example";
const item = (id, extra = {}) => ({ id, title: `Film ${id}`, ...extra });

test("watchlist import skips duplicates without crowding out later valid films", () => {
  const merged = mergeWatchlistItems(
    [item(1)],
    [item(1), item(1), { id: "bad-id", title: "Unsafe" }, item(2), item(2), item(3)],
    origin,
    3,
  );

  assert.deepEqual(merged.map((film) => film.id), ["1", "2", "3"]);
});

test("watchlist normalization keeps only safe poster hosts", () => {
  assert.equal(normalizeWatchlistItem(item(1, { poster: "https://image.tmdb.org/poster.jpg" }), origin).poster,
    "https://image.tmdb.org/poster.jpg");
  assert.equal(normalizeWatchlistItem(item(2, { poster: "https://attacker.example/poster.jpg" }), origin).poster, "");
  assert.equal(normalizeWatchlistItem(item(3, { poster: "/poster.jpg" }), origin).poster,
    "https://cinescope.example/poster.jpg");
});

test("watchlist search and sorting stay local and work across saved metadata", () => {
  const films = normalizeWatchlistItems([
    item(1, { title: "Zodiac", year: "2007", genre: "Drama", rating: "7.8" }),
    item(2, { title: "Arrival", year: "2016", genre: "Sci-Fi", rating: "8.0" }),
  ], origin);
  assert.deepEqual(visibleWatchlistItems(films, "sci-fi", "recent").map((film) => film.id), ["2"]);
  assert.deepEqual(visibleWatchlistItems(films, "", "title").map((film) => film.id), ["2", "1"]);
  assert.deepEqual(visibleWatchlistItems(films, "", "rating").map((film) => film.id), ["2", "1"]);
});

test("watchlist persistence reports browser storage failures", () => {
  const values = new Map();
  const storage = { setItem: (key, value) => values.set(key, value) };
  assert.equal(persistWatchlist(storage, "watchlist", normalizeWatchlistItems([item(1)], origin)), true);
  assert.equal(JSON.parse(values.get("watchlist"))[0].id, "1");
  assert.equal(persistWatchlist({ setItem() { throw new Error("quota"); } }, "watchlist", []), false);
});
