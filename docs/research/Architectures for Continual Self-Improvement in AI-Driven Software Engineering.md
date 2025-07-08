

# **Architectures for Continual Self-Improvement in AI-Driven Software Engineering**

## **Part 1: Foundational Paradigms for Autonomous Code Generation**

The development of an AI agent capable of continuous self-improvement in the domain of software engineering requires a robust foundation in advanced machine learning paradigms. The agent's ability to learn, adapt, and enhance its own code-generation capabilities hinges on the selection and integration of appropriate learning algorithms. This section provides a comprehensive analysis of three foundational approaches: gradient-based policy optimization, gradient-free evolutionary strategies, and performance bootstrapping through self-play and curriculum learning. Each paradigm offers a distinct set of advantages and trade-offs, and their synthesis forms the basis of a powerful, autonomous learning loop.

### **Section 1.1: Gradient-Based Policy Optimization for Code Synthesis**

Gradient-based reinforcement learning (RL), particularly policy optimization methods, has become the predominant approach for fine-tuning Large Language Models (LLMs) to align with complex, preference-based objectives. For code generation, these techniques allow an agent to move beyond simple next-token prediction and learn from the functional outcomes of its generated programs. This section details the evolution of these methods, from the stable and widely adopted Proximal Policy Optimization (PPO) to more recent, highly efficient variants designed to overcome the computational bottlenecks associated with training massive models on long-form generation tasks.

#### **1.1.1 The PPO Baseline**

Proximal Policy Optimization (PPO) is a family of policy gradient methods for reinforcement learning that has demonstrated strong performance and stability across a wide range of tasks, including sequence generation.1 Its core innovation is a "clipped surrogate objective" function, which constrains the size of policy updates at each training step. This clipping mechanism prevents the agent's policy from moving too far from the previous policy in a single update, which mitigates the risk of a catastrophic performance collapse that can occur with standard policy gradient methods. This inherent stability has made PPO a foundational algorithm for Reinforcement Learning from Human Feedback (RLHF) and its automated variants, providing a reliable baseline for fine-tuning code-generating agents.

#### **1.1.2 Efficiency Enhancements: Truncated PPO (T-PPO)**

A significant practical challenge when applying PPO to code generation is its on-policy nature, which typically requires generating a complete program (a full "rollout") before an update can be calculated. For complex coding tasks, these rollouts can be very long, leading to substantial idle time for computational resources and low hardware utilization.2 This inefficiency exacerbates training time and cost, especially with large-scale models.

Truncated Proximal Policy Optimization (T-PPO) is a novel extension designed to address this specific bottleneck. Research indicates that T-PPO can improve the training efficiency of reasoning-intensive LLMs by up to 2.5 times.2 It achieves this through two primary contributions:

1. **Extended Generalized Advantage Estimation (EGAE):** T-PPO introduces EGAE, a method for performing advantage estimation on *incomplete* responses. This allows the learning algorithm to calculate policy updates without waiting for the full code generation to complete, dramatically shortening the feedback loop.  
2. **Decoupled Optimization:** It devises a computationally optimized mechanism for the independent optimization of the policy and value models. By selectively filtering prompt and truncated tokens from the computation, this mechanism reduces redundant calculations and accelerates the training process without compromising the convergence properties of the underlying PPO algorithm.2

For the AI-SWA project, where the agent will be generating potentially long and complex code blocks, the efficiency gains offered by T-PPO make it a compelling alternative to the standard PPO implementation.

#### **1.1.3 Critic-Free Optimization: Group Relative Policy Optimization (GRPO)**

The progression from PPO to more efficient algorithms is a direct consequence of the scaling challenges posed by modern LLMs. In a typical PPO setup, two large neural networks must be held in memory and trained: the policy model (the actor) and the value model (the critic).3 The critic's role is to estimate the expected future reward, which is used to calculate the advantage of taking certain actions. For state-of-the-art LLMs, the critic model is often of a comparable size to the actor model, effectively doubling the memory and compute requirements for training.4 This overhead represents a significant architectural bottleneck.

Group Relative Policy Optimization (GRPO) is a recent and powerful RL technique that elegantly circumvents this issue by eliminating the need for a separate critic network.3 Its mechanism is rooted in relative performance evaluation within a batch of generated samples. For a single prompt, the model generates multiple candidate responses. A reward function then scores each response. Instead of comparing each score to a learned value estimate from a critic, GRPO calculates the advantage of each response relative to the average performance of its peers in the same group (i.e., the other responses to the same prompt).3

This approach offers several advantages for code generation:

* **Resource Efficiency:** By dropping the value model, GRPO significantly reduces the memory footprint and computational complexity of the training loop, making it more feasible to fine-tune very large models.3  
* **Suitability for Code:** GRPO is particularly well-suited for tasks where multiple, syntactically different solutions can be logically correct.6 By rewarding outputs that outperform the group average, it encourages exploration of diverse but effective coding strategies.  
* **Simplified Data Requirements:** GRPO does not require pre-existing labeled preference data. It only needs a "verification oracle"—an automated way to score responses—which can be a compiler, a linter, a set of unit tests, or a static analyzer.7 This aligns perfectly with the software development domain.

GRPO has been successfully applied to train models for complex reasoning tasks, including generating code for underrepresented languages like Prolog by integrating feedback directly from a Prolog interpreter.5 This demonstrated ability to learn from execution-based rewards makes GRPO a leading candidate for the AI-SWA self-improvement architecture.

#### **1.1.4 Iterative Reward Model Refinement: The RewardRanker Method**

While algorithms like PPO and GRPO focus on optimizing the policy (the code generator), a parallel line of research recognizes that the quality of the learning process is fundamentally limited by the quality of the reward signal itself. If the reward model is flawed—for instance, if it fails to distinguish between truly robust code and brittle code that merely passes a few simple tests—the policy learned will also be flawed. This has led to a meta-learning trend where the focus of optimization shifts from the policy alone to the learning signal itself.

The RewardRanker method exemplifies this approach. It is a novel iterative self-training framework designed to produce a more robust *reward/reranking model*.8 Instead of treating the reward model as a static component, RewardRanker continually refines it through a self-improvement loop.8 The iterative workflow proceeds as follows 8:

1. **Supervised Fine-Tuning (SFT):** A base generator model is fine-tuned on a dataset of code to adapt it to the target domain.  
2. **Reward Model Training:** The initial RewardRanker model is trained to score generated code, learning to prefer correct solutions over incorrect ones.  
3. **PPO-based Generation:** A PPO-trained policy uses the current RewardRanker to generate new candidate code solutions.  
4. **Evaluation and Hard Negative Mining:** The newly generated solutions are evaluated against ground-truth test cases. The crucial step is the identification of **hard negatives**: solutions that are functionally *incorrect* but receive a *high score* from the current reward model. These samples represent the blind spots of the reward model.  
5. **Dataset Augmentation and Retraining:** These hard negatives are added to the training set for the reward model. The reward model is then retrained on this augmented dataset, forcing it to learn to correctly identify these previously-missed failure modes.  
6. **Iteration:** A new PPO model is trained from scratch with the improved reward model, and the cycle repeats.

