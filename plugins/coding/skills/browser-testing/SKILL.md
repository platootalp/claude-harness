---
name: browser-testing
description: Browser testing with Playwright (TypeScript E2E + Python local testing) and Cypress. Covers page objects, fixtures, waiting strategies, network mocking, visual regression, accessibility, and server lifecycle management. Use when writing E2E tests, testing web apps, or debugging browser automation.
---

# Browser Testing

Playwright and Cypress patterns for E2E testing (TypeScript) and local web app testing (Python).

## When to Use This Skill

- Implementing end-to-end test automation
- Testing local web applications with Playwright
- Debugging flaky or unreliable browser tests
- Testing critical user workflows
- Setting up CI/CD test pipelines
- Testing across multiple browsers
- Validating accessibility requirements

## Shared Playwright Core Patterns

### Page Object Model

```typescript
import { Page, Locator } from "@playwright/test";

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel("Email");
    this.passwordInput = page.getByLabel("Password");
    this.loginButton = page.getByRole("button", { name: "Login" });
    this.errorMessage = page.getByRole("alert");
  }

  async goto() { await this.page.goto("/login"); }
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }
  async getErrorMessage(): Promise<string> {
    return (await this.errorMessage.textContent()) ?? "";
  }
}
```

### Waiting Strategies

```typescript
// Never use fixed timeouts
await page.waitForTimeout(3000); // Flaky!

// Wait for specific conditions
await page.waitForLoadState("networkidle");
await page.waitForURL("/dashboard");
await page.waitForSelector('[data-testid="user-profile"]');

// Auto-waiting with assertions (preferred)
await expect(page.getByText("Welcome")).toBeVisible();
await expect(page.getByRole("button", { name: "Submit" })).toBeEnabled();

// Wait for API response
const responsePromise = page.waitForResponse(
  (response) => response.url().includes("/api/users") && response.status() === 200,
);
await page.getByRole("button", { name: "Load Users" }).click();
const response = await responsePromise;
```

### Network Mocking

```typescript
// Mock API responses
await page.route("**/api/users", (route) => {
  route.fulfill({ status: 500, contentType: "application/json", body: JSON.stringify({ error: "Internal Server Error" }) });
});

// Intercept and modify requests
await page.route("**/api/users", async (route) => {
  const postData = JSON.parse(route.request().postData() || "{}");
  postData.role = "admin";
  await route.continue({ postData: JSON.stringify(postData) });
});
```

### Selectors

```typescript
// Bad: CSS classes, nth-child
cy.get(".btn.btn-primary.submit-button").click();
cy.get("div > form > div:nth-child(2) > input").type("text");

// Good: Semantic queries, data-testid
cy.getByRole("button", { name: "Submit" }).click();
cy.getByLabel("Email address").type("user@example.com");
cy.get('[data-testid="email-input"]').type("user@example.com");
```

---

## TypeScript E2E Testing (Playwright + Cypress)

### Playwright Configuration

```typescript
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";
export default defineConfig({
  testDir: "./e2e",
  timeout: 30000,
  expect: { timeout: 5000 },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html"], ["junit", { outputFile: "results.xml" }]],
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "mobile", use: { ...devices["iPhone 13"] } },
  ],
});
```

### Playwright Fixtures for Test Data

```typescript
import { test as base } from "@playwright/test";
type TestData = { testUser: { email: string; password: string; name: string }; };

export const test = base.extend<TestData>({
  testUser: async ({}, use) => {
    const user = { email: `test-${Date.now()}@example.com`, password: "Test123!@#", name: "Test User" };
    await createTestUser(user);
    await use(user);
    await deleteTestUser(user.email);
  },
});
```

### Visual Regression Testing

```typescript
import { test, expect } from "@playwright/test";
test("homepage looks correct", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveScreenshot("homepage.png", { fullPage: true, maxDiffPixels: 100 });
});

test("button in all states", async ({ page }) => {
  await page.goto("/components");
  const button = page.getByRole("button", { name: "Submit" });
  await expect(button).toHaveScreenshot("button-default.png");
  await button.hover();
  await expect(button).toHaveScreenshot("button-hover.png");
});
```

### Parallel Testing with Sharding

```typescript
export default defineConfig({
  projects: [
    { name: "shard-1", use: { ...devices["Desktop Chrome"] }, shard: { current: 1, total: 4 } },
    { name: "shard-2", use: { ...devices["Desktop Chrome"] }, shard: { current: 2, total: 4 } },
  ],
});
// Run: npx playwright test --shard=1/4
```

### Accessibility Testing

```typescript
import AxeBuilder from "@axe-core/playwright";
test("page should not have accessibility violations", async ({ page }) => {
  await page.goto("/");
  const results = await new AxeBuilder({ page }).exclude("#third-party-widget").analyze();
  expect(results.violations).toEqual([]);
});
```

### Debugging Failing Tests

```bash
npx playwright test --headed
npx playwright test --debug
```

```typescript
test('checkout flow', async ({ page }) => {
    await test.step('Add item to cart', async () => {
        await page.goto('/products');
        await page.getByRole('button', { name: 'Add to Cart' }).click();
    });
    await test.step('Proceed to checkout', async () => {
        await page.goto('/cart');
        await page.getByRole('button', { name: 'Checkout' }).click();
    });
});
await page.pause(); // Pauses execution, opens inspector
```

### Cypress Patterns

For Cypress-specific patterns (custom commands, intercept, configuration), see [references/cypress-patterns.md](references/cypress-patterns.md).

---

## Python Local Testing (Playwright)

### Decision Tree

```
Is it static HTML?
  Yes → Read HTML file directly, identify selectors, write Playwright script
  No → Is the server already running?
    No → Use scripts/with_server.py --help, then write simplified Playwright script
    Yes → Reconnaissance-then-action:
      1. Navigate and wait for networkidle
      2. Take screenshot or inspect DOM
      3. Identify selectors from rendered state
      4. Execute actions with discovered selectors
```

### Server Lifecycle Management

```bash
# Single server
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py

# Multiple servers (backend + frontend)
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

### Python Playwright Script

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')
    page.wait_for_load_state('networkidle')  # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

### Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```
2. **Identify selectors** from inspection results
3. **Execute actions** using discovered selectors

### Critical Rule

Never inspect the DOM before waiting for `networkidle` on dynamic apps. Always use `page.wait_for_load_state('networkidle')` before inspection.

---

## Best Practices

1. **Use data-testid or data-cy** for stable selectors
2. **Avoid brittle selectors** — don't rely on CSS classes or DOM structure
3. **Test user behavior**, not implementation details
4. **Keep tests independent** — each test should run in isolation
5. **Clean up test data** — create and destroy in each test
6. **Use Page Objects** — encapsulate page logic
7. **Meaningful assertions** — check user-visible behavior
8. **Optimize for speed** — mock when possible, parallel execution
9. **Use bundled scripts as black boxes** — run with `--help` first, don't read source

## Common Pitfalls

- **Flaky Tests**: Use proper waits, not fixed timeouts
- **Slow Tests**: Mock external APIs, use parallel execution
- **Over-Testing**: Don't test every edge case with E2E
- **Coupled Tests**: Tests should not depend on each other
- **No Cleanup**: Clean up test data after each test