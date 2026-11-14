# ASCII Seasons

An interactive, canvas-driven ASCII seasonal landscape combining procedural ASCII character art, dynamic atmospheric lighting, real-time weather integration, and particle physics.

---

## Highlights

- **Dynamic Seasonal Modes**:
  - `Winter`: Falling snowflakes (`*`, `.`, `+`, `'`, `❄`) and a frost-kissed ASCII tree.
  - `Spring`: Cherry blossom petals (`*`, `@`, `o`, `❀`) drifting over fresh grass.
  - `Autumn`: Warm amber and rust foliage (`%`, `&`, `~`, `v`, `❧`) carried by the breeze.
  - `Auto`: Detects the current calendar month and switches seasons automatically.
- **Atmospheric Sky**:
  - Real-time diurnality simulating dawn, noon, golden hour, twilight, and star-filled night skies based on the local system clock.
- **Live Weather Integration**:
  - Fetches temperature, conditions (clear, fog, rain, snow), and wind vectors from the Open-Meteo API using browser geolocation (with default fallback coordinates).
  - Wind speed and direction physically steer the particle trajectory and rain slant.
- **Particle Dynamics & Interactivity**:
  - Fluid lateral sway, wind influence, and mouse/touch cursor repulsion field that scatters particles as you hover or drag.
- **Zero Dependencies / No Build Step**:
  - Written completely in pure HTML5, CSS3, and modern vanilla JavaScript running directly on an HTML5 `<canvas>`.

---

## Controls

| Key / Action | Action |
| :--- | :--- |
| `0` | Auto season (switches according to current calendar month) |
| `1` | Force Winter scene (Snowfall) |
| `2` | Force Spring scene (Cherry blossoms) |
| `3` | Force Autumn scene (Autumn foliage) |
| `Space` | Pause / Resume animation |
| `Cursor / Touch` | Interactive force field (deflects nearby particles) |

---

## Local Development

Because ASCII Seasons is a single self-contained application, you can view it directly:

1. Open `index.html` directly in any modern browser.
2. Or serve it with any local static HTTP server (recommended to allow Geolocation and fetch permissions):
   ```bash
   # Using Python
   python -m http.server 8000

   # Or using Node.js npx
   npx serve .
   ```
3. Visit `http://localhost:8000` in your web browser.

---

## Live Deployment (GitHub Pages)

This project is deployed directly from the `repository-of-side-quests` repository without creating a separate repository:

### How to Enable It in 2 Minutes:

1. **Commit and push** your changes to GitHub:
   ```bash
   git add ascii-seasons
   git commit -m "feat: add ascii-seasons with readme and license"
   git push origin main
   ```

2. **Turn on GitHub Pages** in your repository:
   - Go to your repository on GitHub: `https://github.com/NishigandhaSawant/repository-of-side-quests`
   - Click on **Settings** (top menu) > **Pages** (left sidebar under *Code and automation*).
   - Under **Build and deployment** > **Source**, keep/select **Deploy from a branch**.
   - Under **Branch**, select `main` and `/ (root)`.
   - Click **Save**.

3. **Visit your standalone app:**
   Within 1–2 minutes, your ASCII Seasons application will be live at:
   ```
   https://NishigandhaSawant.github.io/repository-of-side-quests/ascii-seasons/
   ```

> [!NOTE]
> Anyone who visits this link gets the full, full-screen, standalone ASCII Seasons experience. You don't need a separate repository! All your other side quest projects with an `index.html` will also get their own live URLs automatically.

---

## License

This project is licensed under the [MIT License](LICENSE).
