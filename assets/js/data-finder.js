/* Data source finder for /teaching/data-sources/.
   Reads the source list (with topics/units/easy tags from _data/data_sources.yml)
   from the #ds-data JSON block and ranks sources against three answers.
   Block comments only: see the minified-HTML note for this site. */
(function () {
  var dataEl = document.getElementById('ds-data');
  var root = document.getElementById('ds-finder');
  if (!dataEl || !root) { return; }

  var groups = JSON.parse(dataEl.textContent);
  var sources = [];
  groups.forEach(function (g) {
    g.sources.forEach(function (s) { sources.push(s); });
  });

  var QUESTIONS = [
    { key: 'topic', label: '1. What is your project about?', options: [
      ['finance', 'Government budgets, taxes, and spending'],
      ['nonprofits', 'Nonprofits and charities'],
      ['economy', 'Jobs, income, and the economy'],
      ['disasters', 'Disasters and extreme weather'],
      ['environment', 'Environment, climate, and energy'],
      ['health', 'Health'],
      ['politics', 'Elections, politics, and public opinion'],
      ['sports', 'Sports'],
      ['arts', 'Arts, culture, and media'],
      ['cities', 'Crime, schools, housing, and city life'],
      ['general', 'Not sure yet']
    ]},
    { key: 'unit', label: '2. What do you want to compare?', options: [
      ['people', 'People (survey respondents, voters, players)'],
      ['orgs', 'Organizations (nonprofits, schools, colleges, agencies, facilities)'],
      ['places', 'Places (cities, counties, states, neighborhoods)'],
      ['countries', 'Countries'],
      ['events', 'Individual events or items (games, storms, crashes, votes, artworks)'],
      ['any', 'Not sure']
    ]},
    { key: 'skill', label: '3. How do you want to work with the data?', options: [
      ['easy', 'Explore it on a website first'],
      ['files', 'Download a spreadsheet or data file'],
      ['any', 'Either is fine']
    ]}
  ];
  var UNIT_WORDS = { people: 'people', orgs: 'organizations', places: 'places',
    countries: 'countries', events: 'events or items' };

  var answers = {};

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) { e.className = cls; }
    if (text) { e.textContent = text; }
    return e;
  }

  function score(s) {
    var t = answers.topic, u = answers.unit, k = answers.skill;
    var idx = s.topics.indexOf(t);
    if (idx < 0) { return -1; }
    var sc = 10 - idx;
    if (u && u !== 'any') { sc += s.units.indexOf(u) >= 0 ? 6 : -4; }
    if (k === 'easy') { sc += s.easy ? 3 : -2; }
    if (k === 'files') { sc += s.easy ? 0 : 1; }
    return sc;
  }

  function renderResults(box) {
    box.innerHTML = '';
    if (!answers.topic) {
      box.appendChild(el('p', 'ds-hint', 'Pick a topic to see suggestions.'));
      return;
    }
    var ranked = sources.map(function (s) { return { s: s, sc: score(s) }; })
      .filter(function (r) { return r.sc >= 0; })
      .sort(function (a, b) { return b.sc - a.sc; });
    var u = answers.unit;
    var strong = ranked.filter(function (r) {
      return !u || u === 'any' || r.s.units.indexOf(u) >= 0;
    });
    var shown = (strong.length ? strong : ranked).slice(0, 6);

    box.appendChild(el('h3', 'ds-res-title', strong.length ?
      'Start with these' :
      'Nothing here is organized around ' + UNIT_WORDS[u] + ' for this topic. The closest matches:'));
    var ul = el('ul', 'ds-res');
    shown.forEach(function (r) {
      var li = el('li');
      var a = el('a', null, r.s.name);
      a.href = r.s.url;
      li.appendChild(a);
      if (r.s.easy) { li.appendChild(el('span', 'ds-tag', 'web tool')); }
      li.appendChild(el('div', 'ds-desc', r.s.desc + (r.s.note ? ' ' + r.s.note : '')));
      ul.appendChild(li);
    });
    box.appendChild(ul);
    if (ranked.length > shown.length) {
      box.appendChild(el('p', 'ds-hint', (ranked.length - shown.length) +
        ' more sources on this topic are in the full list below.'));
    }
  }

  function build() {
    root.innerHTML = '';
    var results = el('div', 'ds-results');
    results.setAttribute('aria-live', 'polite');
    QUESTIONS.forEach(function (q) {
      var fs = el('fieldset', 'ds-q');
      fs.appendChild(el('legend', null, q.label));
      q.options.forEach(function (o) {
        var b = el('button', 'ds-opt', o[1]);
        b.type = 'button';
        b.setAttribute('aria-pressed', answers[q.key] === o[0] ? 'true' : 'false');
        b.addEventListener('click', function () {
          answers[q.key] = o[0];
          fs.querySelectorAll('.ds-opt').forEach(function (x) {
            x.setAttribute('aria-pressed', x === b ? 'true' : 'false');
          });
          renderResults(results);
        });
        fs.appendChild(b);
      });
      root.appendChild(fs);
    });
    var reset = el('button', 'ds-reset', 'Start over');
    reset.type = 'button';
    reset.addEventListener('click', function () { answers = {}; build(); });
    root.appendChild(reset);
    root.appendChild(results);
    renderResults(results);
  }

  build();
})();