This process creates a virtuous cycle where the generator and the reward model co-evolve. The generator produces increasingly sophisticated code, which in turn exposes more subtle flaws in the reward model, whose subsequent improvement provides a better learning signal for the next generation of the policy. This method has proven highly effective, with a 13.4B parameter model using RewardRanker outperforming a 33B model in code generation quality.9 This suggests a powerful hybrid strategy for AI-SWA: using an efficient policy optimizer like GRPO within a RewardRanker-style outer loop to continually improve both the agent's coding ability and its understanding of what constitutes high-quality code.

**Table 1: Comparative Analysis of Policy Optimization Algorithms**

| Algorithm | Core Mechanism | Value/Critic Function | Key Advantage | Key Disadvantage | Best Suited For (AI-SWA Context) |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **PPO** | Clipped surrogate objective to constrain policy updates. | Required | High stability and reliability; well-understood baseline. | High memory/compute overhead with large models; inefficient for long sequences. | Initial baseline development and smaller-scale experiments. |
| **T-PPO** | Advantage estimation on incomplete sequences (EGAE) and decoupled optimization. | Required | Up to 2.5x training speedup for long-form generation tasks like code. | Still requires a critic model; adds implementation complexity over standard PPO. | Scenarios where the agent generates long, complex code blocks and training time is a major constraint. |
| **GRPO** | Advantage calculated relative to the mean reward of a group of peer responses. | Not Required | Drastically reduced memory/compute overhead; simplifies training pipeline. | Performance is sensitive to batch size and the quality of the reward function. | The primary architecture for large-scale, continuous training of the AI-SWA agent due to its efficiency. |
| **RewardRanker** | Iterative self-training loop that uses PPO to generate "hard negatives" to refine the reward model. | Required (for PPO inner loop) | Produces a highly robust reward model that understands subtle code quality issues. | Computationally expensive due to the iterative, from-scratch retraining cycle. | An outer-loop meta-learning strategy to periodically upgrade the reward function used by GRPO. |

### **Section 1.2: Gradient-Free Exploration via Evolutionary Strategies**

While gradient-based methods are powerful, they are constrained to optimizing differentiable objective functions. The domain of program synthesis, however, is rife with objectives that are discrete, non-differentiable, or have sparse, deceptive gradients. Evolutionary Strategies (ES) and Genetic Programming (GP) offer a compelling alternative paradigm that navigates the solution space without relying on gradients, making them uniquely suited for certain aspects of code generation.

#### **1.2.1 Principles of Evolutionary Program Synthesis**

Evolutionary computation frames program synthesis as an optimization problem within the broader field of Search-Based Software Engineering (SBPS).12 Instead of adjusting weights via backpropagation, SBPS employs a population of candidate solutions (programs) and iteratively improves them using mechanisms inspired by biological evolution: selection, crossover, and mutation.12 A fitness function evaluates each program, and those with higher fitness are more likely to survive and reproduce, passing their traits to the next generation.

This paradigm has a long history. The Tierra system, for example, was a pioneering work that created a "digital ecosystem" where self-replicating computer programs competed for CPU time and memory space. Through mutation and natural selection, the system automatically evolved more efficient replicators, demonstrating the power of evolutionary mechanisms to guide program synthesis toward desired properties like efficiency.13 This core principle—creating competitive pressure based on performance metrics—is directly applicable to evolving code for maintainability and resource efficiency.

#### **1.2.2 Key Approaches in Genetic Programming (GP)**

Genetic Programming is the subfield of evolutionary computation that specifically deals with evolving computer programs. Over decades of research, several influential approaches have emerged as particularly effective for program synthesis 14:

* **Stack-based GP:** This approach evolves programs in a stack-based language, such as Push. The language's design allows for the evolution of programs that can manipulate their own code, leading to a high degree of flexibility.  
* **Grammar-guided GP (or Grammatical Evolution):** To ensure that evolution only produces syntactically valid programs, this method uses a formal grammar (like a Backus-Naur Form) to constrain the search space. The evolutionary process manipulates a sequence of choices within the grammar, which is then mapped to a complete, valid program.  
* **Linear GP:** In this variant, programs are represented as a linear sequence of instructions operating on a set of registers. This structure is closer to traditional machine code and can be highly efficient to execute and evolve.

These GP methods have been shown to perform particularly well on benchmark problems where there is a relatively simple mapping from the given inputs to the desired outputs.14

#### **1.2.3 Advanced Selection and Hybridization**

Modern evolutionary approaches incorporate more sophisticated techniques to improve search efficiency and tackle more complex problems.

* **Lexicase Selection:** Traditional selection methods, like tournament selection, often aggregate performance across all test cases into a single fitness score. This can lead to the loss of specialist individuals that perform exceptionally well on a small subset of difficult cases. Lexicase selection addresses this by considering each test case individually and sequentially. To survive a selection event, a program must perform best on a random ordering of test cases. This method has been shown to produce significantly better results in program synthesis by preserving valuable specialists in the population.15  
* **Evolution Strategy (ES) for Sketching:** A powerful hybrid approach combines high-level program structure with low-level evolutionary optimization. In this model, a human or another system defines a high-level program "sketch" with "holes" or undefined coefficients. An Evolution Strategy—a type of evolutionary algorithm well-suited for continuous parameter optimization—is then employed to search for the optimal values to fill these holes.15 This combines the strength of human domain knowledge (in defining the sketch) with the power of automated search (in finding the precise implementation details). For AI-SWA, this could involve generating a high-level code structure with an LLM and then using an ES to fine-tune numerical parameters or select optimal library calls within that structure.

### **Section 1.3: Bootstrapping Performance through Self-Play and Curriculum Learning**

A key differentiator for an advanced AI agent is the ability to improve autonomously, without constant reliance on new, human-curated data. Self-play and curriculum learning are two intertwined concepts that enable this. In this paradigm, the agent becomes its own data generator and its own teacher, creating a virtuous cycle of improvement that allows it to tackle progressively harder problems.

#### **1.3.1 Expert Iteration: Learning from Scratch**

The "expert iteration" framework provides a powerful blueprint for training a code-generation model from scratch, requiring no pre-existing corpus of human-written code.16 This is particularly relevant for proprietary or novel programming domains where large datasets are unavailable. The framework operates in a two-phase loop:

1. **Search Phase (The "Expert"):** In this phase, a search algorithm, guided by the current neural network policy, explores the space of possible programs to find solutions to a given problem. Monte Carlo Tree Search (MCTS) is a common choice for this search procedure. The search acts as an "expert" by discovering correct programs that the policy might not have been able to generate directly in a single pass.16  
2. **Train Phase:** The correct programs discovered by the expert search are used as high-quality training data to update the neural network policy. The model learns to internalize the successful strategies found during the search.

This process creates a positive feedback loop: as the policy improves, it provides better guidance to the search algorithm, enabling it to solve harder problems more efficiently. The solutions to these harder problems then provide even better training data, further improving the policy. This cycle allows the agent to bootstrap its performance from a randomly initialized state to a high level of proficiency.16

#### **1.3.2 The Solver-Verifier (Sol-Ver) Framework**

A critical danger in any self-improvement loop is the risk of "model collapse" or "error accumulation," where a model trained on its own flawed outputs becomes progressively worse.17 The most successful self-improvement frameworks have converged on a "generate-and-verify" pattern to prevent this. While expert iteration uses an external search process as the verifier, the Solver-Verifier (Sol-Ver) framework internalizes this mechanism.17

