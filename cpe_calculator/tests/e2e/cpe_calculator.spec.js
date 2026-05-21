import { test, expect } from '@playwright/test'

const BASE_URL = 'http://localhost:3003'

// ---------------------------------------------------------------------------
// Realistic mock data returned by the /calculate/ endpoint (preview plan)
// ---------------------------------------------------------------------------
const MOCK_CALCULATE_RESPONSE = {
  calculation_id: 'calc-abc-123',
  state_name: 'Texas',
  hours_required: 30,
  hours_completed: 8,
  hours_gap: 22,
  pct_complete: 27,
  days_until_renewal: 180,
  urgency_level: 'medium',
  urgency_message: 'Your renewal is in 6 months — start your CPE plan now to avoid a last-minute rush.',
  summary: 'You need 22 more CPE hours before your Texas license renewal. We recommend the following ACPE-accredited courses.',
  is_preview: true,
  preview_courses_count: 3,
  total_plan_hours: 22,
  member_savings_usd: 349,
  mandatory_covered: true,
  courses: [
    {
      course_id: 'course-1',
      title: 'Texas Jurisprudence & Pharmacy Law Update',
      cpe_hours: 3,
      why_recommended: 'Mandatory Texas law CE requirement for all pharmacists.',
      is_mandatory: true,
      mandatory_reason: 'TX Board requires 1h law CE per renewal cycle',
      price_nonmember: 49,
      url: 'https://pharmacist.com/courses/tx-law',
    },
    {
      course_id: 'course-2',
      title: 'Immunization Delivery: Best Practices & Updates',
      cpe_hours: 2,
      why_recommended: 'Covers the latest CDC immunization schedules relevant to community pharmacy.',
      is_mandatory: false,
      mandatory_reason: null,
      price_nonmember: 35,
      url: 'https://pharmacist.com/courses/immunization',
    },
    {
      course_id: 'course-3',
      title: 'Diabetes Management in Community Pharmacy',
      cpe_hours: 2,
      why_recommended: 'High patient impact topic aligned with your community pharmacy specialty.',
      is_mandatory: false,
      mandatory_reason: null,
      price_nonmember: 35,
      url: 'https://pharmacist.com/courses/diabetes',
    },
  ],
}

// Full plan response (after lead capture)
const MOCK_FULL_PLAN_RESPONSE = {
  ...MOCK_CALCULATE_RESPONSE,
  is_preview: false,
  courses: [
    ...MOCK_CALCULATE_RESPONSE.courses,
    {
      course_id: 'course-4',
      title: 'Medication Safety & Error Prevention',
      cpe_hours: 2,
      why_recommended: 'Addresses ISMP best practices for reducing dispensing errors.',
      is_mandatory: false,
      mandatory_reason: null,
      price_nonmember: 29,
      url: 'https://pharmacist.com/courses/med-safety',
    },
    {
      course_id: 'course-5',
      title: 'Controlled Substances & Opioid Stewardship',
      cpe_hours: 2,
      why_recommended: 'Fulfills recommended opioid education and aligns with DEA best practices.',
      is_mandatory: false,
      mandatory_reason: null,
      price_nonmember: 39,
      url: 'https://pharmacist.com/courses/opioid',
    },
  ],
}

// ---------------------------------------------------------------------------
// Helper: set up API mocks for the happy-path flow
// ---------------------------------------------------------------------------
async function mockCalculateEndpoint(page, response = MOCK_CALCULATE_RESPONSE, status = 200) {
  await page.route('**/calculate/', (route) => {
    if (route.request().method() === 'POST') {
      route.fulfill({ status, contentType: 'application/json', body: JSON.stringify(response) })
    } else {
      route.continue()
    }
  })
}

async function mockFullPlanEndpoint(page, response = MOCK_FULL_PLAN_RESPONSE) {
  await page.route('**/calculate/full/**', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(response) })
  })
}

async function mockLeadEndpoint(page) {
  await page.route('**/leads/', (route) => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ ok: true }) })
  })
}

