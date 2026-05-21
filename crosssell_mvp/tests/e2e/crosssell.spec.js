import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3004';

// ---------------------------------------------------------------------------
// Mock data fixtures
// ---------------------------------------------------------------------------

const MOCK_OVERVIEW = {
  total_active_members: 1240,
  avg_active_streams_per_member: 2.8,
  total_nudges_sent: 520,
  click_rate: 0.34,
  open_rate: 0.62,
  conversion_rate: 0.18,
};

const MOCK_BY_PRODUCT = {
  education: { active_pct: 0.72 },
  publications: { active_pct: 0.55 },
  events: { active_pct: 0.41 },
  career: { active_pct: 0.28 },
  advocacy: { active_pct: 0.15 },
};

const MOCK_MEMBERS = [
  {
    member_id: 'mem-001',
    first_name: 'Alice',
    last_name: 'Johnson',
    email: 'alice.johnson@example.com',
    tier: 'gold_member',
    active_stream_count: 3,
    top_opportunity_product: 'events',
    top_opportunity_score: 85,
    churn_score: 25,
  },
  {
    member_id: 'mem-002',
    first_name: 'Bob',
    last_name: 'Smith',
    email: 'bob.smith@example.com',
    tier: 'silver_member',
    active_stream_count: 1,
    top_opportunity_product: 'education',
    top_opportunity_score: 72,
    churn_score: 65,
  },
];

const MOCK_MEMBER_SCORES = [
  { product: 'education', score: 82, already_active: false, top_reasons: ['Strong CPE history', 'Recent course search'] },
  { product: 'publications', score: 45, already_active: true, top_reasons: [] },
  { product: 'events', score: 68, already_active: false, top_reasons: ['Attended 2 events last year', 'Proximity match'] },
  { product: 'career', score: 30, already_active: false, top_reasons: ['Low engagement'] },
  { product: 'advocacy', score: 15, already_active: true, top_reasons: [] },
];

const MOCK_NUDGES = [
  {
    id: 'nudge-001',
    member_id: 'mem-001-abcd-1234-efgh-56789012',
    product: 'events',
    channel: 'email',
    expansion_score: 85,
    sent_at: '2026-05-15T10:30:00Z',
    opened_at: '2026-05-15T12:00:00Z',
    clicked_at: '2026-05-15T12:05:00Z',
  },
  {
    id: 'nudge-002',
    member_id: 'mem-002-abcd-1234-efgh-56789012',
    product: 'education',
    channel: 'banner',
    expansion_score: 72,
    sent_at: '2026-05-14T09:00:00Z',
    opened_at: '2026-05-14T10:00:00Z',
    clicked_at: null,
  },
  {
    id: 'nudge-003',
    member_id: 'mem-003-abcd-1234-efgh-56789012',
    product: 'career',
    channel: 'email',
    expansion_score: 60,
    sent_at: '2026-05-13T08:00:00Z',
    opened_at: null,
    clicked_at: null,
  },
];

const MOCK_NUDGE_SEND_RESULT = { sent: 12, skipped: 3, failed: 0 };

// ---------------------------------------------------------------------------
// Helper: set up authenticated state and common API mocks
// ---------------------------------------------------------------------------

async function setupAuth(page) {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'fake-jwt-token');
  });
}

async function mockDashboardAPIs(page) {
  await page.route('**/analytics/overview', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_OVERVIEW) })
  );
  await page.route('**/analytics/by-product', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_BY_PRODUCT) })
  );
}

async function mockMembersAPI(page) {
  await page.route('**/scores/members*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_MEMBERS) })
  );
}

async function mockMemberScoresAPI(page) {
  await page.route('**/scores/member/*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_MEMBER_SCORES) })
  );
}

async function mockNudgesAPI(page) {
  await page.route('**/nudges/', (route) => {
    if (route.request().method() === 'GET') {
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_NUDGES) });
    }
    return route.continue();
  });
  await page.route('**/nudges/send', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_NUDGE_SEND_RESULT) })
  );
}

