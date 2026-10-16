**Projected expected worker CPU-hours to K = 2,000 per setting** (median [IQR], largest resolved point estimate; resolved settings of 40, with unresolved zero-hit or no-exposure settings counted)

| Population | n = 0 | n = 30 | n = 300 |
|---|---|---|---|
| wild_dog | 3.8 [3.7–4.1], 4.9 | 4.8 [2.0–14.6], 85.7 | 14.8 [5.5–153], 926 |
| marmot | 3.2 [3.2–3.4], 3.8 | 3.8 [2.8–11.0], 301 | 27.4 [10.0–92.9], 914 |
| ms_woodpecker | 2.6 [2.5–2.7], 3.1 | 4.6 [2.6–23.0], 166 | 32.8 [12.9–131], 1,825 (1 unresolved) |
| rc_woodpecker | 2.5 [2.3–2.6], 2.9 | 4.3 [2.6–7.9], 149 | 18.8 [10.1–36.1], 368 |
| golden_plover | 3.4 [3.1–3.6], 3.9 (1 unresolved) | 4.3 [2.0–12.1], 139 | 17.2 [5.4–111], 1,848 (2 unresolved) |
| whooping_crane | 2.8 [2.6–2.9], 3.3 | 3.3 [2.0–7.5], 78.7 | 19.2 [7.8–41.0], 270 |
| hawaiian_crow | 1.9 [1.8–2.0], 2.2 | 3.2 [1.5–7.9], 166 | 21.7 [5.7–68.5], 1,770 (1 unresolved) |
| wood_turtle_A | 3.1 [3.0–3.3], 3.7 | 3.9 [2.7–15.4], 363 | 36.1 [11.3–77.4], 945 |
| wood_turtle_B | 3.2 [2.9–3.5], 3.8 | 3.2 [2.3–8.6], 51.1 | 16.8 [6.9–35.4], 360 |

By scenario (resolved settings of 90; unresolved counted):

| Scenario | n = 0 | n = 30 | n = 300 |
|---|---|---|---|
| null_prior_predictive | 3.0 [2.6–3.4], 4.3 | 2.9 [1.8–4.8], 139 | 7.2 [4.3–16.7], 125 (1 unresolved) |
| null_low_s | 3.0 [2.6–3.4], 4.8 | 5.5 [3.2–17.7], 301 | 67.8 [20.6–244], 1,848 (2 unresolved) |
| MA_betamin | 3.0 [2.6–3.5], 4.9 | 3.1 [2.3–8.4], 363 | 15.6 [5.3–31.0], 945 |
| MA_d10_0.5 | 3.0 [2.5–3.4], 4.1 (1 unresolved) | 4.6 [2.6–17.8], 361 | 32.8 [15.4–74.5], 1,825 (1 unresolved) |

**Most expensive settings** (projected expected CPU-h to K; interval: suffix retention interval transformed at observed throughput, for expected cost, not a run-time prediction)

| Setting | Population | Outer | n | Hits | CPU-h | 95% interval | Kind |
|---|---|---|---|---|---|---|---|
| 524 | golden_plover | null_low_s/4 | 300 | 1 | 1,848 | 332–73,001 | projected |
| 335 | ms_woodpecker | MA_d10_0.5/1 | 300 | 1 | 1,825 | 328–72,081 | projected |
| 836 | hawaiian_crow | MA_d10_0.5/8 | 300 | 1 | 1,770 | 318–69,907 | projected |
| 905 | wood_turtle_A | MA_betamin/1 | 300 | 2 | 945 | 262–7,800 | projected |
| 38 | wild_dog | null_low_s/2 | 300 | 2 | 926 | 256–7,644 | projected |
| 155 | marmot | null_low_s/1 | 300 | 2 | 914 | 253–7,549 | projected |
| 515 | golden_plover | null_low_s/1 | 300 | 2 | 897 | 248–7,405 | projected |
| 53 | wild_dog | null_low_s/7 | 300 | 2 | 891 | 247–7,356 | projected |
| 50 | wild_dog | null_low_s/6 | 300 | 2 | 841 | 233–6,941 | projected |
| 341 | ms_woodpecker | MA_d10_0.5/3 | 300 | 3 | 618 | 211–2,997 | projected |

**Stage 1b inventory by cell** (12 largest; mean of 10 pilot outers x 200)

| Population | Scenario | n | Mean CPU-h | Max CPU-h | CPU-h for 200 outers | Unresolved |
|---|---|---|---|---|---|---|
| golden_plover | null_low_s | 300 | 568 | 1,848 | 113,664 | 2 |
| wild_dog | null_low_s | 300 | 505 | 926 | 101,013 | 0 |
| ms_woodpecker | MA_d10_0.5 | 300 | 338 | 1,825 | 67,557 | 0 |
| marmot | null_low_s | 300 | 319 | 914 | 63,738 | 0 |
| hawaiian_crow | MA_d10_0.5 | 300 | 285 | 1,770 | 57,065 | 1 |
| ms_woodpecker | null_low_s | 300 | 171 | 355 | 34,234 | 0 |
| wood_turtle_A | MA_betamin | 300 | 130 | 945 | 26,040 | 0 |
| wood_turtle_A | null_low_s | 300 | 114 | 229 | 22,797 | 0 |
| wood_turtle_B | null_low_s | 300 | 109 | 360 | 21,800 | 0 |
| hawaiian_crow | MA_betamin | 300 | 108 | 584 | 21,693 | 0 |
| wild_dog | MA_d10_0.5 | 300 | 106 | 608 | 21,247 | 0 |
| marmot | MA_d10_0.5 | 300 | 96.4 | 363 | 19,273 | 0 |
