import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from crawl4ai import AsyncWebCrawler
from Ai_url_generator import ReplyGenerator
from Scroll_maps_with_count import scroll_google_maps
from lead_extractor import extract_venues_with_selenium
from write_to_csv import save_venues_to_csv_simple
import re
import os

load_dotenv()

def setup_driver():
    """Setup Chrome driver with basic options"""
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1920, 1080")  
    options.add_argument("--incognito") 
    options.add_argument("--no-sandbox")  
    options.add_argument("--blink-settings=imagesEnabled=false")

    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=options
    )
    return driver

def wait_for_google_maps(driver, timeout=30):
    """Wait for Google Maps search results to load"""
    print("⏳ Waiting for Google Maps to load...")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
        )
        time.sleep(3)
        print("✅ Google Maps loaded!")
        return True
    except TimeoutException:
        print("❌ Google Maps failed to load!")
        return False

def main():
    """Main function combining scroll and scrape operations"""
    
    # Configuration
    
    city = input("Enter your city name : ")

    query = input("Enter your query : ")

    # Setup Selenium driver and scroll

    reply = None
    for provider in ["groq", "gemini"]:
        try:
            bot = ReplyGenerator(provider)
            reply = bot.generate_reply(city)
            if reply:
                break
        except Exception as e:
            print("Failed")

    locations = [loc.strip() for loc in reply.split(",")]

    print(f"🤖 commericial Localities for {city}:{locations}")

    for data in locations:

        text = data + " " + city

        query = re.sub(r' ', '+', query)
        
        final_text = query + "+" + re.sub(r' ', '+', text)

        url = f"https://www.google.com/maps/search/{final_text}"

        driver = setup_driver()
        max_scrolls = 20
        scroll_delay = 4.0
        
        try:
            # Load the page
            print("🌐 Loading Google Maps...")
            driver.get(url)
            
            # Wait for page to load
            if not wait_for_google_maps(driver):
                print("❌ Failed to load Google Maps")
                return
            
            # Scroll to load all venues
            print("\n" + "=" * 50)
            print("📜 PHASE 1: SCROLLING")
            scroll_success = scroll_google_maps(driver, max_scrolls, scroll_delay)
            
            if not scroll_success:
                print("❌ Scrolling failed")
                return
            
            # Extract venues directly from the scrolled page
            print("\n" + "=" * 50)
            print("🕷️ PHASE 2: EXTRACTING DATA")
            venues = extract_venues_with_selenium(driver)
            
            if venues:
                output_filename = f"{query}_{city}_venues.csv"
                save_venues_to_csv_simple(venues, output_filename)
                
                print("\n" + "=" * 50)
                print("✅ OPERATION COMPLETE!")
                print(f"📊 Total venues extracted: {len(venues)}")
                print(f"📁 Results saved to: {output_filename}")
                
                # Show sample data
            else:
                print("❌ No venues extracted")

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            print("\n🔧 Cleaning up...")
            driver.quit()
            print("✅ Browser closed")

if __name__ == "__main__":
    main()