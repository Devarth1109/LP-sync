# LPsyncAdmin/tasks.py
from celery import shared_task
import requests
from django.shortcuts import get_object_or_404
from LPsyncAdmin.models import Sitemap, Product, User, ProductWithErrors
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.mail import send_mail
from django.conf import settings
import time
import json
from LPsyncAdmin.web_scraper_variations import run_dynamic_scraper
import random
import string
import traceback

@shared_task
def fetch_linenplus_products(pk):
    try:
        current_user = User.objects.get(pk=pk)
        print(f"Fetching LinenPlus products for user: {current_user.email}")

        # --- Fetch LinenPlus products and save to Product model ---
        auth_url = "https://stage1.linenplus.ca/rest/V1/integration/admin/token"
        auth_payload = {
            "username": "wcmanali",
            "password": "Web@#123!"
        }
        print("Requesting LinenPlus API token...")
        auth_response = requests.post(auth_url, json=auth_payload)
        if auth_response.status_code != 200:
            print(f"Failed to fetch LinenPlus token. Status: {auth_response.status_code}")
            return False
        token = auth_response.json()
        print("Successfully fetched LinenPlus token.")

        base_url = "https://stage1.linenplus.ca/rest/V1/products"
        headers = {
            'Authorization': f'Bearer {token}',
        }
        page = 1
        page_size = 100
        linenplus_skus = set()
        linenplus_data = {}
        total_fetched = 0

        while True:
            params = {
                'searchCriteria[filter_groups][0][filters][0][field]': 'account_number',
                'searchCriteria[filter_groups][0][filters][0][value]': '127448',
                'searchCriteria[filter_groups][0][filters][0][condition_type]': 'eq',
                'searchCriteria[currentPage]': page,
                'searchCriteria[pageSize]': page_size,
                'fields': 'items[sku,name,price],total_count'
            }
            print(f"Fetching LinenPlus products page {page}...")
            response = requests.get(base_url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Failed to fetch products at page {page}. Status: {response.status_code}")
                break
            data = response.json()
            items = data.get('items', [])
            total_count = data.get('total_count', 0)

            if not items:
                print("No more products found from LinenPlus API.")
                break

            for item in items:
                sku = item.get('sku', '')
                name = item.get('name', '')
                price = item.get('price', 0)
                linenplus_skus.add(sku)
                linenplus_data[sku] = {'name': name, 'price': price}

            total_fetched += len(items)
            print(f"Fetched {len(items)} products from page {page}. Total fetched: {total_fetched} / {total_count}")

            # Check if we've fetched all products
            if total_fetched >= total_count or len(items) < page_size:
                print(f"All products fetched. Total: {total_fetched}")
                break

            page += 1

        print(f"Total LinenPlus SKUs fetched: {len(linenplus_skus)}")

        # --- Merge and flag logic ---
        all_products = Product.objects.filter(user=current_user)
        user_skus = set(all_products.values_list('sku', flat=True))
        print(f"User SKUs: {user_skus}")

        # 1. Update or create products based on LinenPlus data
        for sku in linenplus_skus:
            # If product with this SKU exists, update it and set flag to 'update'
            product = Product.objects.filter(sku=sku, user=current_user).first()
            if product:
                product.linenplus_sku = sku
                product.linenplus_price = linenplus_data[sku]['price']
                product.name = linenplus_data[sku]['name']
                product.flag = 'update'
                product.save()
                print(f"Product {sku} set to 'update' (merged LinenPlus data into existing row)")
            else:
                # If not, create a new row with flag 'delete'
                Product.objects.update_or_create(
                    linenplus_sku=sku,
                    user=current_user,
                    defaults={
                        'user': current_user,  # Ensure user is set
                        'name': linenplus_data[sku]['name'],
                        'linenplus_sku': sku,
                        'linenplus_price': linenplus_data[sku]['price'],
                        'flag': 'delete',
                        'product_type': 'simple',
                        'product_price': 0,
                    }
                )
                print(f"Product {sku} set to 'delete' (exists in LinenPlus but not in user products)")

        # 2. Set flag to 'new' for products that do not exist in LinenPlus
        for product in all_products:
            if product.sku and product.sku not in linenplus_skus:
                product.flag = 'new'
                product.save()
                print(f"Product {product.sku} set to 'new' (exists in user products but not in LinenPlus)")

        print("LinenPlus products fetched and flags updated.")
        subject = "LinenPlus Products Sync Completed"
        message = f"LinenPlus products sync completed for user {current_user.email}. Total products processed: {total_fetched}."
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [current_user.email]
        try:
            send_mail(subject, message, from_email, recipient_list)
            print(f"Notification email sent to {current_user.email}")
        except Exception as email_error:
            print(f"Error sending notification email: {email_error}")
        return True

    except Exception as e:
        print(f"Error in fetch_linenplus_products: {e}")
        return False

@shared_task
def send_websocket_update(sitemap_id, saved=0, updated=0, total=None):
    try:
        channel_layer = get_channel_layer()
        if total is None:
            total = Product.objects.filter(sitemap_id=sitemap_id).count()
        message = {
            'type': 'send_product_count',
            'count': {
                'saved': saved,
                'updated': updated,
                'total': total,
                'timestamp': time.time()
            }
        }
        async_to_sync(channel_layer.group_send)(
            f"scrape_count_{sitemap_id}",
            message
        )
        return True
    except Exception as e:
        print(f"Error sending WebSocket update: {e}")
        return False

def send_scrape_complete(sitemap_id):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"scrape_count_{sitemap_id}",
        {
            'type': 'scrape_complete',
            'sitemap_id': sitemap_id,
            'timestamp': time.time()
        }
    )

