import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def run_dynamic_scraper(sitemap_json, product_callback):
    if isinstance(sitemap_json, str):
        try:
            sitemap_json = json.loads(sitemap_json)
        except json.JSONDecodeError:
            return []
    if not sitemap_json or 'startUrl' not in sitemap_json or 'selectors' not in sitemap_json:
        return []
    
    start_url = sitemap_json['startUrl'][0]
    selectors = {s['id']: s for s in sitemap_json['selectors']}
    product_link_selector = selectors['product_url']['selector']
    name_selector = selectors.get('name', {}).get('selector', '')
    sku_selector = selectors.get('sku', {}).get('selector', '')
    price_selector = selectors.get('price', {}).get('selector', '')
    description_selector = selectors.get('description', {}).get('selector', '')
    images_selector = selectors.get('images', {}).get('selector', '')
    pagination_info = selectors.get('more')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(service=Service(), options=options)
    wait = WebDriverWait(driver, 10)

    def detect_variation_structure():
        variation_patterns = {}
        # Detect multi-level variations
        multi_level = {}
        for selector_id, selector_data in selectors.items():
            if selector_data['type'] == 'SelectorElementClick' and selector_id.startswith('variation-'):
                parts = selector_id.split('-')
                if len(parts) > 1 and parts[1].isdigit():
                    level = parts[1]
                    if level not in multi_level:
                        multi_level[level] = {}
                    multi_level[level]['click_selector'] = selector_data
                    # Collect data selectors for this level
                    data_selectors = {}
                    for field in ['name', 'sku', 'price', 'base_image', 'additional_images', 'label', 'text']:
                        key = f'variation-{level}-{field}'
                        if key in selectors:
                            data_selectors[key] = selectors[key]
                    multi_level[level]['data_selectors'] = data_selectors
        if multi_level:
            variation_patterns['multi_level'] = multi_level
        # Detect simple button click variations
        if 'button-click' in selectors:
            variation_patterns['simple_variations'] = {'button_click': selectors['button-click']}
        return variation_patterns

    def safe_click_element(element_or_selector, by_type=By.CSS_SELECTOR, max_retries=3):
        for attempt in range(max_retries):
            try:
                if isinstance(element_or_selector, str):
                    el = driver.find_element(by_type, element_or_selector)
                else:
                    el = element_or_selector
                
                # Check if element is clickable
                if not el.is_displayed() or not el.is_enabled():
                    return False
                    
                # Try JavaScript click first
                try:
                    driver.execute_script("arguments[0].click();", el)
                    return True
                except:
                    # Fallback to regular click
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", el)
                    time.sleep(1)
                    el.click()
                    return True
            except Exception as e:
                print(f"Click attempt {attempt + 1} failed: {e}")
                time.sleep(1)
        return False

    def find_elements_safely(selector, max_retries=3):
        for attempt in range(max_retries):
            try:
                if selector:
                    return driver.find_elements(By.CSS_SELECTOR, selector)
            except Exception:
                time.sleep(1)
        return []

    def get_element_info_safely(element, max_retries=3):
        for attempt in range(max_retries):
            try:
                return {
                    'text': element.text,
                    'is_displayed': element.is_displayed(),
                    'is_enabled': element.is_enabled()
                }
            except Exception:
                time.sleep(1)
        return {'text': '', 'is_displayed': False, 'is_enabled': False}

    def extract_images(soup, selector):
        images = []
        if not selector:
            return images
        img_elements = soup.select(selector) if selector else []
        for img in img_elements:
            src = img.get('src') or img.get('data-src')
            if src:
                images.append(src)
        return images

    def clean_text(text):
        if not text:
            return ''
        return ' '.join(text.strip().split())

    def extract_basic_product_data(soup, url):
        data = {}
        # Name
        if name_selector:
            name_el = soup.select_one(name_selector) if name_selector else None
            data['name'] = clean_text(name_el.text) if name_el else "N/A"
        else:
            data['name'] = "N/A"
        # SKU
        if sku_selector:
            sku_el = soup.select_one(sku_selector) if sku_selector else None
            data['sku'] = clean_text(sku_el.text) if sku_el else "N/A"
        else:
            data['sku'] = "N/A"
        # Price
        if price_selector:
            price_el = soup.select_one(price_selector) if price_selector else None
            data['product_price'] = clean_text(price_el.text) if price_el else "N/A"
        else:
            data['product_price'] = "N/A"
        # Description
        if description_selector:
            desc_el = soup.select_one(description_selector) if description_selector else None
            data['product_description'] = clean_text(desc_el.get_text()) if desc_el else "N/A"
        else:
            data['product_description'] = "N/A"
        # Base image
        base_image_selector = selectors.get('base_image', {}).get('selector', '')
        if base_image_selector:
            base_image_elem = soup.select_one(base_image_selector)
            data['base_image'] = base_image_elem['src'] if base_image_elem and base_image_elem.has_attr('src') else ''
        else:
            data['base_image'] = ''
        # Additional images
        additional_images_selector = selectors.get('additional_images', {}).get('selector', '')
        if additional_images_selector:
            additional_images_elems = soup.select(additional_images_selector)
            data['additional_images'] = '|'.join([img['src'] for img in additional_images_elems if img.has_attr('src')])
        else:
            data['additional_images'] = ''
        # Images (combine base and additional for compatibility)
        images = []
        if data['base_image']:
            images.append(data['base_image'])
        if data['additional_images']:
            images.extend(data['additional_images'].split('|'))
        data['images'] = images
        # Brand
        brand_selector = selectors.get('brand', {}).get('selector', '')
        if brand_selector:
            brand_elem = soup.select_one(brand_selector) if brand_selector else None
            data['brand'] = clean_text(brand_elem.text) if brand_elem else ''
        else:
            data['brand'] = ''
        data['product_url'] = url
        return data

    def extract_variation_data_from_selectors(soup, variation_selectors, url):
        data = {'product_url': url}
        for field_name, selector_info in variation_selectors.items():
            selector = selector_info.get('selector', '')
            el = soup.select_one(selector) if selector else None
            if el:
                if selector_info['type'] == 'SelectorImage':
                    data[field_name] = el.get('src', '')
                else:
                    data[field_name] = clean_text(el.text)
            else:
                data[field_name] = "N/A"
        return data

    def handle_multi_level_variations(soup, url, variation_patterns, level=1, parent_data=None, parent_variation_data=None):
        variations_data = []
        level_key = str(level)
        multi_config = variation_patterns.get('multi_level', {}).get(level_key)
        if not multi_config:
            return []
        click_selector = multi_config.get('click_selector', {}).get('clickElementSelector', '') or multi_config.get('click_selector', {}).get('selector', '')
        if not click_selector:
            return []
        buttons = find_elements_safely(click_selector)
        for idx, button in enumerate(buttons):
            try:
                safe_click_element(button)
                time.sleep(2)
                var_soup = BeautifulSoup(driver.page_source, 'html.parser')
                var_data = extract_variation_data_from_selectors(var_soup, multi_config.get('data_selectors', {}), url)
                # Collect label and value for this level
                variation_data = list(parent_variation_data) if parent_variation_data else []
                label = None
                value = None
                for k in [f'variation-{level}-label', 'variation_label']:
                    if k in var_data and var_data[k] != "N/A":
                        label = var_data[k]
                        break
                for k in [f'variation-{level}-text', 'variation_name']:
                    if k in var_data and var_data[k] != "N/A":
                        value = var_data[k]
                        break
                if label and value:
                    variation_data.append({label: value})
                if parent_data:
                    var_data.update(parent_data)
                # Recursively handle next level
                next_level_data = handle_multi_level_variations(var_soup, url, variation_patterns, level+1, var_data, variation_data)
                if next_level_data:
                    variations_data.extend(next_level_data)
                else:
                    var_data['variation_data'] = variation_data
                    var_data['is_variation'] = True
                    var_data['parent_url'] = url
                    # Fill in other fields from selectors if present
                    for field in ['sku', 'name', 'price', 'base_image', 'additional_images']:
                        key = f'variation-{level}-{field}'
                        if key in selectors:
                            selector = selectors[key]['selector']
                            if selector:
                                if field == 'base_image':
                                    elem = var_soup.select_one(selector)
                                    var_data[field] = elem.get('src', '') if elem else ''
                                elif field == 'additional_images':
                                    imgs = var_soup.select(selector)
                                    var_data[field] = '|'.join([img.get('src', '') for img in imgs if img.get('src', '')])
                                else:
                                    elem = var_soup.select_one(selector)
                                    var_data[field] = clean_text(elem.text) if elem else ''
                    variations_data.append(var_data)
            except Exception:
                continue
        return variations_data

    def handle_simple_variations(soup, url, variation_patterns):
        variations_data = []
        simple_config = variation_patterns.get('simple_variations', {})
        if 'button_click' not in simple_config:
            return []
        button_selector = simple_config['button_click'].get('clickElementSelector', '')
        if not button_selector:
            return []
        try:
            buttons = find_elements_safely(button_selector)
            for button in buttons:
                safe_click_element(button)
                time.sleep(2)
                var_soup = BeautifulSoup(driver.page_source, 'html.parser')
                var_data = extract_basic_product_data(var_soup, url)
                var_data['is_variation'] = True
                var_data['parent_url'] = url
                variations_data.append(var_data)
        except Exception:
            pass
        return variations_data

    def collect_product_links_from_current_page():
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_elements = soup.select(product_link_selector) if product_link_selector else []
        print(f"Found {len(product_elements)} product elements with selector '{product_link_selector}'")
        page_links = []
        for element in product_elements:
            href = element.get('href')
            if href:
                page_links.append(urljoin(start_url, href))
        return page_links

    def handle_pagination():
        all_product_links = []
        seen_links = set()
        initial_links = collect_product_links_from_current_page()
        all_product_links.extend(initial_links)
        seen_links.update(initial_links)
        print(f"Initial page loaded {len(initial_links)} product links")
        
        if not pagination_info:
            print("No pagination info found")
            return all_product_links

        pagination_type = pagination_info.get('type')
        print(f"Pagination type: {pagination_type}")
        
        if pagination_type in ['SelectorElementClick', 'SelectorPagination']:
            more_selector = pagination_info.get('clickElementSelector', '') or pagination_info.get('selector', '')
            print(f"Using pagination selector: {more_selector}")
            
            if not more_selector:
                print("No pagination selector found")
                return all_product_links
            
            consecutive_failures = 0
            max_consecutive_failures = 3
            
            while consecutive_failures < max_consecutive_failures:
                try:
                    print(f"Attempting to load next page dynamically")
                    time.sleep(2)
                    more_btns = find_elements_safely(more_selector)
                    print(f"Found {len(more_btns)} pagination elements")
                    
                    if not more_btns:
                        print("No pagination button found")
                        break
                    
                    pagination_btn = more_btns[0]
                    btn_info = get_element_info_safely(pagination_btn)
                    print(f"Pagination button state: displayed={btn_info['is_displayed']}, enabled={btn_info['is_enabled']}, text='{btn_info['text']}'")
                    
                    if not btn_info['is_displayed'] or not btn_info['is_enabled']:
                        print("Pagination button not clickable")
                        break

                    prev_count = len(all_product_links)
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", pagination_btn)
                    time.sleep(1)
                    
                    success = safe_click_element(pagination_btn)
                    if not success:
                        print("Failed to click pagination button")
                        consecutive_failures += 1
                        continue
                    
                    print("Pagination button clicked successfully")
                    
                    # Wait for new content to load
                    content_loaded = False
                    loading_waits = 0
                    for _ in range(30):  # Wait up to 30 seconds, but break as soon as new links appear
                        time.sleep(1)
                        current_links = collect_product_links_from_current_page()
                        new_unique_links = [l for l in current_links if l not in seen_links]
                        
                        if new_unique_links:
                            print(f"Found {len(new_unique_links)} new products")
                            all_product_links.extend(new_unique_links)
                            seen_links.update(new_unique_links)
                            content_loaded = True
                            consecutive_failures = 0
                            break
                        
                        loading_indicators = find_elements_safely('.loading, .spinner, [class*="load"], [id*="load"]')
                        if loading_indicators:
                            loading_waits += 1
                            print(f"Loading indicator found, continuing to wait... ({loading_waits})")
                            if loading_waits > 10:  # Waited too long for loading
                                print("Loading indicator stuck, breaking pagination loop.")
                                break
                            continue

                    # If no new products were loaded, break the loop
                    if not content_loaded:
                        print("No new content loaded after waiting")
                        consecutive_failures += 1
                        # Check for end-of-results indicators
                        end_indicators = find_elements_safely('.no-more, .end-of-results, [class*="no-more"], [class*="end"]')
                        if end_indicators:
                            print("End of results indicator found")
                            break
                        # If product count did not increase, break
                        if len(all_product_links) == prev_count:
                            print("Product count did not increase after clicking. Breaking pagination loop.")
                            break

                    print(f"Total unique product links so far: {len(all_product_links)}")
                except Exception as e:
                    print(f"Pagination error: {e}")
                    consecutive_failures += 1
                    continue
    
        print(f"Pagination completed. Total products: {len(all_product_links)}")
        return all_product_links

    def normalize_product_data(product_data, is_variation=False):
        images = product_data.get('images', [])
        if not images:
            images = []
        if images:
            product_data['base_image'] = images[0]
            product_data['additional_images'] = '|'.join(images[1:]) if len(images) > 1 else ''
        else:
            product_data['base_image'] = ''
            product_data['additional_images'] = ''
        if is_variation:
            product_data['product_type'] = 'simple'
            product_data['configurable_variation_labels'] = ''
            product_data['configurable_variations'] = ''
            # variation_data should be a list of {label: value} dicts or ""
            if not product_data.get('variation_data'):
                product_data['variation_data'] = ""
        else:
            product_data['product_type'] = 'configurable'
            # configurable_variation_labels and configurable_variations
            # Collect all variation labels and values from variations with this parent_url
            # This will be filled in tasks.py, but you can optionally prepare here if needed
            product_data['variation_data'] = ""
            product_data['configurable_variation_labels'] = ''
            product_data['configurable_variations'] = ''
        product_data['manufacturer_no'] = product_data.get('sku', 'N/A')
        product_data['store_view_code'] = ""
        product_data['visibility'] = "Catalog, Search"
        product_data['product_websites'] = "base"
        product_data['attribute_set_code'] = "Default"
        product_data['categories'] = ""
        product_data['msrp_display_actual_price_type'] = "Use config"
        product_data['account_number'] = "1122334455"
        product_data['type_erp'] = "Consumable"
        product_data['taxes_id'] = "GST for sales - 5%"
        product_data['uom'] = "Each"
        product_data['property_account_income_id'] = "411000 Sales"
        product_data['property_account_expense_id'] = "511100 Purchases / Cost of Goods"
        product_data['cost'] = ""
        product_data['vendor_cost'] = ""
        product_data['stock'] = "10"
        product_data['meta_title'] = product_data.get('name', 'N/A')

    # Main execution
    try:
        driver.get(start_url)
        print(f"Loading initial page: {start_url}")
        time.sleep(5)
        
        variation_patterns = detect_variation_structure()
        print(f"Detected variation patterns: {list(variation_patterns.keys())}")
        
        product_links = handle_pagination()
        unique_product_links = list(dict.fromkeys(product_links))
        print(f"Total unique product links collected: {len(unique_product_links)}")
        
        results = []
        scraped_urls = set()
        
        for idx, url in enumerate(unique_product_links, 1):
            if url in scraped_urls:
                continue
            scraped_urls.add(url)
            
            try:
                print(f"Scraping product {idx}/{len(unique_product_links)}: {url}")
                driver.get(url)
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                product_data = extract_basic_product_data(soup, url)
                normalize_product_data(product_data, is_variation=False)
                
                # Handle variations
                all_variations = []
                if 'multi_level' in variation_patterns:
                    all_variations = handle_multi_level_variations(soup, url, variation_patterns, level=1, parent_data=product_data)
                elif 'simple_variations' in variation_patterns:
                    all_variations = handle_simple_variations(soup, url, variation_patterns)
                
                product_data['is_variation'] = False
                
                # Normalize variations
                for v in all_variations:
                    v['parent_url'] = url
                    normalize_product_data(v, is_variation=True)
                    v['is_variation'] = True
                
                # PROCESS PRODUCT IMMEDIATELY - This is the key change
                product_callback(product_data, all_variations)
                
                # Still add to results for compatibility (if needed)
                results.append(product_data)
                results.extend(all_variations)
                    
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue
                
        print(f"Scraping completed. Total products processed: {len(results)}")
        
    except Exception as e:
        print(f"Fatal error in scraper: {e}")
        
    finally:
        driver.quit()
        
    return results