// ===========================================================================
// LOGIN PAGE
// ===========================================================================

test.describe('Login page', () => {
  test('renders login form with title, inputs, and submit button', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);

    await expect(page.locator('h1')).toHaveText('APhA Cross-Sell');
    await expect(page.locator('input[placeholder="Username"]')).toBeVisible();
    await expect(page.locator('input[placeholder="Password"]')).toBeVisible();
    await expect(page.locator('button', { hasText: 'Sign In' })).toBeVisible();
    await expect(page.locator('text=Demo: admin / apha2026')).toBeVisible();
  });

  test('shows error on invalid credentials', async ({ page }) => {
    await page.route('**/auth/login', (route) =>
      route.fulfill({ status: 400, contentType: 'application/json', body: JSON.stringify({ detail: 'Invalid credentials' }) })
    );

    await page.goto(`${BASE_URL}/login`);
    await page.locator('input[placeholder="Username"]').fill('wrong');
    await page.locator('input[placeholder="Password"]').fill('wrong');
    await page.locator('button', { hasText: 'Sign In' }).click();

    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });

  test('redirects to dashboard on successful login', async ({ page }) => {
    await page.route('**/auth/login', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ access_token: 'fake-jwt-token' }) })
    );
    // Mock dashboard APIs so the redirect page loads successfully
    await mockDashboardAPIs(page);

    await page.goto(`${BASE_URL}/login`);
    await page.locator('input[placeholder="Username"]').fill('admin');
    await page.locator('input[placeholder="Password"]').fill('apha2026');
    await page.locator('button', { hasText: 'Sign In' }).click();

    await page.waitForURL(`${BASE_URL}/`);
    await expect(page).toHaveURL(`${BASE_URL}/`);
  });

  test('unauthenticated user is redirected to /login', async ({ page }) => {
    await page.addInitScript(() => {
      localStorage.removeItem('token');
    });
    await page.goto(`${BASE_URL}/`);
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(`${BASE_URL}/login`);
  });
});

// ===========================================================================
// SIDEBAR NAVIGATION
// ===========================================================================

test.describe('Sidebar navigation', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await mockNudgesAPI(page);
  });

  test('sidebar displays brand and navigation links', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);

    await expect(page.locator('aside')).toContainText('APhA');
    await expect(page.locator('aside')).toContainText('Cross-Sell Engine');
    await expect(page.locator('aside')).toContainText('by Techjays');

    const dashboardLink = page.locator('nav a', { hasText: 'Dashboard' });
    const membersLink = page.locator('nav a', { hasText: 'Members' });
    const nudgesLink = page.locator('nav a', { hasText: 'Nudges' });

    await expect(dashboardLink).toBeVisible();
    await expect(membersLink).toBeVisible();
    await expect(nudgesLink).toBeVisible();
  });

  test('navigates to Members page via sidebar', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.locator('nav a', { hasText: 'Members' }).click();
    await page.waitForURL('**/members');
    await expect(page.locator('h1')).toHaveText('Expansion Opportunities');
  });

  test('navigates to Nudges page via sidebar', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.locator('nav a', { hasText: 'Nudges' }).click();
    await page.waitForURL('**/nudges');
    await expect(page.locator('h1')).toHaveText('Nudge History');
  });

  test('log out button clears token and redirects to login', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const logoutBtn = page.locator('button', { hasText: 'Log out' });
    await expect(logoutBtn).toBeVisible();
    await logoutBtn.click();
    await page.waitForURL('**/login');
    await expect(page).toHaveURL(`${BASE_URL}/login`);
  });
});

// ===========================================================================
// DASHBOARD PAGE
// ===========================================================================

