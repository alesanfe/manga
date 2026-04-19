"""
Selenium Chrome driver management module.

This module provides centralized Chrome driver creation and context management
for web scraping operations.
"""

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options


def create_chrome_driver():
    """
    Create an undetected Chrome driver with standard options for web scraping.
    
    The window is positioned off-screen to avoid Cloudflare detection while
    keeping the browser in normal mode (not headless).
    
    Returns:
        uc.Chrome: Configured Chrome WebDriver instance.
    """
    options = Options()
    options.add_argument('--window-position=-3000,0')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return uc.Chrome(options=options, version_main=None)


class ChromeDriverContext:
    """
    Context manager for Chrome driver to ensure proper cleanup and avoid OSError.
    
    This context manager automatically creates a Chrome driver on entry and
    ensures it is properly closed on exit, handling Windows-specific OSError
    that can occur during driver cleanup.
    
    Usage:
        with ChromeDriverContext() as driver:
            driver.get('https://example.com')
            # Do scraping operations
        # Driver is automatically closed here
    """
    def __enter__(self):
        self.driver = create_chrome_driver()
        return self.driver
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if hasattr(self, 'driver') and self.driver:
                self.driver.quit()
        except OSError:
            pass  # Ignore Windows driver quit error
        return False
