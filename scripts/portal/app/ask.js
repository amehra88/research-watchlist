/* Research Desk — RIS4 portal app, part 3 (slice 3 Task 4: Ask Claude).
 *
 * Asks Claude about what is on screen, on the VIEWER's own Claude account,
 * through the published artifact's `sample` capability. Loaded LAST (after
 * app.js and app2.js) and a clean no-op without them: no `window.RIS`, nothing
 * to extend, no errors. It adds no screen of its own except `#/more/ask`; every
 * other entry point is a `.askslot` placeholder that app.js already renders and
 * this file fills in after a paint.
 *
 * The contract it is written against (artifact-capabilities `sample.d.ts`), and
 * the rules that follow from it:
 *
 *   - `await claude.use("sample")` resolves LATER than this script's first run
 *     and may be `null` (page not framed by a Claude viewer). Nothing reads
 *     `window.claude.sample`. Until it resolves non-null, every Ask affordance
 *     stays absent — an empty `.askslot`, hidden by CSS. No disabled
 *     placeholders: a button that cannot work is worse than no button.
 *   - `sample.limits()` is the only other capability call, and neither call
 *     spends usage. `sample()` itself is called ONLY from a tap. Never on load,
 *     never from a timer, never from a loop, never as a retry.
 *   - `onText({text, delta})` carries the WHOLE answer so far: assign it, never
 *     `+=`. It never fires before the first visible text, so the panel says
 *     "Thinking…" from the tap until it does.
 *   - one NEW `AbortController` per call; Stop aborts it, and so does the next
 *     paint (a navigation or a re-render), through app.js's `paintHooks`.
 *   - every failure is one rejected `{code, message, text?}`. `code` decides:
 *     the hide-the-feature codes take the feature away for this view, the rest
 *     show viewer copy and KEEP the control. Nothing here ever retries by
 *     itself. `refused` withdraws its partial; the other codes may keep `e.text`.
 *   - with `tools`, `cache` must be absent (any value but false rejects
 *     `invalid_request`), tool results must be small, and every round is a
 *     separate paid request — hence the 32 KB running budget across results.
 *
 * Everything injected into the DOM goes through `esc()`, `md()` (html:false) or
 * `textContent`. The panel lives INSIDE `#view`, so paint() destroys it on a
 * route change and its buttons ride app.js's delegated click registry — this
 * file attaches no listener of its own and so can never leak one.
 */
