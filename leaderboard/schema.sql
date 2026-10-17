-- Global leaderboard for the Strait of Hormuz game.
CREATE TABLE IF NOT EXISTS scores (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT    NOT NULL,
  flag        TEXT    NOT NULL,
  nm          INTEGER NOT NULL,
  damage      INTEGER NOT NULL,
  duration_ms INTEGER NOT NULL,
  created_at  INTEGER NOT NULL,   -- unix ms
  ip_hash     TEXT    NOT NULL    -- salted hash, only used for rate limiting
);
CREATE INDEX IF NOT EXISTS idx_scores_rank ON scores (nm DESC, damage ASC, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_scores_ip   ON scores (ip_hash, created_at);
