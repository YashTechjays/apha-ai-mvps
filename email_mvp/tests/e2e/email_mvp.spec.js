import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3002';

// ---------------------------------------------------------------------------
// Shared mock data
// ---------------------------------------------------------------------------

const mockMembers = [
  {
    id: 'aaaa-1111-bbbb-2222',
    first_name: 'Alice',
    last_name: 'Johnson',
    email: 'alice@example.com',
    tier: 'gold',
    cpe_credits_ytd: 24,
    webinars_attended_ytd: 5,
    portal_sessions_last_30d: 12,
    email_open_rate: 0.82,
  },
  {
    id: 'cccc-3333-dddd-4444',
    first_name: 'Bob',
    last_name: 'Smith',
    email: 'bob@example.com',
    tier: 'silver',
    cpe_credits_ytd: 10,
    webinars_attended_ytd: 2,
    portal_sessions_last_30d: 4,
    email_open_rate: 0.45,
  },
  {
    id: 'eeee-5555-ffff-6666',
    first_name: 'Carol',
    last_name: 'Davis',
    email: 'carol@example.com',
    tier: 'bronze',
    cpe_credits_ytd: 6,
    webinars_attended_ytd: 1,
    portal_sessions_last_30d: 1,
    email_open_rate: 0.2,
  },
];

const mockAnalyticsSummary = {
  total_sends: 150,
  open_rate: 0.62,
  click_rate: 0.18,
  delivery_rate: 0.97,
  avg_benefit_value_usd: 320,
  avg_roi_multiplier: 4.2,
  total_value_delivered_usd: 48000,
  avg_qc_score: 0.85,
  avg_personalization_score: 0.78,
  sent: 130,
};

const mockStatusData = [
  { status: 'sent', count: 130 },
  { status: 'qc_passed', count: 8 },
  { status: 'qc_failed', count: 5 },
  { status: 'failed', count: 3 },
  { status: 'pending', count: 4 },
];

const mockEmailSends = [
  {
    id: 'email-001',
    member_id: 'aaaa-1111-bbbb-2222',
    send_month: '2026-05',
    subject_line: 'Your APhA Membership Value Report',
    status: 'sent',
    total_value_usd: 450,
    qc_score: 0.92,
    personalization_score: 0.88,
    opened: true,
    clicked: true,
  },
  {
    id: 'email-002',
    member_id: 'cccc-3333-dddd-4444',
    send_month: '2026-05',
    subject_line: 'Your Monthly Benefits Summary',
    status: 'qc_failed',
    total_value_usd: 200,
    qc_score: 0.55,
    personalization_score: 0.6,
    opened: false,
    clicked: false,
  },
  {
    id: 'email-003',
    member_id: 'eeee-5555-ffff-6666',
    send_month: '2026-05',
    subject_line: null,
    status: 'pending',
    total_value_usd: 120,
    qc_score: null,
    personalization_score: null,
    opened: false,
    clicked: false,
  },
];

const mockTopMembers = [
  {
    member_id: 'aaaa-1111-bbbb-2222',
    name: 'Alice Johnson',
    tier: 'gold',
    total_value_usd: 450,
    status: 'sent',
    opened: true,
  },
  {
    member_id: 'cccc-3333-dddd-4444',
    name: 'Bob Smith',
    tier: 'silver',
    total_value_usd: 200,
    status: 'qc_failed',
    opened: false,
  },
];

const mockBenefitSummary = {
  total_value_usd: 450,
  roi_multiplier: 5.2,
  engagement_level: 'high',
  top_benefit: 'cpe credits',
};

const mockMemberEmails = [
  {
    id: 'email-001',
    send_month: '2026-05',
    status: 'sent',
    total_value_usd: 450,
    qc_score: 0.92,
    opened: true,
    clicked: true,
    sent_at: '2026-05-15T10:30:00Z',
  },
  {
    id: 'email-prev',
    send_month: '2026-04',
    status: 'sent',
    total_value_usd: 380,
    qc_score: 0.87,
    opened: true,
    clicked: false,
    sent_at: '2026-04-14T09:00:00Z',
  },
];

const mockPreview = {
  subject: 'Alice, Your APhA Membership Delivered $450 in Value This Month',
  html_body: '<div><h1>Hello Alice</h1><p>Your membership benefits this month totaled $450.</p></div>',
};

// ---------------------------------------------------------------------------
// Helper: set up common API mocks for each page
// The backend returns raw JSON (no wrapper). Axios sets response.data to the
// parsed body, and the frontend reads r.data directly.
// ---------------------------------------------------------------------------

