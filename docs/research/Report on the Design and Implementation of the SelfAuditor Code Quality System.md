

# **Report on the Design and Implementation of the SelfAuditor Code Quality System**

**Executive Summary**

This report provides a comprehensive analysis and strategic recommendation for the development of the SelfAuditor system, a proposed automated code quality auditor. It critically evaluates the initial research brief (RB-001) and expands upon it using an extensive body of research on code quality metrics, static analysis tooling, and modern software development workflows. The analysis confirms the fundamental viability of the SelfAuditor concept but identifies critical areas for refinement to ensure its effectiveness, robustness, and long-term value.

The core findings of this report are threefold. First, the selection of tooling must be modernized and diversified. While the proposal to use **Radon** for its lightweight, programmatic access to core metrics like Cyclomatic Complexity (CC) and Maintainability Index (MI) is sound, the landscape of Python static analysis has evolved significantly. The emergence of **Ruff**, a high-performance linter written in Rust, presents a compelling opportunity to unify and accelerate many quality checks. This report recommends a hybrid architecture for the SelfAuditor: leveraging Radon's API for the specific metrics required by the core heuristic, while incorporating a pluggable engine that can harness the comprehensive output of tools like **Pylint** or, preferably, **Ruff** to identify a richer set of refactoring opportunities beyond simple complexity.

Second, the proposed quality heuristic requires significant recalibration to align with established industry standards and avoid generating excessive noise. The threshold of Cyclomatic Complexity greater than 15 is a reasonable starting point for "moderate risk," but a more nuanced, tiered system is recommended to differentiate between advisory warnings and critical flags. More importantly, the Maintainability Index threshold of less than 60 is misaligned with the common 0-100 scale used by Radon, where scores above 20 are generally considered maintainable. This report strongly advises adjusting the MI threshold to flag code only when it falls below 20, thereby focusing on modules with genuinely low maintainability.

Third, the implementation strategy must be integrated into a multi-layered quality enforcement framework. The proposed "Auditor Proposes, Planner Executes" model, using a tasks.yml file as an interface, is architecturally sound for its decoupling and safety. However, its reliance on a CI/CD pipeline introduces a delayed feedback loop. To provide developers with immediate feedback and improve workflow efficiency, this report advocates for a two-tiered approach:

1. **Inner Loop (Pre-commit):** Fast, lightweight checks using tools like Ruff or Flake8 to catch style and syntax issues before code is committed.  
2. **Outer Loop (CI/CD):** The full SelfAuditor analysis, performing deeper, more time-consuming checks (CC, MI, historical trends via Wily) and generating structured, actionable refactoring tasks.

This report concludes that the SelfAuditor project is not only feasible but can provide significant value in systematically managing and reducing technical debt. Success hinges on adopting the refined heuristics, a modernized and hybrid tooling approach, and a multi-tiered integration strategy. By transforming static analysis outputs into structured, automatable refactoring tasks, the SelfAuditor can evolve from a simple metric-checker into an intelligent, proactive component of a sophisticated, self-improving software development ecosystem.

---

## **Part I: Foundational Analysis of Code Quality Metrics and Tooling**

This part establishes the fundamental knowledge required to evaluate the SelfAuditor proposal. It provides a deep, comparative analysis of the relevant tools and a theoretical grounding in the software metrics they produce.

### **Section 1: A Comparative Analysis of Python Static Analysis Libraries**

A successful implementation of the SelfAuditor system depends on selecting the right tools for the job. The Python ecosystem offers a mature suite of libraries for static analysis, each with distinct capabilities, architectural trade-offs, and ideal use cases. This section provides a detailed comparative analysis of the tools mentioned in the initial brief and introduces a critical modern alternative.

#### **1.1. Disambiguation of Tooling Names**

Before proceeding with the analysis, it is crucial to clarify the identity of the tools in question, as the provided research contains references to multiple projects sharing the same names. This disambiguation ensures that the subsequent evaluation is based on relevant and accurate information.

* **Radon**: The primary tool of interest is radon, a Python library for computing code metrics from source code.1 This tool is distinct from and should not be confused with:  
  * RadonPy, a library for automating physical property calculations in polymer informatics.4  
  * RepoMiner, a tool for mining Infrastructure-as-Code repositories, which is part of a different "Radon" project (RADON-H2020).5

    The analysis herein pertains exclusively to the radon code metrics tool.  
* **Wily**: The complexity tracking tool under consideration is wily, which uses Git history to analyze trends in code metrics over time.6 It is unrelated to an older project found on GitHub under  
  9wm/wily, which appears to be a window manager for the X Window System.8

This report will focus solely on the radon and wily libraries relevant to Python code quality analysis.

#### **1.2. Lightweight Metric Calculators: Radon and Wily**

The research brief correctly identifies two specialized, lightweight tools for the core tasks of metric calculation and trend analysis.

##### **Radon (The Core Metric Engine)**

Radon (version 5.1.0) is proposed as the central engine for the SelfAuditor's metric calculations. Its design and features make it a strong candidate for this role.

* **Capabilities**: Radon provides both command-line and programmatic API access to four key categories of code metrics:  
  1. **Raw Metrics**: Source Lines of Code (SLOC), logical lines of code (LLOC), comment lines, blank lines, and multi-line string counts.1  
  2. **Cyclomatic Complexity (CC)**: Also known as McCabe's Complexity, which measures the number of independent paths through the code.1  
  3. **Maintainability Index (MI)**: A composite score calculated from other metrics to gauge the ease of maintaining the code.1  
  4. **Halstead Metrics**: A suite of metrics based on the operators and operands in the source code.1

     These capabilities directly map to the requirements of the SelfAuditor's proposed heuristic.  
* **Architecture and Integration**: Radon is intentionally lightweight, with minimal external dependencies (mando, colorama, six), which makes it an excellent choice for embedding within a larger system like the SelfAuditor without introducing significant dependency conflicts or overhead. Its core analysis is performed by parsing the Python source code into an Abstract Syntax Tree (AST) and then traversing this tree to compute the metrics.10 Crucially,  
  Radon offers a well-defined programmatic API, allowing the SelfAuditor to directly invoke its "harvesters" and "visitors" to retrieve metric data as Python objects, rather than parsing text from a command-line interface.1 This API-driven approach is essential for building a robust and reliable automated system. The library also provides a  
  flake8 plugin, demonstrating its ability to integrate within the broader Python quality tooling ecosystem.1

##### **Wily (The Historical Analyst)**

Wily (version 1.25.0) is proposed as an optional component for analyzing trends in code quality over time.

* **Capabilities**: Wily's unique value proposition is its ability to provide historical context to code metrics.11 It achieves this by integrating with a project's Git history, iterating through past revisions (commits), and running metric analyzers (including  
  Radon by default) on the code at each point in time.6 This historical data is then stored and can be used to generate reports and graphs that show how metrics like Cyclomatic Complexity or Maintainability Index have evolved.6 This directly supports the brief's proposal to escalate refactoring priority for modules where complexity consistently increases over several revisions.  
