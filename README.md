# Santa Speed Lab

Venkateshwar Reddy Jambula and Gabriel used Kimi K3.1 Pro on Cerebras with OpenClaw to find five in-stock Christmas gifts for a Eurorack musician. This repository contains the prompts, settings, and timing evidence behind our entry for the Santa’s Speedy Shopper Speed Bounty.

## Results

| Run | Session mean TPS | Final-call TPS | Evidence |
| --- | ---: | ---: | --- |
| Best verified CLI run | **1,375.40** | **1,794.66** | [Timing receipts](replay-archive/milestones/new-cli-peak/provider-stream-receipts.jsonl) · [Saved session in OpenClaw](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/new-cli-peak-archived-session.mp4) |
| Original Trackinizer Experiment #500 | 1,284.83 | 1,597.73 | [Experiment bundle](experiment-500/) |
| Best run recorded live from prompt to products | 1,123.45 | 1,230.92 | [Uncut OpenClaw recording](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/best-live-uncut.mp4) |
| Immediate CLI replay of the best run | 818.27 | 815.75 | [Timing receipts](replay-archive/milestones/immediate-confirmation/provider-stream-receipts.jsonl) |

The official OpenClaw speed patch reports the arithmetic mean of the measured model calls. Each call’s rate is its output token count divided by Cerebras server decode time. For the best CLI run, the discovery call generated 472 tokens in 493.65 ms and the final call generated 156 tokens in 86.92 ms. The OpenClaw recording shows that completed CLI session reopened in the dashboard, which rounds the final call to 1,795 TPS. The original #500 command took 18.72 seconds wall-clock.

## Demo and research graph

https://github.com/user-attachments/assets/13f70c1c-1f45-4d9a-88cc-3b838202b82f

[Download the 29-second Trackinizer replay](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/research-visuals-2026-11-23/trackinizer-blog-29s.mp4) · [**Watch the saved OpenClaw session**](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/new-cli-peak-archived-session.mp4)

![OpenClaw showing the five Eurorack product links and its rounded server TPS readout of 1,375 mean and 1,795 p90](docs/assets/openclaw-peak-result.png)

*The verified CLI session reopened in OpenClaw. The dashboard rounds its rates and labels the second figure p90. The saved receipts give the precise session mean of 1,375.40 TPS and final-call rate of 1,794.66 TPS.*

- **Trackinizer replay.** The 29-second recording starts with 1,687 records. It follows Issue #202, Gabriel’s XML format in Web Result #110, the linked live-shopping test #258, and the resulting shared hypothesis in Belief #346. [See the graph still](docs/assets/trackinizer-issue-202-detail.png)
- **TPS progression.** The chart covers 260 campaign and replay attempts. Its two lines track the best qualifying session mean and the fastest individual call. [Watch the animation](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/research-visuals-2026-11-23/swarm-tps-peak-11s.mp4)
- **OpenClaw evidence.** The recording archive indexes 80 entries and 51 clips, including incomplete runs and setup failures. [Browse the ledger](replay-archive/) · [Download the recordings](https://github.com/Venkat-RJ/santa-speed-lab/releases/tag/experiment-500-proof-2026-11-23)

![TPS progression across 260 attempts, ending at 1,375.40 mean TPS and 1,794.66 TPS for the fastest call](docs/assets/cerebras-tps-chart.png)

## Verify the evidence offline

From the repository root, using Python 3.9+ and Node.js 24:

```sh
python3 experiment-500/verify.py
python3 replay-archive/verify.py
```

Start with the [Experiment #500 guide](experiment-500/README.md) for the original prompt, configuration, timing receipts, and product validation. The [replay archive](replay-archive/README.md) contains the later peak, its immediate replay, and the attempt ledger. For a live rerun, follow the guide with the pinned OpenClaw build and a Cerebras key that has access to the recorded model. As of November 23, 2026, the hackathon trial endpoint returned `model_not_found` for our key. The offline checks use saved evidence.

## Five products found in the run

The prompt supplied live retailer search URLs. OpenClaw discovered the individual products during the run, and the audit matched each link and its then-current stock status to the saved catalog and product-page evidence.

1. [AI024 Eurorack X Filter](https://aisynthesis.com/product/ai024-eurorack-x-filter/)
2. [AI028 Voltage Controlled Matrix Mixer](https://aisynthesis.com/product/ai028-voltage-controlled-matrix-mixer/)
3. [AI011 Analog Voltage Controlled Oscillator](https://aisynthesis.com/product/ai011-voltage-controlled-oscillator/)
4. [AI016 Eurorack Tape Echo Interface](https://aisynthesis.com/product/ai016-eurorack-tape-echo-interface/)
5. [Eurorack Modular Patch Cable 4.9ft](https://aisynthesis.com/product/eurorack-modular-patch-cable-4-9ft/)

[Venkat](https://x.com/venkatGoku) · [Gabriel](https://x.com/areseyefu) · [Trackinizer](https://github.com/rekursiv-ai/trackinizer)