(function () {
  'use strict';

  var R = window.RIS;
  if (!R) return;   /* app.js did not load: nothing to extend, and no errors. */

  var esc = R.esc, arr = R.arr, isObj = R.isObj, href = R.href;
  var md = R.md, section = R.section, row = R.row, wrapWide = R.wrapWide;
  var loadJSON = R.loadJSON, findTicker = R.findTicker, bundlePath = R.bundlePath;
  var allNotes = R.allNotes;
  var morePages = R.morePages, actions = R.actions;

  /* app.js publishes `askSlot`; a stale cached copy of it would not, and the
   * one screen this file owns still has to render something. */
  var askSlot = (typeof R.askSlot === 'function') ? R.askSlot
    : function (scope) { return '<div class="askslot" data-ask-scope="' + esc(scope) + '"></div>'; };

  /* ------------------------------------------------------- capability ----- */

  var SAMPLE = null;      /* the resolved capability, or null: hide everything */
  var LIMITS = null;      /* sample.limits(), with a conservative default       */
  var DESK_OK = false;    /* limits.tools present -> desk mode is offerable     */
  var HIDDEN = false;     /* a hide-the-feature code arrived: stay hidden       */

  var DEFAULT_MAX_PROMPT = 65536;   /* the contract's own 64 KiB, if limits is silent */
  var PROMPT_HEADROOM = 2048;       /* what the assembled prompt must stay under */
  var NOTE_BODY_BYTES = 40 * 1024;
  var TICKER_BRIEF_BYTES = 4 * 1024;
  var TICKER_NOTE_BYTES = 12 * 1024;
  var TOOL_RESULT_BYTES = 10 * 1024;
  var TOOL_BUDGET_BYTES = 32 * 1024;
  var SEARCH_HITS = 8;
  var BRIEF_NOTES = 5;

  /* ------------------------------------------------------------ bytes ----- */

  /* The contract measures `input` in UTF-8 bytes, and this vault is full of
   * em dashes and ellipses, so a `.length` (UTF-16 units) budget would be a
   * guess. TextEncoder is the measure; the manual fallback exists for a bare
   * V8 (the headless harness) that has no Web APIs at all. */
  var ENC = (typeof TextEncoder === 'function') ? new TextEncoder() : null;

  function bytes(value) {
    var t = String(value === null || value === undefined ? '' : value);
    if (ENC) return ENC.encode(t).length;
    var n = 0;
    for (var i = 0; i < t.length; i++) {
      var c = t.charCodeAt(i);
      if (c < 0x80) n += 1;
      else if (c < 0x800) n += 2;
      else if (c >= 0xd800 && c <= 0xdbff && i + 1 < t.length) { n += 4; i++; }
      else n += 3;
    }
    return n;
  }

  /* Cut to at most `cap` BYTES, on a whole character. Returns {text, cut}. */
  function sliceBytes(value, cap) {
    var s = String(value === null || value === undefined ? '' : value);
    if (cap <= 0) return { text: '', cut: s.length > 0 };
    if (bytes(s) <= cap) return { text: s, cut: false };
    var lo = 0, hi = Math.min(s.length, cap);
    while (lo < hi) {
      var mid = Math.ceil((lo + hi) / 2);
      if (bytes(s.slice(0, mid)) <= cap) lo = mid; else hi = mid - 1;
    }
    /* never leave a lone high surrogate at the end */
    var code = lo > 0 ? s.charCodeAt(lo - 1) : 0;
    if (code >= 0xd800 && code <= 0xdbff) lo -= 1;
    return { text: s.slice(0, lo), cut: true };
  }

  var TRIM_MARK = '\n[trimmed]';
  var TRUNC_MARK = '\n[truncated]';

  function cap(value, capBytes) {
    var c = sliceBytes(value, Math.max(0, capBytes - bytes(TRIM_MARK)));
    return c.cut ? c.text + TRIM_MARK : c.text;
  }

  function promptCap() {
    var max = (LIMITS && typeof LIMITS.maxPromptBytes === 'number')
      ? LIMITS.maxPromptBytes : DEFAULT_MAX_PROMPT;
    return max - PROMPT_HEADROOM;
  }

  /* head + body + tail, with `body` (always the largest part by construction:
   * the note text or the brief+note block) sliced if the whole would exceed the
   * view's own maxPromptBytes less the headroom. Returns {text, trimmed}. */
  function assemble(head, body, tail) {
    var limit = promptCap();
    var fixed = bytes(head) + bytes(tail);
    if (fixed + bytes(body) <= limit) return { text: head + body + tail, trimmed: false };
    var room = limit - fixed;
    var cut = sliceBytes(body, Math.max(0, room - bytes(TRIM_MARK)));
    return { text: head + cut.text + (cut.cut ? TRIM_MARK : '') + tail, trimmed: cut.cut };
  }

  function clip(text, n) {
    var s = String(text === null || text === undefined ? '' : text).replace(/\s+/g, ' ').trim();
    return s.length > n ? s.slice(0, n - 1) + '…' : s;
  }

  function todayISO() {
    try { return new Date().toISOString().slice(0, 10); } catch (e) { return ''; }
  }

  /* ------------------------------------------------------- error copy ----- */

  /* Hide the feature for this view: permanent, never re-ask. */
  var HIDE_COPY = {
    not_granted: 'This desk is not allowed to use Claude on your account, so Ask is off for this view.',
    sampling_disabled: 'Claude is not available on this account, so Ask is off.',
    not_declared: 'This published page no longer declares the Claude capability, so Ask is off.',
    capability_disabled: 'Claude is granted but not usable in this view, so Ask is off.',
    capability_removed: 'This viewer app does not carry the Claude method this desk needs, so Ask is off.',
    tools_unavailable: 'This viewer cannot run page tools, so Ask the desk is off — ask about a note or a ticker instead.'
  };

  /* Tell the viewer, keep the control. */
  var ERROR_COPY = {
    rate_limited: 'Claude is rate-limited right now — too many calls, or your own usage limit. Try again later; this desk never retries by itself.',
    session_expired: 'Your Claude session expired. Sign in again in the Claude app, then ask again.',
    refused: 'Claude declined to answer this one, so nothing it had written is kept. Asking the same thing again gives the same answer — change what it asks.',
    empty_completion: 'Claude wrote nothing back. Ask for less, or put the question more plainly.',
    invalid_json: 'Claude’s reply could not be read. Ask again, or ask for less at a time.',
    upstream_error: 'That call failed on its way to Claude. Nothing was lost — ask again when you like.',
    prompt_too_large: 'That is more than one call can carry. Ask about a single note, or ask a shorter question.',
    invalid_request: 'This desk built a malformed request — a bug in the app, not something to fix from here.',
    transform_error: 'This desk could not prepare that request — a bug in the app, not something to fix from here.',
    queue_overflow: 'Too many calls were queued before the Claude runtime started. Reload the desk and ask again.',
    image_rejected: 'That image could not be used. This desk never sends images, so this is unexpected.',
    images_unavailable: 'This view cannot send images. This desk never sends images, so this is unexpected.',
    cancelled: ''
  };

  /* An unknown code is treated as upstream_error, per the contract. */
  function errorCopy(code) {
    var k = String(code || '');
    if (Object.prototype.hasOwnProperty.call(HIDE_COPY, k)) return HIDE_COPY[k];
    if (Object.prototype.hasOwnProperty.call(ERROR_COPY, k)) return ERROR_COPY[k];
    return ERROR_COPY.upstream_error;
  }

  /* Codes that take the whole feature away for this view. `tools_unavailable`
   * is in HIDE_COPY too but only takes DESK mode away -- plain calls still work,
   * so it is handled separately and is deliberately NOT in this map. */
  var HIDE_CODES = {
    not_granted: 1, sampling_disabled: 1, not_declared: 1,
    capability_disabled: 1, capability_removed: 1
  };

  /* ------------------------------------------------------------ state ----- */

  var MODE_LABEL = { note: 'this note', ticker: 'this ticker', desk: 'the whole desk' };

  var ask = {
    open: false,
    mode: null,       /* 'note' | 'ticker' | 'desk'                         */
    arg: null,        /* note id / ticker id / null                         */
    title: '',        /* what the panel header says it is scoped to         */
    q: '',            /* the question, kept so a re-render does not lose it */
    running: false,
    ctl: null,        /* the AbortController of the call in flight          */
    answer: '',
    done: false,      /* answer complete -> render it as markdown           */
    error: '',        /* viewer copy for the last failure                   */
    tier: '',         /* modelTierApplied                                   */
    truncated: false,
    trimmed: false,
    tools: []         /* names of the tools that ran, in order              */
  };

  function resetRun() {
    ask.answer = '';
    ask.done = false;
    ask.error = '';
    ask.tier = '';
    ask.truncated = false;
    ask.trimmed = false;
    ask.tools = [];
  }

  /* Stop and teardown are NOT the same abort. Stop wants the call's own
   * rejection (`cancelled`) to arrive and restore the idle panel, so it leaves
   * `ask.ctl` in place for the handler's superseded-check to match. Teardown (a
   * paint, a close) wants the opposite: clear the handle first, so the late
   * rejection lands on a controller nobody is waiting for and changes nothing. */
  function stopInFlight() {
    if (ask.ctl) { try { ask.ctl.abort(); } catch (e) { /* already settled */ } }
  }

  function abortInFlight() {
    stopInFlight();
    ask.ctl = null;
    ask.running = false;
  }

  /* ------------------------------------------------------------ mount ----- */

  function slotHTML(scope, argv) {
    if (scope === 'note') {
      return btn('Ask about this note', 'note', argv);
    }
    if (scope === 'ticker') {
      return btn('Ask about ' + String(argv || ''), 'ticker', argv);
    }
    if (scope === 'desk') {
      if (!DESK_OK) {
        return '<p class="empty">Ask the desk needs page tools, which this viewer cannot run. ' +
          'Ask is still available on a ticker or on a single note.</p>';
      }
      return btn('Ask the desk', 'desk', null);
    }
    if (scope === 'more') {
      /* A sibling <ul> to the More list, so `.row:last-child { border-bottom: 0 }`
       * leaves no hairline above it -- .askrows puts one back. */
      return '<ul class="rows askrows"><li>' + row(href(['more', 'ask']),
        '<span class="dot-slot"></span><span class="row-title">Ask</span>',
        '<span>' + esc(DESK_OK ? 'Ask Claude across this bundle' : 'Ask Claude about a ticker or a note') +
        '</span>') + '</li></ul>';
    }
    return '';
  }

  function btn(label, scope, argv) {
    return '<button type="button" class="btn btn-ask" data-act="ask-open"' +
      ' data-ask-scope="' + esc(scope) + '"' +
      (argv === null || argv === undefined ? '' : ' data-ask-arg="' + esc(argv) + '"') +
      '>' + esc(label) + '</button>';
  }

  /* Fill every placeholder in the freshly painted view. Called from the paint
   * hook AND once when use("sample") resolves -- the capability lands seconds
   * after load, by which time the first screen is already painted, so without
   * the second trigger Ask would not appear until the operator navigated. */
  function mountAll(root) {
    var view = root || document.getElementById('view');
    if (!view || typeof view.querySelectorAll !== 'function') return;
    var slots = view.querySelectorAll('.askslot');
    for (var i = 0; i < slots.length; i++) {
      var node = slots[i];
      var scope = (node.getAttribute && node.getAttribute('data-ask-scope')) || '';
      var argv = node.getAttribute ? node.getAttribute('data-ask-arg') : null;
      node.innerHTML = (SAMPLE && !HIDDEN) ? slotHTML(scope, argv) : '';
    }
  }

  /* The panel's host: a div appended to #view (not to <body>), so the next
   * paint destroys it exactly as it destroys the rest of the screen. */
  function panelHost() {
    var found = document.getElementById('ask-host');
    if (found) return found;
    var view = document.getElementById('view');
    if (!view || typeof view.appendChild !== 'function') return null;
    var box = document.createElement('div');
    box.setAttribute('id', 'ask-host');
    view.appendChild(box);
    return box;
  }

  /* ----------------------------------------------------------- render ----- */

  function statusLine() {
    var bits = [];
    bits.push('asking about ' + (MODE_LABEL[ask.mode] || 'this desk'));
    if (ask.running && !ask.answer) bits.push('Thinking…');
    else if (ask.running) bits.push('writing…');
    if (ask.tools.length) bits.push('tools: ' + ask.tools.join(', '));
    if (ask.tier) bits.push('answered on the ' + ask.tier + ' tier');
    if (ask.trimmed) bits.push('context trimmed to fit one call');
    if (ask.truncated) bits.push('cut short — ask for less at a time');
    return bits.join(' · ');
  }

  function answerHTML() {
    if (!ask.answer) return '';
    return ask.done ? md(ask.answer) : '<pre class="stream">' + esc(ask.answer) + '</pre>';
  }

  function panelHTML() {
    var canAsk = !!SAMPLE && !HIDDEN;
    return '<section class="asksheet" role="region" aria-label="Ask Claude">' +
      '<div class="asksheet-in">' +
      '<p class="askhead"><span class="eyebrow">' + esc(ask.title || 'Ask Claude') + '</span>' +
      '<button type="button" class="btn btn-mini" data-act="ask-close">Close</button></p>' +
      (canAsk
        ? '<div class="field"><label for="ask-q">Your question</label>' +
          '<textarea id="ask-q" name="ask-q" rows="2" autocapitalize="sentences" spellcheck="true" ' +
          'placeholder="What does this say about…">' + esc(ask.q) + '</textarea></div>' +
          '<p class="askbar">' +
          '<button type="button" class="btn" id="ask-go" data-act="ask-go"' +
          (ask.running ? ' disabled' : '') + '>Ask</button>' +
          (ask.running
            ? '<button type="button" class="btn btn-mini" id="ask-stop" data-act="ask-stop">Stop</button>'
            : '') +
          (ask.answer
            ? '<button type="button" class="btn btn-mini" id="ask-copy" data-act="ask-copy">Copy answer</button>'
            : '') +
          '</p>'
        : '') +
      '<p class="askstatus" id="ask-status" aria-live="polite">' + esc(statusLine()) + '</p>' +
      (ask.error ? '<p class="askerr" id="ask-err">' + esc(ask.error) + '</p>' : '') +
      /* `streaming` keeps the newlines of the plain text onText assigns; the
       * settled render drops it, so markdown-it's own block layout governs. */
      '<div class="askout' + (ask.done ? '' : ' streaming') + '" id="ask-out">' +
      answerHTML() + '</div>' +
      '<p class="empty">Answers are Claude reading this bundle, on your own Claude account. ' +
      'Save to vault arrives in slice 5.</p>' +
      '</div></section>';
  }

  /* A full re-render: only on a state change that changes the panel's SHAPE
   * (open, run start, settle). While text streams, `onText` touches the two
   * live nodes and nothing else, so the textarea keeps its value and focus. */
  function renderPanel() {
    var host = panelHost();
    if (!host) return;
    host.innerHTML = ask.open ? panelHTML() : '';
    if (ask.open && ask.done) wrapWide(host);
  }

  function setLive() {
    var out = document.getElementById('ask-out');
    if (out) out.textContent = ask.answer;
    var st = document.getElementById('ask-status');
    if (st) st.textContent = statusLine();
  }

  /* ------------------------------------------------------------ prompt ---- */

  var RULES =
    'Rules: answer only from the material above — never invent numbers, dates, ' +
    'names or quotes, and never fill a gap from general knowledge; say plainly when ' +
    'this material does not answer the question; cite note ids in [brackets] when you ' +
    'lean on one; keep it short enough to read on a phone.';

  function head(scopeLine) {
    return 'You are answering inside a private equity-research desk: a vault of ' +
      'analyst notes on public technology companies, published as a static bundle. ' +
      'Today is ' + todayISO() + '.\n' + scopeLine + '\n' + RULES + '\n\n';
  }

  function tail(question) {
    return '\n\nQuestion: ' + String(question).trim() + '\n';
  }

  function noteById(bundle, id) {
    var want = String(id), found = null;
    allNotes(bundle).forEach(function (n) { if (n && String(n.id) === want) found = n; });
    return found;
  }

  function noteText(note) {
    if (!isObj(note)) return '';
    if (note.body) return String(note.body);
    return arr(note.sections).map(function (s) {
      return '## ' + String((s && (s.h || s.title)) || '') + '\n' + String((s && s.text) || '');
    }).join('\n\n');
  }

  function routeIdOf(noteId) {
    var s = String(noteId || '');
    var cut = s.indexOf('/');
    return cut < 0 ? '' : s.slice(0, cut);
  }

  /* NOTE MODE -- instructions + this note's body (40 KB) + the question. */
  function buildNote(noteId, question) {
    var routeId = routeIdOf(noteId);
    if (!routeId) return Promise.resolve(null);
    return loadJSON(bundlePath(routeId)).then(function (bundle) {
      var note = noteById(bundle, noteId);
      if (!note) return null;
      var body = 'NOTE ' + String(note.id) +
        '\ntitle: ' + String(note.title || note.rel || note.id) +
        '\ndate: ' + String(note.date || 'undated') +
        '\nkind: ' + String(note.kind || 'note') +
        '\nticker: ' + routeId + '\n\n' + cap(noteText(note), NOTE_BODY_BYTES) + '\n';
      var built = assemble(
        head('Scope: the ONE note below, in full. Nothing else from the vault is in front of you.'),
        body, tail(question));
      return { input: built.text, trimmed: built.trimmed, tools: null };
    });
  }

  /* The ≤4 KB ticker brief -- the same text the desk-mode `ticker_brief` tool
   * returns, so the two can never describe a name differently. */
  function briefText(id, bundle) {
    var meta = findTicker(id);
    var lines = [];
    lines.push('TICKER ' + id + (meta && meta.name ? ' — ' + meta.name : ''));
    if (meta) {
      lines.push('tier: ' + String(meta.tier || 'none') +
        (arr(meta.also_in).length ? ' (also ' + arr(meta.also_in).join(', ') + ')' : ''));
      if (arr(meta.themes).length) lines.push('themes: ' + arr(meta.themes).join(', '));
      var scores = isObj(meta.scores) ? meta.scores : {};
      Object.keys(scores).forEach(function (k) {
        var v = scores[k];
        if (isObj(v)) {
          var sub = [];
          Object.keys(v).forEach(function (kk) {
            if (kk === 'notes') return;          /* prose, and far too long for a brief */
            var val = v[kk];
            if (val !== null && val !== undefined && typeof val !== 'object') sub.push(kk + ' ' + val);
          });
          if (sub.length) lines.push('score ' + k + ': ' + sub.join(', '));
        } else if (v !== null && v !== undefined) {
          lines.push('score ' + k + ': ' + v);
        }
      });
    }
    var thesis = bundle && bundle.thesis;
    var fm = isObj(thesis) && isObj(thesis.fm_without_body) ? thesis.fm_without_body : {};
    var assumptions = arr(fm.assumptions).filter(isObj);
    if (assumptions.length) {
      lines.push('assumptions (' + assumptions.length + '):');
      assumptions.forEach(function (a) {
        lines.push('  - [' + String(a.status || 'unknown') + '] ' +
          clip(a.statement || a.id || '', 200) + ' (' + String(a.id || '') + ')');
      });
    } else {
      lines.push('assumptions: none drafted in this bundle');
    }
    var notes = allNotes(bundle).slice().sort(function (a, b) {
      return String((b && b.date) || '').localeCompare(String((a && a.date) || ''));
    }).slice(0, BRIEF_NOTES);
    if (notes.length) {
      lines.push('most recent notes:');
      notes.forEach(function (n) {
        lines.push('  - ' + String(n.date || 'undated') + ' — ' +
          clip(n.title || n.rel || n.id, 120) + ' [' + String(n.id) + ']');
      });
    } else {
      lines.push('notes: none in this bundle');
    }
    return cap(lines.join('\n'), TICKER_BRIEF_BYTES);
  }

  /* TICKER MODE -- instructions + the brief + the latest note's first 12 KB.
   * No tools: everything this mode can see is already in the prompt. */
  function buildTicker(id, question) {
    return loadJSON(bundlePath(id)).catch(function () { return {}; }).then(function (bundle) {
      var brief = briefText(id, bundle);
      var notes = allNotes(bundle).slice().sort(function (a, b) {
        return String((b && b.date) || '').localeCompare(String((a && a.date) || ''));
      });
      var latest = notes.length ? notes[0] : null;
      var body = brief + '\n\n';
      if (latest) {
        body += 'LATEST NOTE ' + String(latest.id) + ' (' + String(latest.date || 'undated') + ' — ' +
          clip(latest.title || latest.id, 120) + ')\n\n' +
          cap(noteText(latest), TICKER_NOTE_BYTES) + '\n';
      } else {
        body += 'No note text for ' + id + ' in this bundle.\n';
      }
      var built = assemble(
        head('Scope: ONE company, ' + id + '. Its desk brief is below, then its most recent note. ' +
          'Nothing else from the vault is in front of you.'),
        body, tail(question));
      return { input: built.text, trimmed: built.trimmed, tools: null };
    });
  }

  /* ------------------------------------------------------- desk tools ----- */

  function toolRan(name) {
    if (ask.tools[ask.tools.length - 1] !== name) ask.tools.push(name);
    var st = document.getElementById('ask-status');
    if (st) st.textContent = statusLine();
  }

  /* One budget object per CALL, closed over by that call's tools: a few small
   * results keep Claude honest and cheap, and past the ceiling every further
   * tool throws, which the contract turns into "Error: …" for Claude and ends
   * the round rather than failing the call. */
  function newBudget() { return { spent: 0 }; }

  function charge(budget, payload) {
    var s = (typeof payload === 'string') ? payload : JSON.stringify(payload);
    budget.spent += bytes(s);
    return payload;
  }

  function gate(budget, name, ctx) {
    if (ctx && ctx.signal && ctx.signal.aborted) throw new Error('cancelled');
    if (budget.spent >= TOOL_BUDGET_BYTES) throw new Error('budget exhausted, answer now');
    toolRan(name);
  }

  function hitOut(h) {
    var d = (h && h.doc) || {};
    return {
      id: String(d.id === null || d.id === undefined ? '' : d.id),
      title: clip(d.t || d.id || '', 140),
      date: d.d || '',
      ticker: String(arr(d.tk)[0] || ''),
      kind: String(d.k || ''),
      snippet: clip(d.sn || d.t || '', 280),
      f: d.f || null,
      s: (typeof d.s === 'number') ? d.s : null
    };
  }

  function has(list, value) {
    var want = String(value).toLowerCase();
    return arr(list).some(function (v) { return String(v).toLowerCase() === want; });
  }

  function searchTool(budget) {
    return {
      name: 'search_vault',
      description: 'Search this published research bundle -- note sections, theme notes, ' +
        'news rows, filings and ingest items -- for words. Returns up to 8 matches as ' +
        '{id, title, date, ticker, kind, snippet, f, s}; pass a match\'s id to get_note to ' +
        'read the note behind it. Optional ticker/theme/kinds narrow the result set.',
      inputSchema: {
        type: 'object',
        properties: {
          query: { type: 'string', description: 'words to match; all of them first, any of them as a fallback' },
          ticker: { type: 'string', description: 'keep only units tagged with this ticker' },
          theme: { type: 'string', description: 'keep only units tagged with this theme slug' },
          kinds: { type: 'array', items: { type: 'string' }, description: 'keep only these unit kinds (earnings, thesis, news, theme, ...)' },
          limit: { type: 'integer', description: 'how many matches to return, at most 8' }
        },
        required: ['query']
      },
      execute: function (input, ctx) {
        gate(budget, 'search_vault', ctx);
        var q = String((input && input.query) || '').trim();
        if (!q) throw new Error('query is required');
        if (typeof R.searchEnsure !== 'function' || typeof R.searchRun !== 'function') {
          throw new Error('the search index is not available in this build');
        }
        var want = Math.max(1, Math.min(SEARCH_HITS, Number((input && input.limit) || SEARCH_HITS) || SEARCH_HITS));
        return R.searchEnsure().then(function () {
          var res = R.searchRun(q) || {};
          var hits = arr(res.hits).filter(function (h) {
            var d = (h && h.doc) || {};
            if (input && input.ticker && !has(d.tk, input.ticker)) return false;
            if (input && input.theme && !has(d.th, input.theme)) return false;
            if (input && arr(input.kinds).length && !has(input.kinds, d.k || '')) return false;
            return true;
          }).slice(0, want).map(hitOut);
          return charge(budget, {
            query: q,
            matched: arr(res.tokens).join(' '),
            mode: res.mode || 'none',
            hits: hits
          });
        });
      }
    };
  }

  function noteTool(budget) {
    return {
      name: 'get_note',
      description: 'Read one note out of the bundle by the id search_vault returned ' +
        '("<TICKER>/<file>.md"). Returns {id, title, date, kind, text} with the text cut to ' +
        '10 KB and marked [truncated] when it was. Pass `section` to get one section of a ' +
        'long note instead of the whole thing.',
      inputSchema: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'the note id, e.g. NVDA/20260828-2Q27.md' },
          section: { type: 'string', description: 'a section heading to return on its own' }
        },
        required: ['id']
      },
      execute: function (input, ctx) {
        gate(budget, 'get_note', ctx);
        /* a search id can carry a "#<n>" section anchor; the bundle's own note
         * ids never do, so it is stripped before the lookup. */
        var id = String((input && input.id) || '').split('#')[0];
        var routeId = routeIdOf(id);
        var rest = id.slice(routeId.length + 1);
        if (!routeId || !rest) throw new Error('id must look like "<TICKER>/<file>.md"');
        return loadJSON(bundlePath(routeId)).then(function (bundle) {
          /* a thesis is not in bundle.notes: it is bundle.thesis */
          var isThesis = /^_thesis/.test(rest);
          var note = isThesis ? null : noteById(bundle, id);
          var text, title, date, kind;
          if (isThesis) {
            var thesis = bundle && bundle.thesis;
            if (!isObj(thesis)) throw new Error('no thesis note for ' + routeId + ' in this bundle');
            text = String(thesis.body || '');
            title = routeId + ' thesis';
            date = String((isObj(thesis.fm_without_body) && thesis.fm_without_body.drafted) || '');
            kind = 'thesis';
          } else {
            if (!note) throw new Error(id + ' is not in this bundle');
            text = noteText(note);
            title = String(note.title || note.rel || note.id);
            date = String(note.date || '');
            kind = String(note.kind || 'note');
          }
          var wanted = String((input && input.section) || '').trim();
          if (wanted && !isThesis && arr(note && note.sections).length) {
            var needle = wanted.toLowerCase(), picked = null;
            arr(note.sections).forEach(function (s) {
              if (picked || !isObj(s)) return;
              var h = String(s.h || s.title || '').toLowerCase();
              if (h && (h === needle || h.indexOf(needle) >= 0)) picked = s;
            });
            if (picked) { text = String(picked.text || ''); title = title + ' — ' + String(picked.h || picked.title || wanted); }
          }
          var cut = sliceBytes(text, TOOL_RESULT_BYTES - bytes(TRUNC_MARK));
          return charge(budget, {
            id: id, title: title, date: date, kind: kind,
            text: cut.text + (cut.cut ? TRUNC_MARK : '')
          });
        });
      }
    };
  }

  function briefTool(budget) {
    return {
      name: 'ticker_brief',
      description: 'The desk\'s standing brief for one ticker: name, tier, themes, scores, ' +
        'every thesis assumption with its status, and the five most recent note titles with ' +
        'their ids. Use it before search_vault when the question names a company.',
      inputSchema: {
        type: 'object',
        properties: { ticker: { type: 'string', description: 'the ticker as the desk spells it, e.g. NVDA' } },
        required: ['ticker']
      },
      execute: function (input, ctx) {
        gate(budget, 'ticker_brief', ctx);
        var id = String((input && input.ticker) || '').trim();
        if (!id) throw new Error('ticker is required');
        if (!findTicker(id)) throw new Error(id + ' is not in this bundle');
        return loadJSON(bundlePath(id)).catch(function () { return {}; }).then(function (bundle) {
          return charge(budget, briefText(id, bundle));
        });
      }
    };
  }

  /* DESK MODE -- instructions as the LEADING user turn, the question as the
   * last one (the contract's turn list must start and end on `user`), and the
   * vault reached only through tools. `cache` is never passed anywhere in this
   * file, which is what keeps a tools call legal. */
  function buildDesk(question) {
    var budget = newBudget();
    var tools = [searchTool(budget), noteTool(budget), briefTool(budget)];
    var maxTools = (LIMITS && isObj(LIMITS.tools) && typeof LIMITS.tools.maxCount === 'number')
      ? LIMITS.tools.maxCount : tools.length;
    if (tools.length > maxTools) tools = tools.slice(0, Math.max(1, maxTools));
    var instructions =
      'You are answering inside a private equity-research desk: a vault of analyst notes ' +
      'on public technology companies, published as a static bundle. Today is ' + todayISO() + '.\n' +
      'Scope: the whole desk, but ONLY through the tools below — search_vault to find units, ' +
      'get_note to read one, ticker_brief for a company’s standing facts. You cannot see the ' +
      'vault any other way and you cannot browse.\n' +
      'Rules: search before you answer; cite note ids in [brackets] for anything you assert; ' +
      'say plainly when the vault has nothing on the question rather than answering from general ' +
      'knowledge; never invent numbers, dates, names or quotes; if a tool says the budget is ' +
      'exhausted, answer from what you already read; keep it short enough to read on a phone.';
    var q = tail(question).replace(/^\n+/, '');
    var over = bytes(instructions) + bytes(q) - promptCap();
    var trimmed = false;
    if (over > 0) {
      var c = sliceBytes(q, Math.max(1, bytes(q) - over - bytes(TRIM_MARK)));
      q = c.text + (c.cut ? TRIM_MARK : '');
      trimmed = c.cut;
    }
    return Promise.resolve({
      input: [{ role: 'user', content: instructions }, { role: 'user', content: q }],
      trimmed: trimmed,
      tools: tools
    });
  }

  function buildPrompt(mode, argv, question) {
    if (mode === 'note') return buildNote(argv, question);
    if (mode === 'ticker') return buildTicker(argv, question);
    if (mode === 'desk') return buildDesk(question);
    return Promise.resolve(null);
  }

  /* ---------------------------------------------------------- the call ---- */

  function onText(update) {
    if (!ask.running) return;
    /* `text` is the WHOLE answer so far: assign it, never append it. */
    if (update && typeof update.text === 'string') ask.answer = update.text;
    setLive();
  }

  function settle() {
    ask.running = false;
    ask.ctl = null;
    ask.done = true;
    renderPanel();
  }

  function onError(e) {
    var code = (e && e.code) ? String(e.code) : 'upstream_error';
    if (code === 'cancelled') {
      /* the viewer did this: restore the idle UI, keep whatever streamed */
      if (e && typeof e.text === 'string') ask.answer = e.text;
      ask.error = '';
      settle();
      return;
    }
    /* `refused` withdraws its partial; every other code may keep e.text. */
    if (code === 'refused') ask.answer = '';
    else if (e && typeof e.text === 'string' && e.text) ask.answer = e.text;
    ask.error = errorCopy(code);

    if (code === 'tools_unavailable') {
      DESK_OK = false;            /* desk mode only; note and ticker still work */
      settle();
      mountAll();
      return;
    }
    if (Object.prototype.hasOwnProperty.call(HIDE_CODES, code)) {
      /* hide the feature for this view: no way to call again, and the panel
       * keeps the one sentence that says why rather than vanishing mid-tap. */
      HIDDEN = true;
      SAMPLE = null;
      settle();
      mountAll();
      return;
    }
    settle();
  }

  function run() {
    if (!SAMPLE || HIDDEN || ask.running) return;
    var box = document.getElementById('ask-q');
    ask.q = (box && typeof box.value === 'string') ? box.value : '';
    resetRun();
    if (!ask.q.trim()) {
      ask.error = 'Type a question first.';
      renderPanel();
      return;
    }
    var mode = ask.mode, argv = ask.arg;
    buildPrompt(mode, argv, ask.q).then(function (built) {
      if (!built || ask.mode !== mode || ask.arg !== argv) {
        if (!built) {
          ask.error = 'This desk could not assemble the material for that question — the bundle it needs is not in this build.';
          renderPanel();
        }
        return;
      }
      ask.trimmed = built.trimmed;
      ask.running = true;
      renderPanel();

      /* a NEW controller for THIS call; an aborted one would reject instantly */
      var ctl = new AbortController();
      ask.ctl = ctl;
      var opts = { signal: ctl.signal, modelTier: 'default', onText: onText };
      /* `cache` is never passed: omitted means the default five-minute window
       * for note/ticker, and omitted is the ONLY legal value with tools. */
      if (built.tools) opts.tools = built.tools;

      SAMPLE(built.input, opts).then(function (res) {
        if (ask.ctl !== ctl) return;           /* superseded or already closed */
        if (res && typeof res.text === 'string') ask.answer = res.text;
        ask.truncated = !!(res && res.truncated);
        ask.tier = (res && res.modelTierApplied) ? String(res.modelTierApplied) : '';
        settle();
      }, function (e) {
        if (ask.ctl !== ctl) return;
        onError(e);
      });
    }).catch(function () {
      ask.running = false;
      ask.ctl = null;
      ask.error = 'This desk could not read the bundle behind that question. Try again, or open the note itself.';
      renderPanel();
    });
  }

  /* --------------------------------------------------------- the panel ---- */

  function openPanel(scope, argv) {
    if (!SAMPLE || HIDDEN) return;
    if (scope === 'desk' && !DESK_OK) return;
    abortInFlight();
    resetRun();
    ask.open = true;
    ask.mode = scope;
    ask.arg = (argv === undefined) ? null : argv;
    ask.q = '';
    ask.title = scope === 'note' ? 'Ask about this note'
      : (scope === 'ticker' ? 'Ask about ' + String(argv || '') : 'Ask the desk');
    renderPanel();
  }

  function closePanel() {
    abortInFlight();
    ask.open = false;
    ask.mode = null;
    ask.arg = null;
    ask.q = '';
    resetRun();
    renderPanel();
  }

  actions['ask-open'] = function (node) {
    openPanel(node.getAttribute('data-ask-scope') || '', node.getAttribute('data-ask-arg'));
  };
  actions['ask-close'] = function () { closePanel(); };
  actions['ask-go'] = function () { run(); };
  actions['ask-stop'] = function () { stopInFlight(); };

  /* Clipboard only -- a published artifact cannot hand the viewer a file, so
   * there is no "save" here to fail silently. */
  actions['ask-copy'] = function (node) {
    var text = ask.answer || '';
    var said = function (msg) { if (node) node.textContent = msg; };
    if (!text) { said('Nothing to copy'); return; }
    try {
      var nav = window.navigator;
      if (nav && nav.clipboard && typeof nav.clipboard.writeText === 'function') {
        nav.clipboard.writeText(text).then(function () { said('Copied'); },
          function () { said('Copy blocked'); });
        return;
      }
    } catch (e) { /* older WebKit, or a permissions policy that blocks it */ }
    said('Copy unavailable');
  };

  /* --------------------------------------------------------- #/more/ask --- */

  function viewAsk() {
    if (!SAMPLE || HIDDEN) {
      /* The route survives a hide (it was registered when the capability
       * resolved) but the feature does not: say so rather than showing a screen
       * that explains a thing the viewer cannot do. */
      return { title: 'Ask', html: section('Ask the desk',
        '<p class="empty">Asking Claude is not available in this view.</p>') };
    }
    var body = DESK_OK
      ? '<p class="lede">Claude reads this published bundle through three tools — a search over ' +
        'every indexed unit, one note at a time, and a ticker’s standing brief — and answers ' +
        'from what it finds. It never browses, and it is asked nothing until you tap.</p>'
      : '<p class="lede">This viewer cannot run page tools, so the desk-wide question is off. ' +
        'Ask is still on every ticker header and every note.</p>';
    return { title: 'Ask', html: section('Ask the desk', body + askSlot('desk')) };
  }

  /* -------------------------------------------------------------- boot ---- */

  /* Every paint is a navigation or a re-render: stop anything in flight (the
   * contract's "abort on route change"), close the panel, and re-mount into the
   * placeholders the new screen rendered. */
  arr(R.paintHooks).push(function (view) {
    abortInFlight();
    ask.open = false;
    ask.mode = null;
    ask.arg = null;
    ask.q = '';
    resetRun();
    mountAll(view);
  });

  function boot() {
    var claude = window.claude;
    if (!claude || typeof claude.use !== 'function') return;   /* not a Claude viewer */
    var used;
    try { used = claude.use('sample'); } catch (e) { return; }
    if (!used || typeof used.then !== 'function') return;
    used.then(function (fn) {
      if (typeof fn !== 'function') return;     /* null: hide the feature, quietly */
      SAMPLE = fn;
      var limits = null;
      try { limits = (typeof fn.limits === 'function') ? fn.limits() : null; } catch (e) { limits = null; }
      return Promise.resolve(limits).catch(function () { return null; }).then(function (l) {
        LIMITS = isObj(l) ? l : {};
        if (typeof LIMITS.maxPromptBytes !== 'number' || !(LIMITS.maxPromptBytes > 0)) {
          LIMITS.maxPromptBytes = DEFAULT_MAX_PROMPT;
        }
        DESK_OK = isObj(LIMITS.tools) &&
          (typeof LIMITS.tools.maxCount !== 'number' || LIMITS.tools.maxCount > 0);
        morePages.ask = viewAsk;
        /* the first screen is already painted by now: mount into it directly */
        mountAll();
      });
    }).catch(function () { /* absence is the design: no Ask, no error */ });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
