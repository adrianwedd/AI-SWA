

# **Automated Performance Engineering: A Framework for Reinforcement Learning-Driven Compiler Optimization**

## **Part I: The Strategic Imperative for Learned Compilers**

### **Section 1: Beyond Heuristics: The Case for Adaptive Compilation**

Modern compilers are masterpieces of engineering, capable of transforming high-level, human-readable code into efficient machine instructions. Central to this process are optimization levels like \-O2 and \-O3, which apply a predetermined sequence of transformation passes to the code.1 These sequences are built on decades of experience and heuristics designed to yield good average performance across an immense variety of programs and hardware architectures. However, for large-scale, critical services where performance is paramount, "good average performance" represents a significant missed opportunity.

The core limitation of fixed optimization sequences stems from the **phase-ordering problem**: determining the optimal sequence of compiler passes to apply to a given program. This problem is known to be NP-hard, meaning the search space of possible optimization sequences is astronomically large and grows exponentially with the number of available passes and the length of the sequence.5 To illustrate, the LLVM

\-O3 optimization level contains approximately 85 distinct optimization options. The number of potential sequences of just 16 distinct options from this set is a staggering 8516\.6 This combinatorial explosion makes any form of exhaustive search computationally infeasible, forcing compiler developers to rely on hand-tuned, general-purpose heuristics.

These heuristics, while effective on average, are by their nature a compromise. They cannot account for the unique characteristics of a specific program or its interaction with a particular hardware environment. Research has consistently shown that tailoring optimization sequences to individual programs can unlock substantial performance gains. Studies have demonstrated that finding the right number and order of passes can improve performance by over 60% compared to the standard \-O3 level.1 For high-throughput services operating at scale, even fractional improvements in latency or resource utilization translate directly into significant operational cost savings, enhanced system capacity, and improved user experience.7 The pursuit of this untapped optimization potential is not merely an academic exercise; it is a strategic imperative for modern performance engineering.

### **Section 2: Reinforcement Learning as the Optimization Paradigm**

To navigate the vast and complex search space of the phase-ordering problem, a more adaptive and intelligent approach is required. Reinforcement Learning (RL) has emerged as a uniquely powerful paradigm for this task.9 The key is to reframe the problem of finding an optimal sequence of compiler passes as a Markov Decision Process (MDP).1 In this formulation:

* **State (S)**: The current state of the program, typically represented by its Intermediate Representation (IR).  
* **Action (A)**: The application of a single compiler transformation, such as a specific optimization pass.  
* **Reward (R)**: A numerical signal indicating the quality of the action, such as the resulting improvement in execution speed or reduction in code size.  
* **Policy (π)**: The RL agent's learned strategy, which maps a given state (IR) to the next action (transformation) to take, with the goal of maximizing the total cumulative reward over time.

RL is particularly well-suited for this problem compared to other machine learning methodologies. Supervised learning, for instance, would require a massive, pre-existing dataset of programs mapped to their "optimal" optimization sequences. Generating such a labeled dataset is computationally prohibitive and begs the question of how one finds the optimal labels in the first place.1 Unsupervised learning methods, while useful for discovering structure, do not inherently optimize for a specific goal like performance maximization.1 In contrast, RL learns through a trial-and-error process of interacting with its environment. It does not require labeled data, instead using the reward signal to iteratively refine its policy, making it an ideal framework for this type of complex planning and optimization problem.1

