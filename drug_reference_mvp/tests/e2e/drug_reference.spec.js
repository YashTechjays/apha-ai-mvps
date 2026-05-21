import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:3005";

// ---------------------------------------------------------------------------
// Landing Page
// ---------------------------------------------------------------------------
test.describe("Landing Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test("renders hero section with headline and description", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /Trusted clinical drug answers/i })
    ).toBeVisible();
    await expect(
      page.getByText(/APhA Clinical Assistant searches our authoritative drug monographs/i)
    ).toBeVisible();
  });

  test("renders badge text about APhA reference content", async ({ page }) => {
    await expect(
      page.getByText("Backed by APhA reference content · Built for pharmacists")
    ).toBeVisible();
  });

  test("displays Start free and View pricing CTA buttons", async ({ page }) => {
    await expect(page.getByRole("link", { name: /Start free — 10 queries/i })).toBeVisible();
    await expect(page.getByRole("link", { name: /View pricing/i })).toBeVisible();
  });

  test("displays no credit card required note", async ({ page }) => {
    await expect(page.getByText("No credit card required for trial.")).toBeVisible();
  });

  test("renders three feature cards", async ({ page }) => {
    await expect(page.getByText("Cited, evidence-grounded answers")).toBeVisible();
    await expect(page.getByText("Pharmacist-tuned safety")).toBeVisible();
    await expect(page.getByText("API access for teams")).toBeVisible();
  });

  test("renders reference library coverage stats", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: /Reference library coverage/i })
    ).toBeVisible();
    await expect(page.getByText("Drug monographs")).toBeVisible();
    await expect(page.getByText("Clinical guidelines")).toBeVisible();
    await expect(page.getByText("Pharmacy practice topics")).toBeVisible();
  });

  test("renders footer with copyright and links", async ({ page }) => {
    await expect(page.getByText(/APhA Clinical Assistant — Not affiliated/i)).toBeVisible();
    const footer = page.locator("footer");
    await expect(footer.getByRole("link", { name: "Pricing" })).toBeVisible();
    await expect(footer.getByRole("link", { name: "Log in" })).toBeVisible();
  });

  test("Start free CTA navigates to signup page", async ({ page }) => {
    await page.getByRole("link", { name: /Start free — 10 queries/i }).click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
  });

  test("View pricing CTA navigates to pricing page", async ({ page }) => {
    await page.getByRole("link", { name: /View pricing/i }).first().click();
    await expect(page).toHaveURL(`${BASE_URL}/pricing`);
  });
});