@shared_task
def scrape_products_task(sitemap_id):
    try:
        sitemap = Sitemap.objects.get(id=sitemap_id)
        project = sitemap.project
        if not project or not project.sitemap_json:
            raise ValueError(f"Sitemap {sitemap_id} has no associated project or sitemap_json.")
        sitemap_json = json.loads(project.sitemap_json)
        sitemap_json['startUrl'] = [sitemap.url]
        print("Full sitemap_json being used for scraping:")
        print(json.dumps(sitemap_json, indent=2))
        
        # Initialize counters
        saved_count = 0
        updated_count = 0
        total_products_scraped = 0

        def clean_price(price_str):
            if not price_str:
                return 0
            # Remove currency symbols, commas, and letters
            cleaned = (
                str(price_str)
                .replace('$', '')
                .replace(',', '')
                .replace('CAD', '')
                .replace('USD', '')
                .replace('INR', '')
                .replace('₹', '')
                .replace('€', '')
                .replace('£', '')
                .strip()
            )
            try:
                return float(cleaned)
            except Exception:
                return 0

        def generate_random_sku(name):
            base = ''.join(e for e in (name or "NONAME") if e.isalnum()).upper()[:8]
            rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            return f"{base}-{rand}"
        
        def save_product_error(sitemap, product_data, error_message, user=None):
            try:
                ProductWithErrors.objects.create(
                    user=user or sitemap.user,
                    sitemap=sitemap,
                    product_url=product_data.get('product_url', ''),
                    errors=error_message
                )
                print(f"Saved error for product: {product_data.get('name', 'Unknown')} - {error_message}")
            except Exception as e:
                print(f"Failed to save product error: {e}")

        def save_single_product_with_variations(main_product, variations):
            nonlocal saved_count, updated_count, total_products_scraped
            try:
                if not main_product.get('sku') or main_product.get('sku', '').strip().upper() == 'N/A':
                    generated_sku = generate_random_sku(main_product.get('name', ''))
                    main_product['sku'] = f"Config{generated_sku}"

                for v in variations:
                    if not v.get('sku') or v.get('sku', '').strip().upper() == 'N/A':
                        generated_sku = generate_random_sku(v.get('name', ''))
                        v['sku'] = f"Simple{generated_sku}"

                # Collect all unique variation labels and texts
                all_labels = []
                all_texts = []
                for v in variations:
                    vdata = v.get('variation_data')
                    if isinstance(vdata, list):
                        for item in vdata:
                            for label, value in item.items():
                                if label not in all_labels:
                                    all_labels.append(label)
                                if value not in all_texts:
                                    all_texts.append(value)

                # Build configurable_variation_labels and configurable_variations
                configurable_variation_labels = '|'.join(
                    [label.lower().replace(" ", "_").strip("_") for label in all_labels]
                )
                configurable_variations = []
                for v in variations:
                    parts = []
                    if v.get('sku') and v.get('sku', '').strip().upper() != 'N/A':
                        parts.append(f"sku={v['sku']}")
                    vdata = v.get('variation_data')
                    if isinstance(vdata, list):
                        for item in vdata:
                            for label, value in item.items():
                                value = value.lstrip(':').strip()
                                label = label.strip()
                                parts.append(f"{label}={value}")
                    configurable_variations.append(','.join(parts))
                configurable_variations_str = '|'.join(configurable_variations)

                # Save main product as configurable if variations exist
                if variations:
                    main_sku = main_product.get('sku')
                    configurable_sku = f"RFS{main_sku}" if main_sku else None
                    try:
                        obj, created = Product.objects.update_or_create(
                            sku=configurable_sku,
                            sitemap=sitemap,
                            defaults={
                                'user': sitemap.user,
                                'name': main_product.get('name', ''),
                                'product_price': clean_price(main_product.get('product_price', 0)),
                                'product_description': main_product.get('product_description', ''),
                                'base_product_image': main_product.get('base_image', ''),
                                'small_image': main_product.get('small_image', ''),
                                'thumbnail_image': main_product.get('thumbnail_image', ''),
                                'additional_images': main_product.get('additional_images', ''),
                                'product_url': main_product.get('product_url', ''),
                                'product_type': 'configurable',
                                'variation_data': '',  # always empty for configurable
                                'configurable_variation_labels': configurable_variation_labels,  # filled
                                'configurable_variations': configurable_variations_str,         # filled
                                'linenplus_sku': main_product.get('linenplus_sku', main_product.get('sku', '')),
                                'linenplus_price': clean_price(main_product.get('linenplus_price', None)),
                                'flag': main_product.get('flag', '-'),
                                'brand': main_product.get('brand', ''),
                                'store_view_code': main_product.get('store_view_code', ''),
                                'attribute_set_code': main_product.get('attribute_set_code', ''),
                                'categories': main_product.get('categories', ''),
                                'manufacturer_no': main_product.get('manufacturer_no', ''),
                                'visibility': main_product.get('visibility', ''),
                                'stock': main_product.get('stock', ''),
                                'product_websites': main_product.get('product_websites', ''),
                                'msrp_display_actual_price_type': main_product.get('msrp_display_actual_price_type', ''),
                                'uom': main_product.get('uom', 'Each'),
                                'cost': main_product.get('cost', ''),
                                'vendor_cost': main_product.get('vendor_cost', ''),
                                'taxes_id': main_product.get('taxes_id', ''),
                                'account_number': main_product.get('account_number', ''),
                                'delivery_text': main_product.get('delivery_text', ''),
                                'property_account_income_id': main_product.get('property_account_income_id', ''),
                                'property_account_expense_id': main_product.get('property_account_expense_id', ''),
                                'meta_title': main_product.get('meta_title', ''),
                                'meta_keywords': main_product.get('meta_keywords', ''),
                                'meta_description': main_product.get('meta_description', ''),
                                'type_erp': main_product.get('type_erp', ''),
                            }
                        )
                        if created:
                            saved_count += 1
                        else:
                            updated_count += 1
                        
                        total_products_scraped += 1
                        
                        # Send real-time update after saving main product
                        send_websocket_update(
                            sitemap.id, 
                            saved=saved_count,
                            updated=updated_count,
                            total=total_products_scraped
                        )
                    except Exception as e:
                        error_msg = f"Failed to save configurable product: {str(e)}"
                        print(error_msg)
                        save_product_error(sitemap, main_product, error_msg)

                # Save each variation as simple
                for v in variations:
                    try:
                        v_obj, v_created = Product.objects.update_or_create(
                            sku=v.get('sku'),
                            sitemap=sitemap,
                            defaults={
                                'user': sitemap.user,
                                'name': v.get('name', ''),
                                'product_price': clean_price(v.get('product_price', 0)),
                                'product_description': v.get('product_description', ''),
                                'base_product_image': v.get('base_image', ''),
                                'small_image': v.get('small_image', ''),
                                'thumbnail_image': v.get('thumbnail_image', ''),
                                'additional_images': v.get('additional_images', ''),
                                'product_url': v.get('product_url', ''),
                                'product_type': 'simple',
                                'variation_data': json.dumps(v.get('variation_data', '')),  # filled
                                'configurable_variation_labels': '',  # always empty for simple
                                'configurable_variations': '',        # always empty for simple
                                'linenplus_sku': v.get('linenplus_sku', v.get('sku', '')),
                                'linenplus_price': clean_price(v.get('linenplus_price', None)),
                                'flag': v.get('flag', '-'),
                                'brand': v.get('brand', ''),
                                'store_view_code': v.get('store_view_code', ''),
                                'attribute_set_code': v.get('attribute_set_code', ''),
                                'categories': v.get('categories', ''),
                                'manufacturer_no': v.get('manufacturer_no', ''),
                                'visibility': v.get('visibility', ''),
                                'stock': v.get('stock', ''),
                                'product_websites': v.get('product_websites', ''),
                                'msrp_display_actual_price_type': v.get('msrp_display_actual_price_type', ''),
                                'uom': v.get('uom', 'Each'),
                                'cost': v.get('cost', ''),
                                'vendor_cost': v.get('vendor_cost', ''),
                                'taxes_id': v.get('taxes_id', ''),
                                'account_number': v.get('account_number', ''),
                                'delivery_text': v.get('delivery_text', ''),
                                'property_account_income_id': v.get('property_account_income_id', ''),
                                'property_account_expense_id': v.get('property_account_expense_id', ''),
                                'meta_title': v.get('meta_title', ''),
                                'meta_keywords': v.get('meta_keywords', ''),
                                'meta_description': v.get('meta_description', ''),
                                'type_erp': v.get('type_erp', ''),
                            }
                        )
                        if v_created:
                            saved_count += 1
                        else:
                            updated_count += 1
                        
                        total_products_scraped += 1
                        
                        # Send real-time update after each variation
                        send_websocket_update(
                            sitemap.id, 
                            saved=saved_count,
                            updated=updated_count,
                            total=total_products_scraped
                        )
                    except Exception as e:
                        error_msg = f"Failed to save variation product: {str(e)}"
                        print(error_msg)
                        save_product_error(sitemap, v, error_msg)
                else:
                    try:
                        obj, created = Product.objects.update_or_create(
                            sku=main_product.get('sku'),
                            sitemap=sitemap,
                            defaults={
                                'user': sitemap.user,
                                'name': main_product.get('name', ''),
                                'product_price': clean_price(main_product.get('product_price', 0)),
                                'product_description': main_product.get('product_description', ''),
                                'base_product_image': main_product.get('base_image', ''),
                                'small_image': main_product.get('small_image', ''),
                                'thumbnail_image': main_product.get('thumbnail_image', ''),
                                'additional_images': main_product.get('additional_images', ''),
                                'product_url': main_product.get('product_url', ''),
                                'product_type': 'simple',
                                'variation_data': '',
                                'configurable_variation_labels': '',
                                'configurable_variations': '',
                                'linenplus_sku': main_product.get('linenplus_sku', main_product.get('sku', '')),
                                'linenplus_price': clean_price(main_product.get('linenplus_price', None)),
                                'flag': main_product.get('flag', '-'),
                                'brand': main_product.get('brand', ''),
                                'store_view_code': main_product.get('store_view_code', ''),
                                'attribute_set_code': main_product.get('attribute_set_code', ''),
                                'categories': main_product.get('categories', ''),
                                'manufacturer_no': main_product.get('manufacturer_no', ''),
                                'visibility': main_product.get('visibility', ''),
                                'stock': main_product.get('stock', ''),
                                'product_websites': main_product.get('product_websites', ''),
                                'msrp_display_actual_price_type': main_product.get('msrp_display_actual_price_type', ''),
                                'uom': main_product.get('uom', 'Each'),
                                'cost': main_product.get('cost', ''),
                                'vendor_cost': main_product.get('vendor_cost', ''),
                                'taxes_id': main_product.get('taxes_id', ''),
                                'account_number': main_product.get('account_number', ''),
                                'delivery_text': main_product.get('delivery_text', ''),
                                'property_account_income_id': main_product.get('property_account_income_id', ''),
                                'property_account_expense_id': main_product.get('property_account_expense_id', ''),
                                'meta_title': main_product.get('meta_title', ''),
                                'meta_keywords': main_product.get('meta_keywords', ''),
                                'meta_description': main_product.get('meta_description', ''),
                                'type_erp': main_product.get('type_erp', ''),
                            }
                        )
                        if created:
                            saved_count += 1
                        else:
                            updated_count += 1
                        
                        total_products_scraped += 1
                        
                        # Send real-time update after saving simple product
                        send_websocket_update(
                            sitemap.id, 
                            saved=saved_count,
                            updated=updated_count,
                            total=total_products_scraped
                        )

                    except Exception as e:
                        error_msg = f"Failed to save simple product: {str(e)}"
                        print(error_msg)
                        save_product_error(sitemap, main_product, error_msg)

            except Exception as e:
                error_msg = f"General error in save_single_product_with_variations: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                save_product_error(sitemap, main_product, error_msg)


        # Use the modified scraper that processes one product at a time
        results = run_dynamic_scraper(sitemap_json, save_single_product_with_variations)
        
        # Handle any orphan variations that weren't processed
        orphan_variations = [r for r in results if r.get('is_variation') and not any(m.get('product_url') == r.get('parent_url') for m in results if not m.get('is_variation'))]
        
        for v in orphan_variations:
            try:
                if not v.get('sku'):
                    v['sku'] = generate_random_sku(v.get('name', ''))
                # Ensure variation_data is a JSON string
                v_variation_data = v.get('variation_data', [])
                if isinstance(v_variation_data, list):
                    v_variation_data = json.dumps(v_variation_data)
                elif not v_variation_data:
                    v_variation_data = ''
                
                v_obj, v_created = Product.objects.update_or_create(
                    sku=v.get('sku'),
                    sitemap=sitemap,
                    defaults={
                        'user': sitemap.user,
                        'name': v.get('name', ''),
                        'product_price': clean_price(v.get('product_price', 0)),
                        'product_description': v.get('product_description', ''),
                        'base_product_image': v.get('base_image', ''),
                        'small_image': v.get('small_image', ''),
                        'thumbnail_image': v.get('thumbnail_image', ''),
                        'additional_images': v.get('additional_images', ''),
                        'product_url': v.get('product_url', ''),
                        'product_type': 'simple',
                        'variation_data': v_variation_data,
                        'linenplus_sku': v.get('linenplus_sku', v.get('sku', '')),
                        'linenplus_price': clean_price(v.get('linenplus_price', None)),
                        'flag': v.get('flag', '-'),
                        'brand': v.get('brand', ''),
                        'store_view_code': v.get('store_view_code', ''),
                        'attribute_set_code': v.get('attribute_set_code', ''),
                        'categories': v.get('categories', ''),
                        'manufacturer_no': v.get('manufacturer_no', ''),
                        'visibility': v.get('visibility', ''),
                        'stock': v.get('stock', ''),
                        'product_websites': v.get('product_websites', ''),
                        'msrp_display_actual_price_type': v.get('msrp_display_actual_price_type', ''),
                        'uom': v.get('uom', 'Each'),
                        'cost': v.get('cost', ''),
                        'vendor_cost': v.get('vendor_cost', ''),
                        'taxes_id': v.get('taxes_id', ''),
                        'account_number': v.get('account_number', ''),
                        'delivery_text': v.get('delivery_text', ''),
                        'property_account_income_id': v.get('property_account_income_id', ''),
                        'property_account_expense_id': v.get('property_account_expense_id', ''),
                        'meta_title': v.get('meta_title', ''),
                        'meta_keywords': v.get('meta_keywords', ''),
                        'meta_description': v.get('meta_description', ''),
                        'type_erp': v.get('type_erp', ''),
                    }
                )
                if v_created:
                    saved_count += 1
                else:
                    updated_count += 1
                
                total_products_scraped += 1
                
                # Send real-time update for orphan variations
                send_websocket_update(
                    sitemap.id, 
                    saved=saved_count,
                    updated=updated_count,
                    total=total_products_scraped
                )
            except Exception as e:
                error_msg = f"Failed to save orphan variation: {str(e)}"
                print(error_msg)
                save_product_error(sitemap, v, error_msg)

        # Final websocket update and completion signal
        send_websocket_update(
            sitemap.id, 
            saved=saved_count,
            updated=updated_count,
            total=total_products_scraped
        )
        send_scrape_complete(sitemap.id)

        # Send email notification after scrape complete
        send_email_notification.delay(sitemap.id, saved_count, updated_count)

        return {'success': True, 'saved_count': saved_count, 'updated_count': updated_count}
    except Exception as e:
        send_websocket_update(
            sitemap_id, 
            saved=0,
            updated=0,
            total=0
        )
        print(f"Error in scrape_products_task: {e}")
        return {'success': False, 'error': str(e)}