// Helper: fill the form with valid data and submit
async function fillAndSubmitForm(page) {
  await page.selectOption('select:has(option[value="TX"])', 'TX')
  await page.selectOption('select:has(option[value="pharmacist"])', 'pharmacist')
  await page.fill('input[type="date"]', '2027-01-15')
  await page.fill('input[type="number"]', '8')
  await page.click('button[type="submit"]')
}

// ===========================================================================
// TESTS
// ===========================================================================

test.describe('Page rendering & header/footer', () => {
  test('renders header with APhA branding and Join link', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('header >> text=American Pharmacists Association')).toBeVisible()
    await expect(page.locator('header >> text=pharmacist.com')).toBeVisible()

    const joinLink = page.locator('header a:has-text("Join APhA")')
    await expect(joinLink).toBeVisible()
    await expect(joinLink).toHaveAttribute('href', 'https://pharmacist.com/join')
    await expect(joinLink).toHaveAttribute('target', '_blank')
  })

  test('renders footer with copyright and pharmacist.com link', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('footer')).toContainText('American Pharmacists Association')
    await expect(page.locator('footer')).toContainText('ACPE-accredited')
    const footerLink = page.locator('footer a')
    await expect(footerLink).toHaveAttribute('href', 'https://pharmacist.com')
  })

  test('renders the main heading and description', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('h1')).toHaveText('Free CPE Gap Calculator')
    await expect(page.locator('text=Personalized plan in 30 seconds')).toBeVisible()
  })
})

test.describe('Step indicator', () => {
  test('shows three steps with correct labels', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('text=Your info')).toBeVisible()
    await expect(page.getByText('Your plan', { exact: true })).toBeVisible()
    await expect(page.locator('text=Full access')).toBeVisible()
  })

  test('step 1 is active on initial load', async ({ page }) => {
    await page.goto(BASE_URL)

    // The first step circle should contain "1" and be styled as active (bg-apha-blue)
    const stepCircles = page.locator('.rounded-full.flex.items-center.justify-center')
    await expect(stepCircles.first()).toContainText('1')
  })

  test('step 2 becomes active after calculation', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // "Your plan" label should now be the active step
    await expect(page.getByText('Your plan', { exact: true })).toBeVisible()
    // Step 1 circle should show a checkmark (w-6 h-6 scopes to step indicator circles)
    await expect(page.locator('.w-6.h-6.rounded-full.bg-green-500').first()).toContainText('✓')
  })
})

