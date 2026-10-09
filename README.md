# Peer Cert Yelp Demo: Find & Win

Demo assets for the **Find → Win** section of the Agentic Revenue Lifecycle, using Yelp Inc. as a mock customer.
Piper finds the invisible multi-brand owner, Hunter finds the rest of them, and Salesforce keeps the record.

Target org alias: `trailsignup-429cdf`

| Path | What it is |
|---|---|
| [DEMO_SCRIPT.md](DEMO_SCRIPT.md) | 22–25 minute talk track, click path, limitations, Q&A |
| `prototypes/` | Click-through mockups: `piper.html`, `hunter.html`, and `index.html` (launcher) |
| `force-app/` | Salesforce metadata: Lead and Account fields, routing Flow, permission set, list views, layout sections |
| `scripts/demo_data.py` | Single source of demo data. Run it to regenerate `prototypes/data.js` |
| `scripts/seed.py` | Resets and loads demo records in the org |
| `scripts/gen_fields.py`, `scripts/add_layout_sections.py` | Generate the field, permission set, list view, and layout metadata |

## Run it

```bash
sf project deploy start -o trailsignup-429cdf -d force-app     # metadata (already deployed)
python3 scripts/seed.py                                        # reset + load records
python3 -m http.server 8787 --directory prototypes             # mockups at http://localhost:8787
```

Mockup controls: **→ / Space** next · **←** back · **R** restart · **H** hide presenter strip.

Piper and Hunter are mockups (Hunter is a pre-GA prototype). The Salesforce side is real.
