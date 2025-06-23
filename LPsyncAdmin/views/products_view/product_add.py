from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from LPsyncAdmin.models import Sitemap, Product, User

def addproduct(request, pk):
    # Get the user object
    user = get_object_or_404(User, pk=pk)
    sitemaps = Sitemap.objects.all()
    
    if request.method == 'POST':
        try:
            sitemap_id = request.POST.get('sitemap_name')
            
            # Validate sitemap_id
            if not sitemap_id:
                messages.error(request, 'Please select a sitemap.')
                return render(request, 'products/addproduct.html', {
                    'sitemaps': sitemaps,
                    'user': user
                })
            
            sitemap = get_object_or_404(Sitemap, pk=sitemap_id)
            
            # Create the product
            product = Product.objects.create(
                sitemap=sitemap, 
                user=user,
                sku=request.POST.get('sku', ''),
                store_view_code=request.POST.get('store_view_code', ''),
                attribute_set_code=request.POST.get('attribute_set_code', ''),
                categories=request.POST.get('categories', ''),
                manufacturer_no=request.POST.get('manufacturer_no', ''),
                name=request.POST.get('name', ''),
                product_price=request.POST.get('product_price', ''),
                brand=request.POST.get('brand', ''),
                visibility=request.POST.get('visibility', ''),
                product_type=request.POST.get('product_type', ''),
                also_available=request.POST.get('also_available', ''),
                configurable_variation_labels=request.POST.get('configurable_variation_labels', ''),
                configurable_variations=request.POST.get('configurable_variations', ''),
                product_description=request.POST.get('product_description', ''),
                stock=request.POST.get('stock', ''),
                product_websites=request.POST.get('product_websites', ''),
                msrp_display_actual_price_type=request.POST.get('msrp_display_actual_price_type', ''),
                uom=request.POST.get('uom', ''),
                cost=request.POST.get('cost', ''),
                vendor_cost=request.POST.get('vendor_cost', ''),
                taxes_id=request.POST.get('taxes_id', ''),
                account_number=request.POST.get('account_number', ''),
                delivery_text=request.POST.get('delivery_text', ''),
                property_account_income_id=request.POST.get('property_account_income_id', ''),
                property_account_expense_id=request.POST.get('property_account_expense_id', ''),
                meta_title=request.POST.get('meta_title', ''),
                meta_keywords=request.POST.get('meta_keywords', ''),
                meta_description=request.POST.get('meta_description', ''),
                type_erp=request.POST.get('type_erp', ''),
                base_product_image=request.POST.get('base_product_image', ''),
                base_image_label=request.POST.get('base_image_label', ''),
                small_image=request.POST.get('small_image', ''),
                small_image_label=request.POST.get('small_image_label', ''),
                thumbnail_image=request.POST.get('thumbnail_image', ''),
                thumbnail_image_label=request.POST.get('thumbnail_image_label', ''),
                additional_images=request.POST.get('additional_images', ''),
                additional_images_label=request.POST.get('additional_images_label', ''),
                product_url=request.POST.get('product_url', '')
            )
            
            messages.success(request, 'Product added successfully!')
            return redirect(reverse('products-view', kwargs={'pk': pk}))
            
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
            return render(request, 'products/addproduct.html', {
                'sitemaps': sitemaps,
                'user': user
            })
    
    # GET request - show the form
    return render(request, 'products/addproduct.html', {
        'sitemaps': sitemaps,
        'user': user
    })