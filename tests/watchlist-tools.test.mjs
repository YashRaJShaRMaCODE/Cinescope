import assert from "node:assert/strict";
import test from "node:test";
import { mergeWatchlistItems, normalizeWatchlistItem } from "../static/watchlist-tools.mjs";

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
