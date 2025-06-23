# # get_linenplus.py
# from django.shortcuts import redirect
# from django.contrib import messages
# from LPsyncAdmin.models import Product, User
# import requests

# def get_linenplus_products(request, pk):
#     if 'email' not in request.session:
#         messages.error(request, "You need to be logged in.")
#         return redirect('login')
#     current_user = User.objects.get(pk=pk)
#     print(f"Fetching LinenPlus products for user: {current_user.email}")

#     # --- Fetch LinenPlus products and save to Product model ---
#     auth_url = "https://stage1.linenplus.ca/rest/V1/integration/admin/token"
#     auth_payload = {
#         "username": "wcmanali",
#         "password": "Web@#123!"
#     }
#     print("Requesting LinenPlus API token...")
#     auth_response = requests.post(auth_url, json=auth_payload)
#     if auth_response.status_code != 200:
#         print(f"Failed to fetch LinenPlus token. Status: {auth_response.status_code}")
#         messages.error(request, "Failed to fetch LinenPlus token.")
#         return redirect('products-view', pk=pk)
#     token = auth_response.json()
#     print("Successfully fetched LinenPlus token.")

#     base_url = "https://stage1.linenplus.ca/rest/V1/products"
#     headers = {
#         'Authorization': f'Bearer {token}',
#     }
#     page = 1
#     page_size = 50
#     linenplus_skus = set()
#     linenplus_data = {}
#     total_fetched = 0
#     while True:
#         params = {
#             'searchCriteria[filter_groups][0][filters][0][field]': 'account_number',
#             'searchCriteria[filter_groups][0][filters][0][value]': '127448',
#             'searchCriteria[filter_groups][0][filters][0][condition_type]': 'eq',
#             'searchCriteria[currentPage]': page,
#             'searchCriteria[pageSize]': page_size,
#             'fields': 'items[sku,name,price],total_count'
#         }
#         print(f"Fetching LinenPlus products page {page}...")
#         response = requests.get(base_url, headers=headers, params=params)
#         if response.status_code != 200:
#             print(f"Failed to fetch products at page {page}. Status: {response.status_code}")
#             break
#         data = response.json()
#         items = data.get('items', [])
#         if not items:
#             print("No more products found from LinenPlus API.")
#             break
#         for item in items:
#             sku = item.get('sku', '')
#             name = item.get('name', '')
#             price = item.get('price', 0)
#             linenplus_skus.add(sku)
#             linenplus_data[sku] = {'name': name, 'price': price}
#         total_fetched += len(items)
#         print(f"Fetched {len(items)} products from page {page}. Total fetched: {total_fetched}")
#         # For testing, only fetch first 100 products
#         break

#     print(f"Total LinenPlus SKUs fetched: {len(linenplus_skus)}")

#     # --- Merge and flag logic ---
#     all_products = Product.objects.filter(user=current_user)
#     user_skus = set(all_products.values_list('sku', flat=True))
#     print(f"User SKUs: {user_skus}")

#     # 1. Update or create products based on LinenPlus data
#     for sku in linenplus_skus:
#         # If product with this SKU exists, update it and set flag to 'update'
#         product = Product.objects.filter(sku=sku, user=current_user).first()
#         if product:
#             product.linenplus_sku = sku
#             product.linenplus_price = linenplus_data[sku]['price']
#             product.name = linenplus_data[sku]['name']
#             product.flag = 'update'
#             product.save()
#             print(f"Product {sku} set to 'update' (merged LinenPlus data into existing row)")
#         else:
#             # If not, create a new row with flag 'delete'
#             Product.objects.update_or_create(
#                 linenplus_sku=sku,
#                 user=current_user,
#                 defaults={
#                     'name': linenplus_data[sku]['name'],
#                     'linenplus_sku': sku,
#                     'linenplus_price': linenplus_data[sku]['price'],
#                     'flag': 'delete',
#                     'product_type': 'simple',
#                     'product_price': 0,
#                 }
#             )
#             print(f"Product {sku} set to 'delete' (exists in LinenPlus but not in user products)")

#     # 2. Set flag to 'new' for products that do not exist in LinenPlus
#     for product in all_products:
#         if product.sku and product.sku not in linenplus_skus:
#             product.flag = 'new'
#             product.save()
#             print(f"Product {product.sku} set to 'new' (exists in user products but not in LinenPlus)")

#     print("LinenPlus products fetched and flags updated.")
#     messages.success(request, "LinenPlus products fetched and flags updated.")
#     return redirect('products-view', pk=pk)

from django.shortcuts import redirect
from django.contrib import messages
from LPsyncAdmin.tasks import fetch_linenplus_products