// ---------------------------------------------------------------------------
// Header Component
// ---------------------------------------------------------------------------
test.describe("Header — unauthenticated", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
  });

  test("renders logo and brand text", async ({ page }) => {
    await expect(page.getByText("APhA Clinical Assistant")).toBeVisible();
    await expect(page.getByText("Drug Reference for Pharmacists")).toBeVisible();
  });

  test("shows Pricing, Log in, and Start free trial links when logged out", async ({ page }) => {
    const nav = page.locator("nav");
    await expect(nav.getByRole("link", { name: "Pricing" })).toBeVisible();
    await expect(nav.getByRole("link", { name: "Log in" })).toBeVisible();
    await expect(nav.getByRole("link", { name: "Start free trial" })).toBeVisible();
  });

  test("does not show Ask, Dashboard, or Log out when logged out", async ({ page }) => {
    const nav = page.locator("nav");
    await expect(nav.getByRole("link", { name: "Ask" })).not.toBeVisible();
    await expect(nav.getByRole("link", { name: "Dashboard" })).not.toBeVisible();
    await expect(nav.getByRole("button", { name: "Log out" })).not.toBeVisible();
  });

  test("logo links back to landing page", async ({ page }) => {
    await page.goto(`${BASE_URL}/pricing`);
    await page.getByText("APhA Clinical Assistant").click();
    await expect(page).toHaveURL(`${BASE_URL}/`);
  });

  test("Pricing link navigates to /pricing", async ({ page }) => {
    const nav = page.locator("nav");
    await nav.getByRole("link", { name: "Pricing" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/pricing`);
  });
});

test.describe("Header — authenticated", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-test-token"));
    await page.reload();
  });

  test("shows Ask, Dashboard, and Log out when logged in", async ({ page }) => {
    const nav = page.locator("nav");
    await expect(nav.getByRole("link", { name: "Ask" })).toBeVisible();
    await expect(nav.getByRole("link", { name: "Dashboard" })).toBeVisible();
    await expect(nav.getByRole("button", { name: "Log out" })).toBeVisible();
  });

  test("does not show Log in or Start free trial when logged in", async ({ page }) => {
    const nav = page.locator("nav");
    await expect(nav.getByRole("link", { name: "Log in" })).not.toBeVisible();
    await expect(nav.getByRole("link", { name: "Start free trial" })).not.toBeVisible();
  });

  test("Log out clears token and redirects to landing page", async ({ page }) => {
    await page.getByRole("button", { name: "Log out" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/`);
    const token = await page.evaluate(() => localStorage.getItem("apha_token"));
    expect(token).toBeNull();
  });

  test("Ask link navigates to /query", async ({ page }) => {
    const nav = page.locator("nav");
    await nav.getByRole("link", { name: "Ask" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/query`);
  });

  test("Dashboard link navigates to /dashboard", async ({ page }) => {
    const nav = page.locator("nav");
    await nav.getByRole("link", { name: "Dashboard" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
  });
});

// ---------------------------------------------------------------------------
// Login Page
// ---------------------------------------------------------------------------
test.describe("Login Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
  });

  test("renders login heading and description", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Welcome back" })
    ).toBeVisible();
    await expect(
      page.getByText("Sign in to your APhA Clinical Assistant account.")
    ).toBeVisible();
  });

  test("renders email and password fields", async ({ page }) => {
    await expect(page.getByLabel("Email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
  });

  test("renders sign in button", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Sign in" })).toBeVisible();
  });

  test("has link to signup page", async ({ page }) => {
    const link = page.getByRole("link", { name: /Start your free trial/i });
    await expect(link).toBeVisible();
    await link.click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
  });

  test("email field has required and type=email attributes", async ({ page }) => {
    const emailInput = page.getByLabel("Email");
    await expect(emailInput).toHaveAttribute("type", "email");
    await expect(emailInput).toHaveAttribute("required", "");
  });

  test("password field has required and type=password attributes", async ({ page }) => {
    const passwordInput = page.getByLabel("Password");
    await expect(passwordInput).toHaveAttribute("type", "password");
    await expect(passwordInput).toHaveAttribute("required", "");
  });

  test("can type into email and password fields", async ({ page }) => {
    await page.getByLabel("Email").fill("test@example.com");
    await page.getByLabel("Password").fill("secretpass");
    await expect(page.getByLabel("Email")).toHaveValue("test@example.com");
    await expect(page.getByLabel("Password")).toHaveValue("secretpass");
  });

  test("shows error message on failed login", async ({ page }) => {
    // Mock the API to return an error
    await page.route("**/api/v1/auth/login", (route) =>
      route.fulfill({
        status: 401,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Invalid credentials" }),
      })
    );

    await page.getByLabel("Email").fill("bad@example.com");
    await page.getByLabel("Password").fill("wrongpass");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByText("Invalid credentials")).toBeVisible();
  });

  test("successful login stores token and navigates to /query", async ({ page }) => {
    await page.route("**/api/v1/auth/login", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "test-jwt-token" }),
      })
    );

    await page.getByLabel("Email").fill("user@example.com");
    await page.getByLabel("Password").fill("correctpass");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page).toHaveURL(`${BASE_URL}/query`);
    const token = await page.evaluate(() => localStorage.getItem("apha_token"));
    expect(token).toBe("test-jwt-token");
  });

  test("sign in button shows loading state during submission", async ({ page }) => {
    // Delay the response so we can observe the loading state
    await page.route("**/api/v1/auth/login", async (route) => {
      await new Promise((r) => setTimeout(r, 500));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "tok" }),
      });
    });

    await page.getByLabel("Email").fill("user@example.com");
    await page.getByLabel("Password").fill("pass1234");
    await page.getByRole("button", { name: "Sign in" }).click();

    await expect(page.getByRole("button", { name: /Signing in/i })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Signup Page
// ---------------------------------------------------------------------------
test.describe("Signup Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(`${BASE_URL}/signup`);
  });

  test("renders signup heading and description", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Start your free trial" })
    ).toBeVisible();
    await expect(
      page.getByText("10 clinical queries to evaluate. No credit card required.")
    ).toBeVisible();
  });

  test("renders all form fields", async ({ page }) => {
    await expect(page.getByLabel("Full name")).toBeVisible();
    await expect(page.getByLabel("Work email")).toBeVisible();
    await expect(page.getByLabel("Password")).toBeVisible();
    await expect(page.getByLabel(/Organization/i)).toBeVisible();
  });

  test("shows placeholder text on name and organization fields", async ({ page }) => {
    await expect(page.getByLabel("Full name")).toHaveAttribute(
      "placeholder",
      "Jane Patel, PharmD"
    );
    await expect(page.getByLabel(/Organization/i)).toHaveAttribute(
      "placeholder",
      "Riverside Pharmacy"
    );
  });

  test("password field has minLength of 8", async ({ page }) => {
    await expect(page.getByLabel("Password")).toHaveAttribute("minlength", "8");
  });

  test("displays password hint text", async ({ page }) => {
    await expect(page.getByText("8+ characters.")).toBeVisible();
  });

  test("renders Create account button", async ({ page }) => {
    await expect(
      page.getByRole("button", { name: "Create account" })
    ).toBeVisible();
  });

  test("has link to login page", async ({ page }) => {
    const link = page.getByRole("link", { name: "Log in" });
    await expect(link).toBeVisible();
    await link.click();
    await expect(page).toHaveURL(`${BASE_URL}/login`);
  });

  test("email and password are required, name and org are optional", async ({ page }) => {
    await expect(page.getByLabel("Work email")).toHaveAttribute("required", "");
    await expect(page.getByLabel("Password")).toHaveAttribute("required", "");
    // Full name and organization should not have required attribute
    const nameRequired = await page.getByLabel("Full name").getAttribute("required");
    expect(nameRequired).toBeNull();
  });

  test("can fill all form fields", async ({ page }) => {
    await page.getByLabel("Full name").fill("Jane Doe");
    await page.getByLabel("Work email").fill("jane@pharmacy.com");
    await page.getByLabel("Password").fill("securepass123");
    await page.getByLabel(/Organization/i).fill("City Pharmacy");

    await expect(page.getByLabel("Full name")).toHaveValue("Jane Doe");
    await expect(page.getByLabel("Work email")).toHaveValue("jane@pharmacy.com");
    await expect(page.getByLabel("Password")).toHaveValue("securepass123");
    await expect(page.getByLabel(/Organization/i)).toHaveValue("City Pharmacy");
  });

  test("shows error on failed signup", async ({ page }) => {
    await page.route("**/api/v1/auth/signup", (route) =>
      route.fulfill({
        status: 409,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Email already registered" }),
      })
    );

    await page.getByLabel("Work email").fill("existing@example.com");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page.getByText("Email already registered")).toBeVisible();
  });

  test("successful signup stores token and navigates to /query", async ({ page }) => {
    await page.route("**/api/v1/auth/signup", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "new-user-token" }),
      })
    );

    await page.getByLabel("Work email").fill("new@example.com");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(page).toHaveURL(`${BASE_URL}/query`);
    const token = await page.evaluate(() => localStorage.getItem("apha_token"));
    expect(token).toBe("new-user-token");
  });

  test("Create account button shows loading state during submission", async ({ page }) => {
    await page.route("**/api/v1/auth/signup", async (route) => {
      await new Promise((r) => setTimeout(r, 500));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "tok" }),
      });
    });

    await page.getByLabel("Work email").fill("new@example.com");
    await page.getByLabel("Password").fill("password123");
    await page.getByRole("button", { name: "Create account" }).click();

    await expect(
      page.getByRole("button", { name: /Creating account/i })
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Query Page
// ---------------------------------------------------------------------------
test.describe("Query Page", () => {
  test.beforeEach(async ({ page }) => {
    // Set auth token so the page does not redirect
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-test-token"));

    // Mock subscription status endpoint
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "trial",
          queries_used_this_month: 3,
          queries_limit_per_month: 10,
        }),
      })
    );

    await page.goto(`${BASE_URL}/query`);
  });

  test("renders page heading", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Ask a clinical question" })
    ).toBeVisible();
  });

  test("renders subscription status bar", async ({ page }) => {
    await expect(page.getByText(/trial/i)).toBeVisible();
    await expect(page.getByText(/3 \/ 10 queries used this month/i)).toBeVisible();
  });

  test("renders textarea with placeholder", async ({ page }) => {
    const textarea = page.locator("textarea");
    await expect(textarea).toBeVisible();
    await expect(textarea).toHaveAttribute(
      "placeholder",
      "e.g., What is the recommended starting dose of lisinopril in CKD stage 3?"
    );
  });

  test("renders category dropdown with all options", async ({ page }) => {
    const select = page.locator("select");
    await expect(select).toBeVisible();

    const options = select.locator("option");
    await expect(options).toHaveCount(4);
    await expect(options.nth(0)).toHaveText("All categories");
    await expect(options.nth(1)).toHaveText("Drug monographs");
    await expect(options.nth(2)).toHaveText("Clinical guidelines");
    await expect(options.nth(3)).toHaveText("Pharmacy practice");
  });

  test("Ask button is disabled when textarea is empty", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Ask" })).toBeDisabled();
  });

  test("Ask button is enabled when textarea has content", async ({ page }) => {
    await page.locator("textarea").fill("What is metformin used for?");
    await expect(page.getByRole("button", { name: "Ask" })).toBeEnabled();
  });

  test("renders example query buttons", async ({ page }) => {
    await expect(
      page.getByRole("button", { name: "What is the renal dosing for metformin?" })
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Drug interactions between warfarin and amoxicillin?" })
    ).toBeVisible();
    await expect(
      page.getByRole("button", { name: "Counseling points for a new sertraline prescription" })
    ).toBeVisible();
    await expect(
      page.getByRole("button", {
        name: "When should atorvastatin be held perioperatively?",
      })
    ).toBeVisible();
  });

  test("clicking an example populates the textarea", async ({ page }) => {
    await page
      .getByRole("button", { name: "What is the renal dosing for metformin?" })
      .click();
    await expect(page.locator("textarea")).toHaveValue(
      "What is the renal dosing for metformin?"
    );
  });

  test("can select a category from the dropdown", async ({ page }) => {
    const select = page.locator("select");
    await select.selectOption("drug_monograph");
    await expect(select).toHaveValue("drug_monograph");
  });

  test("submitting a query shows response with metadata", async ({ page }) => {
    await page.route("**/api/v1/query", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          query_id: "q-123",
          answer: "Metformin is typically dosed at 500mg twice daily.",
          query_type: "drug_monograph",
          latency_ms: 1200,
          chunks_used: 3,
          used_fallback: false,
          citations: [
            {
              title: "Metformin Monograph",
              category: "drug_monograph",
              max_score: 0.92,
            },
          ],
        }),
      })
    );

    await page.locator("textarea").fill("What is the standard dose for metformin?");
    await page.getByRole("button", { name: "Ask" }).click();

    // Response metadata
    await expect(page.getByText("1200ms")).toBeVisible();
    await expect(page.getByText(/3 sources/)).toBeVisible();
    await expect(page.getByText(/drug_monograph/)).toBeVisible();

    // Answer content
    await expect(
      page.getByText("Metformin is typically dosed at 500mg twice daily.")
    ).toBeVisible();

    // Citations
    await expect(page.getByText("Sources")).toBeVisible();
    await expect(page.getByText("Metformin Monograph")).toBeVisible();
    await expect(page.getByText(/relevance 0\.92/)).toBeVisible();
  });

  test("shows feedback buttons after response", async ({ page }) => {
    await page.route("**/api/v1/query", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          query_id: "q-456",
          answer: "Answer here.",
          query_type: "general",
          latency_ms: 800,
          chunks_used: 2,
          used_fallback: false,
          citations: [],
        }),
      })
    );

    await page.locator("textarea").fill("Test question");
    await page.getByRole("button", { name: "Ask" }).click();

    await expect(page.getByRole("button", { name: "👍" })).toBeVisible();
    await expect(page.getByRole("button", { name: "👎" })).toBeVisible();
  });

  test("shows error message on query failure", async ({ page }) => {
    await page.route("**/api/v1/query", (route) =>
      route.fulfill({
        status: 429,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Rate limit exceeded" }),
      })
    );

    await page.locator("textarea").fill("Some question");
    await page.getByRole("button", { name: "Ask" }).click();

    await expect(page.getByText("Rate limit exceeded")).toBeVisible();
  });

  test("Ask button shows loading state while query is in progress", async ({ page }) => {
    await page.route("**/api/v1/query", async (route) => {
      await new Promise((r) => setTimeout(r, 500));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          query_id: "q-789",
          answer: "Done.",
          query_type: "general",
          latency_ms: 500,
          chunks_used: 1,
          used_fallback: false,
          citations: [],
        }),
      });
    });

    await page.locator("textarea").fill("Test question");
    await page.getByRole("button", { name: "Ask" }).click();

    await expect(page.getByRole("button", { name: /Searching/i })).toBeVisible();
  });

  test("example buttons disappear after a response is shown", async ({ page }) => {
    await page.route("**/api/v1/query", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          query_id: "q-001",
          answer: "Response.",
          query_type: "general",
          latency_ms: 100,
          chunks_used: 1,
          used_fallback: false,
          citations: [],
        }),
      })
    );

    await page.locator("textarea").fill("A question");
    await page.getByRole("button", { name: "Ask" }).click();

    await expect(page.getByText("Response.")).toBeVisible();
    await expect(page.getByText("Try an example:")).not.toBeVisible();
  });

  test("shows Upgrade button when query limit is reached", async ({ page }) => {
    // Re-mock with limit reached
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "trial",
          queries_used_this_month: 10,
          queries_limit_per_month: 10,
        }),
      })
    );

    await page.reload();
    await expect(page.getByRole("link", { name: "Upgrade" })).toBeVisible();
  });

  test("deterministic fallback indicator is shown when used_fallback is true", async ({ page }) => {
    await page.route("**/api/v1/query", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          query_id: "q-fb",
          answer: "Fallback answer.",
          query_type: "general",
          latency_ms: 50,
          chunks_used: 1,
          used_fallback: true,
          citations: [],
        }),
      })
    );

    await page.locator("textarea").fill("Fallback test");
    await page.getByRole("button", { name: "Ask" }).click();

    await expect(page.getByText("deterministic fallback")).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Pricing Page
// ---------------------------------------------------------------------------
test.describe("Pricing Page", () => {
  test.beforeEach(async ({ page }) => {
    // Let the page use its static fallback plans by failing the API call
    await page.route("**/api/v1/subscriptions/plans", (route) =>
      route.fulfill({ status: 500 })
    );
    await page.goto(`${BASE_URL}/pricing`);
  });

  test("renders page heading and description", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Simple, predictable pricing" })
    ).toBeVisible();
    await expect(
      page.getByText(/Choose the plan that fits how you use clinical drug references/i)
    ).toBeVisible();
  });

  test("displays all five pricing plans", async ({ page }) => {
    await expect(page.getByText("Free Trial")).toBeVisible();
    await expect(page.getByText("Individual")).toBeVisible();
    await expect(page.getByText("Pharmacy Team")).toBeVisible();
    await expect(page.getByText("Institution")).toBeVisible();
    await expect(page.getByText("Enterprise")).toBeVisible();
  });

  test("Pharmacy Team plan shows Most popular badge", async ({ page }) => {
    await expect(page.getByText("Most popular")).toBeVisible();
  });

  test("displays correct pricing for each plan", async ({ page }) => {
    await expect(page.getByText("$0")).toBeVisible();
    await expect(page.getByText("$99")).toBeVisible();
    await expect(page.getByText("$299")).toBeVisible();
    await expect(page.getByText("$799")).toBeVisible();
    await expect(page.getByText("Custom")).toBeVisible();
  });

  test("displays feature lists for plans", async ({ page }) => {
    await expect(page.getByText("10 queries / month")).toBeVisible();
    await expect(page.getByText("500 queries / month")).toBeVisible();
    await expect(page.getByText("2,500 queries / month")).toBeVisible();
    await expect(page.getByText("15,000 queries / month")).toBeVisible();
    await expect(page.getByText("Custom volume")).toBeVisible();
  });

  test("displays correct button labels", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Start trial" })).toBeVisible();
    // Individual and Institution have "Subscribe"
    const subscribeButtons = page.getByRole("button", { name: "Subscribe" });
    await expect(subscribeButtons).toHaveCount(2);
    await expect(page.getByRole("button", { name: "Contact sales" })).toBeVisible();
  });

  test("shows sign up link at bottom of page", async ({ page }) => {
    await expect(
      page.getByText(/Need a quote or compliance review/i)
    ).toBeVisible();
    await expect(
      page.getByRole("link", { name: "Sign up" })
    ).toBeVisible();
  });

  test("Start trial redirects to signup when not authenticated", async ({ page }) => {
    await page.evaluate(() => localStorage.removeItem("apha_token"));
    await page.getByRole("button", { name: "Start trial" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
  });

  test("Subscribe redirects to signup when not authenticated", async ({ page }) => {
    await page.evaluate(() => localStorage.removeItem("apha_token"));
    await page.getByRole("button", { name: "Subscribe" }).first().click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
  });

  test("Start trial navigates to /query when authenticated", async ({ page }) => {
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-token"));
    await page.getByRole("button", { name: "Start trial" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/query`);
  });
});

