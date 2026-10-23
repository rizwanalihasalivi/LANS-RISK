# LANS-RISK conference V4: reproducibility details

This supplement describes the existing frozen main-confirmation protocol. It adds no experiments. The seven-page article is `paper.pdf`; this supplement and scenario tables are separate from the manuscript. Source excerpts preserve the executed file bytes; they do not form a standalone installation. The full repository recovery archive provides dependencies, models and original batch logs.

## Actual scene construction

All random draws below are proposals before rejection sampling. Acceptance therefore changes the joint distribution; these are not independent uniform distributions conditional on acceptance. Traffic case seeds are 141000–141099, reused across methods and frozen actors. Units are metres, seconds and radians.

| Scenario | NPC count | Common controller speed reference | Ego initial speed | Goal |
|---|---:|---:|---|---|
| Highway | 5 | 15 m/s | U[11,15] m/s | X − initial X ≥ 80 m |
| Merge | 6 | 12 m/s | U[11,15] m/s | X − initial X ≥ 60 m and abs(Y) < 1 m |
| Intersection | 1 | 8 m/s | U[6,7.5] m/s | X − initial X ≥ 50 m |
| Roundabout | 4 | 9 m/s | U[5.5,7.5] m/s | One unwrapped 2π lap at radius 8 m |

Highway ego starts at (0,0), heading zero. The first NPC has X∼U[25,35], Y∼U[−0.8,0.8]. For each other NPC, with probability 0.7, choose Y=−3.5 or 3.5 with equal probability plus U[−0.5,0.5] and X∼U[35,80]; otherwise Y∼U[−0.8,0.8], X∼U[45,80]. NPC speeds are U[4,9.5], desired speeds U[9.5,13.5]. Headings are zero.

Merge ego starts at (0,−3.5), heading zero. Each NPC uses, with probability 0.8, Y∼U[−0.9,0.9] and X∼U[30,70]; otherwise Y∼U[−4.3,−2.7] and X∼U[20,45]. Speeds and desired speeds match Highway. The base generator draws a small heading perturbation, but the executed traffic subclass resets every NPC heading to zero.

Intersection ego starts at X∼U[−24,−20], Y=0, heading zero. Exactly one crossing NPC is spawned, overriding the nominal configuration count of three. It starts north or south with equal probability, X∼U[−2,2], and absolute Y drawn with equal mixture weight from U[15,22] or U[32,45]. Heading is −π/2 from the north or π/2 from the south, speed U[4.5,6], desired speed U[5,7.5].

Roundabout is circular following, not entry/exit negotiation. Ego angle θ₀∼U[0,2π], with tangent heading. The executed subclass places NPC j at θ₀+2π(j+1)/(n+1)+U[−0.08,0.08], j=0,…,n−1. This replaces the base environment's older placement. NPC speed is U[4,7], desired speed U[5,8].

All scenarios reject a proposal unless every pair of vehicle centres is more than 6 m apart. Highway/Merge additionally check each forward pair with ΔX>0 and abs(ΔY)<4.846. Its longitudinal disc clearance must exceed 1+0.1 max(0,Δv)+max(0,Δv)²/12. The original main study permits at most 10,000 generation attempts. No dense-Merge robustness amendment is used in these main results. Exact operations and RNG order are in `source_excerpt/traffic_v2/benchmark.py` and `source_excerpt/submission_study/lans_env_scenario.py`.

## Traffic, sampling and endpoints

NPCs follow the executed IDM-style longitudinal interaction in `traffic_v2/benchmark.py`. Desired gap is 1+max(0,0.6v+v(v−v_leader)/(2√3)); acceleration is clip(1.5[1−(v/v_desired)^4−(desired_gap/max(0.1,gap))²],−6,1.5). Speeds are clipped to [0,20]. Leader selection uses projected disc geometry on straight headings and arc clearance on the circle. It considers the other NPCs and ego. The controller does not observe NPC desired speed; its forecast extrapolates finite-difference acceleration rather than reproducing this interaction law.