async function mockDashboardAPIs(page) {
  await page.route('**/api/analytics/summary*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockAnalyticsSummary) })
  );
  await page.route('**/api/analytics/by-status*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockStatusData) })
  );
}

async function mockMembersAPI(page) {
  await page.route(/\/api\/members\/?\??\S*$/, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockMembers) })
  );
}

async function mockEmailSendsAPI(page) {
  await page.route('**/api/emails/?**', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockEmailSends) })
  );
  await page.route('**/api/emails/', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockEmailSends) })
  );
}

async function mockAnalyticsAPIs(page) {
  await page.route('**/api/analytics/summary*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockAnalyticsSummary) })
  );
  await page.route('**/api/analytics/top-members*', (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockTopMembers) })
  );
}

async function mockMemberDetailAPIs(page, memberId = 'aaaa-1111-bbbb-2222') {
  await page.route(`**/api/members/${memberId}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockMembers[0]) })
  );
  await page.route(`**/api/members/${memberId}/benefit-summary*`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockBenefitSummary) })
  );
  await page.route(`**/api/emails/member/${memberId}`, (route) =>
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockMemberEmails) })
  );
}

// ---------------------------------------------------------------------------
// Tests: Layout and Navigation
// ---------------------------------------------------------------------------

test.describe('Layout and Navigation', () => {
  test('should render the top navigation bar with app title', async ({ page }) => {
    await mockDashboardAPIs(page);
    await page.goto(BASE_URL);

    await expect(page.locator('nav')).toBeVisible();
    await expect(page.locator('nav >> text=APhA Email MVP')).toBeVisible();
  });

  test('should show all four navigation links', async ({ page }) => {
    await mockDashboardAPIs(page);
    await page.goto(BASE_URL);

    const navLinks = page.locator('nav a');
    await expect(navLinks).toHaveCount(4);
    await expect(navLinks.nth(0)).toHaveText('Dashboard');
    await expect(navLinks.nth(1)).toHaveText('Members');
    await expect(navLinks.nth(2)).toHaveText('Email Sends');
    await expect(navLinks.nth(3)).toHaveText('Analytics');
  });

  test('should highlight the active nav link for Dashboard on /', async ({ page }) => {
    await mockDashboardAPIs(page);
    await page.goto(BASE_URL);

    const dashboardLink = page.locator('nav a', { hasText: 'Dashboard' });
    await expect(dashboardLink).toHaveClass(/font-semibold/);
    await expect(dashboardLink).toHaveClass(/border-b-2/);
  });

  test('should navigate to Members page when clicking Members link', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await page.goto(BASE_URL);

    await page.locator('nav a', { hasText: 'Members' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/members`);
    await expect(page.locator('h1', { hasText: 'Members' })).toBeVisible();
  });

  test('should navigate to Email Sends page', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockEmailSendsAPI(page);
    await page.goto(BASE_URL);

    await page.locator('nav a', { hasText: 'Email Sends' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/emails`);
    await expect(page.locator('h1', { hasText: 'Email Sends' })).toBeVisible();
  });

  test('should navigate to Analytics page', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockAnalyticsAPIs(page);
    await page.goto(BASE_URL);

    await page.locator('nav a', { hasText: 'Analytics' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/analytics`);
    await expect(page.locator('h1', { hasText: 'Analytics' })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Tests: Dashboard Page
// ---------------------------------------------------------------------------

test.describe('Dashboard Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockDashboardAPIs(page);
    await page.goto(BASE_URL);
  });

  test('should display the page heading and description', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Email Campaign Dashboard' })).toBeVisible();
    await expect(page.locator('text=Monthly personalized member value emails')).toBeVisible();
  });

  test('should render four stat cards with correct values', async ({ page }) => {
    await expect(page.locator('text=Total Sends')).toBeVisible();
    await expect(page.locator('text=150')).toBeVisible();

    await expect(page.locator('text=Open Rate').first()).toBeVisible();
    await expect(page.locator('text=62.0%').first()).toBeVisible();

    await expect(page.locator('text=Avg Benefit Value')).toBeVisible();
    await expect(page.locator('text=$320')).toBeVisible();
    await expect(page.locator('text=4.2x ROI')).toBeVisible();

    await expect(page.locator('text=Total Value Delivered').first()).toBeVisible();
    await expect(page.locator('text=$48.0k').first()).toBeVisible();
  });

  test('should display the Email Status Breakdown chart section', async ({ page }) => {
    await expect(page.locator('text=Email Status Breakdown')).toBeVisible();
    // Recharts renders SVG inside a responsive container
    const chartContainer = page.locator('.recharts-responsive-container').first();
    await expect(chartContainer).toBeVisible();
  });

  test('should display the QC & Personalization Scores section with progress bars', async ({ page }) => {
    await expect(page.locator('text=QC & Personalization Scores')).toBeVisible();

    const labels = ['Delivery Rate', 'Open Rate', 'Click Rate', 'Avg QC Score', 'Avg Personalization'];
    for (const label of labels) {
      await expect(page.locator(`text=${label}`).first()).toBeVisible();
    }

    // Verify computed percentage values from mockAnalyticsSummary
    await expect(page.locator('text=97.0%')).toBeVisible(); // delivery_rate
    await expect(page.locator('text=85.0%')).toBeVisible(); // avg_qc_score
    await expect(page.locator('text=78.0%')).toBeVisible(); // avg_personalization_score
  });

  test('should show month selector input', async ({ page }) => {
    const monthInput = page.locator('input[type="month"]');
    await expect(monthInput).toBeVisible();
  });

  test('should show Dry Run and Send Batch buttons', async ({ page }) => {
    await expect(page.locator('button', { hasText: 'Dry Run' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Send Batch' })).toBeVisible();
  });

  test('should show batch result banner after running a dry batch', async ({ page }) => {
    await page.route('**/api/emails/run-batch*', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ sent: 120, qc_failed: 5, failed: 2, skipped: 3 }),
      })
    );

    await page.locator('button', { hasText: 'Dry Run' }).click();

    await expect(page.locator('text=Batch complete')).toBeVisible();
    await expect(page.locator('text=Sent: 120')).toBeVisible();
    await expect(page.locator('text=QC Failed: 5')).toBeVisible();
    await expect(page.locator('text=Errors: 2')).toBeVisible();
    await expect(page.locator('text=Skipped: 3')).toBeVisible();
  });

  test('should show batch result banner after Send Batch', async ({ page }) => {
    await page.route('**/api/emails/run-batch*', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ sent: 95, qc_failed: 10, failed: 0, skipped: 5 }),
      })
    );

    await page.locator('button', { hasText: 'Send Batch' }).click();

    await expect(page.locator('text=Batch complete')).toBeVisible();
    await expect(page.locator('text=Sent: 95')).toBeVisible();
  });

  test('should disable buttons while batch is running', async ({ page }) => {
    await page.route('**/api/emails/run-batch*', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ sent: 1, qc_failed: 0, failed: 0, skipped: 0 }),
      });
    });

    await page.locator('button', { hasText: 'Send Batch' }).click();

    // While running, the button text changes and both buttons are disabled
    await expect(page.locator('button', { hasText: 'Running...' })).toBeVisible();
    await expect(page.locator('button', { hasText: 'Dry Run' })).toBeDisabled();
    await expect(page.locator('button', { hasText: 'Running...' })).toBeDisabled();
  });

  test('should show "No data for this month" when status data is empty', async ({ page }) => {
    await page.route('**/api/analytics/by-status*', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );
    await page.goto(BASE_URL);

    await expect(page.locator('text=No data for this month').first()).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Tests: Members Page
// ---------------------------------------------------------------------------

test.describe('Members Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockMembersAPI(page);
    await page.goto(`${BASE_URL}/members`);
  });

  test('should display the Members heading', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Members' })).toBeVisible();
  });

  test('should render a search input with placeholder', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search name or email..."]');
    await expect(searchInput).toBeVisible();
  });

  test('should render a table with correct column headers', async ({ page }) => {
    const headers = ['Name', 'Email', 'Tier', 'CPE Credits', 'Webinars', 'Portal Sessions', 'Email Open Rate'];
    for (const header of headers) {
      await expect(page.getByRole('columnheader', { name: header, exact: true })).toBeVisible();
    }
  });

  test('should display all three mock members in the table', async ({ page }) => {
    await expect(page.locator('td', { hasText: 'Alice Johnson' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Bob Smith' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Carol Davis' })).toBeVisible();
  });

  test('should display member data correctly in table cells', async ({ page }) => {
    await expect(page.locator('td', { hasText: 'alice@example.com' })).toBeVisible();
    await expect(page.locator('td >> text=gold')).toBeVisible();

    // Check Alice's row for CPE credits and open rate
    const aliceRow = page.locator('tr', { hasText: 'Alice Johnson' });
    await expect(aliceRow.locator('td').nth(3)).toHaveText('24');
    await expect(aliceRow.locator('td').nth(6)).toHaveText('82%');
  });

  test('should filter members by name search', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search name or email..."]');
    await searchInput.fill('Alice');

    await expect(page.locator('td', { hasText: 'Alice Johnson' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Bob Smith' })).not.toBeVisible();
    await expect(page.locator('td', { hasText: 'Carol Davis' })).not.toBeVisible();
  });

  test('should filter members by email search', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search name or email..."]');
    await searchInput.fill('bob@');

    await expect(page.locator('td', { hasText: 'Bob Smith' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Alice Johnson' })).not.toBeVisible();
  });

  test('should show no rows when search matches nothing', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search name or email..."]');
    await searchInput.fill('nonexistent_query_xyz');

    const rows = page.locator('tbody tr');
    await expect(rows).toHaveCount(0);
  });

  test('should perform case-insensitive search', async ({ page }) => {
    const searchInput = page.locator('input[placeholder="Search name or email..."]');
    await searchInput.fill('aLiCe');

    await expect(page.locator('td', { hasText: 'Alice Johnson' })).toBeVisible();
  });

  test('should have View links that navigate to member detail', async ({ page }) => {
    const viewLinks = page.locator('a', { hasText: 'View' });
    await expect(viewLinks).toHaveCount(3);
    await expect(viewLinks.first()).toHaveAttribute('href', '/members/aaaa-1111-bbbb-2222');
  });

  test('should display tier badges with capitalize styling', async ({ page }) => {
    const goldBadge = page.locator('span.capitalize', { hasText: 'gold' });
    await expect(goldBadge).toBeVisible();
    await expect(goldBadge).toHaveClass(/bg-blue-100/);
  });
});

// ---------------------------------------------------------------------------
// Tests: Member Detail Page
// ---------------------------------------------------------------------------

test.describe('Member Detail Page', () => {
  const memberId = 'aaaa-1111-bbbb-2222';

  test.beforeEach(async ({ page }) => {
    await mockMemberDetailAPIs(page, memberId);
    await page.goto(`${BASE_URL}/members/${memberId}`);
  });

  test('should display member name and email', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Alice Johnson' })).toBeVisible();
    await expect(page.locator('text=alice@example.com')).toBeVisible();
  });

  test('should display the member tier badge', async ({ page }) => {
    await expect(page.locator('span.capitalize', { hasText: 'gold' })).toBeVisible();
  });

  test('should display benefit summary cards', async ({ page }) => {
    await expect(page.locator('text=Total Benefit Value')).toBeVisible();
    await expect(page.locator('text=$450').first()).toBeVisible();

    await expect(page.locator('text=ROI Multiplier')).toBeVisible();
    await expect(page.locator('text=5.2x')).toBeVisible();

    await expect(page.locator('text=Engagement Level')).toBeVisible();
    await expect(page.locator('text=high')).toBeVisible();

    await expect(page.locator('text=Top Benefit')).toBeVisible();
    await expect(page.locator('text=cpe credits')).toBeVisible();
  });

  test('should show the email preview section with Generate Preview button', async ({ page }) => {
    await expect(page.locator('text=Email Preview')).toBeVisible();
    await expect(page.locator('button', { hasText: 'Generate Preview' })).toBeVisible();
    await expect(
      page.locator('text=Click "Generate Preview" to see the AI-personalized email for this member.')
    ).toBeVisible();
  });

  test('should not show Send Email button before preview is generated', async ({ page }) => {
    await expect(page.locator('button', { hasText: 'Send Email' })).not.toBeVisible();
  });

  test('should generate and display email preview on button click', async ({ page }) => {
    await page.route(`**/api/emails/preview/${memberId}*`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      })
    );

    await page.locator('button', { hasText: 'Generate Preview' }).click();

    await expect(page.locator('text=Subject')).toBeVisible();
    await expect(
      page.locator('text=Alice, Your APhA Membership Delivered $450 in Value This Month')
    ).toBeVisible();
    // The HTML body should be rendered via dangerouslySetInnerHTML
    await expect(page.locator('text=Hello Alice')).toBeVisible();
  });

  test('should show Send Email button after preview is generated', async ({ page }) => {
    await page.route(`**/api/emails/preview/${memberId}*`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      })
    );

    await page.locator('button', { hasText: 'Generate Preview' }).click();
    await expect(page.locator('button', { hasText: 'Send Email' })).toBeVisible();
  });

  test('should show "Generating..." while preview is loading', async ({ page }) => {
    await page.route(`**/api/emails/preview/${memberId}*`, async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      });
    });

    await page.locator('button', { hasText: 'Generate Preview' }).click();
    await expect(page.locator('button', { hasText: 'Generating...' })).toBeVisible();
  });

  test('should display email history table with correct headers', async ({ page }) => {
    await expect(page.locator('text=Email History')).toBeVisible();

    const headers = ['Month', 'Status', 'Value', 'QC Score', 'Opened', 'Clicked', 'Sent At'];
    for (const h of headers) {
      await expect(page.locator('th', { hasText: h })).toBeVisible();
    }
  });

  test('should display email history rows with correct data', async ({ page }) => {
    await expect(page.locator('td', { hasText: '2026-05' })).toBeVisible();
    await expect(page.locator('td', { hasText: '2026-04' })).toBeVisible();
    await expect(page.locator('td', { hasText: '$450' })).toBeVisible();
    await expect(page.locator('td', { hasText: '92%' })).toBeVisible();
  });

  test('should display status badges in email history', async ({ page }) => {
    const sentBadges = page.locator('span.rounded-full', { hasText: 'sent' });
    await expect(sentBadges.first()).toBeVisible();
  });

  test('should show loading state when member data has not loaded', async ({ page }) => {
    await page.route('**/api/members/slow-member', async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockMembers[0]),
      });
    });
    await page.route('**/api/members/slow-member/benefit-summary*', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(mockBenefitSummary) })
    );
    await page.route('**/api/emails/member/slow-member', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );

    await page.goto(`${BASE_URL}/members/slow-member`);
    await expect(page.locator('text=Loading...')).toBeVisible();
  });

  test('should show "No emails sent yet." when email history is empty', async ({ page }) => {
    await page.route(`**/api/emails/member/${memberId}`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );
    await page.goto(`${BASE_URL}/members/${memberId}`);

    await expect(page.locator('text=No emails sent yet.')).toBeVisible();
  });

  test('should send email, clear preview, and refresh history', async ({ page }) => {
    await page.route(`**/api/emails/preview/${memberId}*`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      })
    );
    await page.route(`**/api/emails/send/${memberId}*`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) })
    );

    // Generate preview
    await page.locator('button', { hasText: 'Generate Preview' }).click();
    await expect(page.locator('button', { hasText: 'Send Email' })).toBeVisible();

    // Send the email
    await page.locator('button', { hasText: 'Send Email' }).click();

    // After sending, preview should be cleared (Subject line from preview gone)
    await expect(page.locator('text=Email History')).toBeVisible();
    // The preview subject should no longer be visible
    await expect(
      page.locator('text=Alice, Your APhA Membership Delivered $450 in Value This Month')
    ).not.toBeVisible();
  });

  test('should show "Sending..." while email is being sent', async ({ page }) => {
    await page.route(`**/api/emails/preview/${memberId}*`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      })
    );
    await page.route(`**/api/emails/send/${memberId}*`, async (route) => {
      await new Promise((resolve) => setTimeout(resolve, 500));
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) });
    });

    await page.locator('button', { hasText: 'Generate Preview' }).click();
    await expect(page.locator('button', { hasText: 'Send Email' })).toBeVisible();
    await page.locator('button', { hasText: 'Send Email' }).click();

    await expect(page.locator('button', { hasText: 'Sending...' })).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Tests: Email Sends Page
