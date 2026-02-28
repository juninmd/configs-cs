```markdown
# AGENTS.md - AI Coding Agent Guidelines

These guidelines are designed to ensure the consistent, efficient, and robust development of AI coding agents within this repository.  Adherence to these principles is critical for maintainability and quality.

## 1. DRY (Don't Repeat Yourself)

*   All code should have a single, clear purpose.
*   Avoid duplicating functionality or logic.
*   When functionality is reused, it should be clearly identified and isolated.
*   Modularize code where possible to reduce redundancy.

## 2. KISS (Keep It Simple, Stupid)

*   Prioritize readability and clarity.
*   Use the simplest solution that achieves the desired outcome.
*   Avoid unnecessary complexity.
*   Strive for straightforward logic and minimal dependencies.

## 3. SOLID Principles

*   **Single Responsibility Principle:** Each class or module should have one, and only one, reason to change.
*   **Open/Closed Principle:** The system should be open for extension but closed for modification.  New features should be implemented without altering existing code.
*   **Liskov Substitution Principle:**  Subclasses must be substitutable for their base classes without altering the correctness of the program.
*   **Interface Segregation Principle:** Clients should not be forced to implement interfaces they do not use.
*   **Dependency Inversion Principle:** Client code should not depend on implementation details.

## 4. YAGNI (You Aren't Gonna Need It)

*   Do not implement features or functionalities that are not currently required.
*   Focus on the essential requirements for the current iteration.
*   Avoid adding unnecessary complexity or features that could be removed later.

## 5. Code Structure & Formatting

*   **File Size Limit:** Each file should not exceed 180 lines of code.
*   **Naming Conventions:** Use consistent naming conventions (e.g., camelCase, snake_case).
*   **Comments:** Provide clear and concise comments to explain complex logic or decisions.  Keep comments focused on *why* not *what*.
*   **Documentation:** Clearly document each function, class, and module with a concise description of its purpose and inputs/outputs.
*   **Code Clarity:** Prioritize readability. Use whitespace to improve visual organization.
*   **Error Handling:**  Implement basic error handling where appropriate to minimize unexpected crashes.

## 6. Test Coverage

*   **All Development Must Be Productive:** The primary focus is on building and testing the AI coding agent’s functionality.
*   **Mocking Only for Tests:**  Use mocks and stubs for testing purposes *only*.  Do not use real implementations in tests.
*   **Test Cases:** Each function and class should have comprehensive test cases covering all edge cases and expected scenarios.
*   **Test Reporting:**  Implement robust test reporting to quickly identify any regressions or failures.

## 7.  Specific Requirements (Example - Adapt as needed):

*   **Data Structures:** Utilize appropriate data structures for efficient data storage and manipulation.
*   **Algorithm Selection:** Carefully consider the most efficient algorithms for each task.
*   **Error Reporting:** Implement informative error messages and logging.
*   **Logging:** Use a logging framework to record events and debugging information.
*   **Configuration:**  Provide a clear and well-documented way to configure the agent.

## 8.  Version Control

*   Use Git for version control.
*   Commit frequently with descriptive commit messages.
*   Follow a branching strategy (e.g., Gitflow).

## 9.  Documentation Standards

*   All code and comments should be updated as needed.
*   Document APIs and data structures concisely.

## 10.  Framework & Libraries (Example - Adapt as needed):

*   Utilize a well-established AI framework (e.g., TensorFlow, PyTorch) if applicable.
*   Choose appropriate libraries for specific tasks.

These guidelines will ensure the creation of high-quality, maintainable, and reliable AI coding agents within this repository. Compliance with these principles is mandatory for all future development activities.
```