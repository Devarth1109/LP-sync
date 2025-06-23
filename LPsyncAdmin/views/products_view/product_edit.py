from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from LPsyncAdmin.models import Product, Sitemap, User

def editproduct(request, id):
    user = get_object_or_404(User, email=request.session.get('email'))
    product = get_object_or_404(Product, id=id)
    sitemaps = Sitemap.objects.all()
    
    # Get the current sitemap ID
    current_sitemap = product.sitemap.id if product.sitemap else None
    
    if request.method == 'POST':
        try:
            # Get the sitemap object based on the selected sitemap_name
            sitemap_id = request.POST.get('sitemap_name')
            selected_sitemap = None
            if sitemap_id:
                try:
                    selected_sitemap = Sitemap.objects.get(id=sitemap_id)
                except Sitemap.DoesNotExist:
                    messages.error(request, 'Selected sitemap does not exist.')
                    return render(request, "products/edit-product.html", {
                        'product': product, 
                        'sitemaps': sitemaps,
                        'current_sitemap': current_sitemap
                    })
            
            # Update product fields (removed trailing commas)
            product.sku = request.POST.get('sku')
            product.store_view_code = request.POST.get('store_view_code')
            product.attribute_set_code = request.POST.get('attribute_set_code')
            product.categories = request.POST.get('categories')
            product.manufacturer_no = request.POST.get('manufacturer_no')
            product.name = request.POST.get('name')
            product.product_price = request.POST.get('product_price')
            product.brand = request.POST.get('brand')
            product.visibility = request.POST.get('visibility')  # Fixed typo: POSt -> POST
            product.product_type = request.POST.get('product_type')
            product.also_available = request.POST.get('also_available')
            product.configurable_variation_labels = request.POST.get('configurable_variation_labels')
            product.configurable_variations = request.POST.get('configurable_variations')
            product.product_description = request.POST.get('product_description')
            product.stock = request.POST.get('stock')
            product.product_websites = request.POST.get('product_websites')
            product.msrp_display_actual_price_type = request.POST.get('msrp_display_actual_price_type')
            product.uom = request.POST.get('uom')
            product.cost = request.POST.get('cost')
            product.vendor_cost = request.POST.get('vendor_cost')
            product.taxes_id = request.POST.get('taxes_id')
            product.account_number = request.POST.get('account_number')
            product.delivery_text = request.POST.get('delivery_text')
            product.property_account_income_id = request.POST.get('property_account_income_id')
            product.property_account_expense_id = request.POST.get('property_account_expense_id')
            product.meta_title = request.POST.get('meta_title')
            product.meta_keywords = request.POST.get('meta_keywords')
            product.meta_description = request.POST.get('meta_description')
            product.type_erp = request.POST.get('type_erp')
            product.base_product_image = request.POST.get('base_product_image')
            product.base_image_label = request.POST.get('base_image_label')
            product.small_image = request.POST.get('small_image')
            product.small_image_label = request.POST.get('small_image_label')
            product.thumbnail_image = request.POST.get('thumbnail_image')
            product.thumbnail_image_label = request.POST.get('thumbnail_image_label')
            product.additional_images = request.POST.get('additional_images')
            product.additional_images_label = request.POST.get('additional_images_label')
            product.product_url = request.POST.get('product_url')
            
            # Set the sitemap 
            product.sitemap = selected_sitemap
            
            product.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products-view', pk=product.sitemap.project.id)  # Added pk parameter
            
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
            return render(request, "products/edit-product.html", {
                'product': product, 
                'sitemaps': sitemaps,
                'current_sitemap': current_sitemap
            })
    
    return render(request, "products/edit-product.html", {
        'product': product, 
        'sitemaps': sitemaps,
        'current_sitemap': current_sitemap,
        'user': user  # Added user to context
    })