// ---------------------------------------------------------------------------

test.describe('Email Sends Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockEmailSendsAPI(page);
    await page.goto(`${BASE_URL}/emails`);
  });

  test('should display the Email Sends heading', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Email Sends' })).toBeVisible();
  });

  test('should render filter controls: month input and status dropdown', async ({ page }) => {
    const monthInput = page.locator('input[type="month"]');
    await expect(monthInput).toBeVisible();

    const statusSelect = page.locator('select');
    await expect(statusSelect).toBeVisible();
  });

  test('should display status dropdown with all options', async ({ page }) => {
    const options = page.locator('select option');
    await expect(options).toHaveCount(5);
    await expect(options.nth(0)).toHaveText('All statuses');
    await expect(options.nth(1)).toHaveText('sent');
    await expect(options.nth(2)).toHaveText('qc_failed');
    await expect(options.nth(3)).toHaveText('failed');
    await expect(options.nth(4)).toHaveText('pending');
  });

  test('should render a table with correct column headers', async ({ page }) => {
    const headers = ['Member', 'Month', 'Subject', 'Status', 'Value', 'QC', 'Personalization', 'Opened', 'Clicked'];
    for (const header of headers) {
      await expect(page.locator('th', { hasText: header })).toBeVisible();
    }
  });

  test('should display email send rows with truncated member IDs', async ({ page }) => {
    // member_id.slice(0, 8) + "..."
    await expect(page.locator('a', { hasText: 'aaaa-111' })).toBeVisible();
    await expect(page.locator('a', { hasText: 'cccc-333' })).toBeVisible();
  });

  test('should display status badges for each email send', async ({ page }) => {
    await expect(page.locator('span.rounded-full', { hasText: 'sent' })).toBeVisible();
    await expect(page.locator('span.rounded-full', { hasText: 'qc failed' })).toBeVisible();
    await expect(page.locator('span.rounded-full', { hasText: 'pending' })).toBeVisible();
  });

  test('StatusBadge should replace underscores with spaces', async ({ page }) => {
    // "qc_failed" should render as "qc failed"
    const badge = page.locator('span.rounded-full', { hasText: 'qc failed' });
    await expect(badge).toBeVisible();
    const text = await badge.textContent();
    expect(text).not.toContain('_');
  });

  test('should show subject lines and dash for null subjects', async ({ page }) => {
    await expect(page.locator('td', { hasText: 'Your APhA Membership Value Report' })).toBeVisible();
    // null subject renders as em-dash
    const pendingRow = page.locator('tr', { hasText: 'pending' });
    await expect(pendingRow.locator('td').nth(2)).toContainText('\u2014');
  });

  test('should display QC scores with color coding', async ({ page }) => {
    // 92% (qc_score 0.92 >= 0.7) should be green
    await expect(page.locator('span.text-green-700', { hasText: '92%' })).toBeVisible();
    // 55% (qc_score 0.55 < 0.7) should be amber
    await expect(page.locator('span.text-amber-600', { hasText: '55%' })).toBeVisible();
  });

  test('should display personalization scores', async ({ page }) => {
    await expect(page.locator('td', { hasText: '88%' })).toBeVisible();
    await expect(page.locator('td', { hasText: '60%' })).toBeVisible();
  });

  test('should display opened/clicked check marks and dashes', async ({ page }) => {
    const sentRow = page.locator('tr').filter({ hasText: 'Your APhA Membership Value Report' });
    await expect(sentRow.locator('td').nth(7)).toContainText('\u2713');
    await expect(sentRow.locator('td').nth(8)).toContainText('\u2713');

    // Pending row should have dashes
    const pendingRow = page.locator('tr', { hasText: 'pending' });
    await expect(pendingRow.locator('td').nth(7)).toContainText('\u2014');
  });

  test('should link member IDs to member detail pages', async ({ page }) => {
    const memberLink = page.locator('a', { hasText: 'aaaa-111' });
    await expect(memberLink).toHaveAttribute('href', '/members/aaaa-1111-bbbb-2222');
  });

  test('should show empty state message when no emails match filter', async ({ page }) => {
    await page.route('**/api/emails/**', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );
    await page.goto(`${BASE_URL}/emails`);

    await expect(page.locator('text=No emails for this filter. Run a batch from the Dashboard.')).toBeVisible();
  });

  test('should refetch data when status filter changes', async ({ page }) => {
    const requests = [];
    await page.route('**/api/emails/**', (route) => {
      requests.push(route.request().url());
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockEmailSends),
      });
    });

    await page.locator('select').selectOption('sent');
    await page.waitForTimeout(300);

    const sentRequest = requests.find((url) => url.includes('status=sent'));
    expect(sentRequest).toBeTruthy();
  });
});