In the Sol-Ver framework, a single LLM is trained to perform two roles jointly:

* **The Solver:** Generates a candidate code solution for a given problem description.  
* **The Verifier:** Generates a suite of unit tests intended to validate the correctness of the generated solution.

The self-play loop works as follows: the model first acts as a solver to generate code, then acts as a verifier to generate tests for that code. The code is then executed against the self-generated tests. Only if the code passes all the tests is the (code, test) pair considered a high-quality, "chosen" example and added to the dataset for fine-tuning. This rigorous self-verification step ensures that the model is not trained on its own erroneous outputs, effectively filtering the synthetic data for correctness and preventing degenerative feedback loops.17 This joint improvement of both coding and testing capabilities is a powerful mechanism for robust, autonomous learning.

#### **1.3.3 Automatic Curriculum Generation**

Manually designing a curriculum of tasks with increasing difficulty is challenging and labor-intensive. Automatic curriculum generation aims to have the system itself propose a sequence of tasks that are optimally suited to the agent's current skill level.

* **Reverse Curriculum Learning:** This elegant approach, inspired by dynamic programming, learns a task "in reverse".18 It begins by training the agent from start states that are already very close to the goal state. As the agent masters these simple final steps, the curriculum generator automatically generates new start states that are progressively further away from the goal. This is achieved by taking a previously successful start state and executing a short random walk away from it. This method requires only a single example of a successful goal state to bootstrap the entire learning process and has been shown to be highly effective for tasks with difficult exploration challenges.18  
* **Goal-Conditioned Curriculum:** Another powerful technique is to automatically propose goals that lie at the "frontier" of an agent's capabilities—neither too easy nor too hard.19 Goals that are too easy provide no new learning signal, while goals that are too difficult are unlikely to be achieved, also resulting in no feedback in sparse-reward settings. By focusing on this frontier of achievable but challenging goals, the agent receives a much stronger and more consistent learning signal, dramatically improving sample efficiency. This can be implemented using a generator model (like a GAN) that is trained to produce goals of intermediate difficulty for the current policy.19

## **Part 2: Addressing Core Challenges in Continual Code Improvement**

While the foundational paradigms described in Part 1 provide the engine for self-improvement, several critical challenges must be addressed to build a system that is robust, efficient, and produces genuinely high-quality software. This part directly tackles the open questions posed in the research brief: how to design reward signals that go beyond simple correctness, how to learn efficiently in the face of sparse rewards, and how to prevent the agent from forgetting past knowledge as it continually learns.

### **Section 2.1: Engineering Reward Signals for High-Quality, Maintainable Code**

The objective of the AI-SWA project is not merely to generate code that passes tests, but to generate code that is maintainable, efficient, and adheres to software engineering best practices. This requires a reward function that is far more nuanced than a simple binary pass/fail signal. The definition of "code quality" is not monolithic; therefore, the reward signal must be a decomposable, multi-objective function that captures the various facets of what makes code "good."

#### **2.1.1 Deconstructing Code Quality into Reward Components**

A robust reward system for code generation should be architected as a composite function, where the total reward is a weighted sum of several independently evaluated components. This modular design allows for easier tuning and iterative refinement of what the agent is being optimized to produce.21 The proposed components are:

* **Functional Correctness:** This is the foundational component. The reward is derived from executing the generated code against a suite of unit tests. This can be a simple binary reward (1.0 for all tests passing, 0 otherwise) or a partial score representing the fraction of tests passed, which can provide a denser learning signal.16  
* **Syntactic and Formatting Correctness:** Code must not only be functionally correct but also readable and consistent. This reward component can be implemented using static checks. For example, regular expressions can verify that the model's output follows a required format (e.g., enclosing reasoning steps in specific tags), which simplifies automated parsing and evaluation.22 Furthermore, integrating a standard code linter (e.g., Flake8 for Python) into the reward function can provide a direct penalty for violations of style guides, encouraging the generation of clean, idiomatic code.7  
* **Logical and Structural Integrity:** This component evaluates the internal logic of the generated code without necessarily executing it. For example, in a mathematical problem-solving context, the reward function could parse the generated equation to verify that all required input numbers were used exactly once and that only permitted arithmetic operations were employed.22 In a general coding context, this could involve checking for anti-patterns or logical inconsistencies.  
* **Maintainability Metrics (Static Analysis):** To directly incentivize the generation of maintainable code, the reward function can incorporate penalties derived from established software metrics. Static analysis tools can compute metrics like cyclomatic complexity (a measure of the number of independent paths through the code), cognitive complexity, and code duplication. A higher complexity or duplication score would result in a negative reward, pushing the agent toward simpler, more modular solutions.  
* **Efficiency Metrics:** Drawing inspiration from early evolutionary systems like Tierra 13, the reward function can include a penalty based on resource consumption. By measuring the execution time and memory usage of the generated code when run against the test suite, the system can create an evolutionary pressure that favors more efficient algorithms and implementations.

#### **2.1.2 Iterative and Automated Reward Design**

Manually designing and weighting the components of such a complex reward function is a significant engineering challenge, often involving a laborious process of trial and error.21 To address this, research is moving toward methods for automating the design of the reward function itself.

* **LLM-Driven Reward Design (CARD):** The Coder-Evaluator Reward Design (CARD) framework offers a sophisticated, automated approach.23 It employs two LLM-based agents: a "Coder" that generates the Python code for the reward function, and an "Evaluator" that provides dynamic feedback to iteratively improve that code. The Evaluator uses clever techniques, such as Trajectory Preference-based Evaluation (TPE), to assess the quality of a candidate reward function without needing to run a full, costly RL training loop for every iteration. This allows the system to autonomously refine its own definition of "good" code, eliminating the need for constant human intervention.23 While some sources reference an unrelated "RLCard" toolkit for card games 24, the CARD framework for reward design is a distinct and highly relevant technology.  
* **Generation from Formal Specifications:** A simpler but related principle is the generation of reward functions from high-level or formal specifications. For example, in control systems, it is possible to automatically generate a MATLAB reward function directly from the cost and constraint definitions in a Model Predictive Control (MPC) object.26 This demonstrates the concept of translating a formal problem definition into an executable reward function, a principle that could be adapted for AI-SWA by defining code quality objectives in a structured format that an LLM can then translate into reward code.

### **Section 2.2: Enhancing Sample Efficiency in Sparse Reward Environments**

A fundamental challenge in training an agent to generate correct code is the sparsity of the reward signal. A program that is 99% correct but contains a single syntax error will fail to compile and execute, yielding a reward of zero. From the perspective of a standard RL algorithm, this outcome is indistinguishable from a program of complete gibberish. This makes credit assignment extremely difficult, as the agent receives no feedback on which of its many actions were productive.19 To learn effectively, the agent must be able to extract a useful learning signal from the vast majority of its attempts, which will be failures.

#### **2.2.1 Hindsight Experience Replay (HER)**

Hindsight Experience Replay (HER) is a powerful and foundational technique for learning in sparse reward environments.28 It transforms failures into learning opportunities by retroactively changing the goal of a given trajectory.