The adoption of RL for compiler optimization signifies a fundamental paradigm shift. Traditionally, compiler optimization is a static, design-time activity; a new version of a compiler comes with a fixed set of heuristics. An RL-based approach decouples the optimization *strategy* (the agent's policy) from the compiler *infrastructure*. The strategy is no longer a static artifact but a dynamic model that can be continuously retrained and improved. When this is further connected to live performance data, it creates a closed-loop system where the real-world behavior of a service directly informs the next iteration of the compiler's optimization policy. This transforms the compiler from a passive tool in a CI/CD pipeline into an active, learning component of the production ecosystem itself. Consequently, "compiler tuning" evolves from a flag set during a build into an automated, online function managed by performance and reliability engineering teams.

## **Part II: Architectural Blueprint for an RL-Powered Build System**

### **Section 3: The Compiler as an RL Environment: Core Components**

To apply reinforcement learning, the compiler toolchain must be exposed as an interactive environment with which an agent can engage. This requires careful design of three core components: the state representation, the action space, and the reward function.

#### **State Representation (The "Observation")**

The agent's policy is a function of its observation of the environment's state. The richness and fidelity of this state representation are critical to the agent's ability to learn an effective policy. Several techniques have been developed:

* **Hand-crafted Feature Vectors**: Early and straightforward approaches represent the program state using a fixed-size vector of static features. A prominent example is the Autophase observation space within the CompilerGym framework, which provides a 56-dimensional vector of program characteristics.11 While simple and fast to compute, these vectors may not capture the full semantic complexity of the code.  
* **IR Embeddings**: A more powerful technique involves learning a dense vector representation (an embedding) of the program's Intermediate Representation (IR). Frameworks like IR2Vec generate these embeddings in an unsupervised manner, capturing intrinsic program characteristics and semantic similarities.13 This allows the agent to reason about code structure in a way that is analogous to how a human expert might recognize patterns.  
* **End-to-End Learned Embeddings**: The most sophisticated approaches learn the state representation and the policy end-to-end. The NeuroVectorizer framework, for example, uses an Abstract Syntax Tree (AST) embedding generator that is trained jointly with the RL agent. This process optimizes the representation specifically for the task of predicting optimal vectorization factors, ensuring the learned features are maximally relevant.14  
* **State Augmentation**: The state can be further enriched by including a history of the actions taken so far. Because the effect of a compiler pass can depend on which passes preceded it, the IR alone may not be a sufficient statistic. Augmenting the state with the action history helps address this non-Markovian property and provides the agent with more context for its decisions.3

#### **Action Space Design (The "Transformations")**

The action space defines the set of optimizations the agent can apply. Its design directly impacts the complexity and effectiveness of the learning problem.

* **Discrete Action Space**: The simplest model defines a discrete set of actions, where each action corresponds to a specific compiler pass (e.g., \-loop-unroll, \-dce). This is a common approach in environments built on top of LLVM.11  
* **Parameterized and Hierarchical Action Spaces**: Many optimizations are not simple on/off choices but require parameters (e.g., the unroll factor for a loop, or the tile sizes for tiling). To manage this complexity, a hierarchical or multi-action space is highly effective. In this model, the agent first selects a transformation (e.g., "Tiling") and then, in a subsequent step, selects the parameters for that transformation (e.g., a vector of tile sizes). This approach, pioneered in recent MLIR-based environments, decomposes a massive, flat action space into a series of smaller, more manageable decisions, which greatly improves learning efficiency.7  
* **Action Masking**: To make exploration more efficient, it is crucial to prevent the agent from selecting invalid actions. An action mask dynamically constrains the available actions at each step based on the current program state. For example, the im2col transformation is only applicable to convolution operations, and a parallelization pass might only be valid to apply once per schedule.7 Action masking guides the agent toward valid and potentially fruitful optimization sequences.

### **Section 4: Integrating with Modern Compiler Toolchains: LLVM and MLIR**

The RL environment must be deeply integrated with a compiler infrastructure to apply transformations and observe their effects. Two prominent infrastructures for this are LLVM and MLIR.

#### **LLVM-based Integration**

Google's MLGO (Machine Learning Guided Optimizations) framework serves as a prime case study for integrating ML into a mature, industrial compiler like LLVM.8 The MLGO approach is "surgical," replacing specific, hard-coded compiler heuristics—such as those for function inlining or register allocation—with a learned RL policy. The training process is online: during compilation, the compiler queries the ML model for a decision (e.g., to inline a function or not). After compilation, a log of the decisions and the final outcome (e.g., code size reduction) is used to calculate a reward and update the policy via policy gradient methods.8 This demonstrates how RL can be retrofitted into an existing compiler to incrementally improve its decision-making logic.

#### **The MLIR Advantage**

For a new initiative, the Multi-Level Intermediate Representation (MLIR) framework offers a more powerful and flexible foundation.23 MLIR's design philosophy is centered on modularity and extensibility through a system of "dialects." A dialect is a custom, domain-specific IR with its own operations and types, which can be defined by compiler engineers.23 This structure is exceptionally well-suited for RL-based optimization. One can define a high-level "optimization dialect" where the RL agent operates, which is then progressively lowered through other dialects to hardware-specific code. This provides a clean, structured mechanism for defining state and action spaces at multiple levels of abstraction.

Recent research has successfully demonstrated the power of this approach by building the first RL environments specifically for MLIR, targeting the optimization of machine learning workloads.7 These studies show that an RL agent operating on MLIR can discover optimization schedules for critical operations that are comparable to, or in some cases even surpass, those found by highly-tuned, specialized frameworks like TensorFlow.18

### **Section 5: Frameworks for Implementation: CompilerGym and Ray RLlib**

Building an RL-driven compiler from scratch is a monumental task. Fortunately, a mature ecosystem of tools can significantly accelerate development.

#### **CompilerGym: The Environment Wrapper**

CompilerGym is a toolkit designed specifically to bridge the gap between compiler research and machine learning research. It exposes complex compiler optimization tasks as standardized OpenAI Gym environments.11 The key value of CompilerGym is abstraction. It utilizes a client-server architecture where a Python frontend (the

env object) communicates with a backend service that wraps the actual compiler.25 This allows engineers and researchers to focus on developing RL agents in Python using a familiar API (

env.make(), env.step(), env.reset()) without needing to become experts in the low-level internals of the compiler.11 The framework is also extensible, providing clear interfaces for creating custom environments for new compilers or optimization tasks.27

#### **Ray RLlib: The Scalable Training Engine**

Training an RL agent for compiler optimization is a computationally intensive process that requires high sample efficiency. Ray RLlib is an industry-grade, open-source library that provides scalable and fault-tolerant implementations of state-of-the-art RL algorithms, such as Proximal Policy Optimization (PPO), which is a common and robust choice for these tasks.29 RLlib's architecture is designed for distributed computing, allowing the workload of data collection (simulating environment steps) and model training to be parallelized across a cluster of machines using its

EnvRunner and Learner abstractions.31 This scalability is essential for tackling the high sample complexity inherent in learning effective compiler optimization policies.

The combination of these tools forms a powerful and modular architectural pattern. MLIR provides the flexible, multi-level compiler *backend* where transformations are defined and applied. CompilerGym serves as the standardized *interface* or "middleware," abstracting the backend into a Pythonic Gym environment. Finally, RLlib provides the scalable *frontend* or training framework where the agent's logic is implemented and its policy is learned. This layered architecture creates a crucial separation of concerns, enabling compiler and systems engineers to focus on the backend infrastructure while ML engineers focus on agent design and training, fostering parallel development and leveraging specialized expertise.

## **Part III: The Reward Signal: Guiding the Agent to Optimal Performance**

The design of the reward function is the most critical aspect of the RL system, as it directly defines the agent's goal. The choice of reward structure involves a fundamental trade-off between the speed of feedback and its alignment with the true performance objective.

### **Section 6: The Reward Dilemma: Immediate vs. Final Feedback**

Two primary reward structures have been explored in the literature, each with distinct advantages and disadvantages.7

#### **Immediate Reward**

* **Definition**: With an immediate reward structure, the agent receives a reward signal after *every single action* it takes.  
* **Source**: This reward is typically based on a fast-to-compute proxy metric that is available statically, without executing the program. A common choice is the change in the number of LLVM IR instructions; a reduction in instructions yields a positive reward.11  
* **Pros**: This approach provides dense, frequent feedback to the agent. This simplifies the **credit assignment problem**—determining which actions were responsible for a good outcome—and can significantly accelerate the initial learning process.  
* **Cons**: The primary risk is that the proxy metric may not correlate perfectly with the true objective, which is typically execution time. For example, optimizing for the smallest instruction count can sometimes harm performance by negatively impacting the instruction cache or other microarchitectural features. This can lead the agent to converge on a policy that is a local optimum with respect to the proxy but is suboptimal for real-world performance.3 Furthermore, if the immediate reward requires recompilation and execution after each step, it can become extremely time-consuming.7

#### **Final Reward**

* **Definition**: With a final reward structure, the agent receives a single, cumulative reward only at the *end of a full optimization sequence* (an episode).  
* **Source**: The reward is based on the measured performance of the fully compiled binary. This is typically the execution time on a benchmark workload, measured in a controlled staging environment.  
* **Pros**: The reward signal is perfectly aligned with the ultimate performance goal. There is no risk of the agent "gaming" a misleading proxy. This approach is also more efficient in terms of wall-clock time per episode, as it requires only one full compilation and benchmark run at the end.7  
* **Cons**: This is a classic **sparse reward** problem. The agent may take dozens of actions before receiving any feedback, which makes credit assignment extremely difficult. The agent must infer which of its many actions in a sequence were beneficial and which were detrimental. This sparsity dramatically increases the sample complexity of the problem, often requiring millions of trials and making the learning process slow and potentially unstable.32

The following table summarizes the trade-offs between these reward structures.

**Table 1: Comparison of Reward Function Structures**

| Characteristic | Immediate Reward (Static Proxy) | Final Reward (Staging Benchmark) | Final Reward (Production SLI) |
| :---- | :---- | :---- | :---- |
| **Feedback Latency** | Instantaneous (per step) | Medium (minutes, per episode) | High (hours/days, per deployment) |
| **Computational Cost** | Low per step (static analysis) | High per episode (compile \+ run) | Very high (requires production deployment) |
| **Signal-to-Noise Ratio** | High (deterministic proxy) | Medium (staging noise) | Low (production variability) |
| **Credit Assignment** | Easy (direct feedback) | Very Difficult (sparse signal) | Extremely Difficult (sparse, delayed signal) |
| **Alignment with Objective** | Partial (proxy metric) | High (benchmark performance) | Perfect (user-facing performance) |
| **Implementation Complexity** | Low | Medium | High |

### **Section 7: The Production Feedback Loop: From SLIs to Dynamic Rewards**

The ultimate goal is to create a system that learns not from proxy metrics or staging benchmarks, but from the actual performance of the code as it runs in the production environment. This creates a powerful feedback loop that aligns compiler optimization directly with business and operational objectives.

#### **Step 1: Defining the Service Level Indicator (SLI)**

Following Google's Site Reliability Engineering (SRE) principles, the first step is to define a quantitative measure of service performance that truly reflects the user experience.33 For a latency-sensitive critical service, an excellent SLI is the

**p95 or p99 request latency**. This metric captures the tail-end of the latency distribution, which is often what users perceive as "slowness." This data should be collected from the observability platform, ideally from the client's perspective or from a load balancer as a close proxy.33

#### **Step 2: Designing the Reward Function from the SLI**

Production latency data is inherently noisy and delayed, so it cannot be used as a raw reward signal. The reward function must be carefully designed to extract a meaningful signal from this data.

* **Reward Formulation**: The reward should represent the *change* in the SLI that is attributable to a new compilation policy. A robust formulation can be derived by comparing the measured SLI against the target Service Level Objective (SLO). For example: Reward=log(SLOtarget​/SLImeasured​).3 This function yields a positive reward when the service meets or exceeds its SLO, a negative reward when it violates the SLO, and a reward of zero when it is exactly at the target. This directly connects the agent's optimization goal to the operational health of the service.  
* **Handling Noise**: Production latency is influenced by numerous confounding factors beyond compiler optimizations (e.g., traffic patterns, network conditions, downstream dependencies). To isolate the impact of the compiler, a canary deployment or A/B testing methodology is essential. A new compiler policy is used to build a binary that is deployed to a small subset of the production fleet (the canary). Its SLI is then compared against the SLI of the baseline fleet over the same time window. The reward is calculated based on this *relative improvement*, which effectively normalizes for global environmental factors.  
* **The Delayed Reward Problem**: Feedback from production is not immediate; it can take hours or even days to collect enough data to achieve a statistically significant measurement of the SLI. This transforms the problem into one of **offline RL** or **batch RL**.34 The agent is not updated in real-time. Instead, trajectories of  
  (state, action\_sequence, reward) are collected over time and used to update the policy in batches.

#### **Step 3: Architectural Pattern for the Feedback Loop**

The full production feedback loop can be implemented as a multi-stage, semi-online process:

1. **Agent Training (Offline)**: The RL agent is first trained in a lab environment using a combination of immediate static rewards and final rewards from a staging benchmark. This develops a robust baseline policy.  
2. **Policy Deployment**: A new candidate policy (a promising optimization sequence) is used to compile a binary, which is then deployed to a canary instance or cluster in production.  
3. **Data Collection**: The observability platform monitors and collects high-fidelity latency data (the SLI) for both the canary and baseline groups.  
4. **Reward Calculation**: An offline "Reward Engine" service periodically queries the observability platform's API. It computes the relative performance difference between the canary and baseline, calculates the final reward for the optimization sequence, and stores it.  
5. **Policy Update**: This new, complete data point is added to a persistent replay buffer. The RL agent's policy is then updated using an offline RL algorithm that trains on the entire buffer of production-validated experiences. The newly updated policy is then used to generate the next candidate for canary deployment, closing the loop.

This architecture fundamentally shifts the optimization target. A staging benchmark optimizes for "program performance" on a synthetic workload.7 A production SLI, however, is a direct measure of "service health" and user satisfaction.33 By using the SLI as the reward signal, the RL agent is forced to optimize for the

*impact of the code on the entire system*. For example, an optimization that improves average-case latency but significantly degrades tail latency would be penalized by a p95 latency SLI, whereas a simple execution-time benchmark might have rewarded it. This approach aligns the automated compiler optimization process directly with the core principles of SRE. The SRE concept of an **error budget** could even be used to manage the agent's exploration/exploitation trade-off: the agent is permitted to "spend" the error budget by trying more aggressive, potentially risky optimizations. If the budget is consumed, it must revert to a more conservative, known-stable policy.33

## **Part IV: From Theory to Practice: A Phased Implementation Roadmap**

This section outlines a practical, three-phase implementation plan designed to build capabilities incrementally and deliver value at each stage, directly addressing the project's acceptance criteria.

### **Section 8: Phase 1 \- Benchmark Optimization**

**Objective**: To build a baseline RL environment and demonstrate a measurable performance gain over default compiler settings for a single, representative benchmark application. This addresses the first two acceptance criteria.

**Steps**:

1. **Select Benchmark**: Identify a critical, self-contained, and computationally intensive service or library from the existing codebase. It must have a reliable and repeatable performance test.  
2. **Setup RL Environment**: Use the CompilerGym toolkit to create a custom CompilerEnv that wraps the project's build system. The env.step(action) method will be implemented to invoke the compiler with a specific optimization flag or pass.25  
3. **Define Initial Components**: To begin, use the simplest, most readily available components.  
   * **State**: Use a pre-packaged observation space from CompilerGym, such as Autophase or InstCount, which provides a simple feature vector representation of the code.24  
   * **Action**: Define a discrete action space consisting of the most common and impactful LLVM optimization passes.  
   * **Reward**: Employ an immediate reward signal based on the change in IrInstructionCount, which is provided out-of-the-box by CompilerGym and serves as an excellent starting point for validating the environment.11  
4. **Train Agent**: Use a standard RL algorithm from the RLlib library, such as PPO, to train an agent on the environment.31  
5. **Demonstrate Gain**: After training, identify the best optimization sequence discovered by the agent. Compile the benchmark with this sequence and compare its execution time against the binary produced by the default \-O3 optimization level. The goal is to demonstrate a statistically significant performance improvement.

### **Section 9: Phase 2 \- The Staging Environment and Final Rewards**

**Objective**: To evolve the reward mechanism from a static proxy to a more accurate signal based on end-to-end performance measured in a controlled staging environment.

**Steps**:

1. **Establish Staging Environment**: Provision a dedicated and stable staging environment. This environment must include a performance testing harness capable of automatically deploying the compiled benchmark, executing it under a realistic load, and reporting its execution time with low variance.  
2. **Modify RL Environment**: Adapt the reward structure in the custom CompilerEnv from "immediate" to "final." The env.step() function will now return a reward of 0 for all intermediate actions.  
3. **Implement Final Reward Calculation**: When an episode terminates (the done flag is true), the environment will trigger a workflow to: compile the final IR, deploy the binary to the staging environment, execute the performance test, and calculate the speedup relative to the \-O3 baseline. This speedup value will be returned as the single, final reward for the entire sequence.  
4. **Retrain and Evaluate**: Retrain the agent using this new sparse reward signal. This phase will likely require significantly more training samples and longer training times due to the credit assignment challenge. The quality of the optimization sequences discovered in this phase should be compared against those from Phase 1 to quantify the benefit of using a more accurate reward signal.

### **Section 10: Phase 3 \- The Production SLI Feedback Loop**

**Objective**: To create a proof-of-concept for the full feedback loop where a production performance SLI directly influences the reward function, satisfying the final acceptance criterion.

**Steps**:

1. **Infrastructure Setup**:  
   * Implement a canary deployment mechanism (e.g., using feature flags or traffic splitting at the load balancer) that can route a small, controlled percentage of production traffic to a new binary.  
   * Configure the observability platform to segment and report the p95 latency SLI for the canary group and the baseline group independently.  
2. **Build the Reward Pipeline**: Create the offline "Reward Engine" service as described in Section 7\. This service will need API access to the observability platform to query the SLI data for the two groups, compute the relative performance improvement, and store the resulting reward.  
3. Integrate with RL Training: Adapt the training process to an offline/batch model. The system will operate in a continuous cycle:  
   a. Use the agent's current best policy to generate a new optimization sequence and compile a canary binary.  
   b. Deploy the canary to production.  
   c. Wait for a sufficient data collection period (e.g., 24 hours).  
   d. The Reward Engine calculates the final reward based on the collected SLI data.  
   e. This new (state, action\_sequence, reward) data point is added to the replay buffer.  
   f. The agent is retrained on the updated buffer.  
4. **Demonstrate the Loop**: Execute the full cycle for several iterations. The primary goal is to demonstrate that the agent's policy evolves and adapts over time based on the feedback signals originating directly from the production environment.

## **Part V: Advanced Topics and Future Frontiers**

As the system matures beyond the initial proof-of-concept, several advanced challenges and research frontiers will become pertinent.

### **Section 11: Overcoming Key Challenges: Generalization, Reproducibility, and Sample Efficiency**

The practical application of RL to real-world systems presents several well-documented difficulties.32

* **Generalization**: A policy trained to optimize one benchmark or service may not perform well on another. Addressing this requires training on a diverse dataset of representative programs and developing more expressive state representations (e.g., learned IR embeddings) that capture fundamental program structures rather than surface-level features, allowing the model to generalize its knowledge.8  
* **Reproducibility and Stability**: RL algorithms can be notoriously sensitive to hyperparameters and random seeds, leading to instability and difficulty in reproducing results.32 Mitigating this requires a disciplined approach, including rigorous experiment tracking, versioning of code and data, using fixed random seeds, and relying on stable, well-maintained algorithm implementations like those in RLlib.  
* **Sample Efficiency**: The primary bottleneck in RL is the vast number of environment interactions (samples) required for learning. Each sample in this context can be expensive, involving a full compile-and-run cycle. Techniques to improve efficiency include using offline RL to learn from pre-existing data, developing surrogate models to predict performance without running the code, and bootstrapping the learning process with knowledge from other sources, such as Large Language Models.

### **Section 12: The Role of Large Language Models (LLMs) in the Loop**

A promising state-of-the-art technique for addressing the sample efficiency problem involves integrating Large Language Models (LLMs) into the training loop. RL agents typically begin learning by exploring the action space randomly, a "slow start" phase that is highly inefficient and can be a major barrier to practical application.6

The DeCOS system pioneers a hybrid architecture to solve this.6 In this model, an LLM (such as GPT-4) acts as a "predictor" or a learned heuristic. During the initial, inefficient exploration phase, the LLM is prompted with the source code of the program to be optimized and asked to suggest a promising set of initial optimizations. This leverages the LLM's vast, pre-trained knowledge of code and programming patterns to provide a strong "prior" or initial guess. The RL agent then takes over, using this suggestion as a starting point for its own fine-grained, environment-specific tuning through trial-and-error. This hybrid approach dramatically accelerates learning by focusing the agent's exploration on high-potential regions of the vast search space, making the entire process more practical and efficient.6

The following table provides a comparative overview of key projects in the field, contextualizing the proposed work within the broader research landscape.

**Table 2: Overview of RL-for-Compiler Frameworks and Projects**

| Project/Framework | Target Compiler | Key Innovation | State Representation | Action Space Type | Typical Reward Signal |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **MLGO** 8 | LLVM | Industrial-grade integration replacing specific heuristics (inlining, regalloc). | Hand-crafted features from call graph/live ranges. | Discrete (e.g., inline/no-inline). | Code size reduction, performance improvement (QPS). |
| **CompilerGym** 11 | LLVM (extensible) | Standardized Gym interface for compiler tasks; client-server architecture. | Pluggable (feature vectors, IR, graphs). | Discrete (pass selection). | Pluggable (instruction count, code size, runtime). |
| **MLIR-RL Env** 7 | MLIR | First RL environment for MLIR; hierarchical action space for parameters. | Feature vector from MLIR operations (loop info, etc.). | Hierarchical (transformation \+ parameters). | Logarithmic speedup (immediate or final). |
| **DeCOS** 6 | LLVM | Data-efficient RL; uses LLM to bootstrap initial exploration. | Augmented code representation with performance counters. | Discrete (optimization options). | Performance of optimized binary. |

## **Conclusion**

The pursuit of automated, adaptive compiler optimization via Reinforcement Learning represents a strategic evolution from static, heuristic-based approaches to a dynamic, data-driven performance engineering discipline. By modeling the compiler phase-ordering problem as a Markov Decision Process, an RL agent can learn workload- and hardware-specific optimization policies that significantly outperform generic, one-size-fits-all heuristics. The architectural blueprint outlined in this report, leveraging the modularity of MLIR, the abstraction of CompilerGym, and the scalability of RLlib, provides a robust foundation for building such a system.

The core of this endeavor lies in the careful design of the reward signal. While immediate, static rewards offer a tractable starting point, the true potential is unlocked by aligning the agent's objective with end-to-end performance, first in a staging environment and ultimately with live production SLIs. A phased implementation, beginning with benchmark optimization and progressively incorporating more sophisticated, production-aware feedback, offers a practical pathway to realizing this vision. This culminates in a closed-loop system where the compiler becomes an intelligent, self-tuning component of the production ecosystem, continuously learning and adapting to optimize not just code, but the health and efficiency of the services it supports. By embracing this paradigm, organizations can unlock new levels of performance and operational efficiency, turning the compiler into a key asset for automated performance engineering in the modern cloud-native landscape.

#### **Works cited**

1. Reinforcement Learning Strategies for Compiler Optimization in High level Synthesis \- Boston University, accessed on July 9, 2025, [https://www.bu.edu/caadlab/Shahzad22.pdf](https://www.bu.edu/caadlab/Shahzad22.pdf)  
2. Reinforcement Learning Strategies for Compiler Optimization in High level Synthesis, accessed on July 9, 2025, [https://www.researchgate.net/publication/367563619\_Reinforcement\_Learning\_Strategies\_for\_Compiler\_Optimization\_in\_High\_level\_Synthesis](https://www.researchgate.net/publication/367563619_Reinforcement_Learning_Strategies_for_Compiler_Optimization_in_High_level_Synthesis)  
3. Static Neural Compiler Optimization via Deep Reinforcement ... \- arXiv, accessed on July 9, 2025, [https://arxiv.org/pdf/2008.08951](https://arxiv.org/pdf/2008.08951)  
4. POSET-RL: Phase ordering for Optimizing Size and Execution Time using Reinforcement Learning \- arXiv, accessed on July 9, 2025, [https://arxiv.org/pdf/2208.04238](https://arxiv.org/pdf/2208.04238)  
5. CS294-112 & CS262A Project Report AUTOPHASING: Learning to Optimize Compiler Passes with Deep Reinforcement Learning \- People @EECS, accessed on July 9, 2025, [https://people.eecs.berkeley.edu/\~kubitron/courses/cs262a-F18/projects/reports/project2\_report\_ver3.pdf](https://people.eecs.berkeley.edu/~kubitron/courses/cs262a-F18/projects/reports/project2_report_ver3.pdf)  
6. DeCOS: Data-Efficient Reinforcement Learning for ... \- GitHub Pages, accessed on July 9, 2025, [https://hpcrl.github.io/ICS2025-webpage/program/Proceedings\_ICS25/ics25-26.pdf](https://hpcrl.github.io/ICS2025-webpage/program/Proceedings_ICS25/ics25-26.pdf)  
7. A Reinforcement Learning Environment for Automatic Code Optimization in the MLIR Compiler \- arXiv, accessed on July 9, 2025, [https://arxiv.org/html/2409.11068v1](https://arxiv.org/html/2409.11068v1)  
8. MLGO: A Machine Learning Framework for Compiler Optimization, accessed on July 9, 2025, [https://research.google/blog/mlgo-a-machine-learning-framework-for-compiler-optimization/](https://research.google/blog/mlgo-a-machine-learning-framework-for-compiler-optimization/)  
9. Enhancing Code LLMs with Reinforcement Learning in Code Generation: A Survey \- Qeios, accessed on July 9, 2025, [https://www.qeios.com/read/8G8TB2](https://www.qeios.com/read/8G8TB2)  
10. Mitigating the Compiler Optimization Phase-Ordering Problem using Machine Learning \- University of Delaware, accessed on July 9, 2025, [https://www.eecis.udel.edu/\~cavazos/oopsla-2012.pdf](https://www.eecis.udel.edu/~cavazos/oopsla-2012.pdf)  
11. facebookresearch/CompilerGym: Reinforcement learning environments for compiler and program optimization tasks \- GitHub, accessed on July 9, 2025, [https://github.com/facebookresearch/CompilerGym](https://github.com/facebookresearch/CompilerGym)  
12. CompilerGym Getting Started.ipynb \- Colab, accessed on July 9, 2025, [https://colab.research.google.com/github/facebookresearch/CompilerGym/blob/stable/examples/getting-started.ipynb](https://colab.research.google.com/github/facebookresearch/CompilerGym/blob/stable/examples/getting-started.ipynb)  
13. IITH-Compilers/ml-llvm-project \- GitHub, accessed on July 9, 2025, [https://github.com/IITH-Compilers/ml-llvm-project](https://github.com/IITH-Compilers/ml-llvm-project)  
14. intel/neuro-vectorizer: NeuroVectorizer is a framework that uses deep reinforcement learning (RL) to predict optimal vectorization compiler pragmas for for loops in C and C++ codes. \- GitHub, accessed on July 9, 2025, [https://github.com/intel/neuro-vectorizer](https://github.com/intel/neuro-vectorizer)  
15. Learning to Vectorize Using Deep Reinforcement Learning \- ML For Systems, accessed on July 9, 2025, [https://mlforsystems.org/assets/papers/neurips2019/vectorize\_haj\_ali.pdf](https://mlforsystems.org/assets/papers/neurips2019/vectorize_haj_ali.pdf)  
16. NeuroVectorizer: End-to-End Vectorization with Deep Reinforcement Learning \- People @EECS, accessed on July 9, 2025, [https://people.eecs.berkeley.edu/\~ysshao/assets/papers/hajali2020-cgo.pdf](https://people.eecs.berkeley.edu/~ysshao/assets/papers/hajali2020-cgo.pdf)  
17. NeuroVectorizer: End-to-End Vectorization with ... \- People @EECS, accessed on July 9, 2025, [https://people.eecs.berkeley.edu/\~krste/papers/neurovectorizer-cgo2020.pdf](https://people.eecs.berkeley.edu/~krste/papers/neurovectorizer-cgo2020.pdf)  
18. A Reinforcement Learning Environment for Automatic Code Optimization in the MLIR Compiler \- Bohrium, accessed on July 9, 2025, [https://www.bohrium.com/paper-details/a-reinforcement-learning-environment-for-automatic-code-optimization-in-the-mlir-compiler/1043407541809184784-108614](https://www.bohrium.com/paper-details/a-reinforcement-learning-environment-for-automatic-code-optimization-in-the-mlir-compiler/1043407541809184784-108614)  
19. \[Papierüberprüfung\] A Reinforcement Learning Environment for Automatic Code Optimization in the MLIR Compiler \- Moonlight | AI Colleague for Research Papers, accessed on July 9, 2025, [https://www.themoonlight.io/de/review/a-reinforcement-learning-environment-for-automatic-code-optimization-in-the-mlir-compiler](https://www.themoonlight.io/de/review/a-reinforcement-learning-environment-for-automatic-code-optimization-in-the-mlir-compiler)  
20. (PDF) A Reinforcement Learning Environment for Automatic Code Optimization in the MLIR Compiler \- ResearchGate, accessed on July 9, 2025, [https://www.researchgate.net/publication/384085729\_A\_Reinforcement\_Learning\_Environment\_for\_Automatic\_Code\_Optimization\_in\_the\_MLIR\_Compiler](https://www.researchgate.net/publication/384085729_A_Reinforcement_Learning_Environment_for_Automatic_Code_Optimization_in_the_MLIR_Compiler)  
21. (PDF) Automatic Code Optimization in the MLIR Compiler Using Deep Reinforcement Learning \- ResearchGate, accessed on July 9, 2025, [https://www.researchgate.net/publication/382047058\_Automatic\_Code\_Optimization\_in\_the\_MLIR\_Compiler\_Using\_Deep\_Reinforcement\_Learning](https://www.researchgate.net/publication/382047058_Automatic_Code_Optimization_in_the_MLIR_Compiler_Using_Deep_Reinforcement_Learning)  
22. Machine Learning Guided Optimizations (MLGO) in LLVM, accessed on July 9, 2025, [https://llvm.org/devmtg/2022-11/slides/Panel1-MLGO.pdf](https://llvm.org/devmtg/2022-11/slides/Panel1-MLGO.pdf)  
23. What about the MLIR compiler infrastructure? (Democratizing AI Compute, Part 8\) \- Modular, accessed on July 9, 2025, [https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure](https://www.modular.com/blog/democratizing-ai-compute-part-8-what-about-the-mlir-compiler-infrastructure)  
24. Getting Started — CompilerGym 0.2.5 documentation, accessed on July 9, 2025, [https://compilergym.com/getting\_started.html](https://compilergym.com/getting_started.html)  
25. CompilerGym: Robust, Performant Compiler Optimization ... \- arXiv, accessed on July 9, 2025, [https://arxiv.org/pdf/2109.08267](https://arxiv.org/pdf/2109.08267)  
26. Hands-On to CompilerGym: A Reinforcement Learning Toolkit for Compiler Optimizations, accessed on July 9, 2025, [https://analyticsindiamag.com/deep-tech/hands-on-to-compilergym-a-reinforcement-learning-toolkit-for-compiler-optimizations/](https://analyticsindiamag.com/deep-tech/hands-on-to-compilergym-a-reinforcement-learning-toolkit-for-compiler-optimizations/)  
27. compiler\_gym.service — CompilerGym 0.2.5 documentation, accessed on July 9, 2025, [https://compilergym.com/compiler\_gym/service.html](https://compilergym.com/compiler_gym/service.html)  
28. Create a gymnasium custom environment (Part 1\) | by Yuki Minai \- Medium, accessed on July 9, 2025, [https://medium.com/@ym1942/create-a-gymnasium-custom-environment-part-1-04ccc280eea9](https://medium.com/@ym1942/create-a-gymnasium-custom-environment-part-1-04ccc280eea9)  
29. Survey on usage of reinforcement learning for compiler optimizations \- YouTube, accessed on July 9, 2025, [https://www.youtube.com/watch?v=zDJo2R4Ck8s](https://www.youtube.com/watch?v=zDJo2R4Ck8s)  
30. Optimizing Assembly Code with LLMs: Reinforcement Learning Outperforms Traditional Compilers : r/machinelearningnews \- Reddit, accessed on July 9, 2025, [https://www.reddit.com/r/machinelearningnews/comments/1kukjwe/optimizing\_assembly\_code\_with\_llms\_reinforcement/](https://www.reddit.com/r/machinelearningnews/comments/1kukjwe/optimizing_assembly_code_with_llms_reinforcement/)  
31. RLlib: Industry-Grade, Scalable Reinforcement Learning \- Ray Docs, accessed on July 9, 2025, [https://docs.ray.io/en/latest/rllib/index.html](https://docs.ray.io/en/latest/rllib/index.html)  
32. Machine Learning in Compiler Optimization \- UC Berkeley EECS, accessed on July 9, 2025, [https://www2.eecs.berkeley.edu/Pubs/TechRpts/2021/EECS-2021-2.pdf](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2021/EECS-2021-2.pdf)  
33. Defining slo: service level objective meaning \- Google SRE, accessed on July 9, 2025, [https://sre.google/sre-book/service-level-objectives/](https://sre.google/sre-book/service-level-objectives/)  
34. Reinforcement Learning AI Course | Stanford Online, accessed on July 9, 2025, [https://online.stanford.edu/courses/xcs234-reinforcement-learning](https://online.stanford.edu/courses/xcs234-reinforcement-learning)  
35. \[D\] What is your honest experience with reinforcement learning? : r/MachineLearning, accessed on July 9, 2025, [https://www.reddit.com/r/MachineLearning/comments/197jp2b/d\_what\_is\_your\_honest\_experience\_with/](https://www.reddit.com/r/MachineLearning/comments/197jp2b/d_what_is_your_honest_experience_with/)