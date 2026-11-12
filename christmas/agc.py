import math
import os
import random
import shutil
import sys
import time

# Enable ANSI escape sequences on Windows terminals
if os.name == "nt":
    os.system("")

FPS = 30
NUM_LIGHTS = 170
NUM_SPARKLES = 160
SHADE_CHARS = " .:-=+*#%@"


def rgb(r: int, g: int, b: int, ch: str) -> str:
    return f"\033[38;2;{r};{g};{b}m{ch}"


def build_tree_geometry():
    """Precompute 3D surface points, normals, and ornaments for the tree."""
    foliage = []
    # Layered pine cone from y = -0.72 to y = 0.94
    rows = 68
    for i in range(rows):
        h = i / (rows - 1)  # 0 at bottom, 1 at top
        y = -0.72 + h * 1.66
        base_r = 0.86 * ((1.0 - h) ** 0.88) + 0.03 * (1.0 - h)
        # Layered bough tiers
        tier_wave = 1.0 + 0.11 * math.sin(h * 28.0)
        circumference_steps = max(14, int(115 * base_r))

        for j in range(circumference_steps):
            theta = (2.0 * math.pi * j) / circumference_steps + (i * 0.17)
            bough_wave = 1.0 + 0.07 * math.sin(theta * 7.0 + h * 15.0)
            r = base_r * tier_wave * bough_wave

            x = r * math.cos(theta)
            z = r * math.sin(theta)

            # Approximate outward surface normal
            nx = math.cos(theta) * 0.88
            ny = 0.47
            nz = math.sin(theta) * 0.88
            foliage.append((x, y, z, nx, ny, nz, h))

    # 170 colored ornaments & fairy lights around the tree surface
    palette = [
        (240, 45, 45),    # Crimson red
        (255, 205, 55),   # Warm gold
        (255, 135, 35),   # Amber orange
        (90, 215, 255),   # Ice blue
        (255, 248, 225),  # Warm white
    ]
    rng = random.Random(2026)
    lights = []
    for idx in range(NUM_LIGHTS):
        h = 0.04 + 0.92 * (idx / NUM_LIGHTS)
        y = -0.72 + h * 1.66
        base_r = 0.86 * ((1.0 - h) ** 0.88) + 0.03 * (1.0 - h)
        tier_wave = 1.0 + 0.11 * math.sin(h * 28.0)
        theta = rng.uniform(0, 2.0 * math.pi)
        r = base_r * tier_wave * 1.04
        x = r * math.cos(theta)
        z = r * math.sin(theta)
        color = palette[idx % len(palette)]
        phase = rng.uniform(0, 2.0 * math.pi)
        glyph = rng.choice(["@", "O", "*", "+"])
        lights.append((x, y, z, color, phase, glyph))

    # 3D gift boxes resting on the ground around the base
    # (cx, cz, half_w, height, box_rgb, ribbon_rgb)
    gifts = [
        (-0.56, 0.36, 0.13, 0.18, (215, 165, 35), (210, 40, 40)),   # Left gold box
        (0.02, 0.56, 0.15, 0.17, (175, 32, 32), (245, 200, 65)),    # Front red box
        (0.46, 0.44, 0.12, 0.16, (225, 228, 235), (215, 45, 45)),   # Right white box
        (0.62, -0.15, 0.13, 0.19, (35, 85, 185), (235, 235, 245)),  # Back-right blue box
    ]

    return foliage, lights, gifts


def init_sparkles():
    rng = random.Random(999)
    sparkles = []
    for _ in range(NUM_SPARKLES):
        sparkles.append([
            rng.uniform(-1.9, 1.9),   # x
            rng.uniform(-0.85, 1.45), # y
            rng.uniform(-1.6, 1.6),   # z
            rng.uniform(0.22, 0.55),  # fall speed
            rng.uniform(0, 6.28),     # horizontal sway phase
            rng.random() < 0.28,      # True = warm gold sparkle, False = silver snow
        ])
    return sparkles


