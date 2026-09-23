var REFRESH_MS = 5000;
var data = {sections: []};
var tab = null;

function esc(x) {
  var d = document.createElement("div");
  d.textContent = String(x);
  return d.innerHTML;
}

function render() {
  var secs = data.sections;
  if (!tab && secs.length) { tab = secs[0].name; }
  var bar = document.getElementById("tabs");
  bar.innerHTML = "";
  secs.forEach(function (s) {
    var b = document.createElement("div");
    b.className = "tab" + (s.name === tab ? " active" : "");
    b.textContent = s.name + " (" + s.count + ")";
    b.onclick = function () { tab = s.name; render(); };
    bar.appendChild(b);
  });
  var hit = null;
  secs.forEach(function (s) { if (s.name === tab) { hit = s; } });
  var out = document.getElementById("out");
  out.innerHTML = "";
  if (!hit) { return; }
  document.getElementById("sec-title").textContent = tab + " section";
  var card = document.createElement("div");
  card.className = "card";
  var ul = document.createElement("ul");
  hit.items.forEach(function (it) {
    var li = document.createElement("li");
    var k = document.createElement("span"); k.className = "k"; k.textContent = esc(it.label);
    var v = document.createElement("span"); v.className = "v"; v.textContent = esc(it.value);
    li.appendChild(k); li.appendChild(v); ul.appendChild(li);
  });
  card.appendChild(ul); out.appendChild(card);
  document.getElementById("items-here").textContent = hit.count + " data items";
}

function fetchItems() {
  fetch("/api/items").then(function (r) { return r.json(); }).then(function (d) {
    data = d;
    document.getElementById("count").textContent = "Total items: " + d.total_items;
    document.getElementById("gen").textContent = "Generated: " + d.generated_at;
    render();
  }).catch(function (e) {
    document.getElementById("recon").textContent = "Refresh failed: " + e;
  });
}
setInterval(fetchItems, REFRESH_MS);
fetchItems();