// ---------------------------------------------------------------------------
// Dashboard Page
// ---------------------------------------------------------------------------
test.describe("Dashboard Page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-test-token"));

    // Mock all dashboard API endpoints
    await page.route("**/api/v1/analytics/usage*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_queries: 42,
          safety_flagged: 2,
          thumbs_up: 30,
          thumbs_down: 5,
          avg_latency_ms: 1150.5,
          by_query_type: [
            { query_type: "drug_monograph", count: 25 },
            { query_type: "clinical_guideline", count: 17 },
          ],
        }),
      })
    );

    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "team",
          queries_used_this_month: 120,
          queries_limit_per_month: 2500,
        }),
      })
    );

    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          {
            id: "h1",
            query_text: "What is the dose for ibuprofen?",
            query_type: "drug_monograph",
            sources_cited: 2,
            latency_ms: 900,
            thumbs_up: true,
          },
        ]),
      })
    );

    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            {
              id: "k1",
              label: "My App",
              key_prefix: "apha_sk_abc",
              is_active: true,
            },
          ]),
        });
      }
      return route.continue();
    });

    await page.goto(`${BASE_URL}/dashboard`);
  });

  test("renders Dashboard heading", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Dashboard" })
    ).toBeVisible();
  });

  test("displays plan stat card", async ({ page }) => {
    await expect(page.getByText("Plan")).toBeVisible();
    await expect(page.getByText("team")).toBeVisible();
  });

  test("displays queries this month stat", async ({ page }) => {
    await expect(page.getByText("Queries this month")).toBeVisible();
    await expect(page.getByText("120 / 2500")).toBeVisible();
  });

  test("displays average latency stat", async ({ page }) => {
    await expect(page.getByText("Avg latency (30d)")).toBeVisible();
    await expect(page.getByText("1151ms")).toBeVisible();
  });

  test("renders recent queries section with history", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Recent queries" })
    ).toBeVisible();
    await expect(page.getByText("What is the dose for ibuprofen?")).toBeVisible();
    await expect(page.getByText(/drug_monograph · 2 sources · 900ms/)).toBeVisible();
  });

  test("renders API Keys section with existing key", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "API Keys" })
    ).toBeVisible();
    await expect(page.getByText("My App")).toBeVisible();
    await expect(page.getByText(/apha_sk_abc/)).toBeVisible();
    await expect(page.getByText("active")).toBeVisible();
  });

  test("renders API key creation form with placeholder", async ({ page }) => {
    const input = page.getByPlaceholder("Label (e.g. 'pharmacy app')");
    await expect(input).toBeVisible();
    await expect(page.getByRole("button", { name: "Create" })).toBeVisible();
  });

  test("renders Revoke button for active keys", async ({ page }) => {
    await expect(page.getByRole("button", { name: "Revoke" })).toBeVisible();
  });

  test("renders usage statistics section", async ({ page }) => {
    await expect(
      page.getByRole("heading", { name: "Usage (last 30 days)" })
    ).toBeVisible();
    await expect(page.getByText("Total queries")).toBeVisible();
    await expect(page.getByText("42")).toBeVisible();
    await expect(page.getByText("Safety flagged")).toBeVisible();
    await expect(page.getByText("Thumbs up")).toBeVisible();
    await expect(page.getByText("Thumbs down")).toBeVisible();
  });

  test("renders by query type breakdown", async ({ page }) => {
    await expect(page.getByText("By query type")).toBeVisible();
    await expect(page.getByText("drug_monograph")).toBeVisible();
    await expect(page.getByText("clinical_guideline")).toBeVisible();
  });

  test("shows empty state when no queries exist", async ({ page }) => {
    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      })
    );

    await page.reload();
    await expect(page.getByText("No queries yet.")).toBeVisible();
  });

  test("shows empty state when no API keys exist", async ({ page }) => {
    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([]),
        });
      }
      return route.continue();
    });

    await page.reload();
    await expect(page.getByText("No API keys yet.")).toBeVisible();
  });

  test("creating an API key shows the raw key warning", async ({ page }) => {
    // Override the api-keys route to handle POST as well
    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            id: "k-new",
            label: "CI Pipeline",
            raw_key: "apha_sk_live_SECRET_KEY_123456",
          }),
        });
      }
      // GET returns existing key after creation
      return route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "k1", label: "My App", key_prefix: "apha_sk_abc", is_active: true },
          { id: "k-new", label: "CI Pipeline", key_prefix: "apha_sk_live", is_active: true },
        ]),
      });
    });

    await page.reload();
    await page.getByPlaceholder("Label (e.g. 'pharmacy app')").fill("CI Pipeline");
    await page.getByRole("button", { name: "Create" }).click();

    await expect(page.getByText(/Save this key/i)).toBeVisible();
    await expect(page.getByText("apha_sk_live_SECRET_KEY_123456")).toBeVisible();
  });

  test("displays revoked keys without Revoke button", async ({ page }) => {
    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify([
            { id: "k1", label: "Active Key", key_prefix: "apha_sk_act", is_active: true },
            { id: "k2", label: "Old Key", key_prefix: "apha_sk_old", is_active: false },
          ]),
        });
      }
      return route.continue();
    });

    await page.reload();

    await expect(page.getByText("Active Key")).toBeVisible();
    await expect(page.getByText("Old Key")).toBeVisible();
    await expect(page.getByText("revoked")).toBeVisible();
    // Only one Revoke button (for the active key)
    await expect(page.getByRole("button", { name: "Revoke" })).toHaveCount(1);
  });
});

