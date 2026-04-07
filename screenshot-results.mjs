/**
 * Screenshot helper — captures the results and compare screens with mock data injected.
 * Usage: node screenshot-results.mjs
 */
import puppeteer from 'puppeteer';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CHROME = 'C:/Users/Hamza/.cache/puppeteer/chrome/win64-146.0.7680.153/chrome-win64/chrome.exe';
const BASE_URL = 'http://localhost:8000';

function nextScreenshotPath(label) {
  const dir = path.join(__dirname, 'temporary screenshots');
  const files = fs.readdirSync(dir).filter(f => f.startsWith('screenshot-'));
  const nums = files.map(f => parseInt(f.match(/screenshot-(\d+)/)?.[1] || '0'));
  const next = (Math.max(0, ...nums) + 1);
  return path.join(dir, `screenshot-${next}-${label}.png`);
}

const MOCK_RESULT = {
  status: "ok",
  error_message: "",
  verdict: "concerning",
  total_toxicants_detected: 3,
  total_relevant_papers: 87,
  detected_toxicants: [
    {
      toxicant_key: "parabens",
      display_name: "Parabens",
      matched_ingredients: ["methylparaben", "propylparaben"],
      tier: "high",
      best_position: 4,
      list_length: 22,
      paper_count: 42,
      top_effects: ["endocrine disruption", "breast cancer association", "reproductive toxicity"],
      top_organs: ["endocrine system", "breast tissue", "reproductive organs"],
      llm_summary: "Parabens are hormone-disrupting preservatives found near the top of this product's ingredient list, meaning they're present at a significant concentration. Forty-two peer-reviewed studies link them to endocrine disruption and reproductive concerns."
    },
    {
      toxicant_key: "formaldehyde_releasers",
      display_name: "Formaldehyde Releasers",
      matched_ingredients: ["dmdm hydantoin"],
      tier: "medium",
      best_position: 11,
      list_length: 22,
      paper_count: 28,
      top_effects: ["carcinogenicity", "skin sensitization", "allergic contact dermatitis"],
      top_organs: ["skin", "lungs", "immune system"],
      llm_summary: "DMDM hydantoin slowly releases formaldehyde, a known carcinogen, into your product over time. Studies link it to skin sensitization and allergic reactions with repeated use."
    },
    {
      toxicant_key: "phthalates",
      display_name: "Phthalates",
      matched_ingredients: ["diethyl phthalate"],
      tier: "low",
      best_position: 18,
      list_length: 22,
      paper_count: 17,
      top_effects: ["endocrine disruption", "reproductive toxicity", "developmental toxicity"],
      top_organs: ["reproductive system", "liver", "kidneys"],
      llm_summary: "Diethyl phthalate is a plasticizer used to make fragrance last longer and appears at a low concentration here. It's been linked to hormonal disruption in multiple studies."
    }
  ],
  unmatched_ingredients: ["aqua", "glycerin", "niacinamide", "cetyl alcohol", "stearic acid", "carbomer", "sodium hydroxide", "panthenol", "allantoin", "tocopherol"],
  all_ingredients: ["aqua", "glycerin", "niacinamide", "methylparaben", "cetyl alcohol", "stearic acid", "propylparaben", "carbomer", "dmdm hydantoin", "sodium hydroxide", "panthenol", "allantoin", "tocopherol", "disodium edta", "citric acid", "xanthan gum", "butylene glycol", "diethyl phthalate", "phenoxyethanol", "sodium pca", "hydroxyacetophenone", "fragrance"]
};