test.describe('Dashboard page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await mockDashboardAPIs(page);
    await mockNudgesAPI(page);
  });

  test('renders page title and subtitle', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await expect(page.locator('h1')).toHaveText('Cross-Sell Engine');
    await expect(page.locator('text=AI-powered product expansion')).toBeVisible();
  });

  test('displays four KPI cards with correct data', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);

    await expect(page.locator('text=Active members')).toBeVisible();
    await expect(page.locator('text=1240')).toBeVisible();

    await expect(page.locator('text=Avg streams/member')).toBeVisible();
    await expect(page.locator('text=2.8')).toBeVisible();

    await expect(page.locator('text=Nudges sent')).toBeVisible();
    await expect(page.locator('text=520')).toBeVisible();

    await expect(page.locator('text=Click rate')).toBeVisible();
    await expect(page.locator('text=34%')).toBeVisible();
  });

  test('displays conversion funnel section', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await expect(page.locator('h2', { hasText: 'Nudge conversion funnel' })).toBeVisible();
  });

  test('displays product stream activity section with all products', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await expect(page.locator('h2', { hasText: 'Product stream activity' })).toBeVisible();

    for (const label of ['CPE', 'Publications', 'Events', 'Career', 'Advocacy']) {
      await expect(page.locator(`text=${label}`).first()).toBeVisible();
    }
  });

  test('Run Scoring button triggers scoring API and refreshes data', async ({ page }) => {
    let scoringCalled = false;
    await page.route('**/scores/run', (route) => {
      scoringCalled = true;
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok' }) });
    });

    await page.goto(`${BASE_URL}/`);
    const runBtn = page.locator('button', { hasText: 'Run Scoring' });
    await expect(runBtn).toBeVisible();
    await runBtn.click();

    // Button should show scoring state
    await expect(page.locator('button', { hasText: 'Scoring...' })).toBeVisible();
    // Wait for it to finish
    await expect(page.locator('button', { hasText: 'Run Scoring' })).toBeVisible({ timeout: 5000 });
    expect(scoringCalled).toBe(true);
  });

  test('Dry Run Nudges button shows dry run result banner', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const dryRunBtn = page.locator('button', { hasText: 'Dry Run Nudges' });
    await dryRunBtn.click();

    await expect(page.locator('text=Dry run:')).toBeVisible();
    await expect(page.locator('text=12 nudges sent')).toBeVisible();
    await expect(page.locator('text=3 skipped')).toBeVisible();
    await expect(page.locator('text=0 failed')).toBeVisible();
  });

  test('Send Nudges button shows sent result banner', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    const sendBtn = page.locator('button', { hasText: 'Send Nudges' });
    await sendBtn.click();

    await expect(page.locator('text=Sent:')).toBeVisible();
    await expect(page.locator('text=12 nudges sent')).toBeVisible();
  });
});

// ===========================================================================
// MEMBERS PAGE
// ===========================================================================

test.describe('Members page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await mockMembersAPI(page);
  });

  test('renders heading and description', async ({ page }) => {
    await page.goto(`${BASE_URL}/members`);
    await expect(page.locator('h1')).toHaveText('Expansion Opportunities');
    await expect(page.locator('text=Members ranked by cross-sell opportunity score')).toBeVisible();
  });

  test('displays product filter buttons', async ({ page }) => {
    await page.goto(`${BASE_URL}/members`);

    await expect(page.locator('button', { hasText: 'All products' })).toBeVisible();
    for (const p of ['education', 'publications', 'events', 'career', 'advocacy']) {
      await expect(page.locator('button', { hasText: new RegExp(p, 'i') })).toBeVisible();
    }
  });

  test('displays member table with correct headers', async ({ page }) => {
    await page.goto(`${BASE_URL}/members`);

    for (const header of ['Member', 'Tier', 'Active streams', 'Top opportunity', 'Score', 'Churn risk']) {
      await expect(page.locator('th', { hasText: header })).toBeVisible();
    }
  });

  test('renders member rows with correct data', async ({ page }) => {
    await page.goto(`${BASE_URL}/members`);

    await expect(page.locator('text=Alice Johnson')).toBeVisible();
    await expect(page.locator('text=alice.johnson@example.com')).toBeVisible();
    await expect(page.locator('text=gold member')).toBeVisible();
    await expect(page.locator('td >> text=85')).toBeVisible();

    await expect(page.locator('text=Bob Smith')).toBeVisible();
    await expect(page.locator('text=bob.smith@example.com')).toBeVisible();
  });

  test('clicking a product filter re-fetches members with product param', async ({ page }) => {
    let capturedUrl = '';
    await page.route('**/scores/members*', (route) => {
      capturedUrl = route.request().url();
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_MEMBERS) });
    });

    await page.goto(`${BASE_URL}/members`);
    await page.locator('button', { hasText: /^.*education$/i }).click();

    // Wait for the request to be made with the product filter
    await page.waitForTimeout(500);
    expect(capturedUrl).toContain('product=education');
  });

  test('clicking a member row navigates to member detail page', async ({ page }) => {
    await mockMemberScoresAPI(page);
    await page.goto(`${BASE_URL}/members`);

    await page.locator('tr', { hasText: 'Alice Johnson' }).click();
    await page.waitForURL('**/members/mem-001');
    await expect(page).toHaveURL(`${BASE_URL}/members/mem-001`);
  });

  test('shows empty state when no members are returned', async ({ page }) => {
    await page.route('**/scores/members*', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );

    await page.goto(`${BASE_URL}/members`);
    await expect(page.locator('text=No opportunities found.')).toBeVisible();
  });
});