// ---------------------------------------------------------------------------
// Pricing Page — API success path
// ---------------------------------------------------------------------------
test.describe("Pricing Page — API success", () => {
  test("loads plans from API when available", async ({ page }) => {
    await page.route("**/api/v1/subscriptions/plans", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { code: "trial", name: "Free Trial", monthly_price_usd: 0, features: ["10 queries / month"] },
          { code: "team", name: "Pharmacy Team", monthly_price_usd: 299, features: ["2,500 queries / month", "API access"] },
        ]),
      })
    );

    await page.goto(`${BASE_URL}/pricing`);
    await expect(page.getByText("Free Trial")).toBeVisible();
    await expect(page.getByText("Pharmacy Team")).toBeVisible();
  });

  test("shows Loading plans... while fetching", async ({ page }) => {
    await page.route("**/api/v1/subscriptions/plans", async (route) => {
      await new Promise((r) => setTimeout(r, 2000));
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([]),
      });
    });

    await page.goto(`${BASE_URL}/pricing`);
    await expect(page.getByText(/Loading plans/i)).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Query Page — feedback highlight
// ---------------------------------------------------------------------------
test.describe("Query Page — feedback interaction", () => {
  test("thumbs up button highlights green after clicking", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-test-token"));

    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan: "trial", queries_used_this_month: 0, queries_limit_per_month: 10 }),
      })
    );

    await page.route("**/api/v1/query", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            query_id: "q-fb",
            answer: "Test answer for feedback.",
            query_type: "general",
            latency_ms: 300,
            chunks_used: 1,
            used_fallback: false,
            citations: [],
          }),
        });
      }
      return route.continue();
    });

    await page.route("**/api/v1/query/feedback", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) })
    );

    await page.goto(`${BASE_URL}/query`);

    await page.locator("textarea").fill("Feedback test");
    await page.getByRole("button", { name: "Ask" }).click();
    await expect(page.getByText("Test answer for feedback.")).toBeVisible();

    // Click thumbs up and verify highlight
    await page.getByRole("button", { name: "👍" }).click();
    await expect(page.getByRole("button", { name: "👍" })).toHaveClass(/bg-green-100/);

    // Thumbs down should not be highlighted
    await expect(page.getByRole("button", { name: "👎" })).not.toHaveClass(/bg-red-100/);
  });

  test("thumbs down button highlights red after clicking", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-test-token"));

    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan: "trial", queries_used_this_month: 0, queries_limit_per_month: 10 }),
      })
    );

    await page.route("**/api/v1/query", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            query_id: "q-fb2",
            answer: "Another test answer.",
            query_type: "general",
            latency_ms: 300,
            chunks_used: 1,
            used_fallback: false,
            citations: [],
          }),
        });
      }
      return route.continue();
    });

    await page.route("**/api/v1/query/feedback", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) })
    );

    await page.goto(`${BASE_URL}/query`);

    await page.locator("textarea").fill("Feedback test");
    await page.getByRole("button", { name: "Ask" }).click();
    await expect(page.getByText("Another test answer.")).toBeVisible();

    await page.getByRole("button", { name: "👎" }).click();
    await expect(page.getByRole("button", { name: "👎" })).toHaveClass(/bg-red-100/);
  });
});