* **Architecture and Integration**: The historical analysis comes at the cost of increased overhead. Wily maintains a local cache (a .wily/ directory) to store the metric data for each analyzed revision, which is more resource-intensive than the on-demand calculations performed by Radon.6 For the SelfAuditor's purposes,  
  Wily's most relevant feature is its diff command, which can compare the metrics of the current codebase against a specific Git reference, such as the previous commit (HEAD^1) or the main branch (master).13 This capability is perfectly suited for integration into a CI/CD pipeline, where the impact of a new pull request on code quality can be explicitly measured against the existing baseline.

#### **1.3. Comprehensive Linters: Pylint and Flake8**

While Radon and Wily are specialized metric calculators, Pylint and Flake8 are general-purpose linters that offer a much broader range of checks. They are relevant to the SelfAuditor as potential sources for identifying a wider variety of refactoring opportunities.

##### **Pylint (The Thorough Inspector)**

Pylint (version 3.3.7) is a mature and highly comprehensive static analysis tool.

* **Capabilities**: Pylint extends far beyond the scope of Radon. It not only checks for style violations (like pycodestyle) and errors (like pyflakes) but also searches for "code smells"—patterns that are not syntactically wrong but indicate deeper design problems.15 It can identify issues such as unused variables, dead code, unnecessary negations, and overly complex class structures (e.g., too many public methods).15 These are all valuable triggers for generating refactoring tasks.  
* **Architecture and Performance**: Pylint's power stems from its use of a dedicated library, astroid, to build an enhanced AST of the code. Unlike a standard AST, astroid performs type inference, allowing Pylint to understand the code's semantics more deeply.15 For example, it can determine that a variable is an instance of a specific class and check for valid method calls. This deep analysis makes  
  Pylint significantly more powerful but also slower than other linters.15  
* **Configurability**: Pylint is exceptionally configurable through a .pylintrc file. This allows teams to enable or disable specific checks, set custom naming conventions, and define thresholds for various metrics, such as maximum arguments, branches, or statements per function.17 This level of control is valuable for tuning the SelfAuditor's behavior.

##### **Flake8 (The Fast Gatekeeper)**

Flake8 (version 7.0.0) is a popular linter known for its speed and extensibility.

* **Capabilities**: Flake8 acts as a wrapper, integrating three distinct tools into a single command-line interface 21:  
  1. pyflakes: Detects logical errors like undefined names or unused imports.  
  2. pycodestyle: Enforces adherence to the PEP 8 style guide.  
  3. mccabe: Checks for Cyclomatic Complexity, similar to Radon.  
     This combination provides a solid baseline of error and style checking.  
* **Architecture and Performance**: Flake8 is faster than Pylint because its constituent parts perform more localized analysis without the deep type inference of astroid.19 Its most significant architectural feature is its robust plugin system, which allows the community to extend its capabilities with hundreds of additional checks, covering everything from docstring style to security issues.21

#### **1.4. The High-Performance Alternative: Ruff**

The initial research brief does not mention Ruff, yet the provided research snippets repeatedly identify it as a transformative tool in the Python linting landscape.19 Any modern system design must consider

Ruff as a primary candidate, as its existence fundamentally alters the traditional trade-offs between performance and comprehensiveness.

* **Capabilities**: Ruff is an extremely fast Python linter and code formatter, written in Rust.24 Its goal is to unify the functionality of many disparate tools into a single, cohesive interface. It can replace  
  Flake8, pycodestyle, pyflakes, isort, pydocstyle, and a large number of flake8 plugins and Pylint rules.24 Critically for the SelfAuditor's long-term vision,  
  Ruff has built-in, high-performance "fix" support, enabling automatic correction of many detected issues.24  
* **Performance**: Ruff's performance is its defining feature. Benchmarks and testimonials report it as being 10 to 100 times faster than Flake8 and even faster compared to Pylint.19 This speed makes it feasible to run an extensive set of checks in environments where performance is critical, such as in pre-commit hooks or even on every file save within an IDE. This capability challenges the traditional model where developers must choose between a fast but limited linter (like  
  Flake8) and a thorough but slow one (like Pylint).

#### **1.5. Synthesis and Tooling Recommendation for SelfAuditor**

Based on this comparative analysis, a multi-tool strategy is recommended for the SelfAuditor. No single tool perfectly fits all requirements, but a combination can provide a robust and flexible solution. The brief's proposal to use Radon is a valid starting point, but it can be significantly enhanced.

* **Core Metric Calculation**: Use **Radon**'s programmatic API for the primary heuristic. Its lightweight nature and direct access to CC and MI values make it the ideal choice for this specific, focused task.  
* **Expanded Refactoring Triggers**: To identify a richer set of refactoring opportunities, the SelfAuditor should be designed with a plugin architecture that can consume the structured output from a more comprehensive linter. **Ruff** is the strongly recommended choice for this role due to its exceptional performance, extensive rule set, and active development. Its speed minimizes the performance impact on the CI/CD pipeline, and its unifying nature simplifies the overall toolchain. Pylint remains a viable alternative if its unique, inference-based checks are deemed essential and its slower performance is acceptable.  
* **Historical Analysis**: The optional use of **Wily** for trend analysis remains a sound recommendation for monitoring the long-term health of critical modules.

This hybrid approach allows the SelfAuditor to be both precise in its core function (using Radon for the specified metrics) and extensible in its ability to detect a wide range of code smells that can be mapped to actionable refactoring patterns (using Ruff or Pylint).

The following table provides a consolidated comparison of the evaluated tools.

| Tool | Primary Function | Key Metrics/Checks | Relative Performance | Extensibility | Ideal Use Case in SelfAuditor Workflow |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Radon 5.1.0** | Lightweight Metric Calculator | CC, MI, Halstead, Raw Metrics 1 | Very Fast | Low (API for integration) | Core engine for calculating CC and MI values programmatically. |
| **Wily 1.25.0** | Historical Complexity Tracker | Tracks metrics from other tools (e.g., Radon) over Git history 6 | Slow (builds a cache) | Moderate (pluggable operators) | Optional analysis of complexity trends to escalate task priority. |
| **Pylint 3.3.7** | Comprehensive Static Analysis | Errors, code smells, style, refactoring suggestions, custom checks 15 | Slow | High (custom plugins) | Secondary analysis engine for detecting a wide range of code smells if deep type inference is required. |
| **Flake8 7.0.0** | Fast Linter Framework | Errors (pyflakes), style (pycodestyle), CC (mccabe) 21 | Fast | Very High (rich plugin ecosystem) | A good baseline for CI checks, but largely superseded by Ruff. |
| **Ruff** | High-Performance Linter/Formatter | Replaces Flake8, isort, pydocstyle, and many Pylint rules; has auto-fix 24 | Extremely Fast | Moderate (built-in rules, some plugin support) | Recommended secondary engine for fast, comprehensive analysis and identifying a broad set of refactoring candidates. |

### **Section 2: A Deep Dive into Core Software Quality Metrics**

