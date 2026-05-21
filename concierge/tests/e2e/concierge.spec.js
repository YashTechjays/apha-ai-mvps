import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:3001';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/** Mock the POST /chat/ endpoint with a configurable response payload. */
async function mockChatApi(page, overrides = {}) {
  const defaultPayload = {
    response: 'APhA offers several membership tiers depending on your role.',
    tier_recommendation: null,
    should_capture_lead: false,
    join_url: null,
    ...overrides,
  };
  await page.route('**/chat/', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(defaultPayload),
      });
    } else {
      route.continue();
    }
  });
}

/** Mock the POST /leads/ endpoint. */
async function mockLeadApi(page, overrides = {}) {
  await page.route('**/leads/', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ status: 'ok', ...overrides }),
    });
  });
}

/** Mock the GET /analytics/summary endpoint. */
async function mockAnalyticsApi(page, overrides = {}) {
  const defaultPayload = {
    total_conversations: 142,
    leads_captured: 38,
    lead_capture_rate: 0.267,
    avg_turns_per_conversation: 4.3,
    intent_breakdown: {
      join: 60,
      renew: 35,
      benefits: 27,
      pricing: 20,
    },
    tier_recommendations: {
      pharmacist: 50,
      student: 42,
      technician: 28,
      new_practitioner: 22,
    },
    ...overrides,
  };
  await page.route('**/analytics/summary', (route) => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(defaultPayload),
    });
  });
}

// ---------------------------------------------------------------------------
// Demo Page – rendering
// ---------------------------------------------------------------------------