@shared_task
def scrape_all_sitemaps_task():
    sitemaps = Sitemap.objects.all().order_by('id')
    total_saved = 0
    total_updated = 0
    results = []
    print(f"Starting to scrape all {len(sitemaps)} sitemaps")
    
    # Initialize progress for all sitemaps before starting
    for sitemap in sitemaps:
        current_count = Product.objects.filter(sitemap=sitemap).count()
        send_websocket_update(sitemap.id, saved=0, updated=0, total=current_count)
        time.sleep(0.5)  # Small delay to prevent message overlap

    for i, sitemap in enumerate(sitemaps):
        if i > 0:
            print(f"Waiting 90 seconds before processing next sitemap...")
            time.sleep(90)
        
        try:
            print(f"Starting to process sitemap {sitemap.id} ({i+1}/{len(sitemaps)}): {sitemap.url}")
            send_websocket_update(
                sitemap.id, 
                saved=0,
                updated=0,
                total=Product.objects.filter(sitemap=sitemap).count()
            )
            
            result = process_sitemap(sitemap)
            total_saved += result['saved_count']
            total_updated += result['updated_count']
            results.append({
                'sitemap_id': sitemap.id,
                'url': sitemap.url,
                'saved_count': result['saved_count'],
                'updated_count': result['updated_count'],
                'success': True
            })
            
            final_count = Product.objects.filter(sitemap=sitemap).count()
            send_websocket_update(
                sitemap.id, 
                saved=result['saved_count'],
                updated=result['updated_count'],
                total=final_count
            )
                        
            print(f"Finished processing sitemap {sitemap.id}: Saved {result['saved_count']}, Updated {result['updated_count']}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing sitemap {sitemap.id}: {error_msg}")
            results.append({
                'sitemap_id': sitemap.id,
                'url': sitemap.url,
                'error': error_msg,
                'success': False
            })
            
            try:
                send_websocket_update(
                    sitemap.id, 
                    saved=0,
                    updated=0,
                    total=Product.objects.filter(sitemap_id=sitemap.id).count()
                )
            except Exception as ws_error:
                print(f"Failed to send websocket update for sitemap {sitemap.id}: {str(ws_error)}")
    
    print(f"Completed scraping all sitemaps. Total saved: {total_saved}, Total updated: {total_updated}")
    
    # Send a final update to all sitemaps
    for sitemap in sitemaps:
        current_count = Product.objects.filter(sitemap=sitemap).count()
        send_websocket_update(sitemap.id, saved=0, updated=0, total=current_count)
        time.sleep(0.5)  # Small delay to prevent message overlap

    # --- Send summary email ---
    try:
        # Get the first user from any sitemap for email notification
        first_sitemap_with_user = None
        for sitemap in sitemaps:
            if sitemap.user_id:
                first_sitemap_with_user = sitemap
                break
        
        if first_sitemap_with_user:
            user = User.objects.get(id=first_sitemap_with_user.user_id)
            subject = "Scrape All Sitemaps Complete"
            message = (
                f"All sitemaps scraped.\n"
                f"Total new: {total_saved}\n"
                f"Total updated: {total_updated}\n"
                f"Sitemaps: {[s.id for s in sitemaps]}"
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print("Summary email sent for all sitemaps.")
        else:
            print("No user found for email notification")
    except Exception as e:
        print(f"Error sending summary email: {e}")

    # --- Send scrape_complete events to all sitemap WebSocket groups ---
    channel_layer = get_channel_layer()
    
    # Send completion event to all individual sitemap groups
    for sitemap in sitemaps:
        async_to_sync(channel_layer.group_send)(
            f"scrape_count_{sitemap.id}",
            {
                'type': 'scrape_complete',
                'sitemap_id': 'all',  # Special identifier for scrape all completion
                'timestamp': time.time()
            }
        )
    
    # Also send to the general scrape_count_all group if needed
    async_to_sync(channel_layer.group_send)(
        "scrape_count_all",
        {
            'type': 'scrape_complete',
            'sitemap_id': 'all',
            'timestamp': time.time()
        }
    )

    return {
        'success': True,
        'total_sitemaps_processed': len(sitemaps),
        'total_saved': total_saved,
        'total_updated': total_updated,
        'results': results
    }

@shared_task
def scrape_selected_sitemaps_task(selected_ids):
    results = {
        'successful': [],
        'failed': []
    }
    total_saved = 0
    total_updated = 0
    user_email = None

    for index, sitemap_id in enumerate(selected_ids):
        try:
            if index > 0:
                print(f"Waiting 90 seconds before processing next sitemap...")
                time.sleep(90)
            sitemap = get_object_or_404(Sitemap, id=sitemap_id)
            # Save user email for summary email
            if not user_email and sitemap.user_id:
                user = User.objects.get(id=sitemap.user_id)
                user_email = user.email

            # Send notification that processing has started
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"scrape_count_{sitemap_id}",
                {
                    'type': 'send_processing_status',
                    'status': {
                        'message': f'Processing sitemap {sitemap_id}',
                        'timestamp': time.time()
                    }
                }
            )
            
            scrape_results = process_sitemap(sitemap)
            saved_count = scrape_results['saved_count']
            updated_count = scrape_results['updated_count']
            total_saved += saved_count
            total_updated += updated_count
            
            final_count = Product.objects.filter(sitemap=sitemap).count()
            send_websocket_update(
                sitemap.id, 
                saved=saved_count,
                updated=updated_count,
                total=final_count
            )
            
            results['successful'].append({
                'sitemap_id': sitemap_id,
                'saved_count': saved_count,
                'updated_count': updated_count
            })
        except Exception as e:
            results['failed'].append({
                'sitemap_id': sitemap_id,
                'error': str(e)
            })
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"scrape_count_{sitemap_id}",
                    {
                        'type': 'send_error_message',
                        'error': {
                            'message': f'Error processing sitemap {sitemap_id}: {str(e)}',
                            'timestamp': time.time()
                        }
                    }
                )
            except:
                pass  # Ignore websocket errors
        finally:
            # Always send scrape_complete, even on error
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"scrape_count_{sitemap_id}",
                {
                    'type': 'scrape_complete',
                    'sitemap_id': sitemap_id,
                    'timestamp': time.time()
                }
            )

    # Send summary email after all selected sitemaps are scraped
    if user_email:
        try:
            subject = "Scrape Selected Sitemaps Complete"
            message = (
                f"Selected sitemaps scraped.\n"
                f"Total new: {total_saved}\n"
                f"Total updated: {total_updated}\n"
                f"Sitemaps: {selected_ids}\n"
                f"Successful: {len(results['successful'])}, Failed: {len(results['failed'])}"
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user_email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            print("Summary email sent for selected sitemaps.")
        except Exception as e:
            print(f"Error sending summary email: {e}")

    return results

@shared_task
def send_email_notification(sitemap_id, saved_count, updated_count):
    try:
        sitemap = Sitemap.objects.get(id=sitemap_id)
        user = User.objects.get(id=sitemap.user_id) if sitemap.user_id else None  # Fetch the user
        if not user:
            print(f"No user found for sitemap {sitemap_id}")
            return False

        total_count = Product.objects.filter(sitemap=sitemap).count()
        total_processed = saved_count + updated_count
        
        subject = "Scrapped Products Information"
        message = f"""
            Sitemap URL: {sitemap.url}
            Total Products in Database: {total_count}
            Products Processed in This Run: {total_processed}
            New Products Added: {saved_count}
            Existing Products Updated: {updated_count}
        """
        
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]  # Send to the registered user's email

        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        send_scrape_complete(sitemap_id)
        print(f"Email notification sent successfully for sitemap {sitemap_id}")
        return True
    except Exception as e:
        print(f"Error sending email notification for sitemap {sitemap_id}: {e}")
        return False

def process_sitemap(sitemap):
    return scrape_products_task.__wrapped__(sitemap.id)