To effectively design and configure the SelfAuditor, a precise understanding of the metrics it employs is essential. Cyclomatic Complexity and Maintainability Index are not arbitrary numbers; they are derived from decades of software engineering research and have specific mathematical foundations and interpretations.

#### **2.1. Cyclomatic Complexity (CC)**

Cyclomatic Complexity, first introduced by Thomas J. McCabe in 1976, is a fundamental metric for quantifying the structural complexity of a program.26

* **Theoretical Underpinnings**: At its core, Cyclomatic Complexity (also known as the McCabe number) measures the number of linearly independent paths through a program's source code.27 It is computed using the program's control-flow graph, where nodes represent blocks of sequential commands and edges represent transfers of control.27 The complexity,  
  M, can be calculated with the formula M=E−N+2P, where E is the number of edges, N is the number of nodes, and P is the number of connected components (for a single function, P=1).26 A simpler way to conceive of it is that CC corresponds to the number of decision points in the code plus one.10 A higher score indicates more decision logic, which directly correlates to greater difficulty in achieving full test coverage and a higher likelihood of defects.28  
* **Calculation in Python (Radon)**: The Radon library calculates CC by analyzing the Abstract Syntax Tree (AST) of a Python program.10 It begins with a baseline complexity of 1 for any function and increments this value for each statement that introduces a new decision branch. These include 10:  
  * if, elif  
  * for, while  
  * except  
  * with  
  * assert  
  * List, set, and dictionary comprehensions, and generator expressions (which are syntactic sugar for loops)  
  * Boolean operators and and or (due to short-circuiting behavior creating implicit branches)  
    Statements like else and finally do not increase complexity because they do not introduce a new decision; they are part of a decision already made by a preceding if or try block.10  
* **Interpretation and Industry Thresholds**: The interpretation of a CC score is crucial for setting meaningful thresholds. While not absolute, several widely cited guidelines exist:  
  * **1 – 10**: Simple, low-risk procedure. This range is broadly considered manageable and easy to test.14 McCabe's original recommendation was to limit complexity to 10\.27  
  * **11 – 20**: More complex, moderate risk. Code in this range is becoming more difficult to understand and requires more comprehensive testing.14 The brief's proposed threshold of 15 falls within this category.  
  * **21 – 50**: Complex, high risk. Such code is difficult to maintain and is considered error-prone.14  
  * **\> 50**: Untestable, very high risk. Code at this level is extremely difficult to reason about and is a prime candidate for immediate refactoring.14

    It is also noteworthy that Microsoft's code analysis tools for Visual Studio issue a warning when CC reaches 25, and SonarQube suggests a default threshold of 15.31 This indicates that while 10 is a common ideal, thresholds up to 20 are used in practice to define the boundary of acceptable complexity.

#### **2.2. Maintainability Index (MI)**

The Maintainability Index is a composite metric designed to provide a single, holistic score representing the ease with which source code can be supported and changed.10

* **Theoretical Underpinnings**: Proposed by Oman and Hagemeister in 1992, the MI combines several other metrics into a single polynomial equation.34 The intent is to capture multiple facets of maintainability—size, structural complexity, and (in some versions) documentation—in one value.  
* **Constituent Metrics and Formula Variations**: The MI is primarily calculated using three metrics 10:  
  1. **Halstead Volume (V)**: A measure of code size and complexity based on operators and operands.  
  2. **Cyclomatic Complexity (G)**: The total CC of the module.  
  3. **Source Lines of Code (L)**: The number of lines of code, excluding comments and blank lines (SLOC).

The research highlights several variations of the formula. The most relevant for the SelfAuditor is the one used by Microsoft Visual Studio and adopted by Radon.10 This formula rescales the original, unbounded index to a more intuitive range of 0 to 100, where a higher score indicates better maintainability:MI=max\[0,100×171171−5.2ln(V)−0.23G−16.2ln(L)​\]Another notable formula, from the Software Engineering Institute (SEI), incorporates the percentage of comment lines, rewarding well-documented code.10 However, the Visual Studio version is the de facto standard in many modern tools.

* **Interpretation and Thresholds**: A significant point of confusion in the field is the interpretation of MI scores, as different scales and thresholds are cited.  
  * **Original Scale (unbounded)**: Scores \>= 85 were considered highly maintainable, 65-85 moderate, and \< 65 difficult to maintain.12  
  * **Visual Studio Scale (0-100)**: This is the most prevalent modern scale. Here, the thresholds are typically color-coded:  
    * **20 – 100 (Green)**: Good maintainability.36  
    * **10 – 19 (Yellow)**: Moderate maintainability.36  
    * **0 – 9 (Red)**: Low maintainability, difficult to maintain.36

      Some sources provide slightly different but directionally similar ranges, such as 0-25 being "unmaintainable" and 25-50 being "worrying".14 The key takeaway is that on the 0-100 scale, the transition from acceptable to problematic occurs around the 20-point mark.

The proposed heuristic of flagging modules with an MI \< 60 is therefore misaligned with these common industry standards. On the Visual Studio scale used by Radon, a score of 59 is well within the "green" zone of good maintainability. Applying this threshold would likely generate a high volume of low-value tasks, creating noise and potentially leading to alert fatigue. A more effective threshold would be **MI \< 20**, which would flag code as it enters the "moderate" and "low" maintainability categories, focusing attention on areas that are genuinely problematic.

#### **2.3. Halstead Complexity Measures**

The Halstead complexity measures are a suite of metrics that form a foundational component of the Maintainability Index. Developed by Maurice Halstead in 1977, they attempt to measure software properties based on a simple count of operators and operands in the source code.39

* **Theoretical Underpinnings**: The theory posits that a program is a collection of tokens that can be classified as either operators (e.g., \+, if, def) or operands (e.g., variables, constants).40 By counting these, one can derive metrics related to the program's size, vocabulary, and the mental effort required to create it.  
* **Core Metrics**: The calculation begins with four basic counts from the source code 39:  
  * n1​: The number of *distinct* operators.  
  * n2​: The number of *distinct* operands.  
  * N1​: The *total* number of operators.  
  * N2​: The *total* number of operands.  
* **Derived Metrics**: From these base counts, several other measures are calculated, the most important of which for this report is the **Halstead Volume (V)**.  
  * **Program Vocabulary (n)**: n=n1​+n2​  
  * **Program Length (N)**: N=N1​+N2​  
  * Volume (V): V=N×log2​(n)  
    The Volume is intended to represent the size of the implementation in bits. Other derived metrics include Difficulty, Effort, Time to program, and estimated Bugs.39  
* **Relevance to SelfAuditor**: The primary relevance of Halstead metrics to the SelfAuditor is the role of **Halstead Volume (V)** as a key input to the Maintainability Index formula.10 While the other Halstead metrics are academically interesting, they are less commonly used in practical, day-to-day code quality gates compared to CC and MI. Therefore, the SelfAuditor should focus on CC and MI as the primary triggers for refactoring tasks, understanding that Halstead Volume is implicitly factored into the MI calculation.

