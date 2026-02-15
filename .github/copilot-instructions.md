# Graaf Zeppelin - Copilot Instructions

## Project Overview

Graaf Zeppelin is a Python framework that uses graph theory to model social relationships in sports clubs. The framework represents members as nodes in a graph, with weighted edges representing relationship quality. It's designed to help analyze and improve team dynamics through quantitative affective metrics.

## Technology Stack

- **Language**: Python
- **Core Libraries**: Graph theory libraries (for relationship modeling)
- **Testing**: unittest module
- **File Formats**: JSON, GEXF, Markdown

## Coding Standards

### File Encoding
- Always use UTF-8 encoding for all file I/O operations
- Add `encoding='utf-8'` parameter when opening JSON, GEXF, and Markdown files

### Path Handling
- Use `tempfile.mkdtemp()` for temporary test files instead of hardcoded `/tmp/` paths
- This ensures cross-platform compatibility (Windows, Linux, macOS)

### Code Style
- Follow PEP 8 conventions for Python code
- Use clear, descriptive variable names
- Add docstrings for public functions and classes

## Architecture & Patterns

### Core Components
1. **Relationship Graph**: Models social relationships using graph nodes (members) and weighted edges (relationship quality)

2. **Affective Metrics**: Measures four key dimensions:
   - Emotional Climate
   - Relational Quality
   - Psychological Safety
   - Cultural Cohesion

### Design Principles
- Separate concerns: Keep graph modeling separate from metric calculations
- Data-driven: Base all metrics on quantifiable graph properties
- Extensibility: Design for adding new affective dimensions easily

## Testing Practices

### Test Structure
- Use unittest module for all testing
- Create separate test files for each major component
- Name test files with `test_` prefix for clarity
- Group related tests in test classes

### Test Commands
- Run individual test files independently from repository root
- Example: `python tests/test_<component>.py`

### Test Best Practices
- Use `tempfile.mkdtemp()` for temporary files in tests
- Clean up temporary resources in tearDown methods
- Test edge cases and boundary conditions
- Ensure tests are deterministic and don't depend on external state

## File Organization

Organize code with clear separation of concerns:
- Core functionality for graph modeling and relationship analysis
- Separate test files for each major component
- Documentation in dedicated docs directory
- Use meaningful module and package names

## Documentation

- Maintain theoretical documentation describing the framework's foundation
- Update README.md with usage examples when adding new features
- Keep documentation in sync with code changes
- Use clear docstrings for all public APIs

## Security Best Practices

- Validate all input data before processing
- Use safe file operations with proper exception handling
- Avoid hardcoding sensitive information
- Use parameterized queries if database operations are added

## Common Patterns

### File I/O Pattern
```python
with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### Temporary File Pattern
```python
import tempfile
temp_dir = tempfile.mkdtemp()
try:
    # Use temp_dir
finally:
    # Clean up
```

## Resources

- README.md: Project overview and basic usage
- Documentation: Theoretical foundation and technical details
- Tests: Reference implementations and usage examples
