# Santa Speed Lab

Our entry for Cerebras’s Santa’s Speedy Shopper Speed Bounty.

[Venkat](https://x.com/venkatGoku) and [Gabriel](https://x.com/areseyefu) used OpenClaw with Kimi K3.1 Pro on Cerebras to find five in-stock Christmas gifts for a Eurorack musician from a live retailer.

## Experiment #500

| Model call | Output tokens | Cerebras decode time | TPS |
| --- | ---: | ---: | ---: |
| Discover products with five live searches | 474 | 487.688936 ms | 971.93 |
| Return the five product links | 156 | 97.638830 ms | **1,597.73** |
| **Official mean across both calls** | | | **1,284.83** |

The official OpenClaw speed patch averages the two per-call decode rates. The measurement uses Cerebras’s server decode time. The recorded OpenClaw command took 18.72 seconds wall-clock. Trackinizer records the run as **Experiment #500** under **Issue #208**.

## November 23 verification and recordings

A fresh replay of the #500 prompt and configuration reached **1,375.40 official mean TPS**. OpenClaw used 472 tokens in 493.653985 ms to request the products and 156 tokens in 86.924623 ms to return their links. The final call scored **1,794.66 TPS**. Its archived session displays 1,795 when OpenClaw rounds to a whole number. The immediate replay returned the same five gifts at **818.27 mean TPS** and **815.75 final-call TPS**. [Peak timing receipts](replay-archive/milestones/new-cli-peak/provider-stream-receipts.jsonl) · [Immediate replay receipts](replay-archive/milestones/immediate-confirmation/provider-stream-receipts.jsonl)

The camera was enabled after the peak CLI run finished. Its video shows OpenClaw reopening the saved session. The strongest qualifying run recorded from before submission through the five product links reached **1,123.45 mean TPS** and **1,230.92 on the final call**. [Archived peak session](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/new-cli-peak-archived-session.mp4) · [Uncut live recording](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/best-live-uncut.mp4)

The [attempt ledger](replay-archive/README.md) includes 80 entries and 51 recordings, including unsuccessful attempts, setup failures and edited demonstrations. Run the offline checks with Python 3.9+ and Node.js 24.

```sh
python3 experiment-500/verify.py
python3 replay-archive/verify.py
```

[Download the full recording archive](https://github.com/Venkat-RJ/santa-speed-lab/releases/tag/experiment-500-proof-2026-11-23)

## Five gifts found in the run

1. [AI024 Eurorack X Filter](https://aisynthesis.com/product/ai024-eurorack-x-filter/)
2. [AI028 Voltage Controlled Matrix Mixer](https://aisynthesis.com/product/ai028-voltage-controlled-matrix-mixer/)
3. [AI011 Analog Voltage Controlled Oscillator](https://aisynthesis.com/product/ai011-voltage-controlled-oscillator/)
4. [AI016 Eurorack Tape Echo Interface](https://aisynthesis.com/product/ai016-eurorack-tape-echo-interface/)
5. [Eurorack Modular Patch Cable 4.9ft](https://aisynthesis.com/product/eurorack-modular-patch-cable-4-9ft/)

The prompt supplied five retailer search URLs. OpenClaw found the individual products during the run. The audit confirmed each returned link and its in-stock status against both the live catalog response and the corresponding product page.

## Verify or replay

**Verify the recorded run offline** with Python 3.9+ and Node.js 24. No API key or OpenClaw installation is needed.

    python3 experiment-500/verify.py

**Replay on live sites** with the pinned OpenClaw source, exact prompt, configuration, and your own Cerebras key with access to the recorded model. The [replay guide](experiment-500/README.md) walks through setup and explains the saved evidence. The original follow-up, Experiment #501, verified five products at **972.95 mean TPS** and **1,319.42 peak TPS**.