---

## **Part II: Critical Evaluation of the SelfAuditor Proposal**

This part directly assesses the user's research brief, using the foundational knowledge from Part I to provide a rigorous critique and suggest refinements to its core components: the quality heuristic and the implementation architecture.

### **Section 3: Analysis of the Proposed Heuristic and Thresholds**

The effectiveness of the SelfAuditor hinges on a well-calibrated heuristic that can accurately identify code in need of refactoring without generating excessive noise. The proposed heuristic—flagging code where CC \> 15 or MI \< 60—serves as a solid starting point but requires critical evaluation and refinement based on established industry practices.

#### **3.1. Evaluating the Cyclomatic Complexity Threshold (CC \> 15\)**

The proposal to flag any function with a Cyclomatic Complexity (CC) greater than 15 is a reasonable, albeit aggressive, choice.

* **Contextual Analysis**: As established in Section 2.1, a CC score between 11 and 20 is widely categorized as indicating "moderate risk" or "more complex" code.14 A threshold of 15 places the trigger firmly within this range. It is more stringent than the default warning level of 25 used in Microsoft's Visual Studio analysis tools but less stringent than the ideal of 10 originally proposed by McCabe.27 This suggests it is a proactive threshold aimed at catching complexity before it becomes critical.  
* **Recommendation for a Tiered System**: While a single threshold is simple to implement, it lacks nuance. A function with a CC of 16 is treated identically to one with a CC of 40, yet the latter represents a significantly higher risk and maintenance burden. A more sophisticated and effective approach would be to implement a tiered threshold system that allows for more granular feedback and prioritization. For example:  
  * **CC \> 10 (Informational/Warning)**: Functions in the 11-20 range could be logged with a lower severity. These could be flagged for review during regular code maintenance cycles or used as learning opportunities for junior developers, without necessarily blocking a build or creating a high-priority task.  
  * **CC \> 20 (Critical/Error)**: Functions exceeding a complexity of 20 align with the "high risk" category.14 Breaching this threshold should trigger the full action proposed in the brief: the creation of a mandatory refactoring task in  
    tasks.yml.  
    This tiered approach provides more valuable information to the downstream Planner component, enabling it to prioritize tasks more intelligently. It separates "code that is becoming complex" from "code that is already critically complex."

#### **3.2. Evaluating the Maintainability Index Threshold (MI \< 60\)**

The proposed threshold to flag modules with a Maintainability Index (MI) of less than 60 is fundamentally misaligned with the standard interpretation of the metric and would be counterproductive in practice.

* **Contextual Analysis**: As detailed in Section 2.2, the Radon library calculates MI using the Visual Studio formula, which produces a score on a bounded 0-100 scale.10 On this scale, a score of 60 falls comfortably within the "green" or "good maintainability" range (20-100).36 Triggering a refactoring task for a module with an MI of 59 would flag code that is, by industry standards, considered perfectly maintainable. This would create a high volume of false positives, leading to alert fatigue and a loss of trust in the SelfAuditor system.  
* **Recommendation for a Corrected Threshold**: The MI threshold must be lowered significantly to be effective. A much more appropriate trigger would be **MI \< 20**. This value corresponds to the boundary where code transitions from "good" (green) to "moderately maintainable" (yellow).36 This ensures that the SelfAuditor flags only those modules that are genuinely approaching or have entered a state of poor maintainability, making the generated tasks more meaningful and actionable.  
* **Considering the Limitations of MI**: It is also important to acknowledge the known criticisms of the Maintainability Index. The metric can be heavily influenced by the raw lines of code and the percentage of comments, sometimes producing a low score for a very long but structurally simple file.10 This reinforces the idea that MI should not be used in isolation. The SelfAuditor's logic should consider both metrics. For example, a module with a low MI but where all constituent functions have a low CC might be a lower-priority candidate for refactoring than a module with both a low MI and at least one function with a high CC.

#### **3.3. The Role of Historical Trends with Wily**

The proposal to optionally use Wily to track complexity trends over time is an advanced and valuable feature.

* **Value Proposition**: Static, point-in-time analysis can miss the gradual erosion of code quality. A module's complexity might increase from 8 to 10 to 12 over three successive commits. While none of these values breach the "critical" threshold, the trend is concerning. Wily is designed to detect exactly this kind of "boiling frog" scenario.6 By analyzing metrics across Git history, it provides the context that a single snapshot lacks.12 The brief's suggestion to escalate priority if complexity rises over three revisions is a sound and practical application of this principle.  
* **Overhead and Implementation**: The primary trade-off is the overhead associated with Wily. It requires building and maintaining a cache of metric data, which consumes storage and processing time.6 Therefore, keeping its use optional, as the brief suggests, is a pragmatic approach. The SelfAuditor should be designed to query  
  Wily's data if available but to function correctly without it. This makes it suitable for projects where the historical analysis is deemed critical for core components but unnecessary for experimental or short-lived feature branches.

### **Section 4: Architectural Review of the Implementation Strategy**

The proposed architecture for the SelfAuditor is conceptually strong, but its success depends heavily on the details of its implementation, particularly the interface between its components.

#### **4.1. The "Auditor Proposes, Planner Executes" Model**

The decision to decouple the auditor from any code modification logic is a key architectural strength.

* **Strengths**: This design adheres to the Single Responsibility Principle, a cornerstone of robust software design.32  
  * **The Auditor**: Its sole responsibility is to analyze code and report findings. It is a pure analysis component.  
  * The Planner/Executor: Their responsibility is to interpret the findings and act upon them.  
    This separation makes the system safer, as the Auditor itself cannot introduce breaking changes. It also enhances modularity and testability. The Auditor can be tested in isolation by providing it with sample code and verifying its output, without needing a complex execution environment. Similarly, the Planner and Executor can be tested by feeding them a synthetic tasks.yml file.  
* **Potential Weaknesses**: The primary weakness of this model is the inherent latency in its feedback loop. A developer might commit code that violates a quality threshold, but this issue is only flagged after the CI pipeline completes. The corresponding refactoring task might not be scheduled by the Planner until a future sprint. This delay contrasts sharply with the immediate feedback provided by tools integrated into the developer's local environment, such as IDE plugins or pre-commit hooks.44 While the "propose-plan-execute" model is excellent for systemic, managed improvement, it is not a substitute for rapid, local feedback. This architectural consideration will be addressed in the strategic recommendations in Part III.

#### **4.2. The tasks.yml as an Actionable Interface**

The tasks.yml file is the central API contract between the SelfAuditor and the rest of the automated system. Its design is paramount to the system's success. A vague task description like "Refactor module X" is insufficient for automation and of limited use to a human developer. The task must be structured, detailed, and machine-readable.

For an automated Planner and Executor to function, they require explicit instructions. The task entry must encode the *what* (the specific refactoring pattern to apply), the *where* (the precise location in the code), and the *why* (the metric violation that triggered the task). This transforms the tasks.yml file from a simple to-do list into a high-fidelity, automated workflow manifest.