def get_linenplus_products(request, pk):
    if 'email' not in request.session:
        messages.error(request, "You need to be logged in.")
        return redirect('login')
    fetch_linenplus_products.delay(pk)
    messages.success(request, "LinenPlus product sync started in background. Please refresh after some time.")
    return redirect('products-view', pk=pk) 

    # current_user = User.objects.get(pk=pk)
    # print(f"Fetching LinenPlus products for user: {current_user.email}")

    # # --- Fetch LinenPlus products and save to Product model ---
    # auth_url = "https://stage1.linenplus.ca/rest/V1/integration/admin/token"
    # auth_payload = {
    #     "username": "wcmanali",
    #     "password": "Web@#123!"
    # }
    # print("Requesting LinenPlus API token...")
    # auth_response = requests.post(auth_url, json=auth_payload)
    # if auth_response.status_code != 200:
    #     print(f"Failed to fetch LinenPlus token. Status: {auth_response.status_code}")
    #     messages.error(request, "Failed to fetch LinenPlus token.")
    #     return redirect('products-view', pk=pk)
    # token = auth_response.json()
    # print("Successfully fetched LinenPlus token.")

    # base_url = "https://stage1.linenplus.ca/rest/V1/products"
    # headers = {
    #     'Authorization': f'Bearer {token}',
    # }
    # page = 1
    # page_size = 100
    # linenplus_skus = set()
    # linenplus_data = {}
    # total_fetched = 0
    
    # while True:
    #     params = {
    #         'searchCriteria[filter_groups][0][filters][0][field]': 'account_number',
    #         'searchCriteria[filter_groups][0][filters][0][value]': '127448',
    #         'searchCriteria[filter_groups][0][filters][0][condition_type]': 'eq',
    #         'searchCriteria[currentPage]': page,
    #         'searchCriteria[pageSize]': page_size,
    #         'fields': 'items[sku,name,price],total_count'
    #     }
    #     print(f"Fetching LinenPlus products page {page}...")
    #     response = requests.get(base_url, headers=headers, params=params)
    #     if response.status_code != 200:
    #         print(f"Failed to fetch products at page {page}. Status: {response.status_code}")
    #         break
    #     data = response.json()
    #     items = data.get('items', [])
    #     total_count = data.get('total_count', 0)
        
    #     if not items:
    #         print("No more products found from LinenPlus API.")
    #         break
            
    #     for item in items:
    #         sku = item.get('sku', '')
    #         name = item.get('name', '')
    #         price = item.get('price', 0)
    #         linenplus_skus.add(sku)
    #         linenplus_data[sku] = {'name': name, 'price': price}
            
    #     total_fetched += len(items)
    #     print(f"Fetched {len(items)} products from page {page}. Total fetched: {total_fetched} / {total_count}")
        
    #     # Check if we've fetched all products
    #     if total_fetched >= total_count or len(items) < page_size:
    #         print(f"All products fetched. Total: {total_fetched}")
    #         break
            
    #     page += 1

    # print(f"Total LinenPlus SKUs fetched: {len(linenplus_skus)}")

    # # --- Merge and flag logic ---
    # all_products = Product.objects.filter(user=current_user)
    # user_skus = set(all_products.values_list('sku', flat=True))
    # print(f"User SKUs: {user_skus}")

    # # 1. Update or create products based on LinenPlus data
    # for sku in linenplus_skus:
    #     # If product with this SKU exists, update it and set flag to 'update'
    #     product = Product.objects.filter(sku=sku, user=current_user).first()
    #     if product:
    #         product.linenplus_sku = sku
    #         product.linenplus_price = linenplus_data[sku]['price']
    #         product.name = linenplus_data[sku]['name']
    #         product.flag = 'update'
    #         product.save()
    #         print(f"Product {sku} set to 'update' (merged LinenPlus data into existing row)")
    #     else:
    #         # If not, create a new row with flag 'delete'
    #         Product.objects.update_or_create(
    #             linenplus_sku=sku,
    #             user=current_user,
    #             defaults={
    #                 'name': linenplus_data[sku]['name'],
    #                 'linenplus_sku': sku,
    #                 'linenplus_price': linenplus_data[sku]['price'],
    #                 'flag': 'delete',
    #                 'product_type': 'simple',
    #                 'product_price': 0,
    #             }
    #         )
    #         print(f"Product {sku} set to 'delete' (exists in LinenPlus but not in user products)")

    # # 2. Set flag to 'new' for products that do not exist in LinenPlus
    # for product in all_products:
    #     if product.sku and product.sku not in linenplus_skus:
    #         product.flag = 'new'
    #         product.save()
    #         print(f"Product {product.sku} set to 'new' (exists in user products but not in LinenPlus)")

    # print("LinenPlus products fetched and flags updated.")
    # messages.success(request, "LinenPlus products fetched and flags updated.")
    # return redirect('products-view', pk=pk)