test.describe('Form fields & validation', () => {
  test('renders all form fields with correct labels', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('text=License state *')).toBeVisible()
    await expect(page.locator('text=License type *')).toBeVisible()
    await expect(page.locator('text=License renewal date *')).toBeVisible()
    await expect(page.locator('text=CPE hours completed so far this cycle *')).toBeVisible()
    await expect(page.locator('text=Practice specialty')).toBeVisible()
  })

  test('state dropdown contains all 50 states + DC', async ({ page }) => {
    await page.goto(BASE_URL)

    const stateSelect = page.locator('select').first()
    const options = stateSelect.locator('option')
    // 51 states/DC + 1 placeholder "Select state" = 52
    await expect(options).toHaveCount(52)
    await expect(options.first()).toHaveText('Select state')
  })

  test('license type dropdown has all four options', async ({ page }) => {
    await page.goto(BASE_URL)

    const licenseSelect = page.locator('select').nth(1)
    await expect(licenseSelect.locator('option')).toHaveCount(4)
    await expect(licenseSelect.locator('option[value="pharmacist"]')).toHaveText('Pharmacist (RPh / PharmD)')
    await expect(licenseSelect.locator('option[value="technician"]')).toHaveText('Pharmacy Technician')
    await expect(licenseSelect.locator('option[value="new_practitioner"]')).toHaveText('New Practitioner (0\u20133 yrs post-grad)')
    await expect(licenseSelect.locator('option[value="student"]')).toHaveText('Student Pharmacist')
  })

  test('specialty dropdown defaults to General / Community Pharmacy', async ({ page }) => {
    await page.goto(BASE_URL)

    // Specialty is the third select
    const specialtySelect = page.locator('select').nth(2)
    await expect(specialtySelect).toHaveValue('General / Community Pharmacy')
  })

  test('CPE hours input has correct attributes', async ({ page }) => {
    await page.goto(BASE_URL)

    const hoursInput = page.locator('input[type="number"]')
    await expect(hoursInput).toHaveAttribute('min', '0')
    await expect(hoursInput).toHaveAttribute('max', '100')
    await expect(hoursInput).toHaveAttribute('step', '0.5')
    await expect(hoursInput).toHaveAttribute('placeholder', 'e.g. 8.5')
  })

  test('shows helper text under CPE hours field', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator("text=Enter 0 if you haven't started yet")).toBeVisible()
  })

  test('submit button shows correct default label', async ({ page }) => {
    await page.goto(BASE_URL)

    const submitBtn = page.locator('button[type="submit"]')
    await expect(submitBtn).toHaveText('Calculate my CPE gap →')
  })

  test('shows trust badge text below submit button', async ({ page }) => {
    await page.goto(BASE_URL)

    await expect(page.locator('text=Free · No account required · Powered by APhA')).toBeVisible()
  })

  test('native validation prevents submission without required fields', async ({ page }) => {
    await page.goto(BASE_URL)

    // Click submit without filling anything — the form should not navigate (native required)
    await page.click('button[type="submit"]')
    // Still on step 1 — heading still visible
    await expect(page.locator('h1')).toHaveText('Free CPE Gap Calculator')
  })
})

test.describe('Calculator flow — happy path', () => {
  test('submitting the form shows loading state', async ({ page }) => {
    // Delay the response so we can observe the loading state
    await page.route('**/calculate/', (route) => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(MOCK_CALCULATE_RESPONSE),
        })
      }, 500)
    })

    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // While loading, button text should change
    await expect(page.locator('button[type="submit"]')).toContainText('Generating your plan')
    // Button should be disabled
    await expect(page.locator('button[type="submit"]')).toBeDisabled()
  })

  test('displays results after successful calculation', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // Wait for step 2 results to appear
    await expect(page.locator('h2:has-text("Texas CPE Plan")')).toBeVisible()
    await expect(page.locator('text=22h still needed')).toBeVisible()
    await expect(page.locator('text=180 days to renewal')).toBeVisible()
    await expect(page.locator('text=Mandatory topics covered')).toBeVisible()
  })

  test('displays urgency message when present', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=Your renewal is in 6 months')).toBeVisible()
  })

  test('shows summary text from API response', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=You need 22 more CPE hours')).toBeVisible()
  })

  test('shows "Start over" link that resets to step 1', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=Texas CPE Plan')).toBeVisible()

    await page.click('button:has-text("Start over")')

    // Back on step 1
    await expect(page.locator('h1')).toHaveText('Free CPE Gap Calculator')
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })
})

test.describe('Gap gauge', () => {
  test('renders SVG gauge with percentage', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // The gauge shows pct_complete rounded: 27%
    await expect(page.locator('svg text:has-text("27%")')).toBeVisible()
    await expect(page.locator('svg text:has-text("complete")')).toBeVisible()
  })

  test('renders hours completed vs required', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // "8 of 30 hours"
    await expect(page.locator('text=/8.*of.*30.*hours/')).toBeVisible()
  })
})