// ===========================================================================
// MEMBER DETAIL PAGE
// ===========================================================================

test.describe('Member detail page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await mockMemberScoresAPI(page);
    await mockNudgesAPI(page);
  });

  test('renders back button, heading, and layout sections', async ({ page }) => {
    await page.goto(`${BASE_URL}/members/mem-001`);

    await expect(page.locator('button', { hasText: 'Back' })).toBeVisible();
    await expect(page.locator('h1')).toHaveText('Member Expansion Profile');
    await expect(page.locator('h2', { hasText: 'Product usage radar' })).toBeVisible();
    await expect(page.locator('h2', { hasText: 'Expansion opportunities' })).toBeVisible();
  });

  test('back button navigates to members list', async ({ page }) => {
    await mockMembersAPI(page);
    await page.goto(`${BASE_URL}/members/mem-001`);

    await page.locator('button', { hasText: 'Back' }).click();
    await page.waitForURL('**/members');
    await expect(page).toHaveURL(`${BASE_URL}/members`);
  });

  test('displays expansion score cards for non-active products only', async ({ page }) => {
    await page.goto(`${BASE_URL}/members/mem-001`);

    // Non-active products should show their labels
    await expect(page.locator('text=CPE & Training')).toBeVisible();
    await expect(page.locator('text=Events & Conferences')).toBeVisible();

    // Active products (publications, advocacy) should not show cards
    // publications is already_active=true, advocacy is already_active=true
    // Career has score 30 so it renders but no nudge button (score < 60)
    await expect(page.locator('text=Career Services')).toBeVisible();
  });

  test('shows expansion score reasons', async ({ page }) => {
    await page.goto(`${BASE_URL}/members/mem-001`);

    await expect(page.locator('text=Strong CPE history')).toBeVisible();
    await expect(page.locator('text=Attended 2 events last year')).toBeVisible();
  });

  test('shows nudge button only for products with score >= 60', async ({ page }) => {
    await page.goto(`${BASE_URL}/members/mem-001`);

    // education (82) and events (68) have score >= 60 and are not active
    await expect(page.locator('button', { hasText: 'Send education nudge' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Send events nudge' })).toBeVisible();

    // career (30) has score < 60, so no nudge button
    await expect(page.locator('button', { hasText: 'Send career nudge' })).not.toBeVisible();
  });

  test('clicking nudge button calls the nudge API', async ({ page }) => {
    const nudgePromise = page.waitForRequest('**/nudges/send');

    await page.goto(`${BASE_URL}/members/mem-001`);

    const nudgeBtn = page.locator('button', { hasText: 'Send education nudge' });
    await nudgeBtn.click();

    // Verify the API was called
    const request = await nudgePromise;
    expect(request.method()).toBe('POST');
  });
});

// ===========================================================================
// NUDGES PAGE
// ===========================================================================

test.describe('Nudges page', () => {
  test.beforeEach(async ({ page }) => {
    await setupAuth(page);
    await mockNudgesAPI(page);
  });

  test('renders heading and description', async ({ page }) => {
    await page.goto(`${BASE_URL}/nudges`);
    await expect(page.locator('h1')).toHaveText('Nudge History');
    await expect(page.locator('text=All cross-sell nudges sent across email + banner channels')).toBeVisible();
  });

  test('displays channel and product filter dropdowns', async ({ page }) => {
    await page.goto(`${BASE_URL}/nudges`);

    const channelSelect = page.locator('select').first();
    const productSelect = page.locator('select').nth(1);

    await expect(channelSelect).toBeVisible();
    await expect(productSelect).toBeVisible();

    // Verify channel options
    await expect(channelSelect.locator('option', { hasText: 'All channels' })).toBeAttached();
    await expect(channelSelect.locator('option', { hasText: 'Email' })).toBeAttached();
    await expect(channelSelect.locator('option', { hasText: 'Banner' })).toBeAttached();

    // Verify product options
    await expect(productSelect.locator('option', { hasText: 'All products' })).toBeAttached();
    await expect(productSelect.locator('option', { hasText: 'Education' })).toBeAttached();
    await expect(productSelect.locator('option', { hasText: 'Events' })).toBeAttached();
  });

  test('displays nudge history table with correct headers', async ({ page }) => {
    await page.goto(`${BASE_URL}/nudges`);

    for (const header of ['Member', 'Product', 'Channel', 'Score', 'Sent', 'Engagement']) {
      await expect(page.locator('th', { hasText: header })).toBeVisible();
    }
  });

  test('renders nudge rows with correct data', async ({ page }) => {
    await page.goto(`${BASE_URL}/nudges`);

    // Check first nudge row data
    await expect(page.locator('td', { hasText: 'events' })).toBeVisible();
    await expect(page.locator('td span', { hasText: 'email' }).first()).toBeVisible();
    await expect(page.locator('text=Clicked').first()).toBeVisible();

    // Second nudge has opened_at but no clicked_at, should show "Opened"
    await expect(page.locator('text=Opened').first()).toBeVisible();
  });

  test('channel filter sends correct query parameter', async ({ page }) => {
    let capturedUrl = '';
    await page.route('**/nudges/*', (route) => {
      if (route.request().method() === 'GET') {
        capturedUrl = route.request().url();
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_NUDGES) });
      }
      return route.continue();
    });

    await page.goto(`${BASE_URL}/nudges`);
    const channelSelect = page.locator('select').first();
    await channelSelect.selectOption('email');

    await page.waitForTimeout(500);
    expect(capturedUrl).toContain('channel=email');
  });

  test('product filter sends correct query parameter', async ({ page }) => {
    let capturedUrl = '';
    await page.route('**/nudges/*', (route) => {
      if (route.request().method() === 'GET') {
        capturedUrl = route.request().url();
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_NUDGES) });
      }
      return route.continue();
    });

    await page.goto(`${BASE_URL}/nudges`);
    const productSelect = page.locator('select').nth(1);
    await productSelect.selectOption('education');

    await page.waitForTimeout(500);
    expect(capturedUrl).toContain('product=education');
  });

  test('shows empty state when no nudges are returned', async ({ page }) => {
    await page.route('**/nudges/', (route) => {
      if (route.request().method() === 'GET') {
        return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) });
      }
      return route.continue();
    });

    await page.goto(`${BASE_URL}/nudges`);
    await expect(page.locator('text=No nudges yet.')).toBeVisible();
  });
});