* **Recommendation for a tasks.yml Schema**: To enable true automation and provide clear, actionable insights, the following detailed YAML schema is proposed for each task entry:  
  YAML  
  \- task\_id: "REF-2025-07-15-A1B2C3D4"  
    source\_commit: "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"  
    rule\_id: "COMPLEXITY\_CYCLOMATIC\_CRITICAL"  
    message: "Function 'process\_complex\_data' in module 'src/core/processing.py' has a Cyclomatic Complexity of 22, exceeding the critical threshold of 20."  
    location:  
      file: "src/core/processing.py"  
      entity\_type: "function"  
      entity\_name: "process\_complex\_data"  
      start\_line: 45  
      end\_line: 150  
    metrics:  
      cyclomatic\_complexity: 22  
      maintainability\_index: 18  
      source\_lines\_of\_code: 105  
    recommended\_refactoring:  
      pattern: "Extract Method"  
      justification: "Function exceeds complexity and length thresholds, suggesting it has multiple responsibilities that could be separated into smaller, more focused functions."  
      \# An advanced, AI-assisted auditor could populate this section:  
      \# suggested\_implementation: |  
      \#   def \_validate\_input(data):  
      \#       \#... validation logic...  
      \#   def \_calculate\_metrics(validated\_data):  
      \#       \#... calculation logic...

This structured format provides several key advantages:

* **Actionability**: It gives a human developer or an automated Executor precise information about where to look and what to do.  
* **Justification**: It clearly states *why* the task was created by including the specific rule and metric values that were violated.  
* **Traceability**: The task\_id and source\_commit allow the task to be tracked back to the specific code change that introduced the quality issue.  
* **Extensibility**: The schema can be extended to include more complex information, such as AI-generated implementation suggestions, without breaking the core structure.

Adopting such a schema is a prerequisite for moving beyond simple reporting and toward a truly automated code quality management system.

---

## **Part III: Strategic Recommendations for Implementation and Evolution**

This final part provides a forward-looking strategy for building and evolving the SelfAuditor. It synthesizes the analysis from the previous parts into a set of actionable recommendations for integrating the system into a modern, effective development workflow and planning for its future growth.

### **Section 5: A Multi-Tiered Strategy for Code Quality Enforcement**

Relying on a single point of quality enforcement is a brittle strategy. A robust system should employ multiple layers of feedback, balancing speed, and analytical depth. The developer experience is significantly improved by immediate feedback for simple issues, while the organization requires deep, auditable checks to ensure long-term quality. Therefore, the SelfAuditor should not exist in isolation but as the centerpiece of a multi-tiered quality strategy.

This approach addresses the primary weakness of the CI-based Auditor: its feedback latency.44 By combining fast, local checks with slower, comprehensive CI checks, the system can provide the right feedback at the right time.

#### **5.1. The Inner Loop: Pre-commit Hooks for Immediate Feedback**

The first tier of quality enforcement should occur on the developer's local machine, providing feedback before code is even committed. This is best accomplished using pre-commit hooks.

* **Recommendation**: Implement a standard set of pre-commit hooks using the pre-commit framework.46 This framework standardizes the management and execution of hooks across the development team, ensuring consistency. The configuration file (  
  .pre-commit-config.yaml) should be checked into the repository.47  
* **Tooling**: The hooks in this tier must be extremely fast to avoid frustrating developers and encouraging them to use the \--no-verify bypass.44 For this reason,  
  **Ruff** is the ideal tool.24 It can perform linting, formatting, and import sorting in milliseconds. A configuration could include checks for basic errors, style violations, and code formatting. This catches a large class of trivial issues instantly, reducing noise in pull requests and saving CI resources.

#### **5.2. The Outer Loop: CI/CD Integration for Comprehensive Analysis**

The second tier is the CI/CD pipeline, which is the proper environment for the SelfAuditor's deep analysis.

* **Recommendation**: The SelfAuditor should be configured as a dedicated job within the CI/CD pipeline (e.g., using GitHub Actions or GitLab CI) that runs on every pull request or push to a main branch.48  
* **Functionality**: This is where the time-consuming analysis should occur:  
  1. **Metric Calculation**: The Auditor uses Radon to calculate CC and MI for all modified files.  
  2. **Trend Analysis**: It optionally queries the Wily cache to check for negative trends in complexity.  
  3. **Task Generation**: If any thresholds defined in the refined heuristic are breached, the Auditor generates a structured task and appends it to tasks.yml, as detailed in Section 4.2.  
* **Quality Gates**: The CI job should be configured as a "quality gate".51 Initially, it can be non-blocking, meaning it generates tasks but does not fail the build. This allows the team to acclimate to the new process. Over time, it can be made stricter. For example, a breach of a "critical" threshold (e.g., CC \> 20\) could be configured to fail the pipeline, preventing the merge of code that does not meet the organization's quality standards.

#### **5.3. Synthesizing the Workflow**

The combined, multi-tiered workflow provides a comprehensive quality net:

1. **Local Development**: A developer writes code in their IDE.  
2. **Commit Time**: The developer runs git commit. The pre-commit framework automatically triggers fast checks using Ruff. It formats the code, sorts imports, and flags simple errors. The developer receives feedback in seconds and can fix issues before the commit is finalized.  
3. **Push/Pull Request**: The developer pushes their changes, creating a pull request.  
4. **CI/CD Pipeline**: The push event triggers the CI/CD pipeline. One of the jobs is the **SelfAuditor**.  
   * The SelfAuditor runs its deep analysis on the changed files using Radon and Wily.  
   * It compares the calculated metrics against the refined, tiered thresholds.  
   * If a threshold is breached, it appends a detailed, structured refactoring task to tasks.yml.  
   * The job reports its status. If configured as a blocking quality gate, it may fail the build, preventing the merge until the critical issue is addressed.  
5. **Planning and Execution**: In a separate process, the automated **Planner** component consumes tasks.yml, prioritizes the refactoring work, and schedules it for future sprints or assigns it to an automated **Executor**.

This workflow ensures that developers are not burdened with slow local checks, trivial style issues are handled automatically, and deep-seated quality problems are systematically identified, tracked, and resolved.

### **Section 6: Advanced Refactoring: From Pattern Identification to Automated Task Generation**

The ultimate goal of the SelfAuditor is not just to report numbers but to generate actionable tasks that lead to concrete improvements in the codebase. This requires a clear mapping from static analysis results to specific, well-defined refactoring patterns.

#### **6.1. Automating the Detection of Refactoring Opportunities**

The brief identifies three key refactoring patterns. The SelfAuditor's logic can be designed to detect candidates for these patterns based on the output of its analysis tools.

The following table provides a blueprint for this mapping.