The ego/plant timestep is 0.1 s. Commands pass through a common zero-initialized FIFO with d=0,2,5,7,10 steps. Goal attainment is nonterminal; the runner retains whether the goal was ever reached and continues until collision or 160 steps. Route completion requires goal attainment and no collision in the episode. Corridor completion additionally requires every recorded lateral-error magnitude ≤1.75 m. Collision checks use disc overlap at sampled states; corridor checks concern the reference point, not the full footprint. Neither is continuous-time safety certification.

## Frozen actor features and deployment

The actor receives the following 18-dimensional legacy vector, with final nonfinite handling and clipping to [−1,1]. The derivative estimates are exponentially filtered using the original environment's alpha. Exact definitions, critical-NPC selection and scaling are in `lans_env_scenario.py:_get_obs` and its called functions.

| Indices (one-based) | Features |
|---|---|
| 1–4 | e_y/5, filtered ė_y/10, e_ψ/π, filtered ė_ψ/2, each clipped to [−1,1] |
| 5 | Ego speed/25, clipped to [0,1] |
| 6–7 | Last executed steering; ego acceleration/a_max clipped to [−1,1] |
| 8–9 | Critical-vehicle D/50 clipped to [−1,1]; T/10 clipped to [0,1], finite-value fallbacks as in source |
| 10 | NPC count/8, clipped to [0,1] |
| 11–14 | Highway/Merge/Intersection/Roundabout one-hot indicators |
| 15 | Critical-vehicle angle/π, clipped to [−1,1] |
| 16 | Synthetic timing (latency_ms−tau_min)/(tau_max−tau_min), clipped to [0,1] |
| 17 | Legacy beta authority-weight feature |
| 18 | LQR steering advice, clipped to [−1,1] |

The actor does not receive the full NPC state set or pending command queue. Its synthetic timing feature is not the imposed FIFO delay. In the executed direct-action path, `TrafficEnv.step` forces beta=1 and disables the legacy safety supervisor. The new observation still includes inherited timing/gain features sampled by the parent. LQR advice in the observation does not create a runtime LQR–PPO actuation-fusion block. PPO predicts deterministically from the frozen checkpoint, and its two outputs are used as a steering/acceleration proposal. This inherited-policy deployment differs from training a policy specifically for the new traffic/FIFO interface.

`evidence/ACTOR_CHECKPOINT_METADATA.json` contains fields extracted by reading each ZIP's plain JSON `data` member without executing model code or unpickling serialized objects. All 12 checkpoints record 311,296 realized timesteps, seeds 42/43/44, network [128,128,64] with ReLU, n_steps=2048, batch_size=64, n_epochs=10, gamma=.995, gae_lambda=.95, clip schedule .2, entropy coefficient .01, value coefficient .5 and max-gradient norm .5. Learning rate is .00025 for Intersection and .0003 otherwise. These are checkpoint-recorded properties, not an independent reconstruction of training history. Historical supervised/blended training code alone does not prove every checkpoint's full training trajectory.

## Evidence and inference

`evidence/descriptive_metrics.csv` supplies per-condition means, sample SD, observed extremes, quantiles and intervals; `paired_tests.csv` supplies paired differences, saved bootstrap intervals, raw p-values and full-family Holm corrections. Tests preserve traffic-case pairing and actor/scenario conditions. Aggregate table denominators of 1,200 include repeated actors on the same 400 traffic cases and must not be treated as independent binomial samples.

For an explicit uncertainty example, Merge at 1,000 ms yields 35/100 corridor completions for LANS actor 42 (Wilson 95% interval 26.3642–44.7456%) and 34/100 for nominal MPC (25.4615–43.7223%). These marginal intervals do not establish equivalence; paired tests are in the CSV.

Saved evidence contains episode-level scalar metrics and binary flags, not full trajectories. Statistical aggregates/tests can be reconstructed; individual RMSE, collision/corridor events, actual queue histories and specific causal failure narratives cannot be independently replayed from these records alone. Forecast-prefix diagnostics are transient; the runner persists its accumulated no-feasible count, not every transient diagnostic. The full ARIS review recomputes all 3,440 paired tests; it does not independently regenerate every saved bootstrap interval or certify historical no-tuning chronology.
