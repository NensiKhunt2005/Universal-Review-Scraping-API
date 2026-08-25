from unittest.mock import MagicMock
# pyrefly: ignore [missing-import]
from src.scrapers.websites.flipkart import FlipkartScraper

RESPONSIVE_MOCK_HTML = """
<html>
<body>
  <!-- Responsive layout review card -->
  <div class="css-g5y9jx" style="padding-left: 16px; padding-top: 16px; padding-bottom: 16px;">
    <div class="css-g5y9jx" style="flex-direction: row; padding-right: 16px; align-items: center;">
      <div class="css-146c3p1">3.0</div>
      <div class="css-146c3p1">Nice</div>
    </div>
    <div class="css-146c3p1">Review for: Quantity 4x250 ml</div>
    <div class="css-146c3p1">
      <span class="css-1jxf684">Really not good</span>
    </div>
    <div class="css-g5y9jx">
      <div class="css-146c3p1">Flipkart Customer</div>
    </div>
    <div class="css-g5y9jx">
      <div class="css-146c3p1">Helpful for 27</div>
      <div class="css-146c3p1">Verified Purchase</div>
    </div>
  </div>
</body>
</html>
"""

DESKTOP_MOCK_HTML = """
<html>
<body>
  <!-- Desktop layout review card -->
  <div class="col _2w1flz">
    <div class="row">
      <div class="col _3pct8L">
        <div class="_3LWZlK _1BLPMq">5★</div>
        <p class="_2-N1ha">Perfect product!</p>
      </div>
    </div>
    <div class="row">
      <div class="t-yD1y">
        <div>Awesome quality, worth the price.</div>
      </div>
    </div>
    <div class="row _2mcB0L">
      <p class="_2sc7ZR _2V5EwF">Certified Buyer</p>
    </div>
  </div>
</body>
</html>
"""

def test_extract_reviews_responsive_layout():
    scraper = FlipkartScraper("https://www.flipkart.com/some-product")
    # Mock driver page_source
    scraper.driver = MagicMock()
    scraper.driver.page_source = RESPONSIVE_MOCK_HTML
    
    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) == 1
    assert reviews[0] == "Really not good"

def test_extract_reviews_desktop_layout():
    scraper = FlipkartScraper("https://www.flipkart.com/some-product")
    # Mock driver page_source
    scraper.driver = MagicMock()
    scraper.driver.page_source = DESKTOP_MOCK_HTML
    
    reviews = scraper.extract_reviews_from_page()
    assert len(reviews) == 1
    assert reviews[0] == "Awesome quality, worth the price."