test.describe('DemoPage – Page Rendering', () => {
  test('displays the APhA header with navigation links', async ({ page }) => {
    await page.goto(BASE_URL);

    // Header brand text
    await expect(page.locator('header').getByText('pharmacist.com')).toBeVisible();

    // Nav links
    for (const label of ['Membership', 'CPE', 'Publications', 'Events']) {
      await expect(page.locator('header').getByText(label)).toBeVisible();
    }
  });

  test('shows the main heading and membership description', async ({ page }) => {
    await page.goto(BASE_URL);

    await expect(
      page.getByRole('heading', { name: 'Join the American Pharmacists Association' }),
    ).toBeVisible();
    await expect(page.getByText('APhA is the largest association of pharmacists')).toBeVisible();
  });

  test('renders three membership tier cards with correct info', async ({ page }) => {
    await page.goto(BASE_URL);

    const tiers = [
      { name: 'Student', price: '~$50/yr', desc: 'For enrolled PharmD students' },
      { name: 'Pharmacist', price: '~$195/yr', desc: 'For licensed practicing pharmacists' },
      { name: 'Technician', price: '~$75/yr', desc: 'For pharmacy technicians' },
    ];

    for (const tier of tiers) {
      await expect(page.getByText(tier.name, { exact: true })).toBeVisible();
      await expect(page.getByText(tier.price)).toBeVisible();
      await expect(page.getByText(tier.desc)).toBeVisible();
    }

    // Three "Join Now" buttons in the tier grid
    const joinButtons = page.locator('main .grid button', { hasText: 'Join Now' });
    await expect(joinButtons).toHaveCount(3);
  });

  test('shows the chat prompt hint at the bottom of the page', async ({ page }) => {
    await page.goto(BASE_URL);

    await expect(
      page.getByText('Not sure which tier is right for you?'),
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Chat Widget – open / close / greeting
// ---------------------------------------------------------------------------

test.describe('ChatWidget – Open, Close, and Greeting', () => {
  test('shows a floating chat button on initial load', async ({ page }) => {
    await page.goto(BASE_URL);

    const chatButton = page.locator('button[title="Chat with APhA Membership Concierge"]');
    await expect(chatButton).toBeVisible();
  });

  test('opens the chat panel when the floating button is clicked', async ({ page }) => {
    await page.goto(BASE_URL);

    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    // Panel header
    await expect(page.getByText('APhA Membership Concierge')).toBeVisible();
    await expect(page.getByText('Powered by AI')).toBeVisible();
  });

  test('displays the greeting message from the assistant', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    await expect(
      page.getByText("I'm the APhA Membership Concierge", { exact: false }),
    ).toBeVisible();
  });

  test('closes the chat panel when the close button is clicked', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    // The close button contains the multiplication sign
    await page.locator('button:has-text("\u00d7")').click();

    // Panel should disappear, floating button should reappear
    await expect(page.getByText('APhA Membership Concierge')).not.toBeVisible();
    await expect(
      page.locator('button[title="Chat with APhA Membership Concierge"]'),
    ).toBeVisible();
  });

  test('has an input field with the correct placeholder', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    await expect(
      page.getByPlaceholder('Ask me anything about APhA membership...'),
    ).toBeVisible();
  });

  test('shows the footer attribution text', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    await expect(page.getByText('AI-powered')).toBeVisible();
    await expect(page.getByText('Built by Techjays for APhA')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Chat Widget – sending messages
// ---------------------------------------------------------------------------

test.describe('ChatWidget – Sending Messages', () => {
  test('sends a message and displays the assistant reply', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Great question! APhA membership starts at $50/year for students.',
    });
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('What are the membership prices?');
    await page.getByRole('button', { name: 'Send' }).click();

    // User message appears
    await expect(page.getByText('What are the membership prices?')).toBeVisible();

    // Assistant reply appears
    await expect(
      page.getByText('Great question! APhA membership starts at $50/year for students.'),
    ).toBeVisible();
  });

  test('sends a message on Enter key press', async ({ page }) => {
    await mockChatApi(page, { response: 'We have several tiers available.' });
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('Tell me about membership tiers');
    await input.press('Enter');

    await expect(page.getByText('Tell me about membership tiers')).toBeVisible();
    await expect(page.getByText('We have several tiers available.')).toBeVisible();
  });

  test('disables send button when input is empty', async ({ page }) => {
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const sendButton = page.getByRole('button', { name: 'Send' });
    await expect(sendButton).toBeDisabled();
  });

  test('shows error message when the API call fails', async ({ page }) => {
    await page.route('**/chat/', (route) => {
      route.fulfill({ status: 500, body: 'Internal Server Error' });
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('Hello');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(
      page.getByText("Sorry, I'm having a brief technical issue"),
    ).toBeVisible();
  });

  test('clears input after sending a message', async ({ page }) => {
    await mockChatApi(page);
    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('Hello there');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(input).toHaveValue('');
  });
});

// ---------------------------------------------------------------------------
// Chat Widget – Tier Recommendation Card
// ---------------------------------------------------------------------------

test.describe('ChatWidget – Tier Recommendation', () => {
  test('shows a TierCard when the API returns a tier_recommendation', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Based on your situation, I recommend the student tier.',
      tier_recommendation: 'student',
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('I am a PharmD student');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Recommended for you')).toBeVisible();
    await expect(page.getByText('Student Pharmacist')).toBeVisible();
    await expect(page.getByText('~$50/year')).toBeVisible();
  });

  test('shows pharmacist tier card with correct details', async ({ page }) => {
    await mockChatApi(page, {
      response: 'The pharmacist tier is great for licensed professionals.',
      tier_recommendation: 'pharmacist',
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('I am a licensed pharmacist');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Full Pharmacist')).toBeVisible();
    await expect(page.getByText('~$195/year')).toBeVisible();
  });

  test('shows technician tier card with correct details', async ({ page }) => {
    await mockChatApi(page, {
      response: 'The technician membership is ideal for you.',
      tier_recommendation: 'technician',
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('I am a pharmacy tech');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Pharmacy Technician')).toBeVisible();
    await expect(page.getByText('~$75/year')).toBeVisible();
  });

  test('TierCard has a Join Now button', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Here is my recommendation.',
      tier_recommendation: 'student',
      join_url: 'https://pharmacist.com/join/student',
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('What tier should I pick?');
    await page.getByRole('button', { name: 'Send' }).click();

    // The TierCard "Join Now" button inside the chat panel
    const tierJoinButton = page.locator('button', { hasText: /Join Now →/ });
    await expect(tierJoinButton).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Chat Widget – Join URL link
// ---------------------------------------------------------------------------

test.describe('ChatWidget – Join URL', () => {
  test('shows "Go to Join / Renew Page" link when join_url is returned', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Here is how to join.',
      join_url: 'https://pharmacist.com/join',
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('How do I join?');
    await page.getByRole('button', { name: 'Send' }).click();

    const joinLink = page.getByRole('link', { name: /Go to Join \/ Renew Page/ });
    await expect(joinLink).toBeVisible();
    await expect(joinLink).toHaveAttribute('href', 'https://pharmacist.com/join');
    await expect(joinLink).toHaveAttribute('target', '_blank');
  });
});

// ---------------------------------------------------------------------------
// Lead Capture Form
// ---------------------------------------------------------------------------

test.describe('ChatWidget – Lead Capture Form', () => {
  test('shows the lead capture form when API sets should_capture_lead', async ({ page }) => {
    await mockChatApi(page, {
      response: 'I can send you more information about membership benefits.',
      should_capture_lead: true,
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('Tell me about benefits');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Want us to send you more info?')).toBeVisible();
    await expect(page.getByPlaceholder('Your name (optional)')).toBeVisible();
    await expect(page.getByPlaceholder('Your email address')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send me info' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Skip' })).toBeVisible();
  });

  test('disables the submit button when email is empty', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Let me capture your info.',
      should_capture_lead: true,
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const input = page.getByPlaceholder('Ask me anything about APhA membership...');
    await input.fill('Benefits?');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Want us to send you more info?')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Send me info' })).toBeDisabled();
  });

  test('submits lead form and shows confirmation message', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Let me get your info.',
      should_capture_lead: true,
    });
    await mockLeadApi(page);

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    // Trigger lead form
    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('I want more info');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Want us to send you more info?')).toBeVisible();

    // Fill out the lead form
    await page.getByPlaceholder('Your name (optional)').fill('Jane Doe');
    await page.getByPlaceholder('Your email address').fill('jane@example.com');
    await page.getByRole('button', { name: 'Send me info' }).click();

    // Confirmation message
    await expect(
      page.getByText("Thanks, Jane Doe! We'll send some info to jane@example.com"),
    ).toBeVisible();
  });

  test('skipping the lead form hides it', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Let me get your info.',
      should_capture_lead: true,
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('Benefits?');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Want us to send you more info?')).toBeVisible();

    await page.getByRole('button', { name: 'Skip' }).click();

    await expect(page.getByText('Want us to send you more info?')).not.toBeVisible();
  });

  test('does not show lead form again after lead has been captured', async ({ page }) => {
    // First response triggers lead capture
    let callCount = 0;
    await page.route('**/chat/', (route) => {
      callCount++;
      if (callCount === 1) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            response: 'Let me get your info.',
            tier_recommendation: null,
            should_capture_lead: true,
            join_url: null,
          }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            response: 'Anything else I can help with?',
            tier_recommendation: null,
            should_capture_lead: true, // API still says capture, but we already captured
            join_url: null,
          }),
        });
      }
    });
    await mockLeadApi(page);

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    // First message: trigger lead form
    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('Tell me about APhA');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Want us to send you more info?')).toBeVisible();

    // Submit lead form
    await page.getByPlaceholder('Your email address').fill('test@example.com');
    await page.getByRole('button', { name: 'Send me info' }).click();
    await expect(page.getByText("We'll send some info to test@example.com")).toBeVisible();

    // Second message: should_capture_lead is true but form should NOT appear
    await chatInput.fill('What else?');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Anything else I can help with?')).toBeVisible();
    await expect(page.getByText('Want us to send you more info?')).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Navigation
