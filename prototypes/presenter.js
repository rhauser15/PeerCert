// Presenter controls shared by the demo mockups.
//   → / Space / PageDown (clicker): next step     ← / PageUp: previous step
//   R: restart                                    H: hide/show presenter notes
//   B: toggle a fake browser bar with a realistic URL (or ?frame=1)
//   ?step=N in the URL jumps to step N
window.Presenter = {
  init(steps, reset) {
    let i = 0, busy = false;
    const box = document.getElementById("presenter");
    const render = () => {
      box.innerHTML = `<b>${i}/${steps.length - 1}</b> ${steps[i]?.[0] || ""}<span class="keys">→ next · ← back · R restart · H hide</span>`;
    };
    const run = async (n, instant) => { busy = true; try { await steps[n][1](instant); } finally { busy = false; } };
    const next = async () => { if (busy || i >= steps.length - 1) return; i++; render(); await run(i, false); };
    const back = async () => {
      if (busy || i === 0) return;
      i--; reset();
      for (let n = 0; n <= i; n++) await run(n, true);
      render();
    };
    document.addEventListener("keydown", e => {
      if (["ArrowRight", " ", "PageDown"].includes(e.key)) { e.preventDefault(); next(); }
      else if (["ArrowLeft", "PageUp"].includes(e.key)) { e.preventDefault(); back(); }
      else if (e.key.toLowerCase() === "r") { i = 0; reset(); run(0, true); render(); }
      else if (e.key.toLowerCase() === "h") box.classList.toggle("hidden");
      else if (e.key.toLowerCase() === "b") this.frame(!document.documentElement.classList.contains("framed"));
    });
    box.addEventListener("click", next);
    const bar = document.createElement("div");
    bar.className = "fakebar";
    const icon = document.querySelector('link[rel="icon"]')?.href || "";
    bar.innerHTML = `<div class="fb-tabs"><span class="fb-lights"><i style="background:#ff5f57"></i><i style="background:#febc2e"></i><i style="background:#28c840"></i></span>
        <span class="fb-tab">${icon ? `<img src="${icon}" alt="">` : ""}<span class="fb-t">${document.title}</span><span class="fb-x">✕</span></span><span class="fb-plus">＋</span></div>
      <div class="fb-bar"><span class="fb-nav">← → ↻</span><span class="fb-url"><span class="fb-lock">🔒</span><span class="fb-host"></span><span class="fb-path"></span></span><span class="fb-me">${document.querySelector(".avatar, .me")?.textContent || ""}</span></div>`;
    document.body.prepend(bar);
    const meta = document.querySelector('meta[name="demo-url"]');
    if (meta) this.setUrl(meta.content);
    const q = new URLSearchParams(location.search).get("frame");
    this.frame(q != null ? q !== "0" : localStorage.getItem("demoFrame") === "1");
    this.next = next;
    reset(); run(0, true); render();
    // ?step=N jumps straight to step N (for rehearsal).
    const jump = parseInt(new URLSearchParams(location.search).get("step"), 10);
    if (jump > 0) (async () => { for (let n = 1; n <= Math.min(jump, steps.length - 1); n++) await run(n, true); i = Math.min(jump, steps.length - 1); render(); })();
  },
  // Show or hide the fake browser bar; the choice is remembered between pages.
  frame(on) {
    document.documentElement.classList.toggle("framed", on);
    localStorage.setItem("demoFrame", on ? "1" : "0");
  },
  setUrl(url) {
    const [host, ...rest] = url.split("/");
    document.querySelectorAll(".fakebar .fb-host").forEach(e => e.textContent = host);
    document.querySelectorAll(".fakebar .fb-path").forEach(e => e.textContent = rest.length ? "/" + rest.join("/") : "");
  },
};
