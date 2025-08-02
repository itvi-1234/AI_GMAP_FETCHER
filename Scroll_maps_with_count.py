import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
def count_venues(driver):
    """Count current number of venues visible"""
    try:
        venues = driver.find_elements(By.CSS_SELECTOR, "div[role='feed'] > div > div[jsaction*='pane']")
        return len(venues)
    except:
        return 0

def check_end_reached(driver):
    """Check if we've reached the end of results"""
    end_phrases = [
        "You've reached the end of the list",
        "That's all the results for this area", 
        "No more results",
        "End of results"
    ]
    
    try:
        page_source = driver.page_source.lower()
        for phrase in end_phrases:
            if phrase.lower() in page_source:
                print(f"Found end message: '{phrase}'")
                return True
        return False
    except:
        return False

def scroll_google_maps(driver, max_scrolls=50, scroll_delay=3.0):
    
    """Scroll Google Maps results panel to load all venues"""
    
    print(f"Starting Google Maps scroll")
    print(f"Max scrolls: {max_scrolls}")
    print(f"Delay between scrolls: {scroll_delay}s")
    print("-" * 50)
    
    try:
        container = driver.find_element(By.CSS_SELECTOR, "div[role='feed']")
        print("Found results container")
    except NoSuchElementException:
        print("Could not find results container!")
        return False
    
    previous_count = 0
    stuck_count = 0
    
    for scroll_num in range(1, max_scrolls + 1):
        print(f"\nScroll {scroll_num}/{max_scrolls}")
        
        current_count = count_venues(driver)
        print(f" Current venues: {current_count}")
        
        if check_end_reached(driver):
            print("Reached end of results!")
            break
        
        if current_count == previous_count:
            stuck_count += 1
            print(f"No new venues loaded ({stuck_count} times)")

            driver.execute_script("""
                arguments[0].scrollTop = arguments[0].scrollTop - 300;
            """, container)
            
            if stuck_count >= 3:
                print("No progress for 3 attempts - stopping")
                break
        else:
            stuck_count = 0
            new_venues = current_count - previous_count
            print(f"Found {new_venues} new venues!")
            previous_count = current_count
        
        try:
            driver.execute_script("""
                arguments[0].scrollTop = arguments[0].scrollHeight;
            """, container)
            print(f"Scrolled to bottom")
        except Exception as e:
            print(f" Scroll failed: {e}")
            continue
        
        print(f" Waiting {scroll_delay}s...")
        time.sleep(scroll_delay)
        
        if stuck_count > 0:
            extra_wait = stuck_count * 1.0
            print(f"Extra wait: {extra_wait}s (stuck {stuck_count} times)")
            time.sleep(extra_wait)
    
    final_count = count_venues(driver)
    print(f"\nScrolling completed!")
    print(f"Final venue count: {final_count}")
    print(f"Total scrolls performed: {min(scroll_num, max_scrolls)}")
    
    # Keep the page loaded for a bit to ensure all content is rendered
    print("Waiting 5 seconds for final content load...")
    time.sleep(5)
    
    return True