// ---------------------------------------------------------------------------

test.describe('Navigation', () => {
  test('navigates from demo page to analytics dashboard via URL', async ({ page }) => {
    await mockAnalyticsApi(page);
    await page.goto(`${BASE_URL}/analytics`);

    await expect(
      page.getByRole('heading', { name: 'Concierge Analytics' }),
    ).toBeVisible();
  });

  test('demo page is served at the root route', async ({ page }) => {
    await page.goto(BASE_URL);

    await expect(
      page.getByRole('heading', { name: 'Join the American Pharmacists Association' }),
    ).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Analytics Dashboard
// ---------------------------------------------------------------------------

test.describe('AnalyticsDashboard – Rendering', () => {
  test('shows loading state before data arrives', async ({ page }) => {
    // Delay the API response so we can observe loading
    await page.route('**/analytics/summary', (route) => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            total_conversations: 0,
            leads_captured: 0,
            lead_capture_rate: 0,
            avg_turns_per_conversation: 0,
            intent_breakdown: {},
            tier_recommendations: {},
          }),
        });
      }, 2000);
    });

    await page.goto(`${BASE_URL}/analytics`);
    await expect(page.getByText('Loading analytics...')).toBeVisible();
  });

  test('displays all four stat cards with correct values', async ({ page }) => {
    await mockAnalyticsApi(page);
    await page.goto(`${BASE_URL}/analytics`);

    await expect(page.getByText('Total Conversations')).toBeVisible();
    await expect(page.getByText('142')).toBeVisible();

    await expect(page.getByText('Leads Captured')).toBeVisible();
    await expect(page.getByText('38')).toBeVisible();

    await expect(page.getByText('Lead Capture Rate')).toBeVisible();
    await expect(page.getByText('27%')).toBeVisible();

    await expect(page.getByText('Avg Turns / Conv.')).toBeVisible();
    await expect(page.getByText('4.3')).toBeVisible();
  });

  test('displays intent breakdown section', async ({ page }) => {
    await mockAnalyticsApi(page);
    await page.goto(`${BASE_URL}/analytics`);

    await expect(
      page.getByRole('heading', { name: 'Intent Breakdown' }),
    ).toBeVisible();

    for (const intent of ['join', 'renew', 'benefits', 'pricing']) {
      await expect(page.getByText(intent)).toBeVisible();
    }
  });

  test('displays tier recommendations section', async ({ page }) => {
    await mockAnalyticsApi(page);
    await page.goto(`${BASE_URL}/analytics`);

    await expect(
      page.getByRole('heading', { name: 'Tier Recommendations' }),
    ).toBeVisible();

    for (const tier of ['pharmacist', 'student', 'technician']) {
      await expect(page.getByText(tier)).toBeVisible();
    }
    // "new_practitioner" renders as "new practitioner" (underscore replaced)
    await expect(page.getByText('new practitioner')).toBeVisible();
  });

  test('shows subtitle text', async ({ page }) => {
    await mockAnalyticsApi(page);
    await page.goto(`${BASE_URL}/analytics`);

    await expect(page.getByText('AI Membership Concierge')).toBeVisible();
  });

  test('shows "No data yet" when intent breakdown is empty', async ({ page }) => {
    await mockAnalyticsApi(page, { intent_breakdown: {} });
    await page.goto(`${BASE_URL}/analytics`);

    await expect(page.getByText('No data yet.')).toBeVisible();
  });

  test('shows "No tier recommendations yet" when tier data is empty', async ({ page }) => {
    await mockAnalyticsApi(page, { tier_recommendations: {} });
    await page.goto(`${BASE_URL}/analytics`);

    await expect(page.getByText('No tier recommendations yet.')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// Full E2E Flows
// ---------------------------------------------------------------------------

test.describe('Full E2E – Membership Inquiry Flow', () => {
  test('complete flow: open chat, ask question, get tier recommendation, capture lead, see join link', async ({
    page,
  }) => {
    let chatCallCount = 0;
    await page.route('**/chat/', (route) => {
      chatCallCount++;
      if (chatCallCount === 1) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            response: 'As a pharmacy student, I recommend the Student Pharmacist tier at ~$50/year.',
            tier_recommendation: 'student',
            should_capture_lead: true,
            join_url: 'https://pharmacist.com/join/student',
          }),
        });
      } else {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            response: 'You are all set! Good luck with your studies.',
            tier_recommendation: 'student',
            should_capture_lead: false,
            join_url: 'https://pharmacist.com/join/student',
          }),
        });
      }
    });
    await mockLeadApi(page);

    await page.goto(BASE_URL);

    // 1. Page loads with tier cards visible
    await expect(page.getByText('Student')).toBeVisible();
    await expect(page.getByText('Pharmacist')).toBeVisible();
    await expect(page.getByText('Technician')).toBeVisible();

    // 2. Open the chat widget
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();
    await expect(page.getByText("I'm the APhA Membership Concierge", { exact: false })).toBeVisible();

    // 3. Ask a question
    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('I am a 2nd year PharmD student, which tier should I pick?');
    await page.getByRole('button', { name: 'Send' }).click();

    // 4. Verify user message and assistant reply
    await expect(page.getByText('I am a 2nd year PharmD student')).toBeVisible();
    await expect(page.getByText('I recommend the Student Pharmacist tier')).toBeVisible();

    // 5. TierCard appears
    await expect(page.getByText('Recommended for you')).toBeVisible();
    await expect(page.getByText('Student Pharmacist')).toBeVisible();
    await expect(page.getByText('~$50/year')).toBeVisible();

    // 6. Lead capture form appears
    await expect(page.getByText('Want us to send you more info?')).toBeVisible();

    // 7. Fill and submit lead form
    await page.getByPlaceholder('Your name (optional)').fill('Alex Student');
    await page.getByPlaceholder('Your email address').fill('alex@pharmacy.edu');
    await page.getByRole('button', { name: 'Send me info' }).click();

    // 8. Confirmation and lead form disappears
    await expect(
      page.getByText("Thanks, Alex Student! We'll send some info to alex@pharmacy.edu"),
    ).toBeVisible();
    await expect(page.getByText('Want us to send you more info?')).not.toBeVisible();

    // 9. Join/Renew link is visible
    const joinLink = page.getByRole('link', { name: /Go to Join \/ Renew Page/ });
    await expect(joinLink).toBeVisible();
    await expect(joinLink).toHaveAttribute('href', 'https://pharmacist.com/join/student');

    // 10. Send a follow-up message
    await chatInput.fill('Thanks!');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('You are all set! Good luck with your studies.')).toBeVisible();
  });

  test('multi-turn conversation maintains message history', async ({ page }) => {
    let callCount = 0;
    await page.route('**/chat/', (route) => {
      callCount++;
      const responses = [
        'Sure, what would you like to know about APhA membership?',
        'We have Student, Pharmacist, Technician, and New Practitioner tiers.',
        'The Student tier is $50/year and includes full CPE access.',
      ];
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: responses[callCount - 1] || 'I can help with that.',
          tier_recommendation: null,
          should_capture_lead: false,
          join_url: null,
        }),
      });
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();
    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');

    // Turn 1
    await chatInput.fill('Hi there');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Hi there')).toBeVisible();
    await expect(page.getByText('Sure, what would you like to know')).toBeVisible();

    // Turn 2
    await chatInput.fill('What tiers are available?');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('What tiers are available?')).toBeVisible();
    await expect(page.getByText('We have Student, Pharmacist, Technician')).toBeVisible();

    // Turn 3
    await chatInput.fill('Tell me about the student tier');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Tell me about the student tier')).toBeVisible();
    await expect(page.getByText('The Student tier is $50/year')).toBeVisible();

    // All previous messages should still be in the panel
    await expect(page.getByText('Hi there')).toBeVisible();
    await expect(page.getByText('What tiers are available?')).toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// API request validation
