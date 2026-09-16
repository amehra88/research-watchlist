/* Research Desk \u2014 RIS4 portal app (Task 7: shell, Today, Tickers, Notes, Thesis, Status).
 *
 * Vanilla ES2020, no build step, no framework. Reads the static JSON bundle that
 * scripts/portal/build_portal.py publishes next to this file (data/manifest.json
 * first, everything else on demand). The only persistence is a localStorage read
 * marker under `ris.read.v1`; every access is wrapped, and the page renders
 * correctly when storage throws or comes back empty.
 *
 * Extension points for Task 8: `views` (route head -> view fn), `tickerTabs`
 * (ticker sub-tab -> view fn) and `morePages` (More sub-page -> view fn). Adding
 * a screen is adding a map entry; nothing here branches on route names.
 *
 * A view is `fn(parts) -> {title, html, after?}` or a Promise of one. `paint()`
 * appends the "as of" footer to every view, so no screen can ship without it.
 */
(function () {
  'use strict';

  var MANIFEST_PATH = 'data/manifest.json';
  var STORE_KEY = 'ris.read.v1';

  var STATE = {
    manifest: null,
    manifestError: null,
    store: null,        // {cards, notes, lastVisit, themeStages} \u2014 always an object
    since: null,        // snapshot of the PREVIOUS visit, taken before we stamp
    md: null            // markdown-it instance, or null if the vendor file failed
  };

  /* ------------------------------------------------------------- helpers -- */

  var ESCAPES = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };

  function esc(value) {
    if (value === null || value === undefined) return '';
    return String(value).replace(/[&<>"']/g, function (c) { return ESCAPES[c]; });
  }

  function el(tag, attrs, html) {
    var node = document.createElement(tag);
    if (attrs) {
      for (var k in attrs) {
        if (Object.prototype.hasOwnProperty.call(attrs, k)) node.setAttribute(k, attrs[k]);
      }
    }
    if (html !== undefined && html !== null) node.innerHTML = html;
    return node;
  }

  function isObj(v) { return !!v && typeof v === 'object' && !Array.isArray(v); }
  function arr(v) { return Array.isArray(v) ? v : []; }
  function href(parts) { return '#/' + parts.map(encodeURIComponent).join('/'); }

  /* Every link that leaves the app \u2014 news `url`, SEC `filing_url`, a markdown
   * link in a note \u2014 opens in a new context. A plain navigation inside the
   * phone's in-app web view replaces the desk with no chrome to come back from.
   * One helper, used by the markdown-it link_open rule AND by every hand-built
   * anchor, so the two can never drift. In-app "#/..." routes get nothing. */
  function extAttrs(url) {
    var s = (url === null || url === undefined) ? '' : String(url);
    return s.charAt(0) === '#' ? '' : ' target="_blank" rel="noopener noreferrer"';
  }

  /* Bundle-supplied URLs are data, not code: only http(s) ever becomes an href,
   * so a `javascript:` or `data:` string in a news row renders as inert text. */
  function safeURL(url) {
    var s = (url === null || url === undefined) ? '' : String(url).trim();
    return /^https?:\/\//i.test(s) ? s : '';
  }

  /* An external link, or the plain escaped text when the URL is not http(s). */
  function extLink(url, text, cls) {
    var u = safeURL(url);
    var label = esc(text === undefined || text === null || text === '' ? url : text);
    if (!u) return label;
    return '<a' + (cls ? ' class="' + cls + '"' : '') + ' href="' + esc(u) + '"' + extAttrs(u) + '>' + label + '</a>';
  }

  function kb(n) {
    if (typeof n !== 'number' || !isFinite(n)) return '\u2014';
    if (n < 1024) return n + ' B';
    if (n < 1048576) return (n / 1024).toFixed(1) + ' KB';
    return (n / 1048576).toFixed(1) + ' MB';
  }

  /* built_at carries 6 fractional-second digits (\u202638.662960+00:00). WebKit's
   * Date parser rejects more than 3, which would print "Invalid Date" on every
   * screen \u2014 trim to 3 and fall back to the raw string if it still won't parse. */
  function parseTS(value) {
    if (!value) return null;
    var d = new Date(String(value).replace(/(\.\d{3})\d+/, '$1'));
    return isNaN(d.getTime()) ? null : d;
  }

  function fmtTS(value) {
    var d = parseTS(value);
    if (!d) return value ? String(value) : '\u2014';
    var p = function (n) { return (n < 10 ? '0' : '') + n; };
    return d.getFullYear() + '-' + p(d.getMonth() + 1) + '-' + p(d.getDate()) +
      ' ' + p(d.getHours()) + ':' + p(d.getMinutes());
  }

  var TIERS = {
    tier_1_bctk: 'T1',
    tier_2_active_candidates: 'T2',
    tier_3_watchlist: 'T3',
    tier_4_ecosystem: 'T4',
    none: 'no tier'
  };
  var TIER_RANK = {
    tier_1_bctk: 0, tier_2_active_candidates: 1, tier_3_watchlist: 2, tier_4_ecosystem: 3, none: 4
  };

  function tierChip(tier, alsoIn) {
    var label = TIERS[tier] || (tier ? String(tier) : 'no tier');
    var cls = 'tier' + (tier === 'tier_1_bctk' ? ' tier-1' : '');
    var out = '<span class="' + cls + '">' + esc(label) + '</span>';
    arr(alsoIn).forEach(function (t) {
      out += ' <span class="tier">also ' + esc(TIERS[t] || t) + '</span>';
    });
    return out;
  }

  var STATUS_PILL = { confirmed: 'pill-ok', challenged: 'pill-bad', open: 'pill-accent', retired: 'pill-neutral' };

  function statusPill(status) {
    var s = status ? String(status) : 'unknown';
    return '<span class="pill ' + (STATUS_PILL[s] || 'pill-neutral') + '">' + esc(s) + '</span>';
  }

  function chips(items, hrefFn) {
    var list = arr(items);
    if (!list.length) return '';
    return '<ul class="chips">' + list.map(function (item) {
      var text = esc(item);
      if (!hrefFn) return '<li><span class="chip">' + text + '</span></li>';
      var target = hrefFn(item);
      return '<li><a class="chip" href="' + esc(target) + '"' + extAttrs(target) + '>' + text + '</a></li>';
    }).join('') + '</ul>';
  }

  function emptyState(sentence) { return '<p class="empty">' + esc(sentence) + '</p>'; }

  function section(eyebrow, body) {
    return '<section class="section"><span class="eyebrow">' + esc(eyebrow) + '</span>' + body + '</section>';
  }

  function fold(summary, count, body, open) {
    return '<details class="fold"' + (open ? ' open' : '') + '><summary>' + esc(summary) +
      (count === null || count === undefined ? '' : '<span class="n">' + esc(count) + '</span>') +
      '</summary><div class="foldbody">' + body + '</div></details>';
  }

  function stream(text) {
    return '<div class="scrollx"><pre class="stream">' + esc(text) + '</pre></div>';
  }

  /* Markdown only ever reaches the DOM through here. html:false means markdown-it
   * escapes any raw HTML in the source itself; if the vendored library is missing
   * we degrade to the escaped source rather than injecting anything unparsed. */
  function md(text) {
    if (!text) return '';
    if (!STATE.md) return stream(text);
    try {
      return '<div class="prose">' + STATE.md.render(String(text)) + '</div>';
    } catch (e) {
      return stream(text);
    }
  }

  /* ------------------------------------------------------------- storage -- */

  function emptyStore() { return { cards: {}, notes: {}, lastVisit: null, themeStages: {} }; }

  function storeRead() {
    var d = emptyStore();
    try {
      var raw = window.localStorage.getItem(STORE_KEY);
      if (!raw) return d;
      var o = JSON.parse(raw);
      if (!isObj(o)) return d;
      if (isObj(o.cards)) d.cards = o.cards;
      if (isObj(o.notes)) d.notes = o.notes;
      if (typeof o.lastVisit === 'string') d.lastVisit = o.lastVisit;
      if (isObj(o.themeStages)) d.themeStages = o.themeStages;
    } catch (e) { /* private mode, blocked site data, corrupt JSON \u2014 start clean */ }
    return d;
  }

  function storeWrite() {
    try {
      window.localStorage.setItem(STORE_KEY, JSON.stringify(STATE.store));
    } catch (e) { /* quota or blocked storage: the in-memory store still works */ }
  }

  function storeBytes() {
    try { return JSON.stringify(STATE.store).length; } catch (e) { return 0; }
  }

  function isRead(bucket, id) {
    return !!(id && STATE.store && STATE.store[bucket] && STATE.store[bucket][id]);
  }

  function markRead(bucket, id) {
    if (!id || !STATE.store || !STATE.store[bucket]) return;
    if (STATE.store[bucket][id]) return;
    STATE.store[bucket][id] = new Date().toISOString();
    storeWrite();
  }

  /* Read the previous visit BEFORE stamping the new one \u2014 stamping first makes
   * "what changed" permanently empty, which looks exactly like "nothing changed". */
  function stampVisit(manifest) {
    var stages = {};
    arr(manifest.themes).forEach(function (t) {
      if (t && t.slug !== undefined && t.stage !== undefined && t.stage !== null) stages[t.slug] = t.stage;
    });
    STATE.store.themeStages = stages;
    STATE.store.lastVisit = new Date().toISOString();
    storeWrite();
  }

  /* ------------------------------------------------------------- loading -- */

  var jsonCache = {};

  /* Every fetch path on this desk comes out of the bundle itself (manifest
   * `card.file`, a news shard name, a search doc's `f`), so it is data, not a
   * constant. Nothing but a literal data/<name>.json under the bundle root is
   * ever fetched; anything else \u2014 an absolute URL, a traversal, a non-JSON
   * name \u2014 rejects here and lands in the caller's existing "could not load"
   * empty state. The `..` check is not redundant: the character class allows
   * both `.` and `/`, so "data/../secrets.json" matches the pattern. */
  var DATA_PATH_RE = /^data\/[A-Za-z0-9_.\-\/]+\.json$/;

  function isDataPath(path) {
    var p = (path === null || path === undefined) ? '' : String(path);
    return DATA_PATH_RE.test(p) && p.indexOf('..') < 0;
  }

  function loadJSON(path) {
    if (!isDataPath(path)) {
      /* A rejected promise, not a throw: callers handle failure in .catch(). */
      return Promise.reject(new Error('refused non-bundle path ' + path));
    }
    if (jsonCache[path]) return jsonCache[path];
    var p = fetch(path).then(function (r) {
      if (!r.ok) throw new Error('HTTP ' + r.status + ' for ' + path);
      return r.json();
    });
    /* Drop a failed fetch from the cache so a later navigation can retry it;
     * the caller still handles this exact promise. */
    p.catch(function () { if (jsonCache[path] === p) delete jsonCache[path]; });
    jsonCache[path] = p;
    return p;
  }

  function bundlePath(id) {
    var s = String(id);
    /* Never uppercase a route id: 000660.KS and simaai.pvt must match verbatim. */
    return /\.pvt$/.test(s)
      ? 'data/pvt/' + s.slice(0, -4) + '.json'
      : 'data/tickers/' + s + '.json';
  }

  function findTicker(id) {
    var rows = arr(STATE.manifest && STATE.manifest.tickers);
    for (var i = 0; i < rows.length; i++) {
      if (rows[i] && String(rows[i].ticker) === String(id)) return rows[i];
    }
    return null;
  }

  /* manifest.tickers carries n_notes but not note ids, and every note id is
   * "<TICKER>/<file>" \u2014 so an exact unread count comes from counting this
   * ticker's read markers, with no bundle fetch. The standing profile is NOT in
   * n_notes (the builder keeps it out of bundle.notes), so reading one must not
   * be counted here or the ticker would show one unread note too few. */
  function unreadNotes(meta) {
    var total = typeof meta.n_notes === 'number' ? meta.n_notes : 0;
    if (!total) return 0;
    var prefix = String(meta.ticker) + '/';
    var read = 0;
    var notes = (STATE.store && STATE.store.notes) || {};
    for (var id in notes) {
      if (!Object.prototype.hasOwnProperty.call(notes, id)) continue;
      if (id.indexOf(prefix) !== 0) continue;
      if (id.slice(prefix.length) === '_profile.md') continue;
      read++;
    }
    return Math.max(0, total - read);
  }

  /* ---------------------------------------------------------------- rows -- */

  function dot(unread) { return unread ? '<span class="dot"></span>' : '<span class="dot-slot"></span>'; }

  function row(link, top, meta) {
    return '<a class="row" href="' + esc(link) + '"' + extAttrs(link) + '><div class="row-top">' + top + '</div>' +
      (meta ? '<div class="row-meta">' + meta + '</div>' : '') + '</a>';
  }

  /* =========================================================== TODAY ====== */

  /* Day granularity on purpose: last_note is YYYY-MM-DD, so ">= the day you last
   * looked" is the only comparison that does not silently hide a note filed later
   * on a day you already visited. */
  function changedSince() {
    var m = STATE.manifest;
    var prevVisit = STATE.since.lastVisit;
    var out = { first: !prevVisit, notes: [], stages: [] };
    if (prevVisit) {
      var cut = String(prevVisit).slice(0, 10);
      arr(m.tickers).forEach(function (t) {
        if (t && t.last_note && String(t.last_note) >= cut) out.notes.push(t);
      });
      out.notes.sort(function (a, b) { return String(b.last_note).localeCompare(String(a.last_note)); });
    }
    var prev = STATE.since.themeStages || {};
    arr(m.themes).forEach(function (t) {
      if (!t || t.slug === undefined) return;
      var was = prev[t.slug];
      if (was === undefined || was === null) return;
      if (t.stage !== undefined && t.stage !== null && String(t.stage) !== String(was)) {
        out.stages.push({ slug: t.slug, from: was, to: t.stage });
      }
    });
    return out;
  }

  function changedBlock() {
    var c = changedSince();
    if (c.first) {
      return section('Since last visit',
        emptyState('First visit on this device \u2014 nothing to compare against yet. The next visit will list notes and theme stages that moved.'));
    }
    if (!c.notes.length && !c.stages.length) {
      return section('Since last visit',
        emptyState('No new notes and no theme stage changes since ' + fmtTS(STATE.since.lastVisit) + '.'));
    }
    var body = '';
    if (c.notes.length) {
      body += '<ul class="rows">' + c.notes.slice(0, 20).map(function (t) {
        return '<li>' + row(href(['ticker', t.ticker]),
          dot(unreadNotes(t)) + '<span class="row-key">' + esc(t.ticker) + '</span>' +
          '<span class="row-title">' + esc(t.name || '') + '</span>' +
          '<span class="row-right">' + esc(t.last_note) + '</span>',
          tierChip(t.tier) + '<span>note filed</span>') + '</li>';
      }).join('') + '</ul>';
      if (c.notes.length > 20) {
        body += '<p class="empty">' + esc((c.notes.length - 20) + ' more tickers filed notes; see Tickers, sorted by last note.') + '</p>';
      }
    }
    if (c.stages.length) {
      body += '<h3 class="subhead">Theme stages moved</h3><ul class="rows">' + c.stages.map(function (s) {
        return '<li>' + row(href(['theme', s.slug]),
          '<span class="dot-slot"></span><span class="row-title mono">' + esc(s.slug) + '</span>' +
          '<span class="row-right">' + esc(s.from) + ' \u2192 ' + esc(s.to) + '</span>', '') + '</li>';
      }).join('') + '</ul>';
    }
    return section('Since last visit', body);
  }

  function groupByDate(cards) {
    var map = {}, order = [];
    cards.forEach(function (c) {
      var d = (c && c.date) ? String(c.date) : 'undated';
      if (!map[d]) { map[d] = []; order.push(d); }
      map[d].push(c);
    });
    order.sort(function (a, b) { return a < b ? 1 : (a > b ? -1 : 0); });
    return order.map(function (d) { return { date: d, cards: map[d] }; });
  }

  function viewToday() {
    var m = STATE.manifest;
    var cards = arr(m.today && m.today.cards);
    var html = changedBlock();

    if (!cards.length) {
      html += section('Reports', emptyState('No report cards in this build \u2014 the premarket, postmarket, digest and alert jobs had nothing to publish for today.'));
    } else {
      var unreadCount = cards.filter(function (c) { return !isRead('cards', c.id); }).length;
      var body = groupByDate(cards).map(function (g) {
        return '<div class="daterule"><span class="d">' + esc(g.date) + '</span>' +
          '<span class="n">' + esc(g.cards.length + (g.cards.length === 1 ? ' card' : ' cards')) + '</span></div>' +
          '<ul class="rows">' + g.cards.map(function (c) {
            return '<li>' + row(href(['today', c.id]),
              dot(!isRead('cards', c.id)) + '<span class="row-title">' + esc(c.title || c.id) + '</span>',
              '<span class="eyebrow">' + esc(c.kind || 'report') + '</span><span class="num">' + esc(kb(c.bytes)) + '</span>') + '</li>';
          }).join('') + '</ul>';
      }).join('');
      html += section(unreadCount ? 'Reports \u2014 ' + unreadCount + ' unread' : 'Reports', body);
    }

    var up = arr(m.upcoming);
    html += section('Upcoming', up.length
      ? '<ul class="rows">' + up.map(function (u) {
        return '<li>' + row(u.ticker ? href(['ticker', u.ticker]) : '#/today',
          '<span class="dot-slot"></span><span class="row-key">' + esc(u.ticker || '') + '</span>' +
          '<span class="row-title">' + esc(u.title || u.kind || '') + '</span>' +
          '<span class="row-right">' + esc(u.date || '') + '</span>', '') + '</li>';
      }).join('') + '</ul>'
      : emptyState('No forward calendar in this build \u2014 the transcript pipeline fetches the event calendar live and never stores it, so there is nothing to publish here yet.'));

    return { title: 'Today', html: html };
  }

  /* A card id is "<kind>:<YYYY-MM-DD>" in every shard this builder writes, so an
   * archive card (More \u2192 Reports, any of the last 14 days) resolves to its own
   * shard without a second route: take the date off the id, and only accept the
   * path if the manifest actually lists that file. Today's cards still resolve
   * from manifest.today.cards, which carries title/bytes for the head. */
  function archiveCardFile(id) {
    var s = String(id);
    var cut = s.lastIndexOf(':');
    var day = cut < 0 ? '' : s.slice(cut + 1);
    if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) return null;
    var path = 'data/reports/' + day + '.json';
    var files = isObj(STATE.manifest.files) ? STATE.manifest.files : {};
    return Object.prototype.hasOwnProperty.call(files, path) ? path : null;
  }

  function viewCard(parts) {
    var id = parts[1];
    var meta = null;
    arr(STATE.manifest.today && STATE.manifest.today.cards).forEach(function (c) {
      if (c && String(c.id) === String(id)) meta = c;
    });
    var file = (meta && meta.file) || archiveCardFile(id);
    if (!meta && !file) {
      return { title: 'Report', html: emptyState('That report is not in this build. Open Today for the cards this bundle actually carries, or More \u2192 Reports for the archive.') };
    }
    if (!file) {
      return { title: (meta && meta.title) || 'Report', html: emptyState('This card has no report file in the bundle.') };
    }
    meta = meta || { id: id, title: id, file: file };
    return loadJSON(file).then(function (payload) {
      var card = meta;
      arr(payload && payload.cards).forEach(function (c) { if (c && String(c.id) === String(id)) card = c; });
      markRead('cards', id);
      var head = '<h2 class="head">' + esc(card.title || id) + '</h2>' +
        '<p class="lede"><span class="mono">' + esc(card.kind || '') + '</span> \u00b7 ' +
        '<span class="mono">' + esc(card.date || '') + '</span> \u00b7 ' +
        '<span class="mono">' + esc(kb(card.bytes)) + '</span></p>';

      var secs = arr(card.sections);
      var body;
      if (!card.text && !secs.length) {
        body = emptyState('This card is listed in the manifest but carries no text in the report file.');
      } else if (secs.length) {
        /* Sections are extracts of `text`, so the full stream goes in a fold of
         * its own rather than being printed twice at full height. */
        body = secs.map(function (s, i) {
          var title = s.title || s.h || ('Section ' + (i + 1));
          return fold(title, kb((s.text || '').length), stream(s.text || ''), i === 0);
        }).join('') + fold('Full report text', kb((card.text || '').length), stream(card.text || ''), false);
      } else {
        body = stream(card.text);
      }
      return { title: card.title || 'Report', html: head + body };
    }).catch(function () {
      return { title: meta.title || 'Report', html: emptyState('Could not load ' + file + ' from this bundle.') };
    });
  }

  /* ========================================================= TICKERS ====== */

  var tickersUI = { q: '', sort: 'last' };

  function tickerRowsHTML() {
    var q = tickersUI.q.trim().toLowerCase();
    var rows = arr(STATE.manifest.tickers).filter(function (t) {
      if (!t || !t.ticker) return false;
      if (!q) return true;
      return String(t.ticker).toLowerCase().indexOf(q) >= 0 ||
        String(t.name || '').toLowerCase().indexOf(q) >= 0;
    });

    var byTicker = function (a, b) { return String(a.ticker).localeCompare(String(b.ticker)); };
    if (tickersUI.sort === 'ticker') {
      rows.sort(byTicker);
    } else if (tickersUI.sort === 'unread') {
      rows.sort(function (a, b) { return (unreadNotes(b) - unreadNotes(a)) || byTicker(a, b); });
    } else if (tickersUI.sort === 'tier') {
      rows.sort(function (a, b) {
        var ra = TIER_RANK[a.tier] === undefined ? 9 : TIER_RANK[a.tier];
        var rb = TIER_RANK[b.tier] === undefined ? 9 : TIER_RANK[b.tier];
        return (ra - rb) || byTicker(a, b);
      });
    } else {
      /* last note, newest first; tickers with no note sink to the bottom in a
       * stable ticker order rather than scrambling the comparator. */
      rows.sort(function (a, b) {
        var la = a.last_note || '', lb = b.last_note || '';
        if (la && lb) return (lb < la ? -1 : (lb > la ? 1 : 0)) || byTicker(a, b);
        if (la) return -1;
        if (lb) return 1;
        return byTicker(a, b);
      });
    }

    if (!rows.length) {
      return emptyState(q ? 'No ticker matches \u201c' + tickersUI.q + '\u201d.' : 'This build carries no tickers.');
    }

    return '<ul class="rows">' + rows.map(function (t) {
      var unread = unreadNotes(t);
      var n = typeof t.n_notes === 'number' ? t.n_notes : 0;
      var notesText = n ? (unread + ' unread of ' + n + (n === 1 ? ' note' : ' notes')) : 'no notes';
      var themeCount = arr(t.themes).length;
      var meta = tierChip(t.tier, t.also_in) +
        '<span>' + esc(notesText) + '</span>' +
        '<span>' + esc(themeCount + (themeCount === 1 ? ' theme' : ' themes')) + '</span>';
      if (arr(t.pending_proposals).length) {
        meta += '<span class="pill pill-warn">' + esc(t.pending_proposals.length + ' proposed') + '</span>';
      }
      return '<li>' + row(href(['ticker', t.ticker]),
        dot(unread) + '<span class="row-key">' + esc(t.ticker) + '</span>' +
        '<span class="row-title">' + esc(t.name || '') + '</span>' +
        '<span class="row-right">' + esc(t.last_note || '\u2014') + '</span>',
        meta) + '</li>';
    }).join('') + '</ul>';
  }

  function viewTickers() {
    var total = arr(STATE.manifest.tickers).length;
    var html =
      '<div class="controls">' +
      '<div class="field"><label for="q-tickers">Find</label>' +
      '<input type="search" id="q-tickers" name="q-tickers" placeholder="Ticker or name" value="' + esc(tickersUI.q) + '" autocomplete="off" autocapitalize="off" spellcheck="false"></div>' +
      '<div class="field"><label for="sort-tickers">Sort</label>' +
      '<select id="sort-tickers" name="sort-tickers">' +
      ['last:Last note', 'ticker:Ticker', 'unread:Unread notes', 'tier:Tier'].map(function (opt) {
        var v = opt.split(':')[0], label = opt.split(':')[1];
        return '<option value="' + v + '"' + (tickersUI.sort === v ? ' selected' : '') + '>' + esc(label) + '</option>';
      }).join('') + '</select></div>' +
      '</div>' +
      '<p class="lede">' + esc(total + ' names in this build.') + '</p>' +
      '<div id="ticker-rows">' + tickerRowsHTML() + '</div>';
    return { title: 'Tickers', html: html };
  }

  /* ========================================================== TICKER ====== */

  function tickerStrip(id, active) {
    var tabs = [
      ['notes', 'Notes'], ['thesis', 'Thesis'], ['signals', 'Signals'],
      ['news', 'News'], ['insiders', 'Insiders'], ['etf', 'ETF']
    ];
    return '<nav class="strip" aria-label="Ticker sections">' + tabs.map(function (t) {
      return '<a href="' + esc(href(['ticker', id, t[0]])) + '"' +
        (t[0] === active ? ' aria-current="page"' : '') + '>' + esc(t[1]) + '</a>';
    }).join('') + '</nav>';
  }

  function tickerHead(meta, id) {
    var name = meta ? (meta.name || '') : '';
    var out = '<h2 class="head">' + esc(id) + (name ? ' <span class="muted">' + esc(name) + '</span>' : '') + '</h2>';
    if (meta) {
      out += '<p class="lede">' + tierChip(meta.tier, meta.also_in);
      if (meta.factset_id) out += ' <span class="chip mono">' + esc(meta.factset_id) + '</span>';
      if (meta.orphan_notes) out += ' <span class="pill pill-warn">orphan notes</span>';
      out += '</p>';
      out += chips(meta.themes, function (slug) { return href(['theme', slug]); });
    }
    return out;
  }

  /* The profile note is note-shaped (same id/rel/body keys), so it joins the note
   * list and resolves through the same id lookup. */
  function allNotes(bundle) {
    var list = arr(bundle && bundle.notes).slice();
    if (bundle && isObj(bundle.profile)) list.unshift(bundle.profile);
    return list;
  }

  function notesTab(bundle, meta, id) {
    var notes = allNotes(bundle);
    if (!notes.length) {
      return emptyState('No notes for ' + id + ' in this build' +
        (bundle && bundle.thesis ? ' \u2014 the Thesis tab still carries its drafted assumptions.' : '.'));
    }
    notes = notes.slice().sort(function (a, b) {
      var da = a.date || '', db = b.date || '';
      if (da && db) return db < da ? -1 : (db > da ? 1 : 0);
      if (da) return -1;
      if (db) return 1;
      return 0;
    });
    return '<ul class="rows">' + notes.map(function (n) {
      var unread = !isRead('notes', n.id);
      var meta2 = '<span class="eyebrow">' + esc(n.kind || 'note') + '</span>' +
        (n.period ? '<span class="mono">' + esc(n.period) + '</span>' : '') +
        '<span class="chip">' + esc(n.provenance || 'unknown') + '</span>';
      return '<li>' + row(href(['ticker', id, 'note', n.id]),
        dot(unread) + '<span class="row-title">' + esc(n.title || n.rel || n.id) + '</span>' +
        '<span class="row-right">' + esc(n.date || '\u2014') + '</span>', meta2) + '</li>';
    }).join('') + '</ul>';
  }

  function noteView(bundle, id, noteId) {
    var note = null;
    allNotes(bundle).forEach(function (n) { if (n && String(n.id) === String(noteId)) note = n; });
    if (!note) {
      return emptyState('That note is not in ' + id + '\u2019s bundle. Open the Notes tab for the notes this build carries.');
    }
    markRead('notes', note.id);
    var head = '<h2 class="head">' + esc(note.title || note.rel || note.id) + '</h2>' +
      '<p class="lede"><span class="mono">' + esc(note.kind || 'note') + '</span>' +
      (note.date ? ' \u00b7 <span class="mono">' + esc(note.date) + '</span>' : '') +
      (note.period ? ' \u00b7 <span class="mono">' + esc(note.period) + '</span>' : '') +
      ' \u00b7 <span class="chip">' + esc(note.provenance || 'unknown') + '</span>' +
      ' \u00b7 <span class="mono">notes/' + esc(note.rel || note.id) + '</span></p>';
    if (!note.body) {
      var secs = arr(note.sections);
      return head + (secs.length
        ? secs.map(function (s, i) { return fold(s.h || s.title || ('Section ' + (i + 1)), null, md(s.text), i === 0); }).join('')
        : emptyState('This note has no body in the bundle.'));
    }
    return head + md(note.body);
  }

  function scoresBlock(fm, meta) {
    var scores = isObj(fm.scores) ? fm.scores : {};
    var proposed = isObj(fm.proposed_scores) ? fm.proposed_scores : {};
    var keys = Object.keys(scores);
    var pendingKeys = arr(meta && meta.pending_proposals);
    if (!keys.length && !pendingKeys.length) {
      return section('Scores', emptyState('No scores recorded on this thesis.'));
    }
    var body = '';
    if (keys.length) {
      body += '<dl class="kv">' + keys.map(function (k) {
        var val = esc(scores[k]);
        if (Object.prototype.hasOwnProperty.call(proposed, k)) {
          val += ' <span class="pill pill-warn">proposed ' + esc(proposed[k]) + '</span>';
        }
        return '<dt>' + esc(k) + '</dt><dd>' + val + '</dd>';
      }).join('') + '</dl>';
    }
    if (pendingKeys.length) {
      body += '<h3 class="subhead">Pending proposals</h3><dl class="kv">' + pendingKeys.map(function (p) {
        return '<dt>' + esc(p.key || '') + '</dt><dd>' + esc(p.applied || '\u2014') + ' \u2192 ' +
          esc(p.value || '\u2014') + ' <span class="muted">' + esc(p.since || '') + '</span></dd>';
      }).join('') + '</dl>';
    }
    return section('Scores', body);
  }

  function pressureBars(p) {
    if (!isObj(p)) return '';
    var confirm = typeof p.confirm === 'number' ? p.confirm : 0;
    var challenge = typeof p.challenge === 'number' ? p.challenge : 0;
    var max = Math.max(confirm, challenge, 1);
    var bar = function (label, value, cls) {
      var pct = Math.max(0, Math.min(100, (value / max) * 100));
      return '<div class="pbar"><span class="lbl">' + esc(label) + '</span>' +
        '<span class="track"><span class="fill ' + cls + '" style="width:' + pct.toFixed(1) + '%"></span></span>' +
        '<span class="val">' + esc(value.toFixed ? value.toFixed(1) : value) + '</span></div>';
    };
    var win = (p.window_days === undefined || p.window_days === null) ? 'no window' : p.window_days + 'd window';
    return '<div class="pressure">' + bar('confirm', confirm, 'fill-ok') + bar('challenge', challenge, 'fill-bad') +
      '<p class="empty">' + esc(win + ' \u00b7 last evidence ' + (p.last_evidence || 'none recorded')) + '</p></div>';
  }

  function assumptionCard(a) {
    if (!isObj(a)) return '';
    var confirmedBy = arr(a.confirmed_by), challengedBy = arr(a.challenged_by);
    var out = '<article class="panel">' +
      '<p class="row-meta">' + statusPill(a.status) +
      '<span class="chip">source: ' + esc(a.status_source || 'unknown') + '</span>' +
      (a.draft ? '<span class="chip">draft</span>' : '') + '</p>' +
      '<p>' + esc(a.statement || a.id || 'Untitled assumption') + '</p>' +
      '<p class="empty mono">' + esc(a.id || '') + (a.derived_from ? ' \u00b7 ' + esc(a.derived_from) : '') + '</p>' +
      pressureBars(a.pressure);
    if (confirmedBy.length) {
      out += fold('Confirmed by', confirmedBy.length, '<ul class="rows">' + confirmedBy.map(function (t) {
        return '<li class="row">' + esc(t) + '</li>';
      }).join('') + '</ul>', false);
    }
    if (challengedBy.length) {
      out += fold('Challenged by', challengedBy.length, '<ul class="rows">' + challengedBy.map(function (t) {
        return '<li class="row">' + esc(t) + '</li>';
      }).join('') + '</ul>', false);
    }
    out += chips(a.themes, function (slug) { return href(['theme', slug]); });
    return out + '</article>';
  }

  function thesisTab(bundle, meta, id) {
    var thesis = bundle && bundle.thesis;
    if (!isObj(thesis)) {
      return emptyState('No thesis note for ' + id + ' in this build.');
    }
    /* The frontmatter dict is `fm_without_body` here, not `fm`. */
    var fm = isObj(thesis.fm_without_body) ? thesis.fm_without_body : {};
    var reviewed = fm.reviewed_by_operator === true;

    var head = '<p class="row-meta">' +
      '<span class="pill ' + (reviewed ? 'pill-ok' : 'pill-neutral') + '">' +
      (reviewed ? 'operator-reviewed' : 'machine-drafted') + '</span>' +
      (fm.thin_inputs ? '<span class="pill pill-warn">thin inputs</span>' : '') + '</p>' +
      '<dl class="kv">' +
      '<dt>drafted</dt><dd>' + esc(fm.drafted || '\u2014') + '</dd>' +
      '<dt>mode</dt><dd>' + esc(fm.draft_mode || '\u2014') + '</dd>' +
      '</dl>';

    var from = arr(fm.drafted_from);
    if (from.length) {
      head += fold('Drafted from', from.length, '<ul class="rows">' + from.map(function (f) {
        return '<li class="row mono">' + esc(f) + '</li>';
      }).join('') + '</ul>', false);
    }

    var html = section('Thesis', head) + scoresBlock(fm, meta);

    var assumptions = arr(fm.assumptions);
    if (!assumptions.length) {
      html += section('Assumptions', emptyState('This thesis carries no assumptions yet.'));
    } else {
      var counts = {};
      assumptions.forEach(function (a) {
        var s = (a && a.status) || 'unknown';
        counts[s] = (counts[s] || 0) + 1;
      });
      var summary = Object.keys(counts).sort().map(function (s) {
        return '<span class="pill ' + (STATUS_PILL[s] || 'pill-neutral') + '">' + esc(counts[s] + ' ' + s) + '</span>';
      }).join(' ');
      html += section('Assumptions \u2014 ' + assumptions.length,
        '<p class="row-meta">' + summary + '</p>' + assumptions.map(assumptionCard).join(''));
    }

    if (thesis.body) {
      html += section('Thesis note', fold('Full thesis note', kb(String(thesis.body).length), md(thesis.body), false));
    }
    return html;
  }

  /* notes/thesis read the ticker bundle the router already fetched; app2.js adds
   * signals/news/insiders/etf, each of which fetches a bundle of its own and so
   * returns a promise of HTML (viewTicker accepts either). */
  var tickerTabs = {
    notes: notesTab,
    thesis: thesisTab
  };

  function viewTicker(parts) {
    var id = parts[1];
    if (!id) {
      return { title: 'Ticker', html: emptyState('No ticker in that link. Open Tickers to pick one.') };
    }
    var meta = findTicker(id);
    var isNote = parts[2] === 'note';
    var tab = isNote ? 'notes' : (parts[2] || 'notes');
    if (!isNote && !tickerTabs[tab]) tab = 'notes';
    var shell = tickerHead(meta, id) + tickerStrip(id, tab);

    if (!meta) {
      return { title: id, html: shell + emptyState(id + ' is not in this build\u2019s manifest. Open Tickers for the names it carries.') };
    }
    if (!meta.has_notes) {
      return {
        title: id,
        html: shell + emptyState('No bundle file for ' + id + ' in this build: it has no notes, thesis or profile yet, so only the watchlist facts above are available.')
      };
    }

    var path = bundlePath(id);
    return loadJSON(path).then(function (bundle) {
      /* A tab may need a second bundle of its own (scores, news, market), so it
       * is allowed to return a promise of HTML as well as a string. */
      return Promise.resolve(isNote
        ? noteView(bundle, id, parts[3])
        : tickerTabs[tab](bundle, meta, id));
    }).then(function (body) {
      return { title: id, html: shell + body };
    }).catch(function () {
      return { title: id, html: shell + emptyState('Could not load ' + path + ' from this bundle.') };
    });
  }

  /* ============================================================ MORE ====== */

  function viewStatus() {
    var m = STATE.manifest;
    var counts = isObj(m.counts) ? m.counts : {};
    var health = isObj(m.health) ? m.health : {};
    var files = isObj(m.files) ? m.files : {};

    var html = section('Build',
      '<dl class="kv">' +
      '<dt>built at</dt><dd>' + esc(fmtTS(m.built_at)) + '</dd>' +
      '<dt>raw</dt><dd>' + esc(m.built_at || '\u2014') + '</dd>' +
      '<dt>git sha</dt><dd>' + esc(m.git_sha || '\u2014') + '</dd>' +
      '<dt>format</dt><dd>' + esc(m.format || '\u2014') + '</dd>' +
      '<dt>markdown</dt><dd>' + (STATE.md ? 'markdown-it loaded' : 'vendor file missing \u2014 notes render as plain text') + '</dd>' +
      '</dl>');

    /* The search index's news window, read from the manifest rather than by
     * fetching the 3MB index itself (state_bundles.manifest() copies it out of
     * the already-written data/search.json). Absent in a bundle built before
     * that, which is why the key is skipped rather than printed as "null". */
    var countKeys = Object.keys(counts).filter(function (k) {
      return !(k === 'search_news_mode' && (counts[k] === null || counts[k] === undefined));
    });
    html += section('Counts', countKeys.length
      ? '<dl class="kv">' + countKeys.map(function (k) {
        return '<dt>' + esc(k) + '</dt><dd>' + esc(counts[k]) + '</dd>';
      }).join('') + '</dl>'
      : emptyState('This build recorded no counts.'));

    var failures = arr(health.last_job_failures);
    var healthBody = '<dl class="kv">' +
      '<dt>stale assumptions</dt><dd>' + esc(health.stale_assumptions === undefined ? '\u2014' : health.stale_assumptions) + '</dd>' +
      '<dt>tickers w/o notes</dt><dd>' + esc(health.tickers_without_notes === undefined ? '\u2014' : health.tickers_without_notes) + '</dd>' +
      '<dt>themes w/o labels</dt><dd>' + esc(arr(health.themes_without_labels).length) + '</dd>' +
      '<dt>candidates pending</dt><dd>' + esc(m.candidates_pending === undefined ? '\u2014' : m.candidates_pending) + '</dd>' +
      '</dl>';
    healthBody += failures.length
      ? fold('Recent job failures', failures.length, '<ul class="rows">' + failures.map(function (f) {
        return '<li class="row"><div class="row-top"><span class="row-key">' + esc('exit ' + (f.exit === undefined ? '?' : f.exit)) + '</span>' +
          '<span class="row-title">' + esc(f.job || 'unknown job') + '</span>' +
          '<span class="row-right">' + esc(fmtTS(f.ts)) + '</span></div>' +
          '<div class="row-meta mono">' + esc(f.cmd || '') + '</div></li>';
      }).join('') + '</ul>', true)
      : emptyState('No job failures recorded in this build.');
    html += section('Health', healthBody);

    var themesNoLabel = arr(health.themes_without_labels);
    if (themesNoLabel.length) {
      html += section('Themes without labels', chips(themesNoLabel, function (s) { return href(['theme', s]); }));
    }

    var store = STATE.store || emptyStore();
    html += section('Read store',
      '<dl class="kv">' +
      '<dt>key</dt><dd>' + esc(STORE_KEY) + '</dd>' +
      '<dt>bytes</dt><dd>' + esc(storeBytes()) + '</dd>' +
      '<dt>cards read</dt><dd>' + esc(Object.keys(store.cards || {}).length) + '</dd>' +
      '<dt>notes read</dt><dd>' + esc(Object.keys(store.notes || {}).length) + '</dd>' +
      '<dt>theme stages</dt><dd>' + esc(Object.keys(store.themeStages || {}).length) + '</dd>' +
      '<dt>last visit</dt><dd>' + esc(STATE.since && STATE.since.lastVisit ? fmtTS(STATE.since.lastVisit) : 'first visit') + '</dd>' +
      '</dl>');

    var paths = Object.keys(files);
    if (!paths.length) {
      html += section('Bundle', emptyState('This manifest lists no files.'));
    } else {
      var total = 0;
      paths.forEach(function (p) { total += (files[p] && files[p].bytes) || 0; });
      var top = paths.slice().sort(function (a, b) {
        return ((files[b] && files[b].bytes) || 0) - ((files[a] && files[a].bytes) || 0);
      }).slice(0, 20);
      html += section('Bundle \u2014 ' + paths.length + ' files, ' + kb(total),
        '<div class="scrollx"><table class="data"><thead><tr><th>file</th><th>bytes</th><th>sha256</th></tr></thead><tbody>' +
        top.map(function (p) {
          var f = files[p] || {};
          return '<tr><td class="mono">' + esc(p) + '</td><td class="n">' + esc(kb(f.bytes)) + '</td>' +
            '<td class="mono">' + esc(String(f.sha256 || '').slice(0, 12)) + '</td></tr>';
        }).join('') + '</tbody></table></div>' +
        '<p class="empty">' + esc('Twenty largest of ' + paths.length + ' files.') + '</p>');
    }

    return { title: 'Status', html: html };
  }

  /* scores/etf/reports/search are registered by app2.js. */
  var morePages = { status: viewStatus };

  function viewMore(parts) {
    var page = parts[1];
    if (page) {
      var fn = morePages[page];
      if (fn) return fn(parts);
      return { title: 'More', html: emptyState('There is no \u201c' + page + '\u201d screen. Open More for the list.') };
    }
    var items = [
      ['scores', 'Scores', 'Tier 1\u20132 score table with proposed changes'],
      ['etf', 'ETF trades', '14-day archive of holdings changes'],
      ['reports', 'Reports', 'Every report card in the last 14 days'],
      ['search', 'Search', 'Notes, news and filings in this bundle'],
      ['status', 'Status', 'Build, health and bundle budget']
    ];
    return {
      title: 'More',
      html: '<ul class="rows">' + items.map(function (it) {
        return '<li>' + row(href(['more', it[0]]),
          '<span class="dot-slot"></span><span class="row-title">' + esc(it[1]) + '</span>',
          '<span>' + esc(it[2]) + '</span>') + '</li>';
      }).join('') + '</ul>'
    };
  }

  /* =========================================================== ROUTER ===== */

  /* themes/theme/ideas are registered by app2.js. */
  var views = {
    today: function (parts) { return parts.length > 1 ? viewCard(parts) : viewToday(parts); },
    tickers: viewTickers,
    ticker: viewTicker,
    more: viewMore
  };

  var TABS = { today: 'today', tickers: 'tickers', themes: 'themes', theme: 'themes', ideas: 'ideas', more: 'more' };

  function parseHash() {
    var raw = String(window.location.hash || '').replace(/^#/, '');
    if (raw.charAt(0) === '/') raw = raw.slice(1);
    return raw.split('/').filter(function (s) { return s !== ''; }).map(function (s) {
      try { return decodeURIComponent(s); } catch (e) { return s; }
    });
  }

  function asOf() {
    if (!STATE.manifest) return 'bundle not loaded';
    return 'as of ' + fmtTS(STATE.manifest.built_at);
  }

  function footer() {
    if (!STATE.manifest) {
      return '<p class="pagefoot">No manifest \u2014 nothing in this view is live data.</p>';
    }
    var m = STATE.manifest;
    var nfiles = Object.keys(isObj(m.files) ? m.files : {}).length;
    return '<p class="pagefoot">' + esc(asOf()) + ' \u00b7 ' + esc(m.git_sha || 'no sha') +
      ' \u00b7 ' + esc(nfiles + ' files') + '</p>';
  }

  /* Wrap anything that can outgrow the column in its own horizontal scroller, so
   * the page body never scrolls sideways. Runs over the whole view, so markdown
   * tables from markdown-it are covered without a per-call-site hook. */
  function wrapWide(root) {
    if (!root) return;
    var wide = root.querySelectorAll('table, pre');
    for (var i = 0; i < wide.length; i++) {
      var node = wide[i];
      var parent = node.parentNode;
      if (!parent || (parent.className && String(parent.className).indexOf('scrollx') >= 0)) continue;
      var box = el('div', { 'class': 'scrollx' });
      parent.insertBefore(box, node);
      box.appendChild(node);
    }
  }

  var ROUTE_LABELS = {
    today: 'Today', tickers: 'Tickers', themes: 'Themes', theme: 'Theme', ideas: 'Ideas', more: 'More'
  };

  /* The header title to show while an async view is still fetching. */
  function routeLabel(parts) {
    var head = (parts && parts[0]) || 'today';
    if (head === 'ticker') return parts[1] ? String(parts[1]) : 'Ticker';
    if (head === 'today' && parts.length > 1) return 'Report';
    if (head === 'theme' && parts[1]) return String(parts[1]);
    return ROUTE_LABELS[head] || 'Research Desk';
  }

  function errorRes(err) {
    return {
      title: 'Something broke',
      html: emptyState('This screen could not be built: ' + (err && err.message ? err.message : String(err)) +
        '. Open Today to start over.')
    };
  }

  var renderToken = 0;

  function paint(res, parts) {
    var view = document.getElementById('view');
    document.getElementById('page-title').textContent = (res && res.title) || 'Research Desk';
    document.getElementById('page-sub').textContent = asOf();
    document.getElementById('btn-back').hidden = !(parts && parts.length > 1);

    var tab = TABS[(parts && parts[0]) || 'today'] || null;
    var tabs = document.querySelectorAll('.tab');
    for (var i = 0; i < tabs.length; i++) {
      if (tabs[i].getAttribute('data-tab') === tab) tabs[i].setAttribute('aria-current', 'page');
      else tabs[i].removeAttribute('aria-current');
    }

    view.innerHTML = ((res && res.html) || '') + footer();
    wrapWide(view);
    if (res && typeof res.after === 'function') {
      try { res.after(view); } catch (e) { /* a broken hook must not blank the screen */ }
    }
    window.scrollTo(0, 0);
    try { view.focus({ preventScroll: true }); } catch (e) { /* older WebKit */ }
  }

  function render() {
    var parts = parseHash();
    var token = ++renderToken;

    if (!STATE.manifest) {
      paint({
        title: 'Research Desk',
        html: emptyState('This desk could not read data/manifest.json, so there is nothing to show. ' +
          'Rebuild the bundle with scripts/portal/build_portal.py and republish.')
      }, []);
      return;
    }

    var head = parts[0] || 'today';
    var fn = views[head];
    if (!fn) {
      paint({ title: 'Not found', html: emptyState('There is no \u201c' + head + '\u201d screen on this desk. Open Today to start over.') }, parts);
      return;
    }

    var out;
    try {
      out = fn(parts);
    } catch (err) {
      paint(errorRes(err), parts);
      return;
    }

    if (!out || typeof out.then !== 'function') {
      paint(out, parts);
      return;
    }

    /* An async view fetches a bundle that can run to a few hundred KB, so paint a
     * skeleton NOW rather than leaving the previous screen frozen under the tap.
     * The token check below still discards this render if another one overtakes it. */
    paint({ title: routeLabel(parts), html: '<p class="skeleton">Loading\u2026</p>' }, parts);
    out.then(function (res) { if (token === renderToken) paint(res, parts); })
      .catch(function (err) { if (token === renderToken) paint(errorRes(err), parts); });
  }

  /* Two delegated registries so a screen never wires its own listener (and never
   * leaks one when the view is replaced): `controls` keyed by element id for
   * input/change, `actions` keyed by data-act for clicks. A screen adds an entry
   * and re-renders its own sub-container; the router owns everything else. */
  var controls = {};
  var actions = {};

  controls['q-tickers'] = function (t) {
    tickersUI.q = t.value || '';
    var box = document.getElementById('ticker-rows');
    if (box) box.innerHTML = tickerRowsHTML();
  };
  controls['sort-tickers'] = function (t) {
    tickersUI.sort = t.value || 'last';
    var box = document.getElementById('ticker-rows');
    if (box) box.innerHTML = tickerRowsHTML();
  };

  function onControl(ev) {
    var t = ev.target;
    if (!t || !t.id) return;
    var fn = controls[t.id];
    if (!fn) return;
    try { fn(t, ev); } catch (e) { /* a broken control must not blank the screen */ }
  }

  function onClick(ev) {
    var node = ev.target;
    while (node && node !== ev.currentTarget) {
      if (node.getAttribute && node.getAttribute('data-act')) break;
      node = node.parentNode;
    }
    if (!node || node === ev.currentTarget || !node.getAttribute) return;
    if (node.disabled) return;
    var fn = actions[node.getAttribute('data-act')];
    if (!fn) return;
    ev.preventDefault();
    try { fn(node, ev); } catch (e) { /* same \u2014 a broken action is not fatal */ }
  }

  /* --------------------------------------------------------- app2.js ------ */

  /* Task 8's screens live in app2.js (this file would be past 2,300 lines with
   * them inlined). They are not a second app: they are handed these helpers and
   * they REGISTER into the same `views` / `tickerTabs` / `morePages` / `controls`
   * / `actions` objects, so the router, the delegated listeners and the "as of"
   * footer keep their single implementation here. app2.js is a plain script
   * loaded after this one; boot() below runs on DOMContentLoaded, by which time
   * its registrations are in place. If it fails to load, this app still runs --
   * the unregistered routes fall through to the router's own "no such screen"
   * empty state instead of breaking a screen that did load. */
  window.RIS = {
    esc: esc, arr: arr, isObj: isObj, href: href, kb: kb,
    chips: chips, emptyState: emptyState, section: section, fold: fold, md: md,
    row: row, dot: dot, wrapWide: wrapWide,
    loadJSON: loadJSON, findTicker: findTicker,
    safeURL: safeURL, extLink: extLink, isRead: isRead,
    STATE: STATE, views: views, tickerTabs: tickerTabs, morePages: morePages,
    controls: controls, actions: actions
  };

  function boot() {
    try {
      STATE.md = (typeof window.markdownit === 'function')
        ? window.markdownit({ html: false, linkify: false, typographer: false })
        : null;
    } catch (e) { STATE.md = null; }

    /* Every markdown link in today's bundle is an in-app "#/..." route (556 of
     * 556 across all 103 bundles), but a note or a Task 8 headline may link out,
     * and a plain navigation inside the phone's in-app web view leaves the app
     * with no chrome to come back from. Anything not starting with "#" opens in
     * a new context instead. */
    if (STATE.md) {
      try {
        var passThrough = STATE.md.renderer.rules.link_open || function (tokens, idx, options, env, self) {
          return self.renderToken(tokens, idx, options);
        };
        STATE.md.renderer.rules.link_open = function (tokens, idx, options, env, self) {
          var target = tokens[idx].attrGet('href') || '';
          if (extAttrs(target)) {
            tokens[idx].attrSet('target', '_blank');
            tokens[idx].attrSet('rel', 'noopener noreferrer');
          }
          return passThrough(tokens, idx, options, env, self);
        };
      } catch (e) { /* older markdown-it renderer shape: links stay as-is */ }
    }

    STATE.store = storeRead();
    STATE.since = {
      lastVisit: STATE.store.lastVisit,
      themeStages: STATE.store.themeStages || {}
    };

    document.getElementById('btn-back').addEventListener('click', function () { window.history.back(); });
    var view = document.getElementById('view');
    view.addEventListener('input', onControl);
    view.addEventListener('change', onControl);
    view.addEventListener('click', onClick);
    window.addEventListener('hashchange', render);

    loadJSON(MANIFEST_PATH).then(function (m) {
      STATE.manifest = isObj(m) ? m : {};
      stampVisit(STATE.manifest);
    }).catch(function (err) {
      STATE.manifestError = err;
    }).then(function () { render(); });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
