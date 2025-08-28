const form = document.getElementById("ner-form");
const txt = document.getElementById("text");
const resultEl = document.getElementById("result");
const detailEl = document.getElementById("detail");
const queueEl = document.getElementById("queue");
const addBtn = document.getElementById("add-selection");
const clearBtn = document.getElementById("clear-added");
const labelSel = document.getElementById("label");
const customIn = document.getElementById("custom");

// Client-side store of user-added entities: [{start,end,label}]
let userAdded = [];

function currentLabel() {
  const custom = (customIn.value || "").trim();
  return custom || labelSel.value;
}

function showDetail({ text, label, start, end }) {
  detailEl.innerHTML = `
            <div><b>Text:</b><br/>${escapeHtml(text)}</div>
            <div style="margin-top: 8px;"><b>Label:</b> ${escapeHtml(
              label
            )}</div>
            <div><b>Offsets:</b> [${start}, ${end})</div>
            <div style="margin-top: 10px;">
                <button class="btn" id="queue-action">Add to Queue</button>
            </div>
        `;
  detailEl.querySelector("#queue-action").addEventListener("click", () => {
    queueItem({ text, label, start, end });
  });
}

function queueItem(ent) {
  const node = document.createElement("div");
  node.textContent = `${ent.label}: "${ent.text}" [${ent.start},${ent.end})`;
  queueEl.appendChild(node);
}

// Escape to avoid HTML injection in detail panel
function escapeHtml(s) {
  return s.replace(
    /[&<>"']/g,
    (m) =>
      ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      }[m])
  );
}

// Compute selection offsets relative to the text content of resultEl (which
// is the same as the original text). Uses Range-toString length trick.
function getSelectionOffsetsWithin(element) {
  const sel = window.getSelection();
  if (!sel || sel.rangeCount === 0) return null;

  const range = sel.getRangeAt(0);
  if (!element.contains(range.commonAncestorContainer)) return null;

  // clone range from start of element to selection start
  const preRange = document.createRange();
  preRange.selectNodeContents(element);
  preRange.setEnd(range.startContainer, range.startOffset);
  const start = preRange.toString().length;

  // clone range from start to selection end
  const preRange2 = document.createRange();
  preRange2.selectNodeContents(element);
  preRange2.setEnd(range.endContainer, range.endOffset);
  const end = preRange2.toString().length;

  return { start, end };
}

async function analyze() {
  const payload = {
    text: txt.value,
    user_ents: userAdded,
  };
  const res = await fetch("/components/analyze/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const html = await res.text();
  resultEl.innerHTML = html;
  attachEntityClicks();
}

function attachEntityClicks() {
  resultEl.querySelectorAll(".ent").forEach((span) => {
    span.addEventListener("click", (e) => {
      e.stopPropagation();
      const data = {
        text: span.getAttribute("data-text"),
        label: span.getAttribute("data-label"),
        start: Number(span.getAttribute("data-start")),
        end: Number(span.getAttribute("data-end")),
      };
      showDetail(data);
    });
  });
}

addBtn.addEventListener("click", async () => {
  const offs = getSelectionOffsetsWithin(resultEl);
  if (!offs || offs.start === offs.end) {
    alert("Select text in the result panel first.");
    return;
  }
  const label = currentLabel();

  // Record locally; the server remains stateless in this demo
  userAdded.push({ start: offs.start, end: offs.end, label });
  await analyze();

  // Clear text selection
  const sel = window.getSelection();
  if (sel) sel.removeAllRanges();
});

clearBtn.addEventListener("click", async () => {
  userAdded = [];
  await analyze();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  await analyze();
});

// Initial render
analyze();
