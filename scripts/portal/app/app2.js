/* Research Desk — RIS4 portal app, part 2 (Task 8: Themes, Ideas, Scores,
 * Signals, News, Insiders, ETF trades, the Reports archive and Search).
 *
 * A continuation of app.js, not a second app. app.js publishes a small surface
 * on `window.RIS` (its escaping/markdown/row helpers, the guarded `loadJSON`,
 * and the `views` / `tickerTabs` / `morePages` / `controls` / `actions` maps);
 * this file adds screens by MUTATING those maps at the bottom. The router, the
 * delegated input/click listeners, the read store and the "as of built_at"
 * footer all stay in app.js and are not reimplemented here.
 *
 * It is split out purely for size: inlined, app.js would run past 2,300 lines.
 * Load order is index.html's (app.js, then this); if app.js is missing this
 * file is a clean no-op.
 *
 * Every screen below: escapes every injected string, reaches the network only
 * through `loadJSON` (which refuses anything but a data/<name>.json path in the
 * bundle), tolerates an absent or empty bundle with a one-sentence empty state,
 * and puts anything that can outgrow the column in a `.scrollx` box.
 */
(function () {
  'use strict';

  var R = window.RIS;
  if (!R) return;   /* app.js did not load: nothing to extend, and no errors. */

  var esc = R.esc, arr = R.arr, isObj = R.isObj, href = R.href, kb = R.kb;
  var chips = R.chips, emptyState = R.emptyState, section = R.section, fold = R.fold;
  var md = R.md, row = R.row, dot = R.dot, wrapWide = R.wrapWide;
  var loadJSON = R.loadJSON, findTicker = R.findTicker;
  var safeURL = R.safeURL, extLink = R.extLink, isRead = R.isRead;
  var itemsSummary = R.itemsSummary;
  var STATE = R.STATE;
  var views = R.views, tickerTabs = R.tickerTabs, morePages = R.morePages;
  var controls = R.controls, actions = R.actions;

  /* A screen returns HTML, or a promise of it. One that filters in place keeps
   * its state in a module-level UI object and re-renders only its own
   * sub-container, through the delegated `controls` (input/change, keyed by
   * element id) and `actions` (click, keyed by data-act) registries -- no screen
   * attaches a listener of its own, so none can leak one when the view is
   * replaced. The bundle paths every screen reads: */

  var THEMES_PATH = 'data/themes.json';
  var IDEAS_PATH = 'data/ideas.json';
  var SCORES_PATH = 'data/scores.json';
  var MARKET_PATH = 'data/market.json';
  var INSIDERS_PATH = 'data/insiders.json';
  var ETF_PATH = 'data/etf_trades.json';
  var SEC_PATH = 'data/sec_30d.json';
  var NEWS_INDEX_PATH = 'data/news_index.json';
  var SEARCH_PATH = 'data/search.json';

  function num(v) {
    var n = (typeof v === 'number') ? v : parseFloat(v);
    return (typeof n === 'number' && isFinite(n)) ? n : null;
  }

  /* One line of plain text out of anything: markdown excerpts in the bundle run
   * to several hundred characters and are only ever a preview here. */
  function clip(text, n) {
    var s = String(text === null || text === undefined ? '' : text).replace(/\s+/g, ' ').trim();
    return s.length > n ? s.slice(0, n - 1) + '…' : s;
  }

  function loadFail(path) {
    return emptyState('Could not load ' + path + ' from this bundle — rebuild it with scripts/portal/build_portal.py and republish.');
  }

  /* Controls that exist so the screen reads honestly but do nothing until the
   * write path ships: rendered, visible, and genuinely inert (a disabled
   * <button>, never a styled <a>, which stays clickable). */
  function slice5Btn(label) {
    return '<button type="button" class="btn btn-mini" disabled title="slice 5">' + esc(label) + '</button>';
  }

  function filterChips(act, options, current) {
    return '<div class="filters" role="group">' + options.map(function (o) {
      var on = String(o[0]) === String(current);
      return '<button type="button" class="fchip" data-act="' + esc(act) + '" data-v="' + esc(o[0]) + '"' +
        (on ? ' aria-pressed="true"' : ' aria-pressed="false"') + '>' + esc(o[1]) + '</button>';
    }).join('') + '</div>';
  }

  function repaint(id, html) {
    var box = document.getElementById(id);
    if (box) { box.innerHTML = html; wrapWide(box); }
  }

  /* ---------------------------------------------------------- THEMES ------ */

  /* diffusion.current_quarter can name a quarter that has no `metrics` rows yet
   * (the quarter is "current" by the calendar, not by the evidence), so both the
   * breadth table and the delta key off the most recent quarters actually
   * PRESENT in metrics, and the screen prints which quarter it used. */
  function quartersPresent(metrics) {
    var seen = {}, out = [];
    arr(metrics).forEach(function (m) {
      var q = m && m.cal_quarter;
      if (q && !seen[q]) { seen[q] = 1; out.push(String(q)); }
    });
    out.sort();
    out.reverse();
    return out;
  }

  function metricsFor(metrics, quarter) {
    var map = {};
    arr(metrics).forEach(function (m) {
      if (m && String(m.cal_quarter) === String(quarter) && m.theme !== undefined) map[String(m.theme)] = m;
    });
    return map;
  }

  function stagePill(stage) {
    var n = num(stage);
    if (n === null) return '<span class="pill pill-neutral">no stage</span>';
    var cls = n >= 3 ? 'pill-ok' : (n === 2 ? 'pill-accent' : 'pill-warn');
    return '<span class="pill ' + cls + '">stage ' + esc(n) + '</span>';
  }

  /* Three different nothings, and they do not mean the same thing: a theme with
   * no row this quarter is quiet, a theme with no row last quarter is new, and a
   * theme with the same breadth in both is flat. */
  function deltaSpan(d, mark) {
    if (mark === 'none') return '<span class="muted">quiet</span>';
    if (mark === 'new') return '<span class="up">new</span>';
    if (d === 0) return '<span class="muted">±0</span>';
    return '<span class="' + (d > 0 ? 'up' : 'down') + '">' + (d > 0 ? '+' : '−') + esc(Math.abs(d)) + '</span>';
  }

  function themeRows(payload) {
    var themes = arr(payload.themes);
    if (!themes.length) return emptyState('This build carries no accepted themes.');
    var diff = isObj(payload.diffusion) ? payload.diffusion : {};
    var qs = quartersPresent(diff.metrics);
    var cur = metricsFor(diff.metrics, qs[0]);
    var prev = metricsFor(diff.metrics, qs[1]);

    var rows = themes.map(function (t) {
      var slug = String(t.slug === undefined ? '' : t.slug);
      var fm = isObj(t.fm) ? t.fm : {};
      var c = cur[slug], p = prev[slug];
      var nc = c ? num(c.n_companies) : null;
      var np = p ? num(p.n_companies) : null;
      var mark = (nc === null) ? 'none' : (np === null ? 'new' : '');
      var delta = mark ? null : (nc - np);
      return { slug: slug, fm: fm, cur: c, delta: delta, mark: mark, tickers: arr(fm.tickers).length };
    });
    /* Movers first (that is the whole point of the delta), then alphabetical so
     * the long flat tail of unchanged themes stays scannable. */
    rows.sort(function (a, b) {
      /* movers first, then the new arrivals, then everything flat or quiet */
      var da = a.delta === null ? (a.mark === 'new' ? 0.5 : -1) : Math.abs(a.delta);
      var db = b.delta === null ? (b.mark === 'new' ? 0.5 : -1) : Math.abs(b.delta);
      return (db - da) || a.slug.localeCompare(b.slug);
    });

    return '<ul class="rows">' + rows.map(function (r) {
      var c = r.cur || {};
      var meta = '<span>' + esc(r.tickers + (r.tickers === 1 ? ' ticker' : ' tickers')) + '</span>' +
        '<span>' + esc((num(c.n_banks) === null ? 0 : c.n_banks) + ' banks') + '</span>' +
        '<span>' + esc((num(c.n_companies) === null ? 0 : c.n_companies) + ' asked') + '</span>' +
        '<span>' + esc((num(c.n_disclosing) === null ? 0 : c.n_disclosing) + ' disclosing') + '</span>' +
        '<span class="mono">' + esc(r.fm.updated || '—') + '</span>';
      return '<li>' + row(href(['theme', r.slug]),
        '<span class="dot-slot"></span><span class="row-title mono">' + esc(r.slug) + '</span>' +
        '<span class="row-right">' + deltaSpan(r.delta, r.mark) + '</span>',
        stagePill(r.fm.stage) + meta) + '</li>';
    }).join('') + '</ul>' +
      '<p class="empty">' + esc('Change is in companies asked, ' + (qs[0] || 'latest quarter') +
        ' vs ' + (qs[1] || 'no prior quarter') +
        '; “quiet” means no analyst or filing evidence at all in ' + (qs[0] || 'the latest quarter') + '.') + '</p>';
  }

  function candidateBlock(payload) {
    var cands = arr(payload.candidates);
    if (!cands.length) {
      return emptyState('No theme candidates are waiting on a decision in this build.');
    }
    return cands.map(function (c) {
      var name = c.suggested_name || c.label || c.id || 'candidate';
      return '<article class="panel">' +
        '<p class="row-top"><span class="row-title mono">' + esc(name) + '</span>' +
        '<span class="row-right">' + esc(c.first_seen || '—') + '</span></p>' +
        '<p class="row-meta">' +
        '<span>' + esc((c.n_exchanges === undefined ? 0 : c.n_exchanges) + ' exchanges') + '</span>' +
        '<span>' + esc((c.n_companies === undefined ? 0 : c.n_companies) + ' companies') + '</span>' +
        '<span>' + esc((c.n_banks === undefined ? 0 : c.n_banks) + ' banks') + '</span>' +
        (c.label && c.label !== name ? '<span class="chip">' + esc(c.label) + '</span>' : '') + '</p>' +
        chips(arr(c.ngrams).slice(0, 8)) +
        chips(arr(c.tickers), function (t) { return href(['ticker', t]); }) +
        '<p class="row-meta">' + slice5Btn('✓ Accept') + slice5Btn('✗ Reject') +
        '<span class="muted">decisions land in slice 5</span></p>' +
        '</article>';
    }).join('');
  }

  function breadthTable(payload) {
    var diff = isObj(payload.diffusion) ? payload.diffusion : {};
    var qs = quartersPresent(diff.metrics);
    if (!qs.length) return emptyState('This build carries no diffusion metrics.');
    var q = qs[0];
    var rows = arr(diff.metrics).filter(function (m) { return m && String(m.cal_quarter) === q; });
    rows.sort(function (a, b) {
      return ((num(b.n_disclosing) || 0) - (num(a.n_disclosing) || 0)) ||
        ((num(b.n_companies) || 0) - (num(a.n_companies) || 0)) ||
        String(a.theme).localeCompare(String(b.theme));
    });
    var lag = isObj(diff.lag_summary) ? diff.lag_summary : {};
    return '<p class="lede">' + esc(q + ' · ' + rows.length + ' themes with evidence' +
      (lag.median === undefined || lag.median === null ? '' : ' · median lag ' + lag.median + 'd over ' + (lag.n || 0) + ' first reads')) + '</p>' +
      '<div class="scrollx"><table class="data"><thead><tr><th>theme</th><th>banks</th><th>asked</th><th>disclosing</th></tr></thead><tbody>' +
      rows.map(function (m) {
        return '<tr><td><a href="' + esc(href(['theme', m.theme])) + '">' + esc(m.theme) + '</a></td>' +
          '<td class="n">' + esc(num(m.n_banks) === null ? 0 : m.n_banks) + '</td>' +
          '<td class="n">' + esc(num(m.n_companies) === null ? 0 : m.n_companies) + '</td>' +
          '<td class="n">' + esc(num(m.n_disclosing) === null ? 0 : m.n_disclosing) + '</td></tr>';
      }).join('') + '</tbody></table></div>';
  }

  function viewThemes() {
    return loadJSON(THEMES_PATH).then(function (payload) {
      var p = isObj(payload) ? payload : {};
      var nCand = arr(p.candidates).length;
      return {
        title: 'Themes',
        html: section('Accepted themes — ' + arr(p.themes).length, themeRows(p)) +
          section('Candidates' + (nCand ? ' — ' + nCand + ' pending' : ''), candidateBlock(p)) +
          section('Breadth this quarter', breadthTable(p))
      };
    }).catch(function () {
      return { title: 'Themes', html: loadFail(THEMES_PATH) };
    });
  }

  /* The theme body is one markdown document with a `## <quarter>` heading per
   * quarter; split on those so the newest quarter opens first instead of making
   * the reader scroll past a year of history. */
  function splitQuarters(body) {
    var text = String(body === null || body === undefined ? '' : body);
    if (!text.trim()) return [];
    var re = /^##[ \t]+(.+)$/gm, m, heads = [];
    while ((m = re.exec(text)) !== null) heads.push({ title: m[1], at: m.index, from: re.lastIndex });
    if (!heads.length) return [{ title: 'Note', text: text }];
    var out = [];
    var pre = text.slice(0, heads[0].at).trim();
    heads.forEach(function (h, i) {
      var end = (i + 1 < heads.length) ? heads[i + 1].at : text.length;
      out.push({ title: h.title, text: text.slice(h.from, end).trim() });
    });
    out.reverse();
    if (pre) out.push({ title: 'Preamble', text: pre });
    return out;
  }

  function viewTheme(parts) {
    var slug = parts[1];
    if (!slug) return { title: 'Theme', html: emptyState('No theme in that link. Open Themes to pick one.') };
    return loadJSON(THEMES_PATH).then(function (payload) {
      var p = isObj(payload) ? payload : {};
      var theme = null;
      arr(p.themes).forEach(function (t) { if (t && String(t.slug) === String(slug)) theme = t; });
      if (!theme) {
        return {
          title: String(slug),
          html: emptyState(slug + ' is not an accepted theme in this build. Open Themes for the ' +
            arr(p.themes).length + ' it carries.')
        };
      }
      var fm = isObj(theme.fm) ? theme.fm : {};
      var html = '<h2 class="head mono">' + esc(slug) + '</h2>' +
        '<p class="lede">' + stagePill(fm.stage) +
        ' <span class="chip">' + esc(fm.status || 'unknown') + '</span>' +
        (theme.in_vocab === false ? ' <span class="pill pill-warn">not in vocabulary</span>' : '') + '</p>';

      var facts = [
        ['first question', fm.first_question_date],
        ['first evidence', fm.first_evidence_date],
        ['lag (days)', fm.lag_days],
        ['updated', fm.updated]
      ].filter(function (f) { return f[1] !== undefined && f[1] !== null && f[1] !== ''; });
      html += section('Facts', facts.length
        ? '<dl class="kv">' + facts.map(function (f) {
          return '<dt>' + esc(f[0]) + '</dt><dd>' + esc(f[1]) + '</dd>';
        }).join('') + '</dl>'
        : emptyState('This theme note carries no frontmatter facts.'));

      var tickers = arr(fm.tickers);
      var affects = arr(fm.affects);
      var stages = isObj(theme.stages_by_ticker) ? theme.stages_by_ticker : {};
      var stageKeys = Object.keys(stages).sort(function (a, b) {
        return ((num(stages[b]) || 0) - (num(stages[a]) || 0)) || a.localeCompare(b);
      });
      var who = tickers.length
        ? '<h3 class="subhead">Tickers</h3>' + chips(tickers, function (t) { return href(['ticker', t]); })
        : emptyState('No tickers are tagged with this theme.');
      if (affects.length) {
        who += '<h3 class="subhead">Affects</h3>' + chips(affects, function (t) { return href(['ticker', t]); });
      }
      if (stageKeys.length) {
        who += '<h3 class="subhead">Stage by ticker</h3><div class="scrollx"><table class="data">' +
          '<thead><tr><th>ticker</th><th>stage</th></tr></thead><tbody>' +
          stageKeys.map(function (t) {
            return '<tr><td><a href="' + esc(href(['ticker', t])) + '">' + esc(t) + '</a></td>' +
              '<td class="n">' + esc(stages[t]) + '</td></tr>';
          }).join('') + '</tbody></table></div>';
      }
      html += section('Who', who);

      var quarters = splitQuarters(theme.body);
      html += section('By quarter', quarters.length
        ? quarters.map(function (q, i) { return fold(q.title, null, md(q.text), i === 0); }).join('')
        : emptyState('This theme note has no body in the bundle.'));

      var diff = isObj(p.diffusion) ? p.diffusion : {};
      var mine = arr(diff.metrics).filter(function (m) { return m && String(m.theme) === String(slug); });
      mine.sort(function (a, b) { return String(b.cal_quarter).localeCompare(String(a.cal_quarter)); });
      html += section('Breadth by quarter', mine.length
        ? '<div class="scrollx"><table class="data"><thead><tr><th>quarter</th><th>banks</th><th>asked</th><th>exchanges</th><th>disclosing</th></tr></thead><tbody>' +
        mine.map(function (m) {
          return '<tr><td class="mono">' + esc(m.cal_quarter) + '</td>' +
            '<td class="n">' + esc(num(m.n_banks) === null ? 0 : m.n_banks) + '</td>' +
            '<td class="n">' + esc(num(m.n_companies) === null ? 0 : m.n_companies) + '</td>' +
            '<td class="n">' + esc(num(m.n_exchanges) === null ? 0 : m.n_exchanges) + '</td>' +
            '<td class="n">' + esc(num(m.n_disclosing) === null ? 0 : m.n_disclosing) + '</td></tr>';
        }).join('') + '</tbody></table></div>'
        : emptyState('No diffusion metrics recorded for this theme.'));

      var events = arr(p.stage_events).filter(function (e) { return e && String(e.theme) === String(slug); });
      events.sort(function (a, b) { return String(b.detected_on).localeCompare(String(a.detected_on)); });
      if (events.length) {
        html += section('Stage detections — ' + events.length,
          '<ul class="rows">' + events.slice(0, 40).map(function (e) {
            return '<li>' + row(href(['ticker', e.ticker]),
              '<span class="dot-slot"></span><span class="row-key">' + esc(e.ticker) + '</span>' +
              '<span class="row-title">' + esc('stage ' + (e.stage === undefined ? '?' : e.stage)) + '</span>' +
              '<span class="row-right">' + esc(e.detected_on || '') + '</span>',
              '<span>' + esc(arr(e.evidence_sources).join(', ') || 'no source') + '</span>' +
              '<span>' + esc((e.n_evidence === undefined ? 0 : e.n_evidence) + ' evidence') + '</span>' +
              (e.first_evidence_date ? '<span class="mono">since ' + esc(e.first_evidence_date) + '</span>' : '')) + '</li>';
          }).join('') + '</ul>');
      }
      return { title: String(slug), html: html };
    }).catch(function () {
      return { title: String(slug), html: loadFail(THEMES_PATH) };
    });
  }

  /* ----------------------------------------------------------- IDEAS ------ */

  /* The six streams the generator can emit, in the order the brief lists them.
   * A stream with no rows in this build still gets a chip (with a 0) rather than
   * disappearing -- "nothing in this stream today" is itself the signal. */
  var IDEA_STREAMS = [
    ['candidate', 'Candidates'], ['newly_said', 'Newly said'], ['gap', 'Gaps'],
    ['stage', 'Stage'], ['screen', 'Screens'], ['novel', 'Novel']
  ];
  var IDEA_CAP = 60;
  var ideasUI = { stream: 'all', payload: null };

  function ideaRowsHTML() {
    var p = isObj(ideasUI.payload) ? ideasUI.payload : {};
    var rows = arr(p.ideas).filter(function (i) {
      return i && (ideasUI.stream === 'all' || String(i.stream) === ideasUI.stream);
    });
    if (!rows.length) {
      return emptyState(ideasUI.stream === 'all'
        ? 'This build generated no ideas.'
        : 'No ' + ideasUI.stream.replace('_', ' ') + ' ideas in this build.');
    }
    rows.sort(function (a, b) {
      return ((num(b.score) || 0) - (num(a.score) || 0)) ||
        String(b.first_seen || '').localeCompare(String(a.first_seen || ''));
    });
    var shown = rows.slice(0, IDEA_CAP);
    return '<ul class="rows">' + shown.map(function (i) {
      var links = isObj(i.links) ? i.links : {};
      var out = '<li class="row"><div class="row-top">' +
        '<span class="chip">' + esc(i.stream || 'idea') + '</span>' +
        '<span class="row-title">' + esc(i.title || i.id || 'untitled idea') + '</span>' +
        '<span class="row-right">' + esc(num(i.score) === null ? '—' : i.score) + '</span></div>';
      if (i.detail) out += '<div class="row-meta">' + esc(clip(i.detail, 260)) + '</div>';
      var linkChips = [];
      if (links.ticker) linkChips.push('<a class="chip" href="' + esc(href(['ticker', links.ticker])) + '">' + esc(links.ticker) + '</a>');
      if (links.theme || i.theme) {
        var th = links.theme || i.theme;
        linkChips.push('<a class="chip" href="' + esc(href(['theme', th])) + '">' + esc(th) + '</a>');
      }
      if (links.note && links.ticker) {
        linkChips.push('<a class="chip" href="' + esc(href(['ticker', links.ticker, 'note', links.note])) + '">note</a>');
      }
      arr(i.tickers).slice(0, 8).forEach(function (t) {
        if (links.ticker && String(links.ticker) === String(t)) return;
        linkChips.push('<a class="chip" href="' + esc(href(['ticker', t])) + '">' + esc(t) + '</a>');
      });
      if (arr(i.tickers).length > 8) linkChips.push('<span class="chip">+' + esc(arr(i.tickers).length - 8) + '</span>');
      out += '<div class="row-meta"><span class="chips-inline">' + linkChips.join('') + '</span>' +
        (i.first_seen ? '<span class="mono">' + esc(i.first_seen) + '</span>' : '') +
        slice5Btn('Dismiss') + slice5Btn('Act') + '</div>';
      return out + '</li>';
    }).join('') + '</ul>' +
      (rows.length > shown.length
        ? '<p class="empty">' + esc((rows.length - shown.length) + ' lower-scoring ideas not shown; filter by stream to reach them.') + '</p>'
        : '');
  }

  function viewIdeas() {
    return loadJSON(IDEAS_PATH).then(function (payload) {
      ideasUI.payload = isObj(payload) ? payload : {};
      var counts = {};
      arr(ideasUI.payload.ideas).forEach(function (i) {
        var s = (i && i.stream) ? String(i.stream) : 'other';
        counts[s] = (counts[s] || 0) + 1;
      });
      var opts = [['all', 'All ' + arr(ideasUI.payload.ideas).length]].concat(IDEA_STREAMS.map(function (s) {
        return [s[0], s[1] + ' ' + (counts[s[0]] || 0)];
      }));
      return {
        title: 'Ideas',
        html: filterChips('idea-stream', opts, ideasUI.stream) +
          '<p class="lede">' + esc('Generated ' + (ideasUI.payload.as_of || 'unknown date') + '. Dismiss and Act land in slice 5.') + '</p>' +
          '<div id="idea-rows">' + ideaRowsHTML() + '</div>'
      };
    }).catch(function () {
      return { title: 'Ideas', html: loadFail(IDEAS_PATH) };
    });
  }

  actions['idea-stream'] = function (node) {
    ideasUI.stream = node.getAttribute('data-v') || 'all';
    var group = node.parentNode;
    if (group) {
      var btns = group.querySelectorAll('.fchip');
      for (var i = 0; i < btns.length; i++) {
        btns[i].setAttribute('aria-pressed', btns[i].getAttribute('data-v') === ideasUI.stream ? 'true' : 'false');
      }
    }
    repaint('idea-rows', ideaRowsHTML());
  };

  /* ---------------------------------------------------------- SCORES ------ */

  /* `proposed` is keyed by DOTTED PATH into `current` ("competitive_advantage.
   * innovation_rate"), so resolving the applied value is a walk, not a lookup. */
  function pathGet(obj, path) {
    var node = obj;
    var bits = String(path).split('.');
    for (var i = 0; i < bits.length; i++) {
      if (!isObj(node)) return null;
      node = node[bits[i]];
    }
    return (node === undefined) ? null : node;
  }

  var SCORE_TIERS = { tier_1_bctk: 1, tier_2_active_candidates: 2 };

  function scoreDelta(entry) {
    var proposed = isObj(entry.proposed) ? entry.proposed : {};
    var keys = Object.keys(proposed);
    if (!keys.length) return { has: false, mag: 0, keys: [] };
    var mag = 0;
    keys.forEach(function (k) {
      var was = num(pathGet(entry.current, k));
      var now = num(isObj(proposed[k]) ? proposed[k].value : proposed[k]);
      if (was !== null && now !== null) mag = Math.max(mag, Math.abs(now - was));
    });
    /* "4+" against an applied "4" parses to a delta of 0 but is still a real
     * proposal, so `has` -- not the magnitude -- carries the sort. */
    return { has: true, mag: mag, keys: keys };
  }

  function latestRead(entry) {
    var best = null;
    arr(entry.reads).forEach(function (r) {
      if (!r || !r.date) return;
      if (!best || String(r.date) > String(best)) best = String(r.date);
    });
    return best;
  }

  function proposedCell(entry) {
    var d = scoreDelta(entry);
    if (!d.has) return '<span class="muted">—</span>';
    var proposed = isObj(entry.proposed) ? entry.proposed : {};
    return d.keys.map(function (k) {
      var v = isObj(proposed[k]) ? proposed[k].value : proposed[k];
      var was = pathGet(entry.current, k);
      return '<span class="pill pill-warn">' + esc(k.split('.').pop() + ' ' + (was === null ? '—' : was) +
        '→' + (v === undefined || v === null ? '—' : v)) + '</span>';
    }).join(' ');
  }

  function readBlock(r, showLink) {
    var noteLink = '';
    if (showLink && r.note_id) {
      var t = String(r.note_id).split('/')[0];
      noteLink = ' · <a href="' + esc(href(['ticker', t, 'note', r.note_id])) + '">open note</a>';
    }
    var body = ['ai_positioning', 'competitive_advantage', 'investor_interest'].map(function (k) {
      return r[k] ? '<h4 class="subhead">' + esc(k) + '</h4>' + md(r[k]) : '';
    }).join('');
    return '<p class="row-meta"><span class="mono">' + esc(r.quarter || '') + '</span>' +
      '<span class="mono">' + esc(r.date || '') + '</span>' +
      '<span class="mono">' + esc(r.note_id || '') + '</span></p>' +
      '<p class="empty">read from this note' + noteLink + '</p>' + (body || emptyState('This read recorded no excerpts.'));
  }

  var scoresUI = { open: {} };

  function scoresTableHTML(payload) {
    var tickers = isObj(payload.tickers) ? payload.tickers : {};
    var rows = [], unmatched = [];
    Object.keys(tickers).forEach(function (t) {
      var meta = findTicker(t);
      /* scores.json and manifest.tickers are built from different sources, so a
       * name can be scored here and carry no tier 1-2 there (or not be there at
       * all). Dropping it from a tier 1-2 table is right; dropping it INVISIBLY
       * is not, so it is collected, counted in the lede and listed below. */
      var tier = meta ? SCORE_TIERS[meta.tier] : undefined;
      if (!tier) {
        unmatched.push({ ticker: t, why: meta ? (meta.tier ? String(meta.tier) : 'no tier') : 'not in the manifest' });
        return;
      }
      var entry = isObj(tickers[t]) ? tickers[t] : {};
      rows.push({ ticker: t, tier: tier, entry: entry, d: scoreDelta(entry), last: latestRead(entry) });
    });
    if (!rows.length) {
      return emptyState('No tier 1 or tier 2 name in this build carries a score.') + unmatchedBlock(unmatched);
    }
    rows.sort(function (a, b) {
      return ((b.d.has ? 1 : 0) - (a.d.has ? 1 : 0)) || (b.d.mag - a.d.mag) ||
        (a.tier - b.tier) || a.ticker.localeCompare(b.ticker);
    });
    var nProposed = rows.filter(function (r) { return r.d.has; }).length;
    return '<p class="lede">' + esc(rows.length + ' tier 1–2 names · ' + nProposed +
      ' with a proposed change · tap a row for the reads behind it.' +
      (unmatched.length
        ? ' ' + unmatched.length + ' scored name' + (unmatched.length === 1 ? '' : 's') +
          ' could not be matched to a manifest tier and ' + (unmatched.length === 1 ? 'is' : 'are') +
          ' not shown in the table.'
        : '')) + '</p>' +
      '<div class="scrollx"><table class="data"><thead><tr>' +
      '<th>ticker</th><th>ai</th><th>ca</th><th>interest</th><th>proposed</th><th>last read</th>' +
      '</tr></thead><tbody>' + rows.map(function (r) {
        var cur = isObj(r.entry.current) ? r.entry.current : {};
        var ca = isObj(cur.competitive_advantage) ? cur.competitive_advantage : {};
        var open = !!scoresUI.open[r.ticker];
        var id = 'sc-' + r.ticker;
        return '<tr' + (r.d.has ? ' class="hot"' : '') + '>' +
          '<td><button type="button" class="linkbtn" data-act="score-row" data-v="' + esc(r.ticker) + '"' +
          ' aria-expanded="' + (open ? 'true' : 'false') + '" aria-controls="' + esc(id) + '">' + esc(r.ticker) + '</button></td>' +
          '<td class="n">' + esc(cur.ai_positioning === null || cur.ai_positioning === undefined ? '—' : cur.ai_positioning) + '</td>' +
          '<td class="n">' + esc(ca.overall === null || ca.overall === undefined ? '—' : ca.overall) + '</td>' +
          '<td class="n">' + esc(cur.investor_interest === null || cur.investor_interest === undefined ? '—' : cur.investor_interest) + '</td>' +
          '<td>' + proposedCell(r.entry) + '</td>' +
          '<td class="mono">' + esc(r.last || '—') + '</td></tr>' +
          '<tr class="expand" id="' + esc(id) + '"' + (open ? '' : ' hidden') + '><td colspan="6">' +
          '<div class="expand-in">' + scoreDetailHTML(r.ticker, r.entry) + '</div></td></tr>';
      }).join('') + '</tbody></table></div>' + unmatchedBlock(unmatched);
  }

  /* The names scores.json carries that the tier 1-2 table cannot show, each
   * with the reason, so "not in the table" never reads as "not in the build". */
  function unmatchedBlock(unmatched) {
    if (!arr(unmatched).length) return '';
    return fold('Scored names not in this table', unmatched.length,
      '<ul class="rows">' + unmatched.map(function (u) {
        return '<li>' + row(href(['ticker', u.ticker]),
          '<span class="dot-slot"></span><span class="row-title mono">' + esc(u.ticker) + '</span>' +
          '<span class="row-right">' + esc(u.why) + '</span>', '') + '</li>';
      }).join('') + '</ul>', false);
  }

  function scoreDetailHTML(ticker, entry) {
    var cur = isObj(entry.current) ? entry.current : {};
    var ca = isObj(cur.competitive_advantage) ? cur.competitive_advantage : {};
    var out = '<dl class="kv">' +
      '<dt>innovation</dt><dd>' + esc(ca.innovation_rate === null || ca.innovation_rate === undefined ? '—' : ca.innovation_rate) + '</dd>' +
      '<dt>distribution</dt><dd>' + esc(ca.distribution === null || ca.distribution === undefined ? '—' : ca.distribution) + '</dd>' +
      '</dl>';
    var pending = arr(entry.pending_proposals);
    if (pending.length) {
      out += '<p class="row-meta">' + pending.map(function (p) {
        return '<span class="pill pill-warn">' + esc((p.key || '') + ' ' + (p.applied || '—') + '→' + (p.value || '—')) + '</span>';
      }).join(' ') + '</p>';
    }
    var reads = arr(entry.reads).slice().sort(function (a, b) {
      return String(b.date || '').localeCompare(String(a.date || ''));
    });
    if (!reads.length) {
      out += emptyState('No scored read recorded for ' + ticker + ' yet.');
    } else {
      out += reads.slice(0, 4).map(function (r) {
        var t = String(r.note_id || '').split('/')[0] || ticker;
        var link = r.note_id
          ? '<a href="' + esc(href(['ticker', t, 'note', r.note_id])) + '">' + esc(r.quarter || r.date || 'read') + '</a>'
          : esc(r.quarter || r.date || 'read');
        return '<p class="readline"><span class="mono">' + esc(r.date || '') + '</span> ' + link + '<br>' +
          '<span class="muted">' + esc(clip(r.ai_positioning, 200)) + '</span></p>';
      }).join('') +
        '<p class="empty"><a href="' + esc(href(['ticker', ticker, 'signals'])) + '">' +
        esc('All ' + reads.length + ' reads for ' + ticker) + '</a></p>';
    }
    return out;
  }

  actions['score-row'] = function (node) {
    var t = node.getAttribute('data-v') || '';
    var tr = document.getElementById('sc-' + t);
    if (!tr) return;
    var open = !!tr.hidden;
    tr.hidden = !open;
    scoresUI.open[t] = open;
    node.setAttribute('aria-expanded', open ? 'true' : 'false');
  };

  function viewScores() {
    return loadJSON(SCORES_PATH).then(function (payload) {
      var p = isObj(payload) ? payload : {};
      return {
        title: 'Scores',
        html: section('Tier 1–2 scores', scoresTableHTML(p)) +
          '<p class="empty">' + esc('Scores as of ' + (p.as_of || 'unknown date') +
            '. Sorted by proposed change first, then by the size of the change.') + '</p>'
      };
    }).catch(function () {
      return { title: 'Scores', html: loadFail(SCORES_PATH) };
    });
  }

  /* --------------------------------------------------------- SIGNALS ------ */

  function signalsTab(bundle, meta, id) {
    return loadJSON(SCORES_PATH).then(function (payload) {
      var all = isObj(payload) && isObj(payload.tickers) ? payload.tickers : {};
      var entry = isObj(all[id]) ? all[id] : null;
      if (!entry) {
        return emptyState('No score record for ' + id + ' in this build — scores are kept for the names that carry a scoring block.');
      }
      var cur = isObj(entry.current) ? entry.current : {};
      var ca = isObj(cur.competitive_advantage) ? cur.competitive_advantage : {};
      var html = section('Current',
        '<dl class="kv">' +
        '<dt>ai positioning</dt><dd>' + esc(cur.ai_positioning === null || cur.ai_positioning === undefined ? '—' : cur.ai_positioning) + '</dd>' +
        '<dt>ca overall</dt><dd>' + esc(ca.overall === null || ca.overall === undefined ? '—' : ca.overall) + '</dd>' +
        '<dt>innovation</dt><dd>' + esc(ca.innovation_rate === null || ca.innovation_rate === undefined ? '—' : ca.innovation_rate) + '</dd>' +
        '<dt>distribution</dt><dd>' + esc(ca.distribution === null || ca.distribution === undefined ? '—' : ca.distribution) + '</dd>' +
        '<dt>investor interest</dt><dd>' + esc(cur.investor_interest === null || cur.investor_interest === undefined ? '—' : cur.investor_interest) + '</dd>' +
        '</dl>');

      var proposed = isObj(entry.proposed) ? entry.proposed : {};
      var pkeys = Object.keys(proposed);
      var pending = arr(entry.pending_proposals);
      var pbody = '';
      if (pkeys.length) {
        pbody += '<dl class="kv">' + pkeys.map(function (k) {
          var p = isObj(proposed[k]) ? proposed[k] : { value: proposed[k] };
          var was = pathGet(entry.current, k);
          return '<dt>' + esc(k) + '</dt><dd>' + esc((was === null ? '—' : was) + ' → ' + (p.value === undefined ? '—' : p.value)) +
            ' <span class="muted">' + esc(p.since || '') + '</span></dd>';
        }).join('') + '</dl>';
      }
      if (pending.length) {
        pbody += '<p class="row-meta">' + pending.map(function (p) {
          return '<span class="chip mono">' + esc(p.source || '') + '</span>';
        }).join('') + '</p>';
      }
      html += section('Proposed', pbody || emptyState('No score change is proposed for ' + id + '.'));

      var reads = arr(entry.reads).slice().sort(function (a, b) {
        return String(b.date || '').localeCompare(String(a.date || ''));
      });
      html += section('Reads — ' + reads.length, reads.length
        ? reads.map(function (r, i) {
          return fold((r.quarter || 'read') + '  ' + (r.date || ''), null, readBlock(r, true), i === 0);
        }).join('')
        : emptyState('No scored read for ' + id + ' yet — a read is written when an earnings note scores the three dimensions.'));
      return html;
    }).catch(function () {
      return loadFail(SCORES_PATH);
    });
  }

  /* ------------------------------------------------------------ NEWS ------ */

  /* news_index maps a ticker to [shard, row-index] pairs; the shards are whole
   * weeks of classified rows and run to a megabyte each, so only the two most
   * recent weeks a ticker appears in load on entry. The rest stay one tap away
   * (never truncated away) behind "load older weeks", and loadJSON memoises, so
   * a second visit to the same ticker costs nothing. */
  var NEWS_SHARD_STEP = 2;
  var CONF_PILL = { high: 'pill-ok', medium: 'pill-accent', low: 'pill-neutral' };
  var newsUI = { ticker: null, conf: 'all', shards: [], loaded: 0, rows: [] };

  function newsShardPath(shard) {
    var s = String(shard === null || shard === undefined ? '' : shard);
    return /^[A-Za-z0-9_.\-]+$/.test(s) ? 'data/news/' + s + '.json' : null;
  }

  function newsLoadShard(sh) {
    if (sh.done) return Promise.resolve();
    sh.done = true;
    var path = newsShardPath(sh.shard);
    if (!path) { sh.failed = true; return Promise.resolve(); }
    /* Whose news this is, captured now: a week file can still be in flight when
     * the reader moves to another ticker, and those rows must not land in the
     * new ticker's list. */
    var owner = newsUI.ticker;
    return loadJSON(path).then(function (payload) {
      if (newsUI.ticker !== owner) return;
      var rows = arr(payload && payload.rows);
      sh.idxs.forEach(function (i) {
        var r = rows[i];
        if (isObj(r)) newsUI.rows.push(r);
      });
    }).catch(function () { sh.failed = true; });
  }

  function newsLoadMore(step) {
    var start = newsUI.loaded;
    var end = Math.min(newsUI.shards.length, start + step);
    newsUI.loaded = end;
    var jobs = [];
    for (var i = start; i < end; i++) jobs.push(newsLoadShard(newsUI.shards[i]));
    return Promise.all(jobs);
  }

  function newsRowsHTML() {
    var rows = newsUI.rows.filter(function (r) {
      return newsUI.conf === 'all' || String(r.confidence) === newsUI.conf;
    });
    if (!rows.length) {
      return emptyState(newsUI.conf === 'all'
        ? 'No classified news rows for ' + newsUI.ticker + ' in the weeks loaded.'
        : 'No ' + newsUI.conf + '-confidence rows for ' + newsUI.ticker + ' in the weeks loaded.');
    }
    rows.sort(function (a, b) { return String(b.date || '').localeCompare(String(a.date || '')); });
    var shown = rows.slice(0, 120);
    return '<ul class="rows">' + shown.map(function (r) {
      var conf = String(r.confidence || 'unknown');
      var out = '<li class="row"><div class="row-top">' +
        '<span class="row-right mono">' + esc(r.date || '') + '</span>' +
        '<span class="row-title">' + extLink(r.url, r.headline || r.id || 'untitled') + '</span></div>' +
        '<div class="row-meta">' +
        '<span class="pill ' + (CONF_PILL[conf] || 'pill-neutral') + '">' + esc(conf) + '</span>' +
        (r.summarized ? '<span class="pill pill-accent">summarized</span>' : '') +
        arr(r.themes).slice(0, 4).map(function (t) {
          return '<a class="chip" href="' + esc(href(['theme', t])) + '">' + esc(t) + '</a>';
        }).join('') +
        arr(r.macro_signals).slice(0, 3).map(function (m) {
          return '<span class="chip">' + esc(m) + '</span>';
        }).join('') + '</div>';
      if (r.rationale) out += '<div class="row-meta">' + esc(clip(r.rationale, 240)) + '</div>';
      return out + '</li>';
    }).join('') + '</ul>' +
      (rows.length > shown.length
        ? '<p class="empty">' + esc((rows.length - shown.length) + ' older rows in the loaded weeks are not shown.') + '</p>'
        : '');
  }

  function newsBodyHTML() {
    var counts = { high: 0, medium: 0, low: 0 };
    newsUI.rows.forEach(function (r) {
      var c = String(r.confidence);
      if (counts[c] !== undefined) counts[c]++;
    });
    var opts = [['all', 'All ' + newsUI.rows.length], ['high', 'High ' + counts.high],
      ['medium', 'Medium ' + counts.medium], ['low', 'Low ' + counts.low]];
    var remaining = newsUI.shards.length - newsUI.loaded;
    var weeks = newsUI.shards.slice(0, newsUI.loaded).map(function (s) { return s.shard; }).join(', ');
    var failed = newsUI.shards.slice(0, newsUI.loaded).filter(function (s) { return s.failed; }).length;
    return filterChips('news-conf', opts, newsUI.conf) +
      '<p class="lede">' + esc(weeks ? 'Weeks loaded: ' + weeks + '.' : 'No news week loaded.') +
      (failed ? esc(' ' + failed + ' week file could not be read.') : '') + '</p>' +
      '<div id="news-rows">' + newsRowsHTML() + '</div>' +
      (remaining > 0
        ? '<p class="row-meta"><button type="button" class="btn" data-act="news-more">' +
          esc('Load older weeks (' + remaining + ')') + '</button></p>'
        : '');
  }

  function secRowsHTML(ticker, rows) {
    var mine = arr(rows).filter(function (r) { return r && String(r.ticker) === String(ticker); });
    if (!mine.length) {
      return emptyState('No SEC filing for ' + ticker + ' in the last 30 days of this bundle.');
    }
    mine.sort(function (a, b) { return String(b.filed_date || '').localeCompare(String(a.filed_date || '')); });
    return '<ul class="rows">' + mine.map(function (r) {
      var links = [];
      var f = safeURL(r.filing_url);
      if (f) links.push(extLink(f, 'EDGAR filing', 'chip'));
      var pr = safeURL(r.press_release_url);
      if (pr) links.push(extLink(pr, 'press release', 'chip'));
      return '<li class="row"><div class="row-top">' +
        '<span class="row-key">' + esc(r.form_type || 'filing') + '</span>' +
        '<span class="row-title">' + esc(arr(r.items).length ? 'items ' + arr(r.items).join(', ') : 'no itemised events') + '</span>' +
        '<span class="row-right mono">' + esc(r.filed_date || '') + '</span></div>' +
        '<div class="row-meta">' + links.join('') +
        arr(r.themes).slice(0, 4).map(function (t) {
          return '<a class="chip" href="' + esc(href(['theme', t])) + '">' + esc(t) + '</a>';
        }).join('') + '</div></li>';
    }).join('') + '</ul>';
  }

  function newsTab(bundle, meta, id) {
    var soft = function (path) { return loadJSON(path).catch(function () { return null; }); };
    return Promise.all([soft(NEWS_INDEX_PATH), soft(SEC_PATH)]).then(function (both) {
      var index = isObj(both[0]) ? both[0] : null;
      var sec = isObj(both[1]) ? both[1] : null;

      var byShard = {}, order = [];
      arr(index && index[id]).forEach(function (pair) {
        if (!Array.isArray(pair) || pair.length < 2) return;
        var shard = String(pair[0]);
        var idx = num(pair[1]);
        if (idx === null) return;
        if (!byShard[shard]) { byShard[shard] = { shard: shard, idxs: [] }; order.push(shard); }
        byShard[shard].idxs.push(idx);
      });
      order.sort();
      order.reverse();

      newsUI.ticker = id;
      newsUI.conf = 'all';
      newsUI.rows = [];
      newsUI.loaded = 0;
      newsUI.shards = order.map(function (s) { return byShard[s]; });

      return newsLoadMore(NEWS_SHARD_STEP).then(function () {
        var newsPart = !index
          ? loadFail(NEWS_INDEX_PATH)
          : (newsUI.shards.length
            ? '<div id="news-body">' + newsBodyHTML() + '</div>'
            : emptyState('No classified news row mentions ' + id + ' in this bundle’s news window.'));
        var secPart = !sec ? loadFail(SEC_PATH) : secRowsHTML(id, sec.rows);
        return section('News', newsPart) + section('SEC filings — last 30 days', secPart);
      });
    }).catch(function () {
      /* The two bundles are already soft-caught, so this only fires on a shape
       * this code did not expect -- still a sentence, not a blank tab. */
      return section('News', emptyState('The news and filings for ' + id + ' could not be assembled from this bundle.'));
    });
  }

  actions['news-conf'] = function (node) {
    newsUI.conf = node.getAttribute('data-v') || 'all';
    repaint('news-body', newsBodyHTML());
  };

  actions['news-more'] = function (node) {
    node.disabled = true;
    node.textContent = 'Loading…';
    newsLoadMore(NEWS_SHARD_STEP).then(function () { repaint('news-body', newsBodyHTML()); });
  };

  /* -------------------------------------------------------- INSIDERS ------ */

  /* data/insiders.json is the small file the builder writes for this tab (~12
   * rows); data/market.json is the ~1MB bundle that also carries them, kept as
   * the fallback for a bundle published before that file existed. */
  function insiderRows() {
    return loadJSON(INSIDERS_PATH).then(function (payload) {
      return arr(isObj(payload) ? payload.rows : null);
    }).catch(function () {
      return loadJSON(MARKET_PATH).then(function (payload) {
        return arr(isObj(payload) ? payload.insiders : null);
      });
    });
  }

  function insidersTab(bundle, meta, id) {
    return insiderRows().then(function (all) {
      var rows = all.filter(function (r) { return r && String(r.ticker) === String(id); });
      var note = '<p class="empty">' + esc('Static rows from this build’s market bundle — the live insider feed goes live in slice 4.') + '</p>';
      if (!rows.length) {
        return section('Insider transactions',
          emptyState('No insider transaction for ' + id + ' in this build’s market bundle.') + note);
      }
      rows.sort(function (a, b) { return String(b.date || '').localeCompare(String(a.date || '')); });
      var table = '<div class="scrollx"><table class="data"><thead><tr>' +
        '<th>date</th><th>insider</th><th>role</th><th>type</th><th>shares</th><th>value</th><th>10b5-1</th>' +
        '</tr></thead><tbody>' + rows.map(function (r) {
          var shares = num(r.shares), value = num(r.value);
          return '<tr><td class="mono">' + esc(r.date || '') + '</td>' +
            '<td>' + esc(r.insider || '') + '</td>' +
            '<td>' + esc(r.position || '') + '</td>' +
            '<td>' + esc(r.txn_type || '') + '</td>' +
            '<td class="n">' + esc(shares === null ? '—' : Math.round(shares).toLocaleString('en-US')) + '</td>' +
            '<td class="n">' + esc(value === null ? '—' : '$' + Math.round(value).toLocaleString('en-US')) + '</td>' +
            '<td>' + (r.tenb5 ? 'yes' : 'no') + '</td></tr>' +
            (r.notable ? '<tr class="expand"><td colspan="7"><div class="expand-in">' + esc(r.notable) + '</div></td></tr>' : '');
        }).join('') + '</tbody></table></div>';
      return section('Insider transactions — ' + rows.length, table + note);
    }).catch(function () { return loadFail(INSIDERS_PATH); });
  }

  /* ------------------------------------------------------------- ETF ------ */

  var ETF_ACTION_PILL = { 'new': 'pill-ok', added: 'pill-accent', trimmed: 'pill-warn', exit: 'pill-bad', exits: 'pill-bad' };

  function etfTab(bundle, meta, id) {
    return loadJSON(ETF_PATH).then(function (payload) {
      var byTicker = isObj(payload) && isObj(payload.by_ticker) ? payload.by_ticker : {};
      var rows = arr(byTicker[id]);
      if (!rows.length) {
        return section('ETF trades',
          emptyState('No tracked ETF traded ' + id + ' in this bundle’s ' + arr(payload && payload.days).length + '-day window.'));
      }
      var body = '<ul class="rows">' + rows.map(function (r) {
        var act = String(r.action || '');
        return '<li class="row"><div class="row-top">' +
          '<span class="row-key">' + esc(r.etf || '') + '</span>' +
          '<span class="row-title"><span class="pill ' + (ETF_ACTION_PILL[act] || 'pill-neutral') + '">' + esc(act || 'change') + '</span></span>' +
          '<span class="row-right mono">' + esc(r.date || '') + '</span></div></li>';
      }).join('') + '</ul>' +
        '<p class="empty"><a href="' + esc(href(['more', 'etf'])) + '">Every ETF’s daily changes</a></p>';
      return section('ETF trades — ' + rows.length, body);
    }).catch(function () { return loadFail(ETF_PATH); });
  }

  function etfItemLine(kind, raw) {
    var item = isObj(raw) ? raw : {};
    var sym = item.sym ? String(item.sym) : '';
    var bits = [];
    if (num(item.weight) !== null) bits.push(num(item.weight).toFixed(2) + '% weight');
    if (num(item.delta_pp) !== null) bits.push((num(item.delta_pp) > 0 ? '+' : '') + num(item.delta_pp).toFixed(2) + 'pp');
    if (num(item.from_weight) !== null && num(item.to_weight) !== null) {
      bits.push(num(item.from_weight).toFixed(2) + '% → ' + num(item.to_weight).toFixed(2) + '%');
    }
    if (num(item.shares) !== null) bits.push(Math.round(num(item.shares)).toLocaleString('en-US') + ' shares');
    return '<li class="row"><div class="row-top">' +
      '<span class="pill ' + (ETF_ACTION_PILL[kind] || 'pill-neutral') + '">' + esc(kind) + '</span>' +
      '<span class="row-title">' + (sym
        ? '<a href="' + esc(href(['ticker', sym])) + '">' + esc(sym) + '</a> <span class="muted">' + esc(item.name || '') + '</span>'
        : esc(item.name || 'unnamed holding')) + '</span></div>' +
      (bits.length ? '<div class="row-meta mono">' + esc(bits.join(' · ')) + '</div>' : '') + '</li>';
  }

  function viewEtfArchive() {
    return loadJSON(ETF_PATH).then(function (payload) {
      var days = arr(isObj(payload) ? payload.days : null);
      if (!days.length) {
        return { title: 'ETF trades', html: emptyState('This build carries no ETF holdings changes.') };
      }
      var sorted = days.slice().sort(function (a, b) { return String(b.date || '').localeCompare(String(a.date || '')); });
      var html = sorted.map(function (day, di) {
        var active = arr(day.etfs).filter(function (e) {
          return e && (arr(e['new']).length || arr(e.exits).length || arr(e.added).length || arr(e.trimmed).length);
        });
        var quiet = arr(day.etfs).length - active.length;
        var body = active.length
          ? active.map(function (e) {
            var items = arr(e['new']).map(function (i) { return etfItemLine('new', i); })
              .concat(arr(e.exits).map(function (i) { return etfItemLine('exit', i); }))
              .concat(arr(e.added).map(function (i) { return etfItemLine('added', i); }))
              .concat(arr(e.trimmed).map(function (i) { return etfItemLine('trimmed', i); }));
            return '<div class="daterule"><span class="d">' + esc(e.etf || '') + '</span>' +
              '<span class="n">' + esc(e.name || '') + '</span></div>' +
              '<ul class="rows">' + items.join('') + '</ul>';
          }).join('')
          : emptyState('No tracked ETF changed a holding on this date.');
        return fold(day.date || 'undated',
          active.length + (active.length === 1 ? ' ETF' : ' ETFs'),
          body + (quiet ? '<p class="empty">' + esc(quiet + ' other tracked ETFs were unchanged.') + '</p>' : ''),
          di === 0);
      }).join('');
      return {
        title: 'ETF trades',
        html: '<p class="lede">' + esc(sorted.length + ' days of tracked ETF holdings changes, newest first.') + '</p>' + html
      };
    }).catch(function () {
      return { title: 'ETF trades', html: loadFail(ETF_PATH) };
    });
  }

  /* --------------------------------------------------------- REPORTS ------ */

  /* The archive's index is the manifest itself -- every data/reports/<date>.json
   * is already listed with its byte size -- so the list screen fetches nothing
   * and a date's shard loads only when that date is opened. */
  function reportDates() {
    var m = isObj(STATE.manifest) ? STATE.manifest : {};
    var files = isObj(m.files) ? m.files : {};
    var out = [];
    Object.keys(files).forEach(function (p) {
      var m = /^data\/reports\/(\d{4}-\d{2}-\d{2})\.json$/.exec(p);
      if (m) out.push({ date: m[1], path: p, bytes: (files[p] && files[p].bytes) || 0 });
    });
    out.sort(function (a, b) { return b.date.localeCompare(a.date); });
    return out;
  }

  function viewReports(parts) {
    var day = parts[2];
    var dates = reportDates();
    if (!day) {
      if (!dates.length) {
        return { title: 'Reports', html: emptyState('This build published no report files.') };
      }
      var todayCards = {};
      var today = isObj(STATE.manifest) ? STATE.manifest.today : null;
      arr(today && today.cards).forEach(function (c) {
        if (c && c.date) todayCards[String(c.date)] = (todayCards[String(c.date)] || 0) + 1;
      });
      return {
        title: 'Reports',
        html: '<p class="lede">' + esc(dates.length + ' days of premarket, postmarket, digest and alert cards.') + '</p>' +
          '<ul class="rows">' + dates.map(function (d) {
            return '<li>' + row(href(['more', 'reports', d.date]),
              '<span class="dot-slot"></span><span class="row-title mono">' + esc(d.date) + '</span>' +
              '<span class="row-right">' + esc(kb(d.bytes)) + '</span>',
              todayCards[d.date] ? '<span>' + esc(todayCards[d.date] + ' cards') + '</span>' : '<span>open for its cards</span>') + '</li>';
          }).join('') + '</ul>'
      };
    }
    var hit = null;
    dates.forEach(function (d) { if (d.date === String(day)) hit = d; });
    if (!hit) {
      return { title: 'Reports', html: emptyState('No report file for ' + day + ' in this build. Open More → Reports for the days it carries.') };
    }
    return loadJSON(hit.path).then(function (payload) {
      var cards = arr(isObj(payload) ? payload.cards : null);
      if (!cards.length) {
        return { title: hit.date, html: emptyState('The report file for ' + hit.date + ' carries no cards.') };
      }
      return {
        title: hit.date,
        html: '<ul class="rows">' + cards.map(function (c) {
          /* This screen has already read the day's shard, so an alert card's
           * item count is free here -- Today pays a fetch for the same line. */
          var summary = itemsSummary ? itemsSummary(c) : '';
          return '<li>' + row(href(['today', c.id]),
            dot(!isRead('cards', c.id)) + '<span class="row-title">' + esc(c.title || c.id) + '</span>',
            '<span class="eyebrow">' + esc(c.kind || 'report') + '</span>' +
            '<span class="num">' + esc(kb(num(c.bytes))) + '</span>' +
            (summary ? '<span class="row-sum">' + esc(summary) + '</span>' : '')) + '</li>';
        }).join('') + '</ul>'
      };
    }).catch(function () {
      return { title: hit.date, html: loadFail(hit.path) };
    });
  }

  /* ---------------------------------------------------------- SEARCH ------ */

  /* TOKENIZER -- mirrors scripts/portal/search_index.py's TOKENIZER SPEC
   * docstring exactly, and any change here is a change there:
   *   1. lowercase the whole string,
   *   2. find-all with /[a-z0-9][a-z0-9.\-]+/g (NOT split-on-whitespace): 2+
   *      chars, leading alphanumeric, `.` and `-` token-internal, a trailing
   *      `.`/`-` NOT stripped,
   *   3. drop exact members of the stoplist -- which is read from the payload
   *      (`stoplist`), never hardcoded here, so the two cannot drift,
   *   4. no stemming, no plural folding,
   *   5. duplicates are not removed by the tokenizer itself. */
  var SEARCH_TOKEN_SRC = '[a-z0-9][a-z0-9.\\-]+';
  var SEARCH_CAP = 80;

  function tokenize(text, stop) {
    var s = String(text === null || text === undefined ? '' : text).toLowerCase();
    var re = new RegExp(SEARCH_TOKEN_SRC, 'g');
    var out = [], m;
    while ((m = re.exec(s)) !== null) {
      if (stop && Object.prototype.hasOwnProperty.call(stop, m[0])) continue;
      out.push(m[0]);
    }
    return out;
  }

  var searchUI = { q: '', state: 'idle', index: null, results: [], pending: null };

  function ensureIndex() {
    if (searchUI.state === 'ready') return Promise.resolve(searchUI.index);
    if (searchUI.pending) return searchUI.pending;
    searchUI.state = 'loading';
    searchUI.pending = loadJSON(SEARCH_PATH).then(function (payload) {
      var p = isObj(payload) ? payload : {};
      var stop = {};
      arr(p.stoplist).forEach(function (w) { stop[String(w)] = 1; });
      searchUI.index = {
        docs: arr(p.docs),
        terms: isObj(p.terms) ? p.terms : {},
        stop: stop,
        news_mode: p.news_mode || ''
      };
      searchUI.state = 'ready';
      return searchUI.index;
    }).catch(function (err) {
      searchUI.state = 'failed';
      searchUI.pending = null;
      throw err;
    });
    return searchUI.pending;
  }

  /* AND over every query token first; only if that is empty does the query fall
   * back to OR, scored by how many of the tokens a doc matched. Ties break on
   * date, newest first. */
  function searchRun(q) {
    var idx = searchUI.index;
    if (!idx) return { tokens: [], hits: [] };
    var seen = {}, tokens = [];
    tokenize(q, idx.stop).forEach(function (t) { if (!seen[t]) { seen[t] = 1; tokens.push(t); } });
    if (!tokens.length) return { tokens: tokens, hits: [] };

    var counts = {};
    tokens.forEach(function (t) {
      arr(idx.terms[t]).forEach(function (d) { counts[d] = (counts[d] || 0) + 1; });
    });
    var and = [], or = [];
    Object.keys(counts).forEach(function (k) {
      var i = parseInt(k, 10);
      var doc = idx.docs[i];
      if (!isObj(doc)) return;
      var hit = { i: i, doc: doc, score: counts[k] };
      if (counts[k] === tokens.length) and.push(hit);
      or.push(hit);
    });
    var hits = and.length ? and : or;
    hits.sort(function (a, b) {
      return (b.score - a.score) ||
        String(b.doc.d || '').localeCompare(String(a.doc.d || '')) ||
        String(a.doc.id || '').localeCompare(String(b.doc.id || ''));
    });
    return { tokens: tokens, hits: hits, mode: and.length ? 'all' : 'any' };
  }

  /* Where a hit goes when tapped. `f` is a data file, not a route, so it is the
   * thing that decides: a ticker bundle routes to the note (or the thesis tab --
   * a thesis is not in bundle.notes and has no note id), themes.json routes to
   * the theme page, and news/ingest items have no screen of their own, so they
   * open inline from their own file. `f: null` (a few report/other units) is
   * text only. */
  function docRoute(doc) {
    var f = String(doc.f === null || doc.f === undefined ? '' : doc.f);
    var base = String(doc.id === null || doc.id === undefined ? '' : doc.id).split('#')[0];
    var m = /^data\/(tickers|pvt)\/(.+)\.json$/.exec(f);
    if (m) {
      /* The unit id is "<route-id>/<file>", and for a private name the route id
       * ("simaai.pvt") is NOT the bundle FILE name ("data/pvt/simaai.json") --
       * so the id's own prefix wins and the file name is only the fallback.
       * For public tickers the two are identical (checked across every
       * ticker/pvt doc in the live index). */
      var t = base.indexOf('/') >= 0 ? base.slice(0, base.indexOf('/')) : m[2];
      var rest = base.indexOf('/') >= 0 ? base.slice(base.indexOf('/') + 1) : base;
      if (/^_thesis/.test(rest)) return { kind: 'link', href: href(['ticker', t, 'thesis']) };
      return { kind: 'link', href: href(['ticker', t, 'note', base]) };
    }
    if (f === THEMES_PATH) {
      var slug = base.replace(/^themes\//, '').replace(/\.md$/, '');
      return { kind: 'link', href: href(['theme', slug]) };
    }
    if (/^data\/news\/.+\.json$/.test(f) || /^data\/ingest\/.+\.json$/.test(f)) {
      return { kind: 'inline', file: f };
    }
    return { kind: 'text' };
  }

  var SEARCH_KIND_ORDER = ['earnings', 'conference', 'thesis', 'synthesis', 'theme', 'news',
    'news_note', 'substack', 'podcast', 'profile', 'pvt_profile', 'report', 'flow', 'foreign', 'sector', 'other'];

  function searchResultsHTML() {
    if (searchUI.state === 'loading') return '<p class="skeleton">Loading the search index…</p>';
    if (searchUI.state === 'failed') return loadFail(SEARCH_PATH);
    if (searchUI.state !== 'ready') {
      return emptyState('Type to search every note section, news row, filing and ingest item in this bundle.');
    }
    var res = searchRun(searchUI.q);
    if (!res.tokens.length) {
      return emptyState(searchUI.q.trim()
        ? 'Every word in that query is a stop word or too short to index (a token is two or more characters).'
        : 'Type to search every note section, news row, filing and ingest item in this bundle.');
    }
    if (!res.hits.length) {
      return emptyState('Nothing in this bundle matches ' + res.tokens.join(' + ') + '.');
    }
    var shown = res.hits.slice(0, SEARCH_CAP);
    var groups = {}, order = [];
    shown.forEach(function (h) {
      var k = String(h.doc.k || 'other');
      if (!groups[k]) { groups[k] = []; order.push(k); }
      groups[k].push(h);
    });
    order.sort(function (a, b) {
      var ra = SEARCH_KIND_ORDER.indexOf(a), rb = SEARCH_KIND_ORDER.indexOf(b);
      return (ra < 0 ? 99 : ra) - (rb < 0 ? 99 : rb);
    });

    var head = '<p class="lede">' + esc(res.hits.length + ' hits for ' + res.tokens.join(' + ') +
      ' (' + (res.mode === 'all' ? 'all terms' : 'any term') + ')' +
      (res.hits.length > shown.length ? ', top ' + shown.length + ' shown' : '')) + '</p>';

    return head + order.map(function (k) {
      return '<div class="daterule"><span class="d">' + esc(k) + '</span>' +
        '<span class="n">' + esc(groups[k].length) + '</span></div>' +
        '<ul class="rows">' + groups[k].map(function (h) {
          var d = h.doc;
          var r = docRoute(d);
          var title = esc(clip(d.t || d.id, 140));
          var top = '<span class="row-title">' +
            (r.kind === 'link' ? '<a href="' + esc(r.href) + '">' + title + '</a>' : title) + '</span>' +
            '<span class="row-right mono">' + esc(d.d || '') + '</span>';
          var meta = arr(d.tk).slice(0, 4).map(function (t) {
            return '<a class="chip" href="' + esc(href(['ticker', t])) + '">' + esc(t) + '</a>';
          }).join('') + arr(d.th).slice(0, 3).map(function (t) {
            return '<a class="chip" href="' + esc(href(['theme', t])) + '">' + esc(t) + '</a>';
          }).join('');
          if (r.kind === 'inline') {
            /* A real control, so a real 44px target: .btn-mini keeps the
             * compact look with a smaller font, not a smaller hit area. */
            meta += '<button type="button" class="btn btn-mini" data-act="search-open"' +
              ' aria-expanded="false" data-i="' + esc(h.i) + '">Open</button>';
          }
          var snip = clip(d.sn || d.t || '', 220);
          return '<li class="row"><div class="row-top">' + top + '</div>' +
            (snip ? '<div class="row-meta">' + esc(snip) + '</div>' : '') +
            (meta ? '<div class="row-meta">' + meta + '</div>' : '') +
            '<div class="inline-doc" id="sr-' + esc(h.i) + '"></div></li>';
        }).join('') + '</ul>';
    }).join('');
  }

  /* A news row and an ingest item have no screen of their own; they open where
   * they are, out of the same file the index points at. */
  /* The button says what the next tap does. */
  function searchOpenLabel(node, open) {
    if (!node) return;
    node.textContent = open ? 'Close' : 'Open';
    if (node.setAttribute) node.setAttribute('aria-expanded', open ? 'true' : 'false');
  }

  actions['search-open'] = function (node) {
    var i = parseInt(node.getAttribute('data-i'), 10);
    var idx = searchUI.index;
    var doc = idx && isObj(idx.docs[i]) ? idx.docs[i] : null;
    var box = document.getElementById('sr-' + i);
    if (!doc || !box) return;
    if (box.innerHTML) { box.innerHTML = ''; searchOpenLabel(node, false); return; }
    searchOpenLabel(node, true);
    box.innerHTML = '<p class="skeleton">Loading…</p>';
    loadJSON(String(doc.f)).then(function (payload) {
      var s = num(doc.s);
      var item = null;
      if (/^data\/news\//.test(String(doc.f))) {
        var rows = arr(payload && payload.rows);
        item = (s !== null && isObj(rows[s])) ? rows[s] : null;
        if (!item) {
          rows.forEach(function (r) { if (r && String(r.id) === String(doc.id)) item = r; });
        }
        if (!item) { box.innerHTML = emptyState('That news row is no longer in its week file.'); return; }
        box.innerHTML = '<div class="panel">' +
          '<p class="row-top"><span class="row-title">' + extLink(item.url, item.headline || item.id) + '</span>' +
          '<span class="row-right mono">' + esc(item.date || '') + '</span></p>' +
          '<p class="row-meta"><span class="pill ' + (CONF_PILL[String(item.confidence)] || 'pill-neutral') + '">' +
          esc(item.confidence || 'unknown') + '</span>' +
          (item.summarized ? '<span class="pill pill-accent">summarized</span>' : '') +
          arr(item.themes).slice(0, 4).map(function (t) {
            return '<a class="chip" href="' + esc(href(['theme', t])) + '">' + esc(t) + '</a>';
          }).join('') + '</p>' +
          (item.rationale ? '<p>' + esc(item.rationale) + '</p>' : '') + '</div>';
        return;
      }
      var items = arr(payload && payload.items);
      items.forEach(function (it) { if (it && String(it.id) === String(doc.id)) item = it; });
      if (!item && s !== null && isObj(items[s])) item = items[s];
      if (!item) { box.innerHTML = emptyState('That item is no longer in its ingest bundle.'); return; }
      box.innerHTML = '<div class="panel">' +
        '<p class="row-meta"><span class="chip">' + esc(item.source || doc.k || 'ingest') + '</span>' +
        '<span class="mono">' + esc(item.date || '') + '</span>' +
        arr(item.tickers).slice(0, 6).map(function (t) {
          return '<a class="chip" href="' + esc(href(['ticker', t])) + '">' + esc(t) + '</a>';
        }).join('') + '</p>' +
        fold(clip(item.title || doc.t || 'item', 90), null, md(item.body || ''), true) + '</div>';
      wrapWide(box);
    }).catch(function () {
      box.innerHTML = loadFail(String(doc.f));
    });
  };

  controls['q-search'] = function (t) {
    searchUI.q = t.value || '';
    if (!searchUI.q.trim()) { repaint('search-results', searchResultsHTML()); return; }
    if (searchUI.state === 'ready' || searchUI.state === 'failed') {
      repaint('search-results', searchResultsHTML());
      return;
    }
    repaint('search-results', '<p class="skeleton">Loading the search index…</p>');
    ensureIndex().then(function () {
      repaint('search-results', searchResultsHTML());
    }).catch(function () {
      repaint('search-results', loadFail(SEARCH_PATH));
    });
  };

  function viewSearch() {
    var mode = searchUI.index ? searchUI.index.news_mode : '';
    return {
      title: 'Search',
      html: '<div class="controls"><div class="field">' +
        '<label for="q-search">Search this bundle</label>' +
        '<input type="search" id="q-search" name="q-search" value="' + esc(searchUI.q) + '"' +
        ' placeholder="ticker, phrase, theme" autocomplete="off" autocapitalize="off" spellcheck="false"></div></div>' +
        '<p class="lede">' + esc('Notes, theme notes, news rows and ingest items' +
          (mode ? ' (news window ' + mode + ')' : '') + '. The index loads once, on your first query.') + '</p>' +
        '<div id="search-results">' + searchResultsHTML() + '</div>'
    };
  }

  /* ---------------------------------------------------- registration ------ */

  views.themes = viewThemes;
  views.theme = viewTheme;
  views.ideas = viewIdeas;

  tickerTabs.signals = signalsTab;
  tickerTabs.news = newsTab;
  tickerTabs.insiders = insidersTab;
  tickerTabs.etf = etfTab;

  morePages.scores = viewScores;
  morePages.etf = viewEtfArchive;
  morePages.reports = viewReports;
  morePages.search = viewSearch;
})();