// ---------------------------------------------------------------------------
// Tests: Analytics Page
// ---------------------------------------------------------------------------

test.describe('Analytics Page', () => {
  test.beforeEach(async ({ page }) => {
    await mockAnalyticsAPIs(page);
    await page.goto(`${BASE_URL}/analytics`);
  });

  test('should display the Analytics heading', async ({ page }) => {
    await expect(page.locator('h1', { hasText: 'Analytics' })).toBeVisible();
  });

  test('should show the month selector', async ({ page }) => {
    const monthInput = page.locator('input[type="month"]');
    await expect(monthInput).toBeVisible();
  });

  test('should render eight stat cards with correct labels', async ({ page }) => {
    const labels = [
      'Emails Sent',
      'Open Rate',
      'Click Rate',
      'Total Value Delivered',
      'Avg Benefit / Member',
      'Avg ROI',
      'Avg QC Score',
      'Avg Personalization',
    ];
    for (const label of labels) {
      await expect(page.locator(`text=${label}`)).toBeVisible();
    }
  });

  test('should display correct stat card values from mock data', async ({ page }) => {
    await expect(page.locator('text=130')).toBeVisible();       // sent
    await expect(page.locator('text=62.0%').first()).toBeVisible(); // open_rate
    await expect(page.locator('text=18.0%')).toBeVisible();     // click_rate
    await expect(page.locator('text=$48.0k')).toBeVisible();    // total value delivered
    await expect(page.locator('text=$320')).toBeVisible();      // avg benefit
    await expect(page.locator('text=4.2x')).toBeVisible();      // avg ROI
    await expect(page.locator('text=85%')).toBeVisible();       // avg QC score
    await expect(page.locator('text=78%')).toBeVisible();       // avg personalization
  });

  test('should display the Top 10 Members by Benefit Value section', async ({ page }) => {
    await expect(page.locator('text=Top 10 Members by Benefit Value')).toBeVisible();
  });

  test('should render the top members table with correct headers', async ({ page }) => {
    const headers = ['Rank', 'Member', 'Tier', 'Benefit Value', 'Status', 'Opened'];
    for (const h of headers) {
      await expect(page.locator('th', { hasText: h })).toBeVisible();
    }
  });

  test('should display top members with rank numbers', async ({ page }) => {
    await expect(page.locator('text=#1')).toBeVisible();
    await expect(page.locator('text=#2')).toBeVisible();
  });

  test('should display top member names as links to detail pages', async ({ page }) => {
    const aliceLink = page.locator('a', { hasText: 'Alice Johnson' });
    await expect(aliceLink).toBeVisible();
    await expect(aliceLink).toHaveAttribute('href', '/members/aaaa-1111-bbbb-2222');
  });

  test('should display tier badges in top members table', async ({ page }) => {
    await expect(page.locator('span.capitalize', { hasText: 'gold' })).toBeVisible();
    await expect(page.locator('span.capitalize', { hasText: 'silver' })).toBeVisible();
  });

  test('should show benefit values in top members table', async ({ page }) => {
    await expect(page.locator('td', { hasText: '$450' })).toBeVisible();
    await expect(page.locator('td', { hasText: '$200' })).toBeVisible();
  });

  test('should show opened indicators in top members table', async ({ page }) => {
    const rows = page.locator('table tbody tr');
    // Alice (opened: true) should show check mark
    await expect(rows.nth(0).locator('td').nth(5)).toContainText('\u2713');
    // Bob (opened: false) should show dash
    await expect(rows.nth(1).locator('td').nth(5)).toContainText('\u2014');
  });

  test('should show empty state when no top members data', async ({ page }) => {
    await page.route('**/api/analytics/top-members*', (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify([]) })
    );
    await page.goto(`${BASE_URL}/analytics`);

    await expect(page.locator('text=No data for this period.')).toBeVisible();
  });

  test('should use green color for QC score card when avg_qc_score >= 0.7', async ({ page }) => {
    // avg_qc_score is 0.85, so StatCard should use color="green" -> border-green-600
    const qcCard = page.locator('.border-l-4', { hasText: 'Avg QC Score' });
    await expect(qcCard).toHaveClass(/border-green-600/);
  });
});