// ---------------------------------------------------------------------------
// Full User Flows (multi-page)
// ---------------------------------------------------------------------------
test.describe("Full User Flows", () => {
  test("signup then ask a clinical query end-to-end", async ({ page }) => {
    // Mock signup
    await page.route("**/api/v1/auth/signup", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "e2e-signup-token" }),
      })
    );

    // Mock subscription
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan: "trial", queries_used_this_month: 0, queries_limit_per_month: 10 }),
      })
    );

    // Mock query
    await page.route("**/api/v1/query", (route) => {
      if (route.request().method() === "POST") {
        return route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            query_id: "q-e2e",
            answer: "Warfarin and amoxicillin may interact by increasing INR values.",
            query_type: "drug_monograph",
            latency_ms: 1100,
            chunks_used: 2,
            used_fallback: false,
            citations: [
              { title: "Warfarin Monograph", category: "drug_monograph", max_score: 0.91 },
            ],
          }),
        });
      }
      return route.continue();
    });

    // 1. Start at landing page
    await page.goto(BASE_URL);
    await expect(page.getByRole("heading", { name: /Trusted clinical drug answers/i })).toBeVisible();

    // 2. Navigate to signup via CTA
    await page.getByRole("link", { name: /Start free — 10 queries/i }).click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);

    // 3. Fill and submit signup form
    await page.getByLabel("Full name").fill("E2E Pharmacist");
    await page.getByLabel("Work email").fill("e2e@pharmacy.com");
    await page.getByLabel("Password").fill("testpass123");
    await page.getByRole("button", { name: "Create account" }).click();

    // 4. Redirected to query page
    await expect(page).toHaveURL(`${BASE_URL}/query`);
    await expect(page.getByRole("heading", { name: "Ask a clinical question" })).toBeVisible();

    // 5. Ask a question
    await page.locator("textarea").fill("Drug interactions between warfarin and amoxicillin?");
    await page.getByRole("button", { name: "Ask" }).click();

    // 6. Verify response
    await expect(page.getByText("Warfarin and amoxicillin may interact")).toBeVisible();
    await expect(page.getByText("Sources")).toBeVisible();
    await expect(page.getByText("Warfarin Monograph")).toBeVisible();
  });

  test("login then navigate to dashboard end-to-end", async ({ page }) => {
    // Mock login
    await page.route("**/api/v1/auth/login", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ access_token: "e2e-login-token" }),
      })
    );

    // Mock subscription
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan: "team", queries_used_this_month: 75, queries_limit_per_month: 2500 }),
      })
    );

    // Mock dashboard endpoints
    await page.route("**/api/v1/analytics/usage*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          total_queries: 75,
          safety_flagged: 0,
          thumbs_up: 50,
          thumbs_down: 2,
          avg_latency_ms: 980,
          by_query_type: [{ query_type: "drug_monograph", count: 50 }],
        }),
      })
    );
    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify([
          { id: "h1", query_text: "Metformin dosing", query_type: "drug_monograph", sources_cited: 3, latency_ms: 800, thumbs_up: true },
        ]),
      })
    );
    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      }
      return route.continue();
    });

    // 1. Go to login
    await page.goto(`${BASE_URL}/login`);
    await page.getByLabel("Email").fill("team@pharmacy.com");
    await page.getByLabel("Password").fill("teampass");
    await page.getByRole("button", { name: "Sign in" }).click();

    // 2. Land on query page
    await expect(page).toHaveURL(`${BASE_URL}/query`);

    // 3. Navigate to dashboard via header
    await page.locator("nav").getByRole("link", { name: "Dashboard" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
    await expect(page.getByText("team")).toBeVisible();
    await expect(page.getByText("Metformin dosing")).toBeVisible();
  });

  test("landing to pricing to signup flow", async ({ page }) => {
    await page.route("**/api/v1/subscriptions/plans", (route) =>
      route.fulfill({ status: 500 })
    );

    // 1. Start at landing
    await page.goto(BASE_URL);

    // 2. Click View pricing
    await page.getByRole("link", { name: /View pricing/i }).first().click();
    await expect(page).toHaveURL(`${BASE_URL}/pricing`);
    await expect(page.getByRole("heading", { name: "Simple, predictable pricing" })).toBeVisible();

    // 3. Click Subscribe (not logged in) -> should redirect to signup
    await page.getByRole("button", { name: "Subscribe" }).first().click();
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
  });

  test("authenticated user navigates between all main pages", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "nav-token"));

    // Mock all necessary endpoints
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ plan: "individual", queries_used_this_month: 5, queries_limit_per_month: 500 }),
      })
    );
    await page.route("**/api/v1/subscriptions/plans", (route) =>
      route.fulfill({ status: 500 })
    );
    await page.route("**/api/v1/analytics/usage*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ total_queries: 5, safety_flagged: 0, thumbs_up: 3, thumbs_down: 0, avg_latency_ms: 1000, by_query_type: [] }) })
    );
    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) })
    );
    await page.route("**/api/v1/auth/api-keys", (route) => {
      if (route.request().method() === "GET") {
        return route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
      }
      return route.continue();
    });

    await page.reload();

    // Navigate: Home -> Ask -> Dashboard -> Pricing -> Home (via logo)
    await page.locator("nav").getByRole("link", { name: "Ask" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/query`);

    await page.locator("nav").getByRole("link", { name: "Dashboard" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);

    await page.locator("nav").getByRole("link", { name: "Pricing" }).click();
    await expect(page).toHaveURL(`${BASE_URL}/pricing`);

    await page.getByText("APhA Clinical Assistant").click();
    await expect(page).toHaveURL(`${BASE_URL}/`);
  });
});

// ---------------------------------------------------------------------------
// Route Navigation
// ---------------------------------------------------------------------------
test.describe("Route Navigation", () => {
  test("/ renders landing page", async ({ page }) => {
    await page.goto(BASE_URL);
    await expect(
      page.getByRole("heading", { name: /Trusted clinical drug answers/i })
    ).toBeVisible();
  });

  test("/login renders login page", async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await expect(
      page.getByRole("heading", { name: "Welcome back" })
    ).toBeVisible();
  });

  test("/signup renders signup page", async ({ page }) => {
    await page.goto(`${BASE_URL}/signup`);
    await expect(
      page.getByRole("heading", { name: "Start your free trial" })
    ).toBeVisible();
  });

  test("/pricing renders pricing page", async ({ page }) => {
    await page.route("**/api/v1/subscriptions/plans", (route) =>
      route.fulfill({ status: 500 })
    );
    await page.goto(`${BASE_URL}/pricing`);
    await expect(
      page.getByRole("heading", { name: "Simple, predictable pricing" })
    ).toBeVisible();
  });

  test("/query renders query page", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-token"));
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          plan: "trial",
          queries_used_this_month: 0,
          queries_limit_per_month: 10,
        }),
      })
    );
    await page.goto(`${BASE_URL}/query`);
    await expect(
      page.getByRole("heading", { name: "Ask a clinical question" })
    ).toBeVisible();
  });

  test("/dashboard renders dashboard page", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-token"));
    // Mock all dashboard endpoints to prevent errors
    await page.route("**/api/v1/analytics/usage*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );
    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.route("**/api/v1/auth/api-keys", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.goto(`${BASE_URL}/dashboard`);
    await expect(
      page.getByRole("heading", { name: "Dashboard" })
    ).toBeVisible();
  });

  test("/billing/success renders dashboard page", async ({ page }) => {
    await page.goto(BASE_URL);
    await page.evaluate(() => localStorage.setItem("apha_token", "fake-token"));
    await page.route("**/api/v1/analytics/usage*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );
    await page.route("**/api/v1/subscriptions/me", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "{}" })
    );
    await page.route("**/api/v1/query/history*", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.route("**/api/v1/auth/api-keys", (route) =>
      route.fulfill({ status: 200, contentType: "application/json", body: "[]" })
    );
    await page.goto(`${BASE_URL}/billing/success`);
    await expect(
      page.getByRole("heading", { name: "Dashboard" })
    ).toBeVisible();
  });
});
