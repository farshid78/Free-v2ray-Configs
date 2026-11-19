// Project overlay for graphify's HTML export, injected by tools/graphify/build.py.
// graphify's own page leaves the canvas unchanged while searching (the query only
// fills a dropdown) and its legend click handler can never solo a community.
// This runs after graphify's inline script and uses the bindings it leaves in the
// global scope: RAW_NODES, nodesDS, network, LEGEND, legendEl, searchInput,
// searchResults.
(() => {
  'use strict';

  const DIM = {
    background: '#242438', border: '#33334d',
    highlight: { background: '#242438', border: '#33334d' },
  };
  const hitsFor = (query) => RAW_NODES.filter((n) => n.label.toLowerCase().includes(query));
  const hitsLabel = (count) => `${count} match${count === 1 ? '' : 'es'}`;

  // ---- search: matching nodes stay lit, everything else is dimmed ----
  const searchCount = document.createElement('div');
  searchCount.id = 'search-count';
  searchInput.insertAdjacentElement('afterend', searchCount);

  function highlight(raw) {
    const query = raw.trim().toLowerCase();
    const hits = query ? hitsFor(query) : [];
    const hitIds = new Set(hits.map((n) => n.id));
    nodesDS.update(RAW_NODES.map((n) => (hitIds.has(n.id)
      ? { id: n.id, color: n.color, borderWidth: 3 }
      : { id: n.id, color: query ? DIM : n.color, borderWidth: 1.5 })));
    if (hits.length) network.selectNodes(hits.slice(0, 250).map((n) => n.id));
    else network.unselectAll();
    searchCount.textContent = !query ? ''
      : hits.length ? `${hitsLabel(hits.length)} highlighted` : 'no match';
  }

  searchInput.addEventListener('input', () => highlight(searchInput.value));

  // Picking a result clears the input in graphify's handler, which used to leave
  // the canvas dimmed with no visible reason. Keep the query and name the focus.
  searchResults.addEventListener('click', (event) => {
    const item = event.target.closest('.search-item');
    if (!item) return;
    const query = searchInput.value;
    const label = item.textContent;
    setTimeout(() => {
      if (!query) return;
      searchInput.value = query;
      searchCount.textContent = `${hitsLabel(hitsFor(query).length)} · focused: ${label}`;
    }, 0);
  }, true);

  // ---- communities: one click hides/shows, a double click solos ----
  const hidden = new Set();
  let solo = null;
  const viewState = document.createElement('div');
  viewState.id = 'view-state';
  legendEl.insertAdjacentElement('beforebegin', viewState);

  function applyVisibility() {
    nodesDS.update(RAW_NODES.map((n) => ({
      id: n.id,
      hidden: solo !== null ? n.community !== solo : hidden.has(n.community),
    })));
    const shown = nodesDS.get({ filter: (n) => !n.hidden }).length;
    const soloRow = LEGEND.find((row) => row.cid === solo);
    viewState.textContent = solo !== null
      ? `solo: ${soloRow ? soloRow.label : solo} · ${shown} nodes`
      : hidden.size ? `${hidden.size} hidden · ${shown} nodes`
      : `all communities · ${shown} nodes`;
    Array.from(legendEl.children).forEach((item, i) => {
      const cid = LEGEND[i].cid;
      item.classList.toggle('dimmed', solo !== null ? cid !== solo : hidden.has(cid));
    });
  }

  // Replace graphify's legend handlers. The single click is held back so the two
  // clicks of a double click cannot undo the solo state it just entered.
  Array.from(legendEl.children).forEach((item, i) => {
    const cid = LEGEND[i].cid;
    let timer = null;
    item.onclick = () => {
      if (timer) return;
      timer = setTimeout(() => {
        timer = null;
        solo = null;
        if (hidden.has(cid)) hidden.delete(cid);
        else hidden.add(cid);
        applyVisibility();
      }, 220);
    };
    item.ondblclick = () => {
      clearTimeout(timer);
      timer = null;
      solo = solo === cid ? null : cid;
      hidden.clear();
      applyVisibility();
    };
  });

  applyVisibility();
})();