test.describe('Course cards (PlanCard)', () => {
  test('renders correct number of preview courses', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // 3 real courses + 2 locked placeholders = we check for the real course titles
    await expect(page.locator('text=Texas Jurisprudence & Pharmacy Law Update')).toBeVisible()
    await expect(page.locator('text=Immunization Delivery: Best Practices & Updates')).toBeVisible()
    await expect(page.locator('text=Diabetes Management in Community Pharmacy')).toBeVisible()
  })

  test('mandatory course has "Required by your state" badge', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=Required by your state')).toBeVisible()
  })

  test('mandatory course shows mandatory reason', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=TX Board requires 1h law CE per renewal cycle')).toBeVisible()
  })

  test('each course card shows CPE hours', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=3h').first()).toBeVisible()
    await expect(page.locator('text=2h').first()).toBeVisible()
  })

  test('each course card has "Free with membership" badge and a "View course" link', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    const freeLabels = page.locator('text=Free with membership')
    // At least 3 visible course cards (not counting locked)
    expect(await freeLabels.count()).toBeGreaterThanOrEqual(3)

    const viewLinks = page.locator('a:has-text("View course")')
    expect(await viewLinks.count()).toBeGreaterThanOrEqual(3)
  })

  test('preview mode shows course count message', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // "Showing 3 of 5+ courses"
    await expect(page.locator('text=/Showing 3 of 5\\+ courses/')).toBeVisible()
  })

  test('locked cards display with "Unlock full plan" button', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('button:has-text("Unlock full plan")')).toBeVisible()
  })
})

test.describe('Lead capture modal', () => {
  test('opens when clicking "Unlock full plan"', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await page.click('button:has-text("Unlock full plan")')

    await expect(page.locator('text=Your full 22h plan is ready')).toBeVisible()
    await expect(page.locator('text=Enter your email to unlock all 5 recommended courses')).toBeVisible()
  })

  test('has name and email inputs', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)
    await page.click('button:has-text("Unlock full plan")')

    await expect(page.locator('input[placeholder="Your name (optional)"]')).toBeVisible()
    await expect(page.locator('input[placeholder="Your email address"]')).toBeVisible()
  })

  test('submit button is disabled without email', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)
    await page.click('button:has-text("Unlock full plan")')

    const unlockBtn = page.locator('button:has-text("Unlock my full CPE plan")')
    await expect(unlockBtn).toBeDisabled()
  })

  test('submit button enables after entering email', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)
    await page.click('button:has-text("Unlock full plan")')

    await page.fill('input[placeholder="Your email address"]', 'test@example.com')
    const unlockBtn = page.locator('button:has-text("Unlock my full CPE plan")')
    await expect(unlockBtn).toBeEnabled()
  })

  test('"Skip for now" closes the modal', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)
    await page.click('button:has-text("Unlock full plan")')

    await expect(page.locator('text=Your full 22h plan is ready')).toBeVisible()

    await page.click('button:has-text("Skip for now")')

    await expect(page.locator('text=Your full 22h plan is ready')).not.toBeVisible()
  })

  test('shows no-spam disclaimer', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)
    await page.click('button:has-text("Unlock full plan")')

    await expect(page.locator('text=No spam')).toBeVisible()
  })

  test('successful lead capture unlocks full plan and shows all courses', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await mockLeadEndpoint(page)
    await mockFullPlanEndpoint(page)
    await page.goto(BASE_URL)

    await fillAndSubmitForm(page)

    await page.click('button:has-text("Unlock full plan")')
    await page.fill('input[placeholder="Your name (optional)"]', 'Jane Doe')
    await page.fill('input[placeholder="Your email address"]', 'jane@example.com')
    await page.click('button:has-text("Unlock my full CPE plan")')

    // Modal should close and full plan should render
    await expect(page.locator('text=Your full 22h plan is ready')).not.toBeVisible()

    // All 5 courses visible (3 original + 2 new)
    await expect(page.locator('text=Medication Safety & Error Prevention')).toBeVisible()
    await expect(page.locator('text=Controlled Substances & Opioid Stewardship')).toBeVisible()

    // Locked card button should no longer exist
    await expect(page.locator('button:has-text("Unlock full plan")')).not.toBeVisible()

    // Full plan shows total count instead of preview count
    await expect(page.locator('text=/5 courses.*22h total/')).toBeVisible()
  })
})

