---
name: testing-patterns
description: Comprehensive testing strategies across JavaScript (Jest/Vitest) and Python (pytest) with shared core concepts, mocking, fixtures, TDD, and coverage. Use when writing tests, setting up test infrastructure, or implementing TDD workflows in any language.
---

# Testing Patterns

Comprehensive testing strategies for JavaScript/TypeScript and Python, sharing core concepts with language-specific implementations.

## When to Use This Skill

- Writing unit, integration, or functional tests
- Setting up test infrastructure for new projects
- Implementing test-driven development (TDD)
- Mocking external dependencies and APIs
- Creating test fixtures and factories
- Setting up continuous testing in CI/CD

## Core Concepts (Language-Agnostic)

### 1. Test Types

- **Unit Tests**: Test individual functions/classes in isolation
- **Integration Tests**: Test interaction between components
- **Functional/E2E Tests**: Test complete features end-to-end
- **Performance Tests**: Measure speed and resource usage

### 2. AAA Pattern (Arrange-Act-Assert)

Every test follows this structure:
- **Arrange**: Set up test data and preconditions
- **Act**: Execute the code under test
- **Assert**: Verify the results

### 3. Test Isolation

- Tests should be independent — no shared state
- Each test should clean up after itself
- Use fixtures for setup/teardown

### 4. Test Coverage

- Measure what code is exercised by tests
- Aim for meaningful coverage, not just high percentages
- Target 80%+ coverage for critical paths

### 5. Naming Convention

Pattern: `test_<unit>_<scenario>_<expected_outcome>`

Bad: `test_1`, `test_user`, `test_function`
Good: `test_create_user_with_valid_data_returns_user`, `test_login_fails_with_invalid_password`

---

## JavaScript Testing (Jest / Vitest)

### Framework Setup

**Jest:**
```typescript
// jest.config.ts
import type { Config } from "jest";
const config: Config = {
  preset: "ts-jest",
  testEnvironment: "node",
  roots: ["<rootDir>/src"],
  testMatch: ["**/__tests__/**/*.ts", "**/?(*.)+(spec|test).ts"],
  collectCoverageFrom: ["src/**/*.ts", "!src/**/*.d.ts"],
  coverageThreshold: { global: { branches: 80, functions: 80, lines: 80, statements: 80 } },
  setupFilesAfterEnv: ["<rootDir>/src/test/setup.ts"],
};
export default config;
```

**Vitest:**
```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    coverage: { provider: "v8", reporter: ["text", "json", "html"], exclude: ["**/*.d.ts", "**/*.config.ts", "**/dist/**"] },
    setupFiles: ["./src/test/setup.ts"],
  },
});
```

### Unit Testing Patterns

```typescript
import { describe, it, expect } from "vitest";
import { add, divide } from "./calculator";

describe("Calculator", () => {
  describe("add", () => {
    it("should add two positive numbers", () => { expect(add(2, 3)).toBe(5); });
    it("should handle zero", () => { expect(add(0, 5)).toBe(5); });
  });
  describe("divide", () => {
    it("should divide two numbers", () => { expect(divide(10, 2)).toBe(5); });
    it("should throw error when dividing by zero", () => { expect(() => divide(10, 0)).toThrow("Division by zero"); });
  });
});
```

### Mocking Patterns

**Module Mocking:**
```typescript
import { describe, it, expect, vi, beforeEach } from "vitest";
vi.mock("nodemailer", () => ({
  default: { createTransport: vi.fn(() => ({ sendMail: vi.fn().mockResolvedValue({ messageId: "123" }) })) },
}));
```

**Dependency Injection:**
```typescript
describe("UserService", () => {
  let service: UserService;
  let mockRepository: IUserRepository;
  beforeEach(() => {
    mockRepository = { findById: vi.fn(), create: vi.fn() };
    service = new UserService(mockRepository);
  });
  it("should return user if found", async () => {
    vi.mocked(mockRepository.findById).mockResolvedValue(mockUser);
    const user = await service.getUser("1");
    expect(user).toEqual(mockUser);
  });
});
```

**Spying:**
```typescript
import { vi, beforeEach, afterEach } from "vitest";
describe("OrderService", () => {
  let loggerSpy: any;
  beforeEach(() => { loggerSpy = vi.spyOn(logger, "info"); });
  afterEach(() => { loggerSpy.mockRestore(); });
  it("should log order processing", async () => {
    await service.processOrder("123");
    expect(loggerSpy).toHaveBeenCalledWith("Processing order 123");
  });
});
```