| Refactoring Pattern | Description | Primary Triggering Metric(s) | Supporting Tool(s) | Example tasks.yml Snippet |
| :---- | :---- | :---- | :---- | :---- |
| **Extract Method** | Split a large, complex function into smaller, single-responsibility functions.52 | High Cyclomatic Complexity (e.g., CC \> 20). High function length (e.g., LLOC \> 80). | Radon, Pylint, Ruff | rule\_id: COMPLEXITY\_CYCLOMATIC\_CRITICAL recommended\_refactoring: { pattern: "Extract Method" } |
| **Introduce Parameter Object** | Group a recurring set of parameters into a dedicated data class or object.53 | Data Clumps: The same group of 3+ parameters appearing in multiple function signatures. | Pylint or custom AST analysis. | rule\_id: CODE\_SMELL\_DATA\_CLUMP recommended\_refactoring: { pattern: "Introduce Parameter Object" } |
| **Replace Conditional with Polymorphism** | Move conditional logic that switches on an object's type into separate classes.54 | High CC in a function that primarily consists of an if/elif chain checking an object's type or state. | Radon (for CC), Pylint (for AST structure analysis) | rule\_id: REFACTOR\_POLYMORPHISM\_CANDIDATE recommended\_refactoring: { pattern: "Replace Conditional with Polymorphism" } |

* **Extract Method**: This is the most straightforward pattern to detect. A function with a high CC score or an excessive number of statements/lines is a prime candidate.52 The metrics from  
  Radon or Pylint can directly trigger this recommendation. The generated task in tasks.yml should pinpoint the specific function that is too large.  
* **Introduce Parameter Object**: Detecting this pattern is more complex as it requires cross-function analysis. It cannot be identified by looking at a single function in isolation. The analyzer needs to identify "data clumps"—identical groups of parameters that are passed to multiple, different functions.53 This capability is beyond  
  Radon and would require a more advanced static analysis engine, such as a custom Pylint checker or a dedicated AST traversal script, that can build a model of function signatures across the codebase.  
* **Replace Conditional with Polymorphism**: This pattern is suggested when a single function contains complex conditional logic (high CC) that switches based on the type or state of an object.54 The trigger would be a combination of high CC and an AST analysis that identifies a dominant  
  if/elif/else or switch-like structure checking the same variable in each branch. The generated task should identify the conditional block and the variable it is switching on.

#### **6.2. Generating High-Fidelity Refactoring Tasks**

As emphasized in Section 4.2, the value of the SelfAuditor is directly proportional to the quality of the tasks it generates. By using the proposed structured schema and the trigger mapping from Section 6.1, the system can produce tasks that are not just reports but are true inputs to an automated or semi-automated workflow. The metrics section of the task provides the quantitative evidence ("the why"), while the location and recommended\_refactoring sections provide the actionable instructions ("the where" and "the what").

#### **6.3. Exploring AI-Assisted Refactoring**

While the brief describes a deterministic, rule-based system, the field of software development is rapidly being influenced by Large Language Models (LLMs) and AI-assisted tooling.57 A forward-looking vision for the SelfAuditor should incorporate this trend.

* **Recommendation for Future Evolution**: An advanced version of the SelfAuditor could use its deterministic analysis as a high-quality prompt for an LLM. For an Extract Method task, for example, the Auditor would first identify the problematic function using Radon. It would then pass the source code of that function to an LLM with a prompt like: "Refactor the following Python function by extracting logical sub-components into new private methods. The primary function has a Cyclomatic Complexity of 22."

The LLM could then generate suggested implementations for the smaller methods. These suggestions would be added to the tasks.yml file, providing the human developer or the automated Executor with a concrete, ready-to-test starting point. This approach combines the rigor of static analysis (identifying the problem) with the generative power of AI (suggesting a solution), potentially accelerating the refactoring process significantly.57

### **Section 7: Future-Proofing the SelfAuditor: Extensibility and Long-Term Vision**

To ensure the SelfAuditor remains a valuable asset as the codebase and the tooling ecosystem evolve, it must be designed for extensibility from the outset.

#### **7.1. A Plugin Architecture for New Metrics and Tools**

The SelfAuditor's core logic should not be tightly coupled to a specific tool like Radon.

* **Recommendation**: Design the system around a **plugin-based architecture**. Define a generic "MetricProvider" interface that specifies methods for analyzing a file and returning a structured report. The initial implementation would consist of a RadonMetricProvider. In the future, a PylintMetricProvider, RuffMetricProvider, or even a SecurityMetricProvider could be added without altering the core auditing engine. This approach makes the system highly extensible and adaptable to new tools and new definitions of "quality."

#### **7.2. Long-Term Recommendations**

Beyond the initial implementation, the SelfAuditor can evolve into a more comprehensive quality management platform.

* **Integrate Security Scanning**: The definition of code quality should be expanded to include security. By adding a plugin for a Static Application Security Testing (SAST) tool like Bandit, the SelfAuditor could also flag potential security vulnerabilities and generate tasks for their remediation.19  
* **Expand Beyond Complexity**: The system should incorporate checks for other significant code smells that are strong indicators for refactoring. One of the most valuable is **code duplication**. Tools like Pylint's symilar or other specialized clones detectors can be integrated to identify duplicated blocks of code, which are prime candidates for an Extract Method or Extract Class refactoring.15  
* **Establish a Feedback Loop**: True continuous improvement requires a closed loop. The system should not only generate tasks but also track their resolution. By correlating task completion with subsequent metric scans, the SelfAuditor can measure the impact of the refactoring work. This data is invaluable for:  
  1. **Validating the Heuristics**: If completing a certain type of refactoring task consistently leads to a significant improvement in MI, it validates the rule that generated it.  
  2. **Demonstrating ROI**: By tracking the overall improvement in codebase metrics over time, the team can demonstrate the tangible return on investment of the SelfAuditor project and the associated refactoring effort.

By following these strategic recommendations, the SelfAuditor can be developed into a powerful, extensible, and future-proof system that systematically improves code quality, reduces technical debt, and enhances developer productivity.

#### **Works cited**