The mechanism of HER is as follows: The agent attempts to achieve a desired goal G. It executes a sequence of actions, resulting in a trajectory of states. At the end of the trajectory, it has reached a final state S', but it has failed to reach G, so it receives a sparse reward of 0\. HER salvages this failed experience by storing a second, modified version of the trajectory in its replay buffer. In this modified version, the goal is replaced with the state that was actually achieved. The agent is asked, in hindsight, "What if your goal all along was to reach S'?" Since it did, in fact, reach S', the reward for this modified trajectory, r', is now positive (e.g., 1.0).27

This technique is more than just a trick for credit assignment; it is a form of automatic curriculum generation and sub-task discovery. In the context of code generation, a "goal" can be defined by a set of passing unit tests.

* **Complex Goal (G):** "Write a program that passes all 10 unit tests."  
* **Attempt 1:** The agent generates code that fails to compile. The achieved state S' is "a program that is syntactically incorrect." The hindsight experience teaches the agent something about how to produce syntactically incorrect code (which, via preference-based methods, helps it learn what to avoid).  
* **Attempt 2:** The agent generates code that compiles but fails all tests. The achieved state S'' is "a program that is syntactically correct." The hindsight experience provides a positive learning signal for the sub-task of "writing compilable code."  
* **Attempt 3:** The agent generates code that passes the first 3 out of 10 tests. The achieved state S''' is "a program that solves the first three sub-problems." The hindsight experience teaches the agent how to solve that specific subset of the problem.

By applying HER, the agent autonomously breaks down the complex, sparse-reward goal of writing a perfect program into a curriculum of simpler, more densely rewarded sub-goals, dramatically accelerating learning.

#### **2.2.2 Advanced Hindsight Techniques**

The core idea of HER has been extended to more complex learning scenarios.

* **Hindsight Task Relabeling (HTR):** This technique adapts HER for the meta-reinforcement learning setting, where the agent must learn to quickly adapt to new, unseen tasks.29 In meta-RL, the task itself is unknown and must be inferred from interaction. HTR allows an agent to relabel an unsuccessful trajectory from an unknown true task as a successful trajectory for an easier, known "hindsight task." This provides the necessary reward signal to bootstrap the learning of the adaptation strategy itself, enabling meta-learning even when the underlying tasks provide only sparse rewards.29  
* **Generalized Back-Stepping Experience Replay (GBER):** This is a more recent technique designed to accelerate learning in sparse-reward environments with complex structures, such as mazes. GBER enhances standard experience replay by generating "back-stepping" transitions—synthetic experiences that trace paths backward from collected states. This helps the agent better understand the connectivity of the state space and propagate value information more effectively from rewarded states.30

For the AI-SWA agent, implementing a HER-based strategy is essential for making the self-improvement loop sample-efficient. By treating every code generation attempt, even failures, as a source of learning, the agent can build up its skills incrementally and avoid the stagnation that often occurs in sparse-reward domains.

### **Section 2.3: Ensuring Knowledge Retention and Preventing Catastrophic Forgetting**

A continually learning system, by definition, is always being updated with new information. A critical challenge in this process is the phenomenon of **catastrophic forgetting**, where a neural network, upon learning a new task, abruptly and drastically loses its ability to perform previously mastered tasks.31 For the AI-SWA agent, this could manifest as learning to fix a new type of bug while simultaneously forgetting how to perform a basic refactoring it had previously learned.

This problem arises from the **stability-plasticity dilemma**.34 A model must be

**plastic** enough to acquire new knowledge and adapt its weights, but also **stable** enough to prevent the overwriting of existing knowledge. The most effective strategies for mitigating catastrophic forgetting are not uniform constraints but rather data-driven, selective approaches that intelligently balance this trade-off.

#### **2.3.1 Rehearsal-Based Methods (Experience Replay)**

The most intuitive way to combat forgetting is to "remind" the model of old tasks while it learns new ones. Rehearsal-based methods achieve this by storing a subset of data from past tasks in a memory buffer and replaying them (i.e., mixing them into the training batches) during continual training.31

* **Uniform Rehearsal:** The simplest strategy is to sample uniformly at random from the memory buffer. This has been shown to be a surprisingly strong and difficult-to-beat baseline.36  
* **Intelligent Sampling (mix-cd):** A more efficient approach is to focus the rehearsal budget on the specific knowledge that is being forgotten. The mix-cd method does exactly this by prioritizing the replay of "collateral damage" samples. These are defined as data points that the model predicted correctly *before* the most recent training update but predicts incorrectly *after* the update.36 By identifying and rehearsing these specific examples,  
  mix-cd directs the model's capacity toward preserving the most vulnerable knowledge, making it significantly more computationally and sample-efficient than uniform rehearsal.  
* **Pseudorehearsal:** In scenarios where storing original data is infeasible due to memory or privacy constraints, pseudorehearsal offers an alternative. This method involves training a generative model to capture the statistical distribution of past data. During continual learning, this generator can create "pseudo-samples" that are then rehearsed, providing the benefits of replay without storing the original data itself.38

#### **2.3.2 Regularization-Based Methods**

Instead of replaying data, regularization-based methods add a penalty term to the model's loss function. This penalty discourages changes to network parameters that are deemed important for performance on previous tasks.

* **Elastic Weight Consolidation (EWC):** EWC is a prominent regularization method inspired by synaptic consolidation in the brain.34 It operates on the principle that not all weights in a neural network are equally important for a given task. EWC identifies the weights that are most critical for past tasks by calculating the diagonal of the  
  **Fisher Information Matrix (FIM)**. The FIM approximates the curvature of the loss landscape, with a high value for a given weight indicating that a small change to that weight will cause a large change in the model's output (and thus, its performance).39 During training on a new task, EWC adds a quadratic penalty to the loss function that is proportional to the FIM values. This acts like an "elastic spring," anchoring the important weights to their previously learned optimal values while allowing less important weights to change more freely to learn the new task.40 This selective constraint is key to balancing stability and plasticity.

#### **2.3.3 Architectural Methods for Code Models**

Some methods are specifically designed to handle the unique challenges of continual learning for code, which often involves stark shifts in data distribution as new libraries, APIs, or programming paradigms are introduced.

* **Prompt Pooling with Teacher Forcing (PP-TF):** This method adapts the Prompt Pooling (PP) technique for continual learning. PP maintains a pool of learnable prompt vectors, and for each task, a selection mechanism chooses the most appropriate prompts to guide the model. However, standard PP can suffer from catastrophic forgetting on coding tasks because the prompt selection mechanism itself can be unstable during training. PP-TF addresses this by introducing a "teacher forcing" constraint that stabilizes the training of the prompt selector, leading to a 21.54% improvement over standard PP on a code-specific continual learning benchmark.42

For AI-SWA, a hybrid approach combining an efficient rehearsal strategy like mix-cd with a regularization method like EWC could provide a robust defense against catastrophic forgetting.

**Table 2: Methodologies for Mitigating Catastrophic Forgetting**

| Approach Family | Method | Mechanism | Resource Requirements | Pros | Cons |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Rehearsal** | **Uniform Rehearsal** | Mixes randomly sampled examples from past tasks into the current training batch. | Memory buffer to store past data. | Simple to implement; strong baseline performance. | Can be inefficient; memory overhead scales with number of tasks. |
| **Rehearsal** | **mix-cd (Collateral Damage)** | Prioritizes replaying past examples that the model has recently started to misclassify. | Memory buffer; tracking of pre- and post-update predictions. | Highly compute- and sample-efficient; focuses on actively forgotten knowledge. | More complex to implement than uniform sampling. |
| **Regularization** | **EWC (Elastic Weight Consolidation)** | Adds a quadratic penalty to the loss, constraining changes to weights deemed important by the Fisher Information Matrix. | Computation of Fisher Information Matrix for past tasks. | No memory buffer required; theoretically grounded in Bayesian inference. | FIM computation can be expensive; may underperform rehearsal in some settings. |
| **Architectural** | **PP-TF (Prompt Pooling w/ Teacher Forcing)** | Learns a pool of prompts and uses a stabilized selection mechanism to instruct a frozen model on a per-task basis. | Storage for a pool of prompt vectors; modified training procedure. | Specifically designed for code models; avoids modifying core model weights. | Requires a model architecture that supports prompting; effectiveness depends on prompt design. |

## **Part 3: A Framework for Implementation, Evaluation, and Safety**

Translating the preceding research analysis into a functional, reliable system requires a concrete implementation plan. This part outlines an architectural framework for the AI-SWA self-improvement loop, addressing the specific acceptance criteria from the research brief. It details the design of core learning components, a novel evaluation strategy based on version control history, and critical safety mechanisms to ensure system stability.

### **Section 3.1: Architecting the Learning Loop: Replay Buffers and Curriculum Generators**

The heart of the continual learning system is a tightly coupled loop between a curriculum generator, which provides tasks, and a replay buffer, which stores the resulting experiences for training.

#### **3.1.1 Implementing the Replay Buffer**

The replay buffer is a data storage component that holds trajectories of experience collected as the agent interacts with its environment. It is a central piece of off-policy RL algorithms, as it decouples data collection from learning and allows experiences to be reused multiple times, improving sample efficiency.27

Several mature RL libraries provide robust, customizable replay buffer implementations, including PyTorch RL 44, Ray RLlib 47, and TensorFlow Agents.48 The PyTorch RL

ReplayBuffer class is recommended for its highly composable and flexible design. Key implementation choices involve selecting the appropriate storage backend and sampling strategy based on the specific needs of the training run.

**Table 3: Replay Buffer Implementation Options and Trade-offs (PyTorch RL)**

| Storage Class | Storage Medium | Data Type Support | Memory Footprint | I/O Speed | Use Case for AI-SWA |
| :---- | :---- | :---- | :---- | :---- | :---- |
| ListStorage | In-Memory (Python List) | Any Python object | High | Fastest | Prototyping or small-scale experiments with non-tensorized data. |
| LazyTensorStorage | In-Memory (Tensor) | Tensors only | Medium | Fast | Default for most training runs, assuming code representations are tensorized. |
| LazyMemmapStorage | On-Disk (Memory-Mapped File) | Tensors only | Low | Slower (disk I/O) | For massive-scale runs where the replay buffer exceeds available system RAM. |

Beyond storage, the choice of a **sampler** is critical. A RandomSampler provides a solid baseline, but a PrioritizedSampler 44 should be used to focus training on experiences with high temporal-difference (TD) error, which correspond to surprising or poorly understood outcomes. For organizing the complex data associated with a single experience (e.g., code prompt, generated code, AST, static analysis results, reward components), the

TensorDict data structure is highly recommended as it keeps related tensors organized in a dictionary-like container.44

#### **3.1.2 Designing the Curriculum Generator**

The curriculum generator is the strategic component of the learning loop. Its purpose is to select or generate the next task for the agent to attempt, with the goal of maximizing learning efficiency. A naive approach might present tasks randomly, but a well-designed curriculum can dramatically accelerate convergence by presenting tasks in a meaningful order.20

The architecture of the curriculum generator should be a stateful module that tracks the agent's performance across a wide range of known tasks and uses this information to propose the next challenge. It should not be an independent module but rather part of a tightly coupled system where the output of the evaluation framework is fed back to inform the curriculum strategy. If evaluation shows the agent is weak at a particular skill (e.g., refactoring large functions), the curriculum generator should prioritize generating more tasks of that type. This creates an adaptive training regimen tailored to the agent's specific, measured weaknesses.

The generator can employ a mixture of strategies to create tasks:

* **Parameter-based Generation:** This involves taking existing tasks and modifying their parameters to increase difficulty. For instance, it could take a known bug-fixing task and apply code obfuscation to the context, or increase the complexity of a function to be refactored.50  
* **Self-Play Generation:** The generator can implement a version of the Sol-Ver 17 or Asymmetric Self-Play 18 frameworks. In this mode, one instance of the agent (the "challenger") could be tasked with modifying a piece of working code to introduce a subtle bug, which another instance (the "solver") must then fix.  
* **Hindsight-based Generation:** As discussed in Section 2.2, failed attempts can be used to define new, simpler sub-tasks. The curriculum generator can analyze failed trajectories from the replay buffer and formally define these discovered sub-tasks for targeted practice.

### **Section 3.2: Measuring Progress: Longitudinal Evaluation Against Version Control History**

Standard, static coding benchmarks like MBPP 8 and HumanEval are invaluable for comparing models at a single point in time. However, they are insufficient for evaluating a

*continually improving* agent, whose capabilities are expected to evolve over time. A more meaningful evaluation framework would measure the agent's ability to perform real-world software engineering tasks, using a benchmark that is itself dynamic and relevant to the agent's own development context.51 The project's own version control history provides an ideal source for such a benchmark.

#### **3.2.1 The GitGoodBench Framework**

The recently proposed GitGoodBench provides a formal methodology for evaluating an AI agent's proficiency with Git-based version control tasks, moving beyond mere programming proficiency.52 It establishes a blueprint for using a project's history to create meaningful evaluation scenarios. We propose adapting the core scenarios from GitGoodBench for the AI-SWA evaluation framework:

1. **Bug Fixing (from Commit History):** A script mines the Git history for commits with messages indicating a bug fix (e.g., containing keywords like "fix," "bug," "error"). For each such commit, a benchmark task is created where the agent is presented with the state of the codebase *before* the fix and is tasked with generating a patch that resolves the issue. The agent's output can be evaluated by applying its patch and running the project's test suite.  
2. **Refactoring (Interactive Rebase Simulation):** The framework identifies sequences of commits that represent a refactoring effort (e.g., multiple consecutive modifications to the same file or module). The agent is presented with the initial state and the final state and tasked with generating an improved Git history—for example, by consolidating trivial commits, reordering changes for logical clarity, and writing better commit messages.52  
3. **Feature Implementation (Iterative Committing):** For large feature branches, the agent is presented with the entire diff (the "disorganized set of changes") and tasked with breaking it down into a sequence of logical, atomic commits with clear, descriptive messages. This tests the agent's ability to structure and communicate its work, a critical software engineering skill.52

The performance on these latter two scenarios, where a single ground truth does not exist, can be evaluated using an LLM-as-a-Judge approach, where a powerful external LLM is prompted to compare the agent-generated history with the original human-written history based on criteria like clarity, cohesion, and logical progression.52 This creates a rich, evolving benchmark suite that directly measures the agent's practical utility on the very codebase it is designed to improve.

### **Section 3.3: System Stability and Safety: Implementing Robust Rollback Mechanisms**

A system that can modify its own behavior is inherently risky. A bug in the self-improvement loop could lead to rapid performance degradation. Therefore, it is imperative to build robust safety mechanisms into the architecture. The mature principles of Continuous Integration and Continuous Delivery (CI/CD) from traditional software engineering provide a strong model for ensuring the safety of a continually learning AI.53

This requires a conceptual shift: each new version of the AI agent produced by the self-improvement loop should be treated as a new "deployment" that must pass a rigorous, automated quality gate before being promoted to "production." This leads to a necessary separation of the evaluation function into two distinct components: one for learning and one for safety.

* **Dynamic Evaluation for Learning:** The Git-based evaluation framework described in Section 3.2 is dynamic and ever-changing. Its purpose is to provide a rich source of challenging and relevant tasks to drive the agent's *learning* via the curriculum generator.  
* **Static Evaluation for Safety:** A rollback decision, however, cannot be based on a moving target. To reliably detect performance degradation, comparisons must be made against a stable, unchanging benchmark.

We therefore propose a "performance gating" system as the primary rollback mechanism:

1. **Agent Versioning:** Every new agent model v\_n+1 that is produced by a training cycle is versioned and stored, for example, by tagging it with the Git hash of the training code and a timestamp.  
2. **Golden Benchmark Suite:** A static, curated set of high-priority evaluation tasks is maintained. This "golden suite" represents the core capabilities that the agent must *never* lose. It should cover a diverse range of critical tasks, including bug fixes, refactorings, and feature implementations that have been manually vetted for quality.  
3. **Automated Gating and Rollback:** Before a new version v\_n+1 can replace the current production version v\_n, it is automatically evaluated on the golden benchmark suite. If its performance score shows a statistically significant degradation compared to v\_n's score on the same suite, the update is automatically rejected. The system "rolls back" by simply keeping v\_n as the active production model, and an alert is raised for human developers to investigate the failure.

This automated rollback mechanism serves as a critical safety net, preventing catastrophic forgetting or other training failures from negatively impacting the agent's deployed performance.53 For debugging and manual intervention, the system should also provide extensive logging of the agent's decision-making process and a command-line interface (CLI) that allows a human operator to manually trigger a rollback to any previously versioned stable state.54

## **Conclusion and Recommendations**

The path to creating a truly self-improving AI software agent is paved with both immense opportunity and significant technical challenges. This report has synthesized a broad range of research to propose a comprehensive architectural blueprint for the AI-SWA project, designed to be efficient, robust, and safe.

The analysis of foundational learning paradigms reveals a clear evolutionary path. While PPO provides a stable baseline, the computational and memory demands of its critic network make it ill-suited for the scale of modern LLMs. **It is therefore recommended to adopt Group Relative Policy Optimization (GRPO) as the core policy optimization algorithm.** Its critic-free design offers substantial efficiency gains without sacrificing performance, making it a more scalable and sustainable choice for a continual learning loop.

However, optimizing the policy is only half the battle. The quality of the learning signal—the reward function—is paramount. A simple pass/fail reward is insufficient for cultivating high-quality, maintainable code. **The proposed architecture must support a multi-objective, composite reward function** that integrates signals from unit tests, static analysis tools (linters, complexity checkers), and performance profiling (execution time, memory usage). To avoid the pitfalls of manual tuning, **it is recommended to implement a meta-learning loop inspired by the RewardRanker framework.** This outer loop would periodically use the agent's own outputs to find "hard negatives" and retrain the reward model, ensuring the agent's concept of "good code" co-evolves with its ability to generate it.

To make this learning process sample-efficient, especially in the sparse-reward domain of code generation, **the implementation of Hindsight Experience Replay (HER) is critical.** By treating every failed attempt as a successful attempt at a simpler, retrospectively defined goal, HER enables the agent to learn from all experiences and autonomously discovers a curriculum of achievable sub-tasks.

As the agent learns, preventing the loss of prior knowledge is essential. The most effective strategies for mitigating catastrophic forgetting are selective and data-driven. **A dual strategy is recommended: employing the mix-cd rehearsal method to efficiently replay the specific past experiences the model is actively forgetting, potentially augmented by a regularization penalty like Elastic Weight Consolidation (EWC) to protect the most critical parameters.**

Finally, this entire learning process must be embedded within a framework that prioritizes safety and rigorous evaluation. The acceptance criteria point toward a novel and powerful evaluation methodology. **It is recommended to implement a dual evaluation framework:**

1. **A dynamic benchmark for learning,** automatically mined from the project's own Git history, adapting scenarios from the GitGoodBench framework. The results from this benchmark should be fed directly to the curriculum generator to create an adaptive training regimen focused on the agent's measured weaknesses.  
2. **A static "golden" benchmark for safety,** representing the core, non-negotiable capabilities of the agent. This suite will serve as an automated quality gate, triggering a rollback to the previous stable version if a new agent update shows any performance degradation.

By integrating these advanced techniques—a GRPO-based policy learner, a self-refining composite reward function, hindsight-driven curriculum generation, selective anti-forgetting mechanisms, and a dual-mode evaluation and safety framework—the AI-SWA project can build a state-of-the-art system capable of robust, efficient, and continuous self-improvement.

#### **Works cited**

1. Proximal Policy Optimization and its Dynamic Version for Sequence Generation \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/1808.07982](https://arxiv.org/abs/1808.07982)  
2. Truncated Proximal Policy Optimization \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/2506.15050](https://arxiv.org/abs/2506.15050)  
3. Theory Behind GRPO \- AI Engineering Academy, accessed on July 9, 2025, [https://aiengineering.academy/LLM/TheoryBehindFinetuning/GRPO/](https://aiengineering.academy/LLM/TheoryBehindFinetuning/GRPO/)  
4. Why GRPO is Important and How it Works \- Oxen.ai, accessed on July 9, 2025, [https://ghost.oxen.ai/why-grpo-is-important-and-how-it-works/](https://ghost.oxen.ai/why-grpo-is-important-and-how-it-works/)  
5. From Reasoning to Code: GRPO Optimization for Underrepresented Languages \- arXiv, accessed on July 9, 2025, [https://arxiv.org/html/2506.11027v2](https://arxiv.org/html/2506.11027v2)  
6. arxiv.org, accessed on July 9, 2025, [https://arxiv.org/html/2506.11027v1](https://arxiv.org/html/2506.11027v1)  
7. What is GRPO? Group Relative Policy Optimization Explained ..., accessed on July 9, 2025, [https://www.datacamp.com/blog/what-is-grpo-group-relative-policy-optimization](https://www.datacamp.com/blog/what-is-grpo-group-relative-policy-optimization)  
8. arxiv.org, accessed on July 9, 2025, [https://arxiv.org/html/2504.09643v1](https://arxiv.org/html/2504.09643v1)  
9. Iterative Self-Training for Code Generation via Reinforced Re-Ranking \- ResearchGate, accessed on July 9, 2025, [https://www.researchgate.net/publication/390772323\_Iterative\_Self-Training\_for\_Code\_Generation\_via\_Reinforced\_Re-Ranking](https://www.researchgate.net/publication/390772323_Iterative_Self-Training_for_Code_Generation_via_Reinforced_Re-Ranking)  
10. Iterative Self-Training for Code Generation via Reinforced Re-Ranking \- Hugging Face, accessed on July 9, 2025, [https://huggingface.co/papers/2504.09643](https://huggingface.co/papers/2504.09643)  
11. \[2504.09643\] Iterative Self-Training for Code Generation via Reinforced Re-Ranking \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/2504.09643](https://arxiv.org/abs/2504.09643)  
12. Review and Mapping of Search-Based Approaches ... \- Preprints.org, accessed on July 9, 2025, [https://www.preprints.org/manuscript/202503.1722/v1/download](https://www.preprints.org/manuscript/202503.1722/v1/download)  
13. AN EVOLUTIONARY APPROACH TO PROGRAM TRANSFORMATION AND SYNTHESIS | International Journal of Software Engineering and Knowledge Engineering \- World Scientific Publishing, accessed on July 9, 2025, [https://worldscientific.com/doi/10.1142/S0218194095000101](https://worldscientific.com/doi/10.1142/S0218194095000101)  
14. (PDF) Recent Developments in Program Synthesis with Evolutionary Algorithms, accessed on July 9, 2025, [https://www.researchgate.net/publication/354208160\_Recent\_Developments\_in\_Program\_Synthesis\_with\_Evolutionary\_Algorithms](https://www.researchgate.net/publication/354208160_Recent_Developments_in_Program_Synthesis_with_Evolutionary_Algorithms)  
15. A Comprehensive Survey on Program Synthesis With Evolutionary Algorithms | Request PDF \- ResearchGate, accessed on July 9, 2025, [https://www.researchgate.net/publication/359492604\_A\_Comprehensive\_Survey\_on\_Program\_Synthesis\_with\_Evolutionary\_Algorithms?\_tp=eyJjb250ZXh0Ijp7InBhZ2UiOiJzY2llbnRpZmljQ29udHJpYnV0aW9ucyIsInByZXZpb3VzUGFnZSI6bnVsbCwic3ViUGFnZSI6bnVsbH19](https://www.researchgate.net/publication/359492604_A_Comprehensive_Survey_on_Program_Synthesis_with_Evolutionary_Algorithms?_tp=eyJjb250ZXh0Ijp7InBhZ2UiOiJzY2llbnRpZmljQ29udHJpYnV0aW9ucyIsInByZXZpb3VzUGFnZSI6bnVsbCwic3ViUGFnZSI6bnVsbH19)  
16. TOWARDS SELF-IMPROVING LANGUAGE MODELS ... \- OpenReview, accessed on July 9, 2025, [https://openreview.net/pdf?id=SA2zPf03zQ](https://openreview.net/pdf?id=SA2zPf03zQ)  
17. Learning to Solve and Verify: A Self-Play Framework for ... \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/2502.14948](https://arxiv.org/abs/2502.14948)  
18. Reverse Curriculum Generation for Reinforcement Learning, accessed on July 9, 2025, [https://www.ri.cmu.edu/app/uploads/2017/11/florensa17a.pdf](https://www.ri.cmu.edu/app/uploads/2017/11/florensa17a.pdf)  
19. Automatic Curriculum Learning through Value Disagreement \- NIPS, accessed on July 9, 2025, [https://proceedings.neurips.cc/paper/2020/file/566f0ea4f6c2e947f36795c8f58ba901-Paper.pdf](https://proceedings.neurips.cc/paper/2020/file/566f0ea4f6c2e947f36795c8f58ba901-Paper.pdf)  
20. Curriculum for Reinforcement Learning | Lil'Log, accessed on July 9, 2025, [https://lilianweng.github.io/posts/2020-01-29-curriculum-rl/](https://lilianweng.github.io/posts/2020-01-29-curriculum-rl/)  
21. What are some best practices when trying to design a reward function? \- AI Stack Exchange, accessed on July 9, 2025, [https://ai.stackexchange.com/questions/22851/what-are-some-best-practices-when-trying-to-design-a-reward-function](https://ai.stackexchange.com/questions/22851/what-are-some-best-practices-when-trying-to-design-a-reward-function)  
22. Guide to Reward Functions in Reinforcement Fine-Tuning \- Predibase, accessed on July 9, 2025, [https://predibase.com/blog/reward-functions-reinforcement-fine-tuning](https://predibase.com/blog/reward-functions-reinforcement-fine-tuning)  
23. arxiv.org, accessed on July 9, 2025, [https://arxiv.org/html/2410.14660v1](https://arxiv.org/html/2410.14660v1)  
24. RLCard: A Toolkit for Reinforcement Learning in Card Games \- Daochen Zha, accessed on July 9, 2025, [https://dczha.com/files/rlcard-a-toolkit.pdf](https://dczha.com/files/rlcard-a-toolkit.pdf)  
25. RLCard: A Platform for Reinforcement Learning in Card Games \- ResearchGate, accessed on July 9, 2025, [https://www.researchgate.net/publication/342811762\_RLCard\_A\_Platform\_for\_Reinforcement\_Learning\_in\_Card\_Games](https://www.researchgate.net/publication/342811762_RLCard_A_Platform_for_Reinforcement_Learning_in_Card_Games)  
26. generateRewardFunction \- Generate a reward function from control specifications to train a reinforcement learning agent \- MATLAB \- MathWorks, accessed on July 9, 2025, [https://www.mathworks.com/help/reinforcement-learning/ref/generaterewardfunction.html](https://www.mathworks.com/help/reinforcement-learning/ref/generaterewardfunction.html)  
27. Deep Reinforcement Learning with Experience Replay | by Hey Amit \- Medium, accessed on July 9, 2025, [https://medium.com/@heyamit10/deep-reinforcement-learning-with-experience-replay-1222ea711897](https://medium.com/@heyamit10/deep-reinforcement-learning-with-experience-replay-1222ea711897)  
28. Learn from Sparse Reward: HER. Revisit one classic paper ..., accessed on July 9, 2025, [https://medium.com/@kaige.yang0110/learn-from-sparse-reward-her-b27e3dd3d37c](https://medium.com/@kaige.yang0110/learn-from-sparse-reward-her-b27e3dd3d37c)  
29. Hindsight Task Relabelling: Experience Replay for Sparse Reward ..., accessed on July 9, 2025, [https://proceedings.neurips.cc/paper/2021/file/1454ca2270599546dfcd2a3700e4d2f1-Paper.pdf](https://proceedings.neurips.cc/paper/2021/file/1454ca2270599546dfcd2a3700e4d2f1-Paper.pdf)  
30. \[2412.15525\] Generalized Back-Stepping Experience Replay in Sparse-Reward Environments \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/2412.15525](https://arxiv.org/abs/2412.15525)  
31. Catastrophic Forgetting or the Challenge of Continuous Learning ..., accessed on July 9, 2025, [https://medium.com/@thomas.zilliox/catastrophic-forgetting-or-the-challenge-of-continuous-learning-1278a1179811](https://medium.com/@thomas.zilliox/catastrophic-forgetting-or-the-challenge-of-continuous-learning-1278a1179811)  
32. Reducing Catastrophic Forgetting With Associative Learning: A Lesson From Fruit Flies | Neural Computation \- MIT Press Direct, accessed on July 9, 2025, [https://direct.mit.edu/neco/article/35/11/1797/117579/Reducing-Catastrophic-Forgetting-With-Associative](https://direct.mit.edu/neco/article/35/11/1797/117579/Reducing-Catastrophic-Forgetting-With-Associative)  
33. Mitigating Catastrophic Forgetting in Continual Learning Using the Gradient-Based Approach: A Literature Review, accessed on July 9, 2025, [https://thesai.org/Downloads/Volume16No4/Paper\_14-Mitigating\_Catastrophic\_Forgetting\_in\_Continual\_Learning.pdf](https://thesai.org/Downloads/Volume16No4/Paper_14-Mitigating_Catastrophic_Forgetting_in_Continual_Learning.pdf)  
34. Continual Learning and Catastrophic Forgetting: The Challenges and Strategies in AI | by Siddhartha Pramanik | Medium, accessed on July 9, 2025, [https://medium.com/@siddharthapramanik771/continual-learning-and-catastrophic-forgetting-the-challenges-and-strategies-in-ai-636e79a6a449](https://medium.com/@siddharthapramanik771/continual-learning-and-catastrophic-forgetting-the-challenges-and-strategies-in-ai-636e79a6a449)  
35. Revisions | OpenReview, accessed on July 9, 2025, [https://openreview.net/revisions?id=tHgJoMfy6nI](https://openreview.net/revisions?id=tHgJoMfy6nI)  
36. An Efficient Rehearsal Scheme for Catastrophic ... \- ACL Anthology, accessed on July 9, 2025, [https://aclanthology.org/2025.findings-naacl.138.pdf](https://aclanthology.org/2025.findings-naacl.138.pdf)  
37. \[Literature Review\] An Efficient Rehearsal Scheme for Catastrophic Forgetting Mitigation during Multi-stage Fine-tuning \- Moonlight | AI Colleague for Research Papers, accessed on July 9, 2025, [https://www.themoonlight.io/en/review/an-efficient-rehearsal-scheme-for-catastrophic-forgetting-mitigation-during-multi-stage-fine-tuning](https://www.themoonlight.io/en/review/an-efficient-rehearsal-scheme-for-catastrophic-forgetting-mitigation-during-multi-stage-fine-tuning)  
38. Catastrophic forgetting, rehearsal and pseudorehearsal \- SciSpace, accessed on July 9, 2025, [https://scispace.com/pdf/catastrophic-forgetting-rehearsal-and-pseudorehearsal-4e9ku43sdc.pdf](https://scispace.com/pdf/catastrophic-forgetting-rehearsal-and-pseudorehearsal-4e9ku43sdc.pdf)  
39. Overcoming Catastrophic Forgetting: A Simple Guide to Elastic ..., accessed on July 9, 2025, [https://pub.towardsai.net/overcoming-catastrophic-forgetting-a-simple-guide-to-elastic-weight-consolidation-122d7ac54328](https://pub.towardsai.net/overcoming-catastrophic-forgetting-a-simple-guide-to-elastic-weight-consolidation-122d7ac54328)  
40. What is elastic weight consolidation? \- Statistical Odds & Ends, accessed on July 9, 2025, [https://statisticaloddsandends.wordpress.com/2024/06/26/what-is-elastic-weight-consolidation/](https://statisticaloddsandends.wordpress.com/2024/06/26/what-is-elastic-weight-consolidation/)  
41. Explanation of Overcoming Catastrophic Forgetting in Neural Networks \- Rylan Schaeffer, accessed on July 9, 2025, [https://rylanschaeffer.github.io/content/research/elastic\_weight\_consolidation/main.html](https://rylanschaeffer.github.io/content/research/elastic_weight_consolidation/main.html)  
42. Exploring Continual Learning for Code Generation Models ..., accessed on July 9, 2025, [https://www.researchgate.net/publication/372136097\_Exploring\_Continual\_Learning\_for\_Code\_Generation\_Models](https://www.researchgate.net/publication/372136097_Exploring_Continual_Learning_for_Code_Generation_Models)  
43. How to train a self-driving vehicle: On the added value (or lack thereof) of curriculum learning and replay buffers \- Frontiers, accessed on July 9, 2025, [https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1098982/full](https://www.frontiersin.org/journals/artificial-intelligence/articles/10.3389/frai.2023.1098982/full)  
44. Using Replay Buffers — torchrl main documentation, accessed on July 9, 2025, [https://docs.pytorch.org/rl/main/tutorials/rb\_tutorial.html](https://docs.pytorch.org/rl/main/tutorials/rb_tutorial.html)  
45. ReplayBuffer — torchrl main documentation, accessed on July 9, 2025, [https://docs.pytorch.org/rl/main/reference/generated/torchrl.data.ReplayBuffer.html](https://docs.pytorch.org/rl/main/reference/generated/torchrl.data.ReplayBuffer.html)  
46. Using Replay Buffers — torchrl 0.4 documentation, accessed on July 9, 2025, [https://docs.pytorch.org/rl/0.4/tutorials/rb\_tutorial.html](https://docs.pytorch.org/rl/0.4/tutorials/rb_tutorial.html)  
47. Replay Buffers — Ray 2.47.1 \- Ray Docs, accessed on July 9, 2025, [https://docs.ray.io/en/latest/rllib/rllib-replay-buffers.html](https://docs.ray.io/en/latest/rllib/rllib-replay-buffers.html)  
48. Replay Buffers | TensorFlow Agents, accessed on July 9, 2025, [https://www.tensorflow.org/agents/tutorials/5\_replay\_buffers\_tutorial](https://www.tensorflow.org/agents/tutorials/5_replay_buffers_tutorial)  
49. Designing Curriculum for Deep Reinforcement Learning in StarCraft II \- Open Research Repository, accessed on July 9, 2025, [https://openresearch-repository.anu.edu.au/server/api/core/bitstreams/e8f19c78-8153-4b8d-ac23-15a2cb1697ca/content](https://openresearch-repository.anu.edu.au/server/api/core/bitstreams/e8f19c78-8153-4b8d-ac23-15a2cb1697ca/content)  
50. CAUSALLY ALIGNED CURRICULUM LEARNING \- Elias Bareinboim, accessed on July 9, 2025, [https://causalai.net/r102.pdf](https://causalai.net/r102.pdf)  
51. MaximeRobeyns/self\_improving\_coding\_agent: A coding agent framework, that works on its own codebase. \- GitHub, accessed on July 9, 2025, [https://github.com/MaximeRobeyns/self\_improving\_coding\_agent](https://github.com/MaximeRobeyns/self_improving_coding_agent)  
52. GitGoodBench: A Novel Benchmark For Evaluating Agentic ... \- arXiv, accessed on July 9, 2025, [https://arxiv.org/pdf/2505.22583](https://arxiv.org/pdf/2505.22583)  
53. Automating Rollbacks: Safety Nets for Rolling Upgrades \- Alibaba ..., accessed on July 9, 2025, [https://www.alibabacloud.com/tech-news/a/rolling\_upgrades/gv69skjuqg-automating-rollbacks-safety-nets-for-rolling-upgrades](https://www.alibabacloud.com/tech-news/a/rolling_upgrades/gv69skjuqg-automating-rollbacks-safety-nets-for-rolling-upgrades)  
54. Design of a Self-Improving Gödel Agent with CrewAI and LangGraph \- GitHub Gist, accessed on July 9, 2025, [https://gist.github.com/ruvnet/15c6ef556be49e173ab0ecd6d252a7b9](https://gist.github.com/ruvnet/15c6ef556be49e173ab0ecd6d252a7b9)