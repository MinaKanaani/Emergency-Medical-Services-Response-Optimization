## Results & Analysis

### GA-Optimized Response Time Across Availability Thresholds

This project evaluates a Genetic Algorithm (GA) that optimizes ambulance repositioning strategies under different system availability thresholds (θ).

For each threshold value, the GA searches for a station ordering that minimizes the **median emergency response time**, using a discrete-event EMS simulation as the fitness function. The threshold controls how aggressively idle ambulances are repositioned when system availability decreases.

**Key observations:**
- The GA consistently converges to improved response times across generations.
- Different threshold values lead to different optimal repositioning patterns.
- More aggressive thresholds tend to reduce response time but increase operational movement.

🖼️ *Figure: Best GA response time across different availability thresholds (illustrative run).*

---

### GA Response Time vs Fatigue-Aware Service Time

To ensure operational realism, GA-optimized response time is compared against **fatigue-related service time indicators** derived from the simulation.

Fatigue is captured indirectly through:
- cumulative repositioning time,
- interrupted repositioning travel,
- consecutive missions without rest.

This comparison highlights the trade-off between service performance and crew workload.

**Key observations:**
- Strategies optimized purely for response time can increase fatigue-related workload.
- Fatigue-aware evaluation identifies strategies that achieve more sustainable system performance.
- The GA framework enables explicit exploration of this trade-off.

🖼️ *Figure: Comparison of GA-optimized response time and fatigue-aware service time (normalized illustration).*

---

### Interpretation

Overall, the results demonstrate that simulation-based optimization using a Genetic Algorithm can significantly improve EMS response performance while revealing important trade-offs between service quality and operational sustainability.

> Note: Figures shown in this repository are generated from synthetic or normalized outputs for demonstration purposes.  
> Real operational datasets and unpublished experimental results are intentionally not included.