// ---------------------------------------------------------------------------

test.describe('API Request Validation', () => {
  test('chat API request includes session_token, message, and page_url', async ({ page }) => {
    let capturedBody = null;
    await page.route('**/chat/', (route) => {
      capturedBody = route.request().postDataJSON();
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          response: 'Got it.',
          tier_recommendation: null,
          should_capture_lead: false,
          join_url: null,
        }),
      });
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('Hello');
    await page.getByRole('button', { name: 'Send' }).click();

    await expect(page.getByText('Got it.')).toBeVisible();

    expect(capturedBody).toBeTruthy();
    expect(capturedBody.session_token).toBeTruthy();
    expect(capturedBody.message).toBe('Hello');
    expect(capturedBody.page_url).toContain('localhost');
  });

  test('lead capture API request includes correct fields', async ({ page }) => {
    await mockChatApi(page, {
      response: 'Let me get your details.',
      should_capture_lead: true,
      tier_recommendation: 'pharmacist',
    });

    let capturedLeadBody = null;
    await page.route('**/leads/', (route) => {
      capturedLeadBody = route.request().postDataJSON();
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ok' }),
      });
    });

    await page.goto(BASE_URL);
    await page.locator('button[title="Chat with APhA Membership Concierge"]').click();

    const chatInput = page.getByPlaceholder('Ask me anything about APhA membership...');
    await chatInput.fill('I want to join');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('Want us to send you more info?')).toBeVisible();

    await page.getByPlaceholder('Your name (optional)').fill('Dr. Smith');
    await page.getByPlaceholder('Your email address').fill('smith@hospital.org');
    await page.getByRole('button', { name: 'Send me info' }).click();

    await expect(page.getByText("We'll send some info to smith@hospital.org")).toBeVisible();

    expect(capturedLeadBody).toBeTruthy();
    expect(capturedLeadBody.session_token).toBeTruthy();
    expect(capturedLeadBody.email).toBe('smith@hospital.org');
    expect(capturedLeadBody.name).toBe('Dr. Smith');
    expect(capturedLeadBody.interested_tier).toBe('pharmacist');
  });
});