def render():
    foliage, lights, gifts = build_tree_geometry()
    sparkles = init_sparkles()

    # Light direction (normalized upper-front-left)
    lx, ly, lz = -0.42, 0.52, 0.74
    tilt = 0.21
    cos_t = math.cos(tilt)
    sin_t = math.sin(tilt)
    z_cam = 3.55

    sys.stdout.write("\033[?25l\033[2J")
    sys.stdout.flush()

    start_time = time.perf_counter()
    prev_time = start_time

    try:
        while True:
            now = time.perf_counter()
            dt = min(0.1, now - prev_time)
            prev_time = now
            elapsed = now - start_time

            cols, rows = shutil.get_terminal_size((110, 42))
            width = min(116, max(72, cols - 1))
            height = min(44, max(28, rows - 1))

            zbuf = [[-1e9] * width for _ in range(height)]
            cbuf = [[" "] * width for _ in range(height)]
            letter_count = 0

            angle = elapsed * 0.85
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            fov = height * 1.12

            def plot(x: float, y: float, z: float, colored_ch: str, count_letter: bool = True):
                nonlocal letter_count
                # Tilt camera view slightly downward
                y2 = y * cos_t - z * sin_t
                z2 = y * sin_t + z * cos_t
                denom = z_cam - z2
                if denom <= 0.25:
                    return
                inv_z = 1.0 / denom
                sx = int(width * 0.5 + x * fov * 2.05 * inv_z)
                sy = int(height * 0.47 - y2 * fov * inv_z)
                if 0 <= sx < width and 0 <= sy < height:
                    if z2 > zbuf[sy][sx]:
                        if count_letter and cbuf[sy][sx] == " ":
                            letter_count += 1
                        zbuf[sy][sx] = z2
                        cbuf[sy][sx] = colored_ch

            # 1. Ground snow disc (y = -0.82)
            ground_y = -0.82
            for ri in range(1, 26):
                gr = (ri / 25.0) * 1.58
                steps = int(18 + ri * 5)
                fade = max(0.18, 1.0 - (ri / 27.0) ** 1.4)
                for si in range(steps):
                    ga = (2.0 * math.pi * si) / steps + angle * 0.35
                    gx = gr * math.cos(ga)
                    gz = gr * math.sin(ga)
                    v = int(75 + 135 * fade)
                    gch = "+" if ri < 8 and si % 3 == 0 else (":" if ri < 16 else ".")
                    plot(gx, ground_y, gz, rgb(v, v, min(255, v + 15), gch), count_letter=False)

            # 2. Tree trunk
            for ty_i in range(6):
                ty = -0.82 + (ty_i / 5.0) * 0.12
                for ta_i in range(20):
                    ta = (2.0 * math.pi * ta_i) / 20.0 + angle
                    tx = 0.11 * math.cos(ta)
                    tz = 0.11 * math.sin(ta)
                    shade = 0.55 + 0.45 * max(0.0, math.cos(ta) * lx + math.sin(ta) * lz)
                    plot(tx, ty, tz, rgb(int(115 * shade), int(68 * shade), int(35 * shade), "#"))

            # 3. 3D Gift boxes at the base
            for cx, cz, hw, gh, box_col, rib_col in gifts:
                rcx = cx * cos_a - cz * sin_a
                rcz = cx * sin_a + cz * cos_a
                steps = 9
                for ix in range(steps):
                    u = -hw + (2.0 * hw * ix) / (steps - 1)
                    for iy in range(steps - 2):
                        v = ground_y + (gh * iy) / (steps - 3)
                        for iz in range(steps):
                            if ix not in (0, steps - 1) and iz not in (0, steps - 1) and iy != steps - 3:
                                continue
                            w = -hw + (2.0 * hw * iz) / (steps - 1)
                            px = rcx + u * cos_a - w * sin_a
                            pz = rcz + u * sin_a + w * cos_a
                            is_ribbon = abs(u) < hw * 0.24 or abs(w) < hw * 0.24
                            base_c = rib_col if is_ribbon else box_col
                            lit = 0.72 + 0.28 * (iy / max(1, steps - 3))
                            col_str = rgb(int(base_c[0] * lit), int(base_c[1] * lit), int(base_c[2] * lit), "#")
                            plot(px, v, pz, col_str)

            # 4. Rotating evergreen tree foliage
            for x, y, z, nx, ny, nz, h in foliage:
                rx = x * cos_a - z * sin_a
                rz = x * sin_a + z * cos_a
                rnx = nx * cos_a - nz * sin_a
                rnz = nx * sin_a + nz * cos_a

                diff = max(0.14, rnx * lx + ny * ly + rnz * lz)
                ch_idx = min(len(SHADE_CHARS) - 1, int(diff * (len(SHADE_CHARS) - 1)))
                ch = SHADE_CHARS[ch_idx]
                if ch == " ":
                    ch = "."

                r_col = int(10 + 34 * diff)
                g_col = int(42 + 175 * diff)
                b_col = int(16 + 42 * diff)
                plot(rx, y, rz, rgb(r_col, g_col, b_col, ch))

            # 5. 170 Twinkling ornaments & fairy lights
            for x, y, z, color, phase, glyph in lights:
                rx = x * cos_a - z * sin_a
                rz = x * sin_a + z * cos_a
                pulse = 0.62 + 0.38 * math.sin(elapsed * 4.8 + phase)
                lr = min(255, int(color[0] * pulse + 30))
                lg = min(255, int(color[1] * pulse + 30))
                lb = min(255, int(color[2] * pulse + 30))
                ch = glyph if pulse > 0.75 else "*"
                plot(rx, y, rz, rgb(lr, lg, lb, ch))

            # 6. Top glowing star + radiating light rays
            star_y = 1.03
            star_pulse = 0.82 + 0.18 * math.sin(elapsed * 6.0)
            sr = int(255 * star_pulse)
            sg = int(225 * star_pulse)
            sb = int(75 * star_pulse)
            star_offsets = [
                (0.0, 0.06, "#"), (-0.04, 0.03, "#"), (0.04, 0.03, "#"),
                (-0.07, 0.01, "*"), (0.0, 0.01, "@"), (0.07, 0.01, "*"),
                (-0.04, -0.02, "#"), (0.0, -0.02, "#"), (0.04, -0.02, "#"),
                (-0.05, -0.05, "*"), (0.05, -0.05, "*"),
            ]
            for ox, oy, sch in star_offsets:
                rox = ox * math.cos(angle * 1.5)
                roz = ox * math.sin(angle * 1.5)
                plot(rox, star_y + oy, roz, rgb(sr, sg, sb, sch))

            # Subtle rays shooting up from the star
            for ray_i in range(1, 7):
                d = ray_i * 0.045
                fade = max(90, 235 - ray_i * 24)
                plot(0.0, star_y + 0.07 + d, 0.0, rgb(fade, int(fade * 0.88), 90, "|"), count_letter=False)
                plot(-d * 0.65, star_y + 0.05 + d * 0.85, 0.0, rgb(fade, int(fade * 0.85), 80, "\\"), count_letter=False)
                plot(d * 0.65, star_y + 0.05 + d * 0.85, 0.0, rgb(fade, int(fade * 0.85), 80, "/"), count_letter=False)

            # 7. Falling sparkles & snow particles
            for sp in sparkles:
                sp[1] -= sp[3] * dt
                if sp[1] < -0.84:
                    sp[1] = 1.45
                sway_x = sp[0] + 0.06 * math.sin(elapsed * 1.8 + sp[4])
                if sp[5]:
                    twinkle = 0.65 + 0.35 * math.sin(elapsed * 7.0 + sp[4])
                    sch = "*" if twinkle > 0.8 else "+"
                    col = rgb(int(255 * twinkle), int(215 * twinkle), int(110 * twinkle), sch)
                else:
                    col = rgb(195, 205, 225, "·" if sp[2] < 0 else "*")
                plot(sway_x, sp[1], sp[2], col, count_letter=False)

            # Build frame lines
            lines = ["".join(row) + "\033[0m" for row in cbuf]

            # Top-right timer HUD
            timer_txt = f"t {elapsed:5.2f}s"
            if width > len(timer_txt) + 4:
                lines[0] = (
                    "".join(cbuf[0][: width - len(timer_txt) - 2])
                    + rgb(235, 105, 70, timer_txt)
                    + "\033[0m"
                )

            # Bottom status HUD matching the screenshot
            rot_deg = (math.degrees(angle)) % 360.0
            hud_1 = rgb(150, 155, 165, "@999.2006.01.19 · 2026")
            hud_2 = rgb(175, 180, 190, f"rotation {rot_deg:6.2f}°      lights {NUM_LIGHTS}")
            hud_3 = rgb(175, 180, 190, f"letters {letter_count:,}")
            left_4 = "py agac.py"
            right_4 = f"running · {FPS} fps"
            pad_4 = " " * max(2, width - len(left_4) - len(right_4) - 2)
            hud_4 = rgb(135, 140, 150, f"{left_4}{pad_4}{right_4}")

            if height >= 6:
                lines[-4] = hud_1 + "\033[0m"
                lines[-3] = hud_2 + "\033[0m"
                lines[-2] = hud_3 + "\033[0m"
                lines[-1] = hud_4 + "\033[0m"

            sys.stdout.write("\033[H" + "\n".join(lines))
            sys.stdout.flush()

            frame_time = time.perf_counter() - now
            sleep_for = (1.0 / FPS) - frame_time
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[0m\033[?25h\n")
        sys.stdout.flush()


if __name__ == "__main__":
    render()