### Frontend Testing (Testing Library)

Test React components by rendering and querying by role, placeholder, or test ID. Prefer semantic queries (`getByRole`, `getByPlaceholderText`) over `data-testid`.

For complete React component test examples and hooks testing, see [references/js-advanced-patterns.md](references/js-advanced-patterns.md).

### Test Fixtures and Factories

```typescript
import { faker } from "@faker-js/faker";
export function createUserFixture(overrides?: Partial<User>): User {
  return {
    id: faker.string.uuid(),
    name: faker.person.fullName(),
    email: faker.internet.email(),
    createdAt: faker.date.past(),
    ...overrides,
  };
}
```

### Integration Testing

Use `supertest` for API endpoint testing. Always truncate tables in `beforeEach` and tear down in `afterAll`.

For full API integration test examples, see [references/js-advanced-patterns.md](references/js-advanced-patterns.md).

---

## Python Testing (pytest)

### Quick Start

```python
# test_example.py
def add(a, b):
    return a + b

def test_add():
    result = add(2, 3)
    assert result == 5

# Run with: pytest test_example.py
```

### Fixtures for Setup and Teardown

```python
import pytest
from typing import Generator

@pytest.fixture
def db() -> Generator[Database, None, None]:
    database = Database("sqlite:///:memory:")
    database.connect()
    yield database
    database.disconnect()

def test_database_query(db):
    results = db.query("SELECT * FROM users")
    assert len(results) == 1

@pytest.fixture(scope="session")
def app_config():
    return {"database_url": "postgresql://localhost/test", "api_key": "test-key", "debug": True}
```

### Parameterized Tests

```python
@pytest.mark.parametrize("email,expected", [
    ("user@example.com", True),
    ("invalid.email", False),
    ("", False),
])
def test_email_validation(email, expected):
    assert is_valid_email(email) == expected

@pytest.mark.parametrize("value,expected", [
    pytest.param(1, True, id="positive"),
    pytest.param(0, False, id="zero"),
])
def test_is_positive(value, expected):
    assert (value > 0) == expected
```

### Mocking with unittest.mock

```python
from unittest.mock import Mock, patch, MagicMock
import requests

def test_get_user_success():
    client = APIClient("https://api.example.com")
    mock_response = Mock()
    mock_response.json.return_value = {"id": 1, "name": "John Doe"}
    mock_response.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_response) as mock_get:
        user = client.get_user(1)
        assert user["id"] == 1
        mock_get.assert_called_once_with("https://api.example.com/users/1")

@patch("requests.post")
def test_create_user(mock_post):
    client = APIClient("https://api.example.com")
    mock_post.return_value.json.return_value = {"id": 2, "name": "Jane Doe"}
    result = client.create_user({"name": "Jane Doe", "email": "jane@example.com"})
    assert result["id"] == 2
```

### Testing Exceptions

```python
def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_exception_message():
    with pytest.raises(ZeroDivisionError, match="Division by zero"):
        divide(5, 0)
```

### Test Markers

```python
@pytest.mark.slow
def test_slow_operation(): pass

@pytest.mark.integration
def test_database_integration(): pass

@pytest.mark.skip(reason="Feature not implemented yet")
def test_future_feature(): pass

@pytest.mark.xfail(reason="Known bug #123")
def test_known_bug(): assert False

# Run with: pytest -m slow, pytest -m "not slow", pytest -m integration
```

### Coverage Reporting

```bash
pip install pytest-cov
pytest --cov=myapp tests/
pytest --cov=myapp --cov-report=html tests/
pytest --cov=myapp --cov-fail-under=80 tests/
pytest --cov=myapp --cov-report=term-missing tests/
```

For advanced patterns (async testing, monkeypatching, property-based testing, database testing, CI/CD), see [references/py-advanced-patterns.md](references/py-advanced-patterns.md).

---

## Shared Best Practices

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **One behavior per test**: Each test verifies exactly one behavior
3. **Test error paths**: Not just happy paths — test failure cases too
4. **Mock external dependencies**: Keep tests isolated
5. **Use test factories**: For consistent, realistic test data
6. **Descriptive test names**: Should describe what is being tested
7. **Keep tests fast**: Mock slow operations
8. **Maintain test coverage**: Aim for 80%+ coverage
9. **Clean up after tests**: Prevent test pollution
10. **Avoid implementation details**: Test behavior, not internals