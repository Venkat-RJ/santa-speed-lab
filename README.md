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
