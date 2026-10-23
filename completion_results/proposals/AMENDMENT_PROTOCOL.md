# Proposed initialization-only amendment — approval required

Scope: only the 33 denser-Merge robustness conditions, 50 traffic seeds161000–161049, seven original controllers, actors42/43/44 where applicable, delays0/500/1000ms. The original 44,000 confirmation records and 231 completed robustness conditions remain unchanged.

Raise the collision-free initialization rejection budget from10,000 to200,000 attempts in a separate derivative of traffic_v2/benchmark.py. Preserve the same RNG seed/stream, seven NPCs, all safety predicates, plant, controllers, models, candidate budgets, delays and episode counts. Original source files and freeze manifests remain untouched. Results use a separate stage directory and an amended source fingerprint; they must never be represented as having used the original frozen sampler.

The preflight compares all original-success initial states and checks all50seeds under the larger budget. Original failure is a setup failure, never counted as a controller collision or an evaluated episode.