const MOCK_COMPARE = {
  results: [
    {
      name: "Product A (Daily Moisturizer)",
      analysis: {
        status: "ok",
        verdict: "clean",
        total_toxicants_detected: 0,
        total_relevant_papers: 0,
        detected_toxicants: [],
        unmatched_ingredients: ["aqua", "glycerin", "niacinamide", "hyaluronic acid", "ceramide np", "tocopherol"],
        all_ingredients: ["aqua", "glycerin", "niacinamide", "hyaluronic acid", "ceramide np", "tocopherol"]
      }
    },
    {
      name: "Product B (Facial Cream)",
      analysis: {
        status: "ok",
        verdict: "caution",
        total_toxicants_detected: 1,
        total_relevant_papers: 42,
        detected_toxicants: [
          {
            toxicant_key: "parabens",
            display_name: "Parabens",
            matched_ingredients: ["methylparaben"],
            tier: "high",
            best_position: 3,
            list_length: 18,
            paper_count: 42,
            top_effects: ["endocrine disruption", "reproductive toxicity"],
            top_organs: ["endocrine system", "reproductive organs"],
            llm_summary: "Methylparaben is a preservative that disrupts hormone function and appears high on this ingredient list, meaning it's at a significant concentration."
          }
        ],
        unmatched_ingredients: ["aqua", "petrolatum", "mineral oil", "glycerin"],
        all_ingredients: ["aqua", "petrolatum", "methylparaben", "mineral oil", "glycerin"]
      }
    },
    {
      name: "Product C (Night Serum)",
      analysis: {
        status: "ok",
        verdict: "concerning",
        total_toxicants_detected: 2,
        total_relevant_papers: 70,
        detected_toxicants: [
          {
            toxicant_key: "parabens",
            display_name: "Parabens",
            matched_ingredients: ["methylparaben", "butylparaben"],
            tier: "high",
            best_position: 2,
            list_length: 20,
            paper_count: 42,
            top_effects: ["endocrine disruption", "breast cancer association"],
            top_organs: ["endocrine system", "breast tissue"],
            llm_summary: "Parabens are high on the ingredient list here at a significant concentration, linked to endocrine disruption and breast tissue effects."
          },
          {
            toxicant_key: "formaldehyde_releasers",
            display_name: "Formaldehyde Releasers",
            matched_ingredients: ["quaternium-15"],
            tier: "medium",
            best_position: 9,
            list_length: 20,
            paper_count: 28,
            top_effects: ["carcinogenicity", "skin sensitization"],
            top_organs: ["skin", "lungs"],
            llm_summary: "Quaternium-15 releases formaldehyde over time, a known carcinogen. It's been repeatedly linked to skin sensitization and allergic reactions."
          }
        ],
        unmatched_ingredients: ["aqua", "retinol", "vitamin c", "peptides"],
        all_ingredients: ["aqua", "methylparaben", "retinol", "butylparaben", "vitamin c", "peptides", "glycerin", "carbomer", "quaternium-15", "fragrance"]
      }
    }
  ],
  recommendation: {
    winner_name: "Product A (Daily Moisturizer)",
    winner_verdict: "clean",
    reason: "Product A (Daily Moisturizer) has no detected toxicant concerns. Product B (Facial Cream) contains Parabens; Product C (Night Serum) contains Parabens and Formaldehyde Releasers.",
    scores: [
      { name: "Product A (Daily Moisturizer)", score: 0 },
      { name: "Product B (Facial Cream)", score: 126 },
      { name: "Product C (Night Serum)", score: 182 }
    ]
  }
};

const browser = await puppeteer.launch({
  executablePath: CHROME,
  headless: true,
  args: ['--no-sandbox', '--disable-setuid-sandbox']
});

async function shot(page, label) {
  const outPath = nextScreenshotPath(label);
  await page.screenshot({ path: outPath, fullPage: false });
  console.log(outPath);
  return outPath;
}

// --- Results screen ---
{
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle0' });

  await page.evaluate((mockResult) => {
    renderResults("Daily Glow Face Wash", mockResult);
    showScreen('results');
  }, MOCK_RESULT);

  await new Promise(r => setTimeout(r, 800));
  await shot(page, 'results-top');

  // Scroll down to see toxicant cards
  await page.evaluate(() => window.scrollTo(0, 350));
  await new Promise(r => setTimeout(r, 300));
  await shot(page, 'results-cards');

  await page.close();
}

// --- Compare results screen ---
{
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle0' });

  await page.evaluate((mockCompare) => {
    renderCompareResults(mockCompare);
    showScreen('compare-results');
  }, MOCK_COMPARE);

  await new Promise(r => setTimeout(r, 800));
  await shot(page, 'compare-results');

  await page.close();
}

// --- Watchlist screen ---
{
  const page = await browser.newPage();
  await page.setViewport({ width: 390, height: 844, deviceScaleFactor: 2 });
  await page.goto(BASE_URL, { waitUntil: 'networkidle0' });

  await page.evaluate(() => {
    showScreen('watchlist');
  });

  await new Promise(r => setTimeout(r, 600));
  await shot(page, 'watchlist');

  await page.close();
}

await browser.close();
