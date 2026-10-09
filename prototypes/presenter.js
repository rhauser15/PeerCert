// Presenter controls shared by the demo mockups.
//   → / Space / PageDown (clicker): next step     ← / PageUp: previous step
//   R: restart                                    H: hide/show presenter notes
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
    });
    box.addEventListener("click", next);
    this.next = next;
    reset(); run(0, true); render();
    // ?step=N jumps straight to step N (for rehearsal).
    const jump = parseInt(new URLSearchParams(location.search).get("step"), 10);
    if (jump > 0) (async () => { for (let n = 1; n <= Math.min(jump, steps.length - 1); n++) await run(n, true); i = Math.min(jump, steps.length - 1); render(); })();
  },
};
