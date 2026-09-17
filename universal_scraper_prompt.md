# Prompt for Feedback: Universal E-Commerce Review Scraper Architecture

Copy and paste the prompt below to ask other AI models, senior developers, or community forums (like Reddit, Stack Overflow, or tech communities) for suggestions on building a single universal review scraping logic.

---

```text
I am building a web scraping microservice in Python (using FastAPI, Selenium, BeautifulSoup, and Pydantic) designed to extract user reviews from e-commerce websites.

### What is Currently Working Properly:
1. **Core Scraping Engine**: Headless Selenium WebDriver management, browser lifecycle control, scrolling logic, and error handling.
2. **Current Website Scrapers**: 
   - `FlipkartScraper`: Fully functional; successfully extracts reviews from Flipkart by navigating dynamic DOM trees and handling both legacy desktop HTML layouts and modern responsive React Native Web layouts.
   - `AmazonScraper`: Working selector-based extraction for Amazon review pages.
3. **Data Post-Processing Pipeline**: 
   - `TextCleaner`: HTML stripping, whitespace normalization, and emoji removal.
   - `Deduplicator`: Case-insensitive and string-level review deduplication.
   - `StorageExporter`: Clean export of scraped data into JSON, CSV, and SQLite formats.
4. **API & Testing Infrastructure**: FastAPI REST API endpoints (`/api/v1/scrape`, `/api/v1/health`) with automated unit/integration test suites (`pytest`).

### The Challenge & Goal:
Although site-specific scrapers (like `AmazonScraper` and `FlipkartScraper`) work properly, e-commerce sites frequently update their CSS classes and DOM structures. Maintaining separate scraper files or domain-specific YAML selectors per website creates ongoing maintenance overhead as new sites are added.

I want to eliminate site-specific code files and manual CSS selector configurations completely. I want to build a SINGLE, UNIFIED, HEURISTIC-BASED SCRAPER (`UniversalScraper`) that can extract clean product reviews from ANY e-commerce website dynamically (Amazon, Flipkart, Walmart, eBay, Best Buy, Shopify stores, etc.) without requiring domain-specific selector updates.

### Current Idea for Universal Logic:
1. Detect "Anchor" elements containing common review markers (e.g., "Verified Purchase", "Certified Buyer", star ratings like "5.0", "Helpful").
2. Traverse up the DOM tree from each anchor to find the "Review Card Container" (using DOM depth heuristics or boundary detection where parent text size expands).
3. Inside each container, filter out metadata (dates, author names, helpful counts, star ratings) using regex/patterns.
4. Extract the primary text block (usually the longest remaining text node) as the review body.

### Questions for You:
1. **DOM Traversal & Card Detection**: What are the most reliable heuristics or algorithms (e.g., text density analysis, lowest common ancestor (LCA), DOM layout tree analysis) to detect review containers across arbitrary websites without site-specific selectors?
2. **Metadata Filtering**: How can I cleanly distinguish between the review body text vs. metadata (author name, location, date, product variants) across different languages and site layouts?
3. **Universal Pagination**: What is the best generic logic to handle pagination (Next buttons, page numbers) vs. infinite scroll dynamically across any site?
4. **Resilience & Edge Cases**: What edge cases should I watch out for (e.g., nested seller reviews, Q&A sections, truncated "Read More" text), and how can I handle them generically?
5. **Alternative Approaches**: Would you recommend combining HTML heuristics with lightweight local NLP models or LLMs for layout classification/parsing? If so, what architecture works best for high throughput and low cost?

Please provide architectural suggestions, alternative heuristics, sample Python code logic, or best practices!
```