test.describe('Membership upsell', () => {
  test('renders after result with savings and hours', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=Get all 22 hours free with APhA membership')).toBeVisible()
    await expect(page.locator('text=$349')).toBeVisible()
  })

  test('shows membership benefits badges', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=300+ CPE hours included')).toBeVisible()
    await expect(page.locator('text=JAPhA journal access')).toBeVisible()
    await expect(page.locator('text=Career resources')).toBeVisible()
    await expect(page.locator('text=Annual Meeting discounts')).toBeVisible()
  })

  test('has a "Join APhA" CTA linking to pharmacist.com/join', async ({ page }) => {
    await mockCalculateEndpoint(page)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    const joinCta = page.locator('a:has-text("Join APhA")')
    // The results section has its own join link (the upsell one)
    const upsellJoin = joinCta.last()
    await expect(upsellJoin).toHaveAttribute('href', 'https://pharmacist.com/join')
    await expect(upsellJoin).toHaveAttribute('target', '_blank')
  })
})

test.describe('Error handling', () => {
  test('shows error message when API returns an error', async ({ page }) => {
    await mockCalculateEndpoint(page, { detail: 'Invalid state code provided.' }, 422)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=Invalid state code provided.')).toBeVisible()
    // Still on step 1 form
    await expect(page.locator('button[type="submit"]')).toBeVisible()
  })

  test('shows generic error message on network failure', async ({ page }) => {
    await page.route('**/calculate/', (route) => {
      route.abort('connectionrefused')
    })
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // The hook falls back to "Something went wrong. Please try again."
    await expect(page.locator('.bg-red-50')).toBeVisible()
  })

  test('error clears when user submits again successfully', async ({ page }) => {
    // First call: error
    let callCount = 0
    await page.route('**/calculate/', (route) => {
      callCount++
      if (callCount === 1) {
        route.fulfill({ status: 500, contentType: 'application/json', body: JSON.stringify({ detail: 'Server error' }) })
      } else {
        route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify(MOCK_CALCULATE_RESPONSE) })
      }
    })

    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    // First call: error visible
    await expect(page.locator('.bg-red-50')).toBeVisible()

    // Submit again
    await page.click('button[type="submit"]')

    // Error should clear and results should appear
    await expect(page.locator('h2:has-text("Texas CPE Plan")')).toBeVisible()
  })
})

test.describe('Urgency levels styling', () => {
  test('critical urgency renders with red styling', async ({ page }) => {
    const criticalResponse = {
      ...MOCK_CALCULATE_RESPONSE,
      urgency_level: 'critical',
      urgency_message: 'Your renewal is in 2 weeks! Act now.',
    }
    await mockCalculateEndpoint(page, criticalResponse)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    const urgencyBanner = page.locator('text=Your renewal is in 2 weeks! Act now.')
    await expect(urgencyBanner).toBeVisible()
    // The parent div should have bg-red-50 class for critical
    const container = page.locator('.bg-red-50.border.rounded-xl')
    await expect(container).toBeVisible()
  })

  test('low urgency renders with green styling', async ({ page }) => {
    const lowResponse = {
      ...MOCK_CALCULATE_RESPONSE,
      urgency_level: 'low',
      urgency_message: 'You have plenty of time — no rush.',
    }
    await mockCalculateEndpoint(page, lowResponse)
    await page.goto(BASE_URL)
    await fillAndSubmitForm(page)

    await expect(page.locator('text=You have plenty of time')).toBeVisible()
    const container = page.locator('.bg-green-50.border.rounded-xl')
    await expect(container).toBeVisible()
  })
})

test.describe('Routing', () => {
  test('root path loads the calculator page', async ({ page }) => {
    await page.goto(BASE_URL)
    await expect(page.locator('h1')).toHaveText('Free CPE Gap Calculator')
  })

  test('/state/:stateCode path loads the calculator page', async ({ page }) => {
    await page.goto(`${BASE_URL}/state/TX`)
    await expect(page.locator('h1')).toHaveText('Free CPE Gap Calculator')
  })
})