1. Welcome to Radon's documentation\! — Radon 4.1.0 documentation, accessed on July 9, 2025, [https://radon.readthedocs.io/en/latest/](https://radon.readthedocs.io/en/latest/)  
2. radon \- PyPI, accessed on July 9, 2025, [https://pypi.org/project/radon/0.4/](https://pypi.org/project/radon/0.4/)  
3. Learning About Code Metrics in Python with Radon, accessed on July 9, 2025, [https://www.blog.pythonlibrary.org/2023/09/20/learning-about-code-metrics-in-python-with-radon/](https://www.blog.pythonlibrary.org/2023/09/20/learning-about-code-metrics-in-python-with-radon/)  
4. RadonPy is a Python library to automate physical property calculations for polymer informatics. \- GitHub, accessed on July 9, 2025, [https://github.com/RadonPy/RadonPy](https://github.com/RadonPy/RadonPy)  
5. radon-repository-miner 0.8.13 documentation \- GitHub Pages, accessed on July 9, 2025, [https://radon-h2020.github.io/radon-repository-miner/](https://radon-h2020.github.io/radon-repository-miner/)  
6. Wily — wily develop documentation, accessed on July 9, 2025, [https://wily.readthedocs.io/](https://wily.readthedocs.io/)  
7. Maintain readability of code in time with Wily | by Aritra Biswas \- Medium, accessed on July 9, 2025, [https://medium.com/@pandalearnstocode/maintain-readability-of-code-in-time-with-wily-b57c0c1e6ff](https://medium.com/@pandalearnstocode/maintain-readability-of-code-in-time-with-wily-b57c0c1e6ff)  
8. Wily Homepage, accessed on July 9, 2025, [http://www.cs.yorku.ca/\~oz/wily/](http://www.cs.yorku.ca/~oz/wily/)  
9. 9wm/wily: Gary Capell's wily, an acme work-alike \- GitHub, accessed on July 9, 2025, [https://github.com/9wm/wily](https://github.com/9wm/wily)  
10. Introduction to Code Metrics \- Radon's documentation\! \- Read the Docs, accessed on July 9, 2025, [https://radon.readthedocs.io/en/latest/intro.html](https://radon.readthedocs.io/en/latest/intro.html)  
11. Counteracting Code Complexity With Wily \- The Python Podcast.init, accessed on July 9, 2025, [https://www.pythonpodcast.com/wily-code-complexity-episode-195/](https://www.pythonpodcast.com/wily-code-complexity-episode-195/)  
12. Simplify your Python Code: Automating Code Complexity Analysis with Wily, accessed on July 9, 2025, [https://towardsdatascience.com/simplify-your-python-code-automating-code-complexity-analysis-with-wily-5c1e90c9a485/](https://towardsdatascience.com/simplify-your-python-code-automating-code-complexity-analysis-with-wily-5c1e90c9a485/)  
13. Using Wily in a CI/CD pipeline \- Read the Docs, accessed on July 9, 2025, [https://wily.readthedocs.io/en/latest/ci.html](https://wily.readthedocs.io/en/latest/ci.html)  
14. Wily \- Python for Data Science 24.3.0, accessed on July 9, 2025, [https://www.python4data.science/en/24.3.0/productive/qa/wily.html](https://www.python4data.science/en/24.3.0/productive/qa/wily.html)  
15. Pylint 3.3.7 documentation, accessed on July 9, 2025, [https://pylint.readthedocs.io/](https://pylint.readthedocs.io/)  
16. How To Get Started With Pylint. Star your python code. | by Oliyadk | Medium, accessed on July 9, 2025, [https://medium.com/@oliyadkebede32/how-to-get-started-with-pylint-79bf950f61a8](https://medium.com/@oliyadkebede32/how-to-get-started-with-pylint-79bf950f61a8)  
17. Pylint features — Pylint 1.5.4 documentation, accessed on July 9, 2025, [https://docs.pylint.org/features.html](https://docs.pylint.org/features.html)  
18. pylint·PyPI, accessed on July 9, 2025, [https://pypi.org/project/pylint/](https://pypi.org/project/pylint/)  
19. Trunk \- Comparing Ruff, Flake8, and Pylint | Linting Speed \- Trunk.io, accessed on July 9, 2025, [https://trunk.io/learn/comparing-ruff-flake8-and-pylint-linting-speed](https://trunk.io/learn/comparing-ruff-flake8-and-pylint-linting-speed)  
20. Pylint configuration \- Codeac, accessed on July 9, 2025, [https://www.codeac.io/documentation/pylint-configuration.html](https://www.codeac.io/documentation/pylint-configuration.html)  
21. PyCQA/flake8: flake8 is a python tool that glues together pycodestyle, pyflakes, mccabe, and third-party plugins to check the style and quality of some python code. \- GitHub, accessed on July 9, 2025, [https://github.com/PyCQA/flake8](https://github.com/PyCQA/flake8)  
22. Flake8 \- PyPI, accessed on July 9, 2025, [https://pypi.org/project/flake8/](https://pypi.org/project/flake8/)  
23. Any advantages of Flake8 over PyLint? : r/Python \- Reddit, accessed on July 9, 2025, [https://www.reddit.com/r/Python/comments/82hgzm/any\_advantages\_of\_flake8\_over\_pylint/](https://www.reddit.com/r/Python/comments/82hgzm/any_advantages_of_flake8_over_pylint/)  
24. astral-sh/ruff: An extremely fast Python linter and code formatter, written in Rust. \- GitHub, accessed on July 9, 2025, [https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff)  
25. Few choices of linter and formatter \- HackMD, accessed on July 9, 2025, [https://hackmd.io/@dinhanhx/B1vXJdGAi](https://hackmd.io/@dinhanhx/B1vXJdGAi)  
26. What is Cyclomatic Complexity? Definition Guide & Examples \- Sonar, accessed on July 9, 2025, [https://www.sonarsource.com/learn/cyclomatic-complexity/](https://www.sonarsource.com/learn/cyclomatic-complexity/)  
27. Cyclomatic complexity \- Wikipedia, accessed on July 9, 2025, [https://en.wikipedia.org/wiki/Cyclomatic\_complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity)  
28. What Is Cyclomatic Complexity and How to Calculate Cyclomatic Complexity? \- Perforce, accessed on July 9, 2025, [https://www.perforce.com/blog/qac/what-cyclomatic-complexity](https://www.perforce.com/blog/qac/what-cyclomatic-complexity)  
29. Cyclomatic Complexity 101: Benefits, Drawbacks & Best Practices \- Brainhub, accessed on July 9, 2025, [https://brainhub.eu/library/measuring-cyclomatic-complexity](https://brainhub.eu/library/measuring-cyclomatic-complexity)  
30. Mastering Maintainability Metrics in Software \- Number Analytics, accessed on July 9, 2025, [https://www.numberanalytics.com/blog/mastering-maintainability-metrics-software](https://www.numberanalytics.com/blog/mastering-maintainability-metrics-software)  
31. Code metrics \- Cyclomatic complexity \- Visual Studio (Windows ..., accessed on July 9, 2025, [https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-cyclomatic-complexity?view=vs-2022](https://learn.microsoft.com/en-us/visualstudio/code-quality/code-metrics-cyclomatic-complexity?view=vs-2022)  
32. Managing Code Complexity | Developer Guidelines, accessed on July 9, 2025, [https://devguide.trimble.com/development-practices/managing-code-complexity/](https://devguide.trimble.com/development-practices/managing-code-complexity/)  
33. Quality Metrics \- Maintainability Index \- YouTube, accessed on July 9, 2025, [https://www.youtube.com/watch?v=0JhcrZvEWLA](https://www.youtube.com/watch?v=0JhcrZvEWLA)  
34. Maintainability Index \- Manoj Phadnis, accessed on July 9, 2025, [https://www.manojphadnis.net/code-analysis/code-metrics/maintainability-index](https://www.manojphadnis.net/code-analysis/code-metrics/maintainability-index)  
35. SEI maintanability index | objectscriptQuality, accessed on July 9, 2025, [https://objectscriptquality.com/docs/metrics/sei-maintanability-index](https://objectscriptquality.com/docs/metrics/sei-maintanability-index)  
36. Maintainability Index \- What is it and where does it fall short? \- Sourcery, accessed on July 9, 2025, [https://sourcery.ai/blog/maintainability-index](https://sourcery.ai/blog/maintainability-index)  
37. Visual Studio Code Metrics and the Maintainability index of switch case \- Stack Overflow, accessed on July 9, 2025, [https://stackoverflow.com/questions/2936814/visual-studio-code-metrics-and-the-maintainability-index-of-switch-case](https://stackoverflow.com/questions/2936814/visual-studio-code-metrics-and-the-maintainability-index-of-switch-case)  
38. Code Metrics – Maintainability Index \- The Ultimate Visual Studio Tips and Tricks Blog, accessed on July 9, 2025, [https://people.scs.carleton.ca/\~jeanpier/sharedF14/T1/extra%20stuff/about%20metrics/Code%20Metrics%20%E2%80%93%20Maintainability%20Index%20-%20The%20Ultimate%20Visual%20Studio%20Tips%20and%20Tricks%20Blog%20-%20Site%20Home%20-%20MSDN%20Blogs.pdf](https://people.scs.carleton.ca/~jeanpier/sharedF14/T1/extra%20stuff/about%20metrics/Code%20Metrics%20%E2%80%93%20Maintainability%20Index%20-%20The%20Ultimate%20Visual%20Studio%20Tips%20and%20Tricks%20Blog%20-%20Site%20Home%20-%20MSDN%20Blogs.pdf)  
39. Halstead Metrics \- IBM, accessed on July 9, 2025, [https://www.ibm.com/docs/en/devops-test-embedded/9.0.0?topic=metrics-halstead](https://www.ibm.com/docs/en/devops-test-embedded/9.0.0?topic=metrics-halstead)  
40. Halstead complexity measures \- Wikipedia, accessed on July 9, 2025, [https://en.wikipedia.org/wiki/Halstead\_complexity\_measures](https://en.wikipedia.org/wiki/Halstead_complexity_measures)  
41. Software Design Complexity, accessed on July 9, 2025, [https://sceweb.uhcl.edu/helm/WEBPAGES-SoftwareEngineering/myfiles/TableContents/Module-10/software\_design\_complexity.html](https://sceweb.uhcl.edu/helm/WEBPAGES-SoftwareEngineering/myfiles/TableContents/Module-10/software_design_complexity.html)  
42. Mastering Halstead Complexity Measures \- Number Analytics, accessed on July 9, 2025, [https://www.numberanalytics.com/blog/mastering-halstead-complexity-measures](https://www.numberanalytics.com/blog/mastering-halstead-complexity-measures)  
43. Understanding Code Complexity: Measurement and Reduction Techniques \- Metabob, accessed on July 9, 2025, [https://metabob.com/blog-articles/understanding-code-complexity-measurement-and-reduction-techniques.html](https://metabob.com/blog-articles/understanding-code-complexity-measurement-and-reduction-techniques.html)  
44. Pre-Commit or CI/CD. At work, we're moving from a… | by Craig ..., accessed on July 9, 2025, [https://motlin.medium.com/pre-commit-or-ci-cd-5779d3a0e566](https://motlin.medium.com/pre-commit-or-ci-cd-5779d3a0e566)  
45. pre-commit vs. CI \- Sebastian Witowski, accessed on July 9, 2025, [https://switowski.com/blog/pre-commit-vs-ci/](https://switowski.com/blog/pre-commit-vs-ci/)  
46. pre-commit, accessed on July 9, 2025, [https://pre-commit.com/](https://pre-commit.com/)  
47. Implementing pre-commit hooks to enforce code quality \- Graphite, accessed on July 9, 2025, [https://graphite.dev/guides/implementing-pre-commit-hooks-to-enforce-code-quality](https://graphite.dev/guides/implementing-pre-commit-hooks-to-enforce-code-quality)  
48. Integrating Code Quality Checks in CI/CD Pipelines for Faster ..., accessed on July 9, 2025, [https://www.ijcttjournal.org/2025/Volume-73%20Issue-3/IJCTT-V73I3P115.pdf](https://www.ijcttjournal.org/2025/Volume-73%20Issue-3/IJCTT-V73I3P115.pdf)  
49. How to Integrate Code Review Tools into Your CI/CD Pipeline \- PixelFreeStudio Blog, accessed on July 9, 2025, [https://blog.pixelfreestudio.com/how-to-integrate-code-review-tools-into-your-ci-cd-pipeline/](https://blog.pixelfreestudio.com/how-to-integrate-code-review-tools-into-your-ci-cd-pipeline/)  
50. Code Quality \- GitLab Docs, accessed on July 9, 2025, [https://docs.gitlab.com/ci/testing/code\_quality/](https://docs.gitlab.com/ci/testing/code_quality/)  
51. Continuous Code Quality: Integrating Static Code Analysis in CI/CD Pipelines, accessed on July 9, 2025, [https://blog.codacy.com/continuous-code-quality](https://blog.codacy.com/continuous-code-quality)  
52. Extract Method \- Refactoring.Guru, accessed on July 9, 2025, [https://refactoring.guru/extract-method](https://refactoring.guru/extract-method)  
53. Introduce Parameter Object \- Refactoring.Guru, accessed on July 9, 2025, [https://refactoring.guru/introduce-parameter-object](https://refactoring.guru/introduce-parameter-object)  
54. Replace Conditional with Polymorphism \- Refactoring.Guru, accessed on July 9, 2025, [https://refactoring.guru/replace-conditional-with-polymorphism](https://refactoring.guru/replace-conditional-with-polymorphism)  
55. Extract method | PyCharm Documentation \- JetBrains, accessed on July 9, 2025, [https://www.jetbrains.com/help/pycharm/extract-method.html](https://www.jetbrains.com/help/pycharm/extract-method.html)  
56. Long Parameter List \- Refactoring.Guru, accessed on July 9, 2025, [https://refactoring.guru/smells/long-parameter-list](https://refactoring.guru/smells/long-parameter-list)  
57. Together We Go Further: LLMs and IDE Static Analysis for ... \- arXiv, accessed on July 9, 2025, [https://arxiv.org/abs/2401.15298](https://arxiv.org/abs/2401.15298)  
58. 5 Essential AI Code Refactoring Tool Comparisons for Developers \- Kodezi Blog, accessed on July 9, 2025, [https://blog.kodezi.com/5-essential-ai-code-refactoring-tool-comparisons-for-developers/](https://blog.kodezi.com/5-essential-ai-code-refactoring-tool-comparisons-for-developers/)  
59. CodeGPT: AI Agents for Software Development, accessed on July 9, 2025, [https://codegpt.co/](https://codegpt.co/)  
60. Python Refactorings \- Part 8 \- Sourcery, accessed on July 9, 2025, [https://sourcery.ai/blog/explaining-refactorings-8/](https://sourcery.ai/blog/explaining-refactorings-8/)