// ===========================================================================
// FULL USER FLOWS
// ===========================================================================

test.describe('Full user flows', () => {
  test('login -> dashboard -> run scoring -> send nudges -> view nudges', async ({ page }) => {
    // Step 1: Login
    await page.route('**/auth/login', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ access_token: 'fake-jwt-token' }) })
    );
    await mockDashboardAPIs(page);
    await mockNudgesAPI(page);
    await page.route('**/scores/run', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ status: 'ok' }) })
    );

    await page.goto(`${BASE_URL}/login`);
    await page.locator('input[placeholder="Username"]').fill('admin');
    await page.locator('input[placeholder="Password"]').fill('apha2026');
    await page.locator('button', { hasText: 'Sign In' }).click();
    await page.waitForURL(`${BASE_URL}/`);

    // Step 2: Verify dashboard loaded
    await expect(page.locator('h1')).toHaveText('Cross-Sell Engine');
    await expect(page.locator('text=1240')).toBeVisible();

    // Step 3: Run scoring
    await page.locator('button', { hasText: 'Run Scoring' }).click();
    await expect(page.locator('button', { hasText: 'Run Scoring' })).toBeVisible({ timeout: 5000 });

    // Step 4: Send nudges
    await page.locator('button', { hasText: 'Send Nudges' }).click();
    await expect(page.locator('text=12 nudges sent')).toBeVisible();

    // Step 5: Navigate to nudges page
    await page.locator('nav a', { hasText: 'Nudges' }).click();
    await page.waitForURL('**/nudges');
    await expect(page.locator('h1')).toHaveText('Nudge History');
  });

  test('login -> members -> filter by product -> view member detail -> send nudge', async ({ page }) => {
    // Setup auth
    await page.route('**/auth/login', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ access_token: 'fake-jwt-token' }) })
    );
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await mockMemberScoresAPI(page);
    await mockNudgesAPI(page);

    // Step 1: Login
    await page.goto(`${BASE_URL}/login`);
    await page.locator('input[placeholder="Username"]').fill('admin');
    await page.locator('input[placeholder="Password"]').fill('apha2026');
    await page.locator('button', { hasText: 'Sign In' }).click();
    await page.waitForURL(`${BASE_URL}/`);

    // Step 2: Navigate to members
    await page.locator('nav a', { hasText: 'Members' }).click();
    await page.waitForURL('**/members');
    await expect(page.locator('text=Alice Johnson')).toBeVisible();

    // Step 3: Apply a product filter
    await page.locator('button', { hasText: /^.*education$/i }).click();
    await page.waitForTimeout(300);

    // Step 4: Click a member to view detail
    await page.locator('tr', { hasText: 'Alice Johnson' }).click();
    await page.waitForURL('**/members/mem-001');
    await expect(page.locator('h1')).toHaveText('Member Expansion Profile');

    // Step 5: Send a nudge from member detail
    await expect(page.locator('text=CPE & Training')).toBeVisible();
    const nudgeRequest = page.waitForRequest('**/nudges/send');
    await page.locator('button', { hasText: 'Send education nudge' }).click();
    const req = await nudgeRequest;
    expect(req.method()).toBe('POST');
  });

  test('dashboard -> members -> back to dashboard via sidebar', async ({ page }) => {
    await setupAuth(page);
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await mockNudgesAPI(page);

    await page.goto(`${BASE_URL}/`);
    await expect(page.locator('h1')).toHaveText('Cross-Sell Engine');

    // Navigate to members
    await page.locator('nav a', { hasText: 'Members' }).click();
    await page.waitForURL('**/members');
    await expect(page.locator('h1')).toHaveText('Expansion Opportunities');

    // Navigate back to dashboard
    await page.locator('nav a', { hasText: 'Dashboard' }).click();
    await page.waitForURL(`${BASE_URL}/`);
    await expect(page.locator('h1')).toHaveText('Cross-Sell Engine');
  });

  test('member detail -> back button -> returns to members list', async ({ page }) => {
    await setupAuth(page);
    await mockMembersAPI(page);
    await mockMemberScoresAPI(page);
    await mockNudgesAPI(page);

    await page.goto(`${BASE_URL}/members/mem-001`);
    await expect(page.locator('h1')).toHaveText('Member Expansion Profile');

    await page.locator('button', { hasText: 'Back' }).click();
    await page.waitForURL('**/members');
    await expect(page.locator('h1')).toHaveText('Expansion Opportunities');
  });
});
