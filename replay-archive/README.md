# Experiment #500 replay archive

This archive covers the saved #500 prompt replays, same-prompt configuration variants, associated launch failures, and related dashboard diagnostics in the local research lab. Each ledger entry links to the source fields needed to audit its timing and shopping outcome. A missing final-call TPS means no completed timed final answer was established. The model is Kimi K3.1 Pro on Cerebras.

| Session | Official mean TPS | Final-call TPS | Recording |
| --- | ---: | ---: | --- |
| Original #500 | 1,284.83 | 1,597.73 | [Native UI reopened after completion](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/experiment-500-archived-session.mp4) |
| New CLI peak | 1,375.40 | 1,794.66 | [Native UI reopened after completion](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/new-cli-peak-archived-session.mp4) |
| Immediate CLI replay | 818.27 | 815.75 | CLI receipts |
| Highest verified live recording | 1,123.45 | 1,230.92 | [Uncut recording](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/best-live-uncut.mp4) · [Copy with full final dashboard frame](https://github.com/Venkat-RJ/santa-speed-lab/releases/download/experiment-500-proof-2026-11-23/best-live-with-final-dashboard-frame.mp4) |

The original, new peak and immediate replay returned the same five verified product links. All three used 156 output tokens for the final answer. Their server decode times were 97.638830 ms, 86.924623 ms and 191.235687 ms respectively. The official mean averages all server-timed model calls in the session. A p90 badge can represent the discovery call in another run.

## Verify locally

Use Python 3.9+ and Node.js 24 from the repository root.

```sh
python3 experiment-500/verify.py
python3 replay-archive/verify.py
python3 replay-archive/verify.py --zip /path/to/experiment-500-recordings.zip
```

The archive verifier uses the original OpenClaw scorer. It recomputes the per-session mean, checks the final assistant call, and matches all qualifying gifts to the in-session catalog responses and product-page JSON-LD excerpts. For the three benchmark milestones it compares each measured duration with the original Cerebras timing frames. The ZIP check verifies the inventory, file sizes and SHA-256 of each video file. The [existing replay guide](../experiment-500/README.md) runs the same prompt against live websites with your own Cerebras credential.

Public evidence retains tool calls, catalog rows, server timings, final product links, retail offer excerpts and source hashes. Retry prompts, private reasoning text, local authentication and session database files stay outside the public packets. The gateway HTTP status fields use the run's time window when several sessions share one observation log. Variant labels and observed request settings are in the [machine-readable ledger](attempts.json).

## Recording archive

The [GitHub release](https://github.com/Venkat-RJ/santa-speed-lab/releases/tag/experiment-500-proof-2026-11-23) includes the browser recording originals, MP4 playback copies, and separate viewing copies with the final full dashboard screenshot held for three seconds where available. Some browser originals clip the bottom of the viewport. The final dashboard frame in the viewing copy comes from that same session. Setup clips and edited demos have separate labels. The pre-connection WebM in clip-005 ends prematurely. Its original bytes and the playable MP4 are both preserved. See the [recording manifest](recordings.json) for file names, linked attempts, durations and hashes.

| Outcome | Count | Interpretation |
| --- | ---: | --- |
| cached-retail-results | 2 | The gateway returned cached retailer data. |
| incomplete-or-rate-limited | 8 | The session did not finish with a timed final answer. This category includes provider rate limits. |
| launch-failed | 1 | The CLI refused to run against a state directory with an active gateway. |
| qualified | 64 | Verified five distinct gifts against uncached in-session retail responses and saved product-page offers. The transcript has an official score. |
| setup-only | 4 | The setup or navigation attempt ended before a benchmark was submitted. |
| shopping-or-timing-unverified | 1 | The available records did not satisfy the product and timing checks. |

## Attempts

The displayed rates are rounded to two decimals. Non-qualifying rows can have partial measured rates. A dash indicates unavailable evidence. Clip IDs identify files in the recording ZIP.

| ID | Attempt | Outcome | Mean TPS | Final TPS | Gifts verified | Clips |
| --- | --- | --- | ---: | ---: | ---: | --- |
| [run-001](evidence/run-001.json) | original-500 | qualified | 1,284.83 | 1,597.73 | 5 | clip-009, clip-050 |
| [run-002](evidence/run-002.json) | santa-astra-208-replay-500/jsonl-replay-500 | qualified | 972.95 | 1,319.42 | 5 | – |
| [run-003](evidence/run-003.json) | santa-astra-208-five-arguments-cap1024/jsonl-cap1024 | qualified | 1,038.26 | 1,196.14 | 5 | – |
| [run-004](evidence/run-004.json) | santa-astra-208-wrapped-retail-json/jsonl-wrapped-retail-json | qualified | 705.10 | 645.65 | 5 | – |
| [run-005](evidence/run-005.json) | santa-astra-208-full-retail-json/jsonl-full-retail-json | incomplete-or-rate-limited | 905.89 | – | 0 | – |
| [run-006](evidence/run-006.json) | santa-astra-208-five-arguments-temp-zero/jsonl-temp-zero | incomplete-or-rate-limited | – | – | 0 | – |
| [run-007](evidence/run-007.json) | santa-astra-208-required-discovery/jsonl-required-discovery | qualified | 918.09 | 978.15 | 5 | – |
| [run-008](evidence/run-008.json) | santa-astra-208-temp-zero-queue-retry/jsonl-temp-zero-retry | incomplete-or-rate-limited | 711.63 | – | 0 | – |
| [run-009](evidence/run-009.json) | santa-astra-208-peak-control-1432/jsonl-peak-control | incomplete-or-rate-limited | 681.44 | – | 0 | – |
| [run-010](evidence/run-010.json) | santa-astra-208-nonstreaming/jsonl-nonstreaming | qualified | 807.68 | 610.84 | 5 | – |
| [run-011](evidence/run-011.json) | santa-demo-replay-500-20261122-221837/jsonl-demo-replay-500 | setup-only | – | – | 0 | – |
| [run-012](evidence/run-012.json) | santa-demo-replay-500-20261122-221837/jsonl-demo-replay-500-clean | qualified | 1,005.29 | 1,007.85 | 5 | – |
| [run-013](evidence/run-013.json) | santa-openclaw-dashboard-500.I3GisnTx | incomplete-or-rate-limited | 346.68 | – | 0 | – |
| [run-014](evidence/run-014.json) | santa-openclaw-dashboard-exact-500.nU7qUuRB | shopping-or-timing-unverified | 531.86 | 323.64 | 0 | – |
| [run-015](evidence/run-015.json) | santa-public-reproduction-500-20261122-230432-31760 | incomplete-or-rate-limited | – | – | 0 | – |
| [run-016](evidence/run-016.json) | santa-public-reproduction-500-20261122-230751-b8e29 | qualified | 918.24 | 1,077.39 | 5 | – |
| [run-017](evidence/run-017.json) | santa-exp500-repeat-20261122-230954-20661/run-01 | qualified | 559.39 | 579.78 | 5 | – |
| [run-018](evidence/run-018.json) | santa-exp500-repeat-20261122-230954-20661/run-02 | qualified | 729.99 | 712.44 | 5 | – |
| [run-019](evidence/run-019.json) | santa-exp500-repeat-20261122-230954-20661/run-03 | qualified | 728.47 | 688.62 | 5 | – |
| [run-020](evidence/run-020.json) | santa-exp500-repeat-20261122-230954-20661/run-04 | qualified | 852.82 | 882.66 | 5 | – |
| [run-021](evidence/run-021.json) | santa-exp500-repeat-20261122-230954-20661/run-05 | incomplete-or-rate-limited | – | – | 0 | – |
| [run-022](evidence/run-022.json) | santa-exp500-repeat-20261122-230954-20661/run-06 | qualified | 692.55 | 708.92 | 5 | – |
| [run-023](evidence/run-023.json) | santa-claims-20261122-234030 | qualified | 828.76 | 1,067.51 | 5 | – |
| [run-024](evidence/run-024.json) | santa-best-once-20261122-234418 | qualified | 857.64 | 1,062.23 | 5 | – |
| [run-025](evidence/run-025.json) | santa-500-final-recheck-20261122-234826 | qualified | 666.76 | 678.45 | 5 | – |
| [run-026](evidence/run-026.json) | santa-ui-live-W3stZp/initial-navigation | setup-only | – | – | 0 | clip-001 |
| [run-027](evidence/run-027.json) | santa-ui-live-W3stZp/trial-1 | qualified | 751.26 | 795.82 | 5 | clip-002 |
| [run-028](evidence/run-028.json) | santa-ui-live-W3stZp/trial-2 | cached-retail-results | 746.17 | 655.49 | 0 | clip-003 |
| [run-029](evidence/run-029.json) | santa-ui-live-W3stZp/trial-3 | cached-retail-results | 821.35 | 771.81 | 0 | clip-004 |
| [run-030](evidence/run-030.json) | santa-ui-fresh-jhqIr0/pre-connect | setup-only | – | – | 0 | clip-005 |
| [run-031](evidence/run-031.json) | santa-ui-fresh-jhqIr0/trial-1 | qualified | 791.86 | 939.54 | 5 | clip-006 |
| [run-032](evidence/run-032.json) | santa-ui-fresh-jhqIr0/trial-2 | qualified | 799.52 | 684.97 | 5 | clip-007 |
| [run-033](evidence/run-033.json) | santa-ui-fresh-jhqIr0/trial-3 | qualified | 818.15 | 763.27 | 5 | clip-008 |
| [run-034](evidence/run-034.json) | santa-astra-208-five-arguments/ui-companion-20261123-000152 | setup-only | – | – | 0 | – |
| [run-035](evidence/run-035.json) | santa-astra-208-five-arguments/ui-companion-cli-20261123-000156 | qualified | 1,043.51 | 1,331.59 | 5 | – |
| [run-036](evidence/run-036.json) | santa-astra-208-five-arguments/ui-companion-cli-20261123-000230 | qualified | 940.07 | 1,146.64 | 5 | – |
| [run-037](evidence/run-037.json) | santa-astra-208-five-arguments/ui-companion-cli-20261123-000254 | qualified | 704.93 | 720.90 | 5 | – |
| [run-038](evidence/run-038.json) | santa-500-ui-batch-cSzufF/run-01 | qualified | 1,024.50 | 891.99 | 5 | clip-026 |
| [run-039](evidence/run-039.json) | santa-500-ui-batch-cSzufF/run-02 | qualified | 893.47 | 783.55 | 5 | clip-027 |
| [run-040](evidence/run-040.json) | santa-500-ui-batch-cSzufF/run-03 | qualified | 779.62 | 602.19 | 5 | clip-028 |
| [run-041](evidence/run-041.json) | santa-500-ui-batch-cSzufF/run-04 | qualified | 880.07 | 836.84 | 5 | clip-029 |
| [run-042](evidence/run-042.json) | santa-500-ui-batch-cSzufF/run-05 | qualified | 691.95 | 750.58 | 5 | clip-030 |
| [run-043](evidence/run-043.json) | santa-500-ui-batch-cSzufF/run-06 | qualified | 946.81 | 999.96 | 5 | clip-031 |
| [run-044](evidence/run-044.json) | santa-500-ui-batch-cSzufF/run-07 | qualified | 1,052.84 | 928.90 | 5 | clip-032 |
| [run-045](evidence/run-045.json) | santa-500-ui-batch-cSzufF/run-08 | qualified | 726.65 | 740.06 | 5 | clip-033 |
| [run-046](evidence/run-046.json) | santa-500-ui-batch-cSzufF/run-09 | qualified | 836.46 | 909.31 | 5 | clip-034 |
| [run-047](evidence/run-047.json) | santa-500-ui-batch-cSzufF/run-10 | qualified | 887.88 | 980.15 | 5 | clip-035 |
| [run-048](evidence/run-048.json) | santa-500-ui-batch-cSzufF/run-11 | qualified | 903.13 | 890.35 | 5 | clip-036 |
| [run-049](evidence/run-049.json) | santa-500-ui-batch-cSzufF/run-12 | qualified | 1,123.45 | 1,230.92 | 5 | clip-037 |
| [run-050](evidence/run-050.json) | santa-500-ui-batch-cSzufF/run-13 | qualified | 816.44 | 784.14 | 5 | clip-038 |
| [run-051](evidence/run-051.json) | santa-500-ui-batch-cSzufF/run-14 | qualified | 810.54 | 980.34 | 5 | clip-039 |
| [run-052](evidence/run-052.json) | santa-500-ui-batch-cSzufF/run-15 | qualified | 722.57 | 842.19 | 5 | clip-040 |
| [run-053](evidence/run-053.json) | santa-500-ui-batch-cSzufF/run-16 | qualified | 667.34 | 689.43 | 5 | clip-041 |
| [run-054](evidence/run-054.json) | santa-500-ui-batch-cSzufF/run-17 | qualified | 759.46 | 779.41 | 5 | clip-042 |
| [run-055](evidence/run-055.json) | santa-500-ui-batch-cSzufF/run-18 | qualified | 821.38 | 744.33 | 5 | clip-043 |
| [run-056](evidence/run-056.json) | santa-astra-208-five-arguments/proof-cli-20261123-002107 | qualified | 923.73 | 985.96 | 5 | – |
| [run-057](evidence/run-057.json) | santa-500-crosscheck-8v0b0C/run-01 | qualified | 774.60 | 755.39 | 5 | clip-010 |
| [run-058](evidence/run-058.json) | santa-500-crosscheck-8v0b0C/run-02 | qualified | 712.77 | 577.76 | 5 | clip-011 |
| [run-059](evidence/run-059.json) | santa-500-crosscheck-8v0b0C/run-03 | qualified | 747.63 | 711.67 | 5 | clip-012 |
| [run-060](evidence/run-060.json) | santa-500-crosscheck-8v0b0C/run-04 | qualified | 854.05 | 1,087.58 | 5 | clip-013 |
| [run-061](evidence/run-061.json) | santa-astra-208-five-arguments/proof-cli-20261123-002457 | qualified | 957.92 | 1,039.60 | 5 | – |
| [run-062](evidence/run-062.json) | new-cli-peak | qualified | 1,375.40 | 1,794.66 | 5 | clip-014 |
| [run-063](evidence/run-063.json) | immediate-confirmation | qualified | 818.27 | 815.75 | 5 | – |
| [run-064](evidence/run-064.json) | santa-500-newpeak-ui-n3fhx_dv/run-01 | qualified | 1,094.65 | 867.82 | 5 | clip-016 |
| [run-065](evidence/run-065.json) | santa-500-newpeak-ui-n3fhx_dv/run-02 | qualified | 815.30 | 758.99 | 5 | clip-017 |
| [run-066](evidence/run-066.json) | santa-500-newpeak-ui-n3fhx_dv/run-03 | qualified | 787.11 | 889.86 | 5 | clip-018 |
| [run-067](evidence/run-067.json) | santa-500-newpeak-ui-n3fhx_dv/run-04 | qualified | 891.95 | 1,088.45 | 5 | clip-019 |
| [run-068](evidence/run-068.json) | santa-500-newpeak-ui-n3fhx_dv/run-05 | qualified | 614.43 | 522.75 | 5 | clip-020 |
| [run-069](evidence/run-069.json) | santa-500-newpeak-ui-n3fhx_dv/run-06 | qualified | 643.84 | 636.94 | 5 | clip-021 |
| [run-070](evidence/run-070.json) | santa-500-newpeak-ui-n3fhx_dv/run-07 | qualified | 1,116.67 | 1,141.49 | 5 | clip-022 |
| [run-071](evidence/run-071.json) | santa-500-newpeak-ui-n3fhx_dv/run-08 | qualified | 687.28 | 611.91 | 5 | clip-023 |
| [run-072](evidence/run-072.json) | santa-500-newpeak-ui-n3fhx_dv/joint-recipe/joint-live-01 | launch-failed | – | – | 0 | clip-015 |
| [run-073](evidence/run-073.json) | santa-500-newpeak-ui-n3fhx_dv/run-09 | qualified | 930.20 | 1,005.80 | 5 | clip-024 |
| [run-074](evidence/run-074.json) | santa-500-newpeak-ui-n3fhx_dv/run-10 | qualified | 791.63 | 728.62 | 5 | clip-025 |
| [run-075](evidence/run-075.json) | santa-500-live-target-V46yx1/run-01 | qualified | 925.96 | 1,129.67 | 5 | clip-044 |
| [run-076](evidence/run-076.json) | santa-500-live-target-V46yx1/run-02 | qualified | 963.35 | 760.37 | 5 | clip-045 |
| [run-077](evidence/run-077.json) | santa-500-live-target-V46yx1/run-03 | qualified | 937.73 | 915.87 | 5 | clip-046 |
| [run-078](evidence/run-078.json) | santa-500-live-target-V46yx1/run-04 | qualified | 947.15 | 995.56 | 5 | clip-047 |
| [run-079](evidence/run-079.json) | santa-500-live-target-V46yx1/run-05 | incomplete-or-rate-limited | 719.11 | – | 0 | clip-048 |
| [run-080](evidence/run-080.json) | santa-500-live-target-V46yx1/run-06 | qualified | 685.99 | 572.70 | 5 | clip-049 |
