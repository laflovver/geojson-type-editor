# Contributing to GeoJSON Editor

Thank you for your interest in contributing to GeoJSON Editor! We appreciate your time and effort in helping to improve this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/geojson-type-editor.git
   cd geojson-type-editor
   ```
3. **Set up the development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -e ".[dev]"
   ```

## Development Workflow

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure tests pass:
   ```bash
   pytest
   ```

3. **Format your code** before committing:
   ```bash
   black .
   isort .
   ```

4. **Commit your changes** with a descriptive message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

5. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a pull request** against the `main` branch.

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code.
- Use type hints for all function signatures.
- Keep lines under 88 characters (Black's default line length).
- Write docstrings following the Google style guide.

## Testing

- Write tests for new features and bug fixes.
- Run tests locally before submitting a pull request:
  ```bash
  pytest
  ```

## Reporting Issues

When reporting bugs, please include:

1. A clear title and description.
2. Steps to reproduce the issue.
3. Expected vs. actual behavior.
4. Any relevant error messages or screenshots.
5. Your operating system and Python version.

## Feature Requests

For feature requests, please:

1. Check if a similar feature request already exists.
2. Clearly describe the problem you're trying to solve.
3. Explain why this feature would be valuable.

## Code Review Process

1. A maintainer will review your pull request.
2. You may be asked to make changes or provide additional information.
3. Once approved, a maintainer will merge your changes.

Thank you for contributing to GeoJSON Editor! 🚀
