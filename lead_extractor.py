import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
def extract_venues_with_selenium(driver):
    """Extract venue data directly using Selenium after scrolling"""
    
    print("\n" + "=" * 50)
    print("Extracting venues with Selenium...")
    
    try:
        # Wait a bit more for all content to be fully rendered
        time.sleep(5)
        
        # Find all venue elements
        venue_elements = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div[jsaction*='pane']")
        print(f"📊 Found {len(venue_elements)} venue containers")
        
        venues = []
        
        for i, venue_element in enumerate(venue_elements):
            try:
                venue_data = {}
                
                # Extract venue name
                try:
                    name_element = venue_element.find_element(By.CSS_SELECTOR, "[class*='fontHeadlineSmall']")
                    venue_data['name'] = name_element.text.strip()
                except NoSuchElementException:
                    venue_data['name'] = "N/A"
                
                detail_parent = venue_element.find_element(By.CSS_SELECTOR, ".UaQhfb.fontBodyMedium")
                
                # Find the div that contains category and location
                try:
                    category_location_div = detail_parent.find_elements(By.CSS_SELECTOR, "div.W4Efsd")[1]
                    spans = category_location_div.find_elements(By.TAG_NAME, "span")
                    
                    # Assume the first span with text is the category, and the last is the location
                    
                    venue_data['category'] = spans[0].text.strip()
                    venue_data['location'] = spans[2].text.strip()
                except (NoSuchElementException, IndexError):
                    pass
                
                try:
                    phone_element = venue_element.find_element(By.CSS_SELECTOR, "span.UsdlK")
                    venue_data['phone'] = phone_element.text
                except NoSuchElementException:
                    venue_data['phone'] = "N/A"
                
                if venue_data['name'] != "N/A":
                    venues.append(venue_data)

            except Exception as e:
                print(f"Error processing venue {i}")
                continue
        
        print(f"Successfully extracted {len(venues)} venues")
        return venues
        
    except Exception as e:
        print(f"Error during extraction: {e}")
        return []