// ---------------------------------------------------------------------------
// Tests: Full User Flows
// ---------------------------------------------------------------------------

test.describe('Full User Flows', () => {
  test('flow: Dashboard -> Members -> search -> view member detail', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await mockMemberDetailAPIs(page, 'aaaa-1111-bbbb-2222');

    // Start on Dashboard
    await page.goto(BASE_URL);
    await expect(page.locator('h1', { hasText: 'Email Campaign Dashboard' })).toBeVisible();

    // Navigate to Members
    await page.locator('nav a', { hasText: 'Members' }).click();
    await expect(page.locator('h1', { hasText: 'Members' })).toBeVisible();

    // Search for Alice
    await page.locator('input[placeholder="Search name or email..."]').fill('Alice');
    await expect(page.locator('td', { hasText: 'Alice Johnson' })).toBeVisible();
    await expect(page.locator('td', { hasText: 'Bob Smith' })).not.toBeVisible();

    // Click View to go to detail page
    await page.locator('a', { hasText: 'View' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/members/aaaa-1111-bbbb-2222`);
    await expect(page.locator('h1', { hasText: 'Alice Johnson' })).toBeVisible();
    await expect(page.locator('text=alice@example.com')).toBeVisible();
  });

  test('flow: Dashboard -> run dry batch -> check Email Sends', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockEmailSendsAPI(page);

    await page.route('**/api/emails/run-batch*', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ sent: 100, qc_failed: 3, failed: 1, skipped: 2 }),
      })
    );

    await page.goto(BASE_URL);

    // Run dry batch
    await page.locator('button', { hasText: 'Dry Run' }).click();
    await expect(page.locator('text=Batch complete')).toBeVisible();
    await expect(page.locator('text=Sent: 100')).toBeVisible();

    // Navigate to Email Sends
    await page.locator('nav a', { hasText: 'Email Sends' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/emails`);
    await expect(page.locator('h1', { hasText: 'Email Sends' })).toBeVisible();
  });

  test('flow: preview and send an email from member detail page', async ({ page }) => {
    const memberId = 'aaaa-1111-bbbb-2222';
    await mockMemberDetailAPIs(page, memberId);

    await page.route(`**/api/emails/preview/${memberId}*`, (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockPreview),
      })
    );
    await page.route(`**/api/emails/send/${memberId}*`, (route) =>
      route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) })
    );

    await page.goto(`${BASE_URL}/members/${memberId}`);
    await expect(page.locator('h1', { hasText: 'Alice Johnson' })).toBeVisible();

    // Generate preview
    await page.locator('button', { hasText: 'Generate Preview' }).click();
    await expect(page.locator('text=Subject')).toBeVisible();
    await expect(
      page.locator('text=Alice, Your APhA Membership Delivered $450 in Value This Month')
    ).toBeVisible();

    // Send email
    await page.locator('button', { hasText: 'Send Email' }).click();

    // After send, email history should still be visible and preview cleared
    await expect(page.locator('text=Email History')).toBeVisible();
  });

  test('flow: navigate through all pages via the nav bar', async ({ page }) => {
    await mockDashboardAPIs(page);
    await mockMembersAPI(page);
    await mockEmailSendsAPI(page);
    await mockAnalyticsAPIs(page);

    // Dashboard
    await page.goto(BASE_URL);
    await expect(page.locator('h1', { hasText: 'Email Campaign Dashboard' })).toBeVisible();

    // Members
    await page.locator('nav a', { hasText: 'Members' }).click();
    await expect(page.locator('h1', { hasText: 'Members' })).toBeVisible();
    await expect(page).toHaveURL(`${BASE_URL}/members`);

    // Email Sends
    await page.locator('nav a', { hasText: 'Email Sends' }).click();
    await expect(page.locator('h1', { hasText: 'Email Sends' })).toBeVisible();
    await expect(page).toHaveURL(`${BASE_URL}/emails`);

    // Analytics
    await page.locator('nav a', { hasText: 'Analytics' }).click();
    await expect(page.locator('h1', { hasText: 'Analytics' })).toBeVisible();
    await expect(page).toHaveURL(`${BASE_URL}/analytics`);

    // Back to Dashboard
    await page.locator('nav a', { hasText: 'Dashboard' }).click();
    await expect(page.locator('h1', { hasText: 'Email Campaign Dashboard' })).toBeVisible();
    await expect(page).toHaveURL(`${BASE_URL}/`);
  });

  test('flow: Email Sends -> click member link -> member detail page', async ({ page }) => {
    await mockEmailSendsAPI(page);
    await mockMemberDetailAPIs(page, 'aaaa-1111-bbbb-2222');

    await page.goto(`${BASE_URL}/emails`);

    // Click on the first truncated member ID link
    await page.locator('a', { hasText: 'aaaa-111' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/members/aaaa-1111-bbbb-2222`);
    await expect(page.locator('h1', { hasText: 'Alice Johnson' })).toBeVisible();
  });

  test('flow: Analytics top members -> click member -> member detail', async ({ page }) => {
    await mockAnalyticsAPIs(page);
    await mockMemberDetailAPIs(page, 'aaaa-1111-bbbb-2222');

    await page.goto(`${BASE_URL}/analytics`);

    await page.locator('a', { hasText: 'Alice Johnson' }).click();
    await expect(page).toHaveURL(`${BASE_URL}/members/aaaa-1111-bbbb-2222`);
    await expect(page.locator('h1', { hasText: 'Alice Johnson' })).toBeVisible();
  });
});
