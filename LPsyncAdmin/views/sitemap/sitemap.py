from django.shortcuts import render, redirect
from LPsyncAdmin.models import Sitemap, Product, User, Project
from django.contrib import messages
import requests
import json
from django.shortcuts import get_object_or_404

def sitemap(request, pk):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        project = get_object_or_404(Project, id=pk, user=current_user)
        # Show only sitemaps for this project:
        sitemaps = Sitemap.objects.filter(project=project)
        return render(request, 'sitemap/site_map.html', {
            'sitemaps': sitemaps,
            'user': current_user,
            'project': project,
        })
    else:
        return redirect('login')

def run_external_script(request, id):
    # Define the variable `product`
    product = Product.objects.all()

    # Retrieve the necessary data from the database
    products = product.filter(sitemap_id=id)
    product_count = len(products)

    for product in products:
        sku = product.sku
        title = product.name
        price = str(product.product_price)  # Convert Decimal to string

        url = "/rest/default/V1/products"
        payload = json.dumps({
            "product": {
                "sku": sku,
                "name": title,
                "attribute_set_id": 4,
                "price": price,
                "status": 1,
                "visibility": 1,
                "type_id": "simple",
                "weight": "1"
            }
        })

        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJraWQiOiIxIiwiYWxnIjoiSFMyNTYifQ.eyJ1aWQiOjEsInV0eXBpZCI6MiwiaWF0IjoxNjg5MDgyNDAzLCJleHAiOjE2ODkwODYwMDN9.iyo1LoWviiZ4wMwPOMZhrnIDvfMSulmD7VZWJtMigcY'
        }

        response = requests.post(url, headers=headers, data=payload)
        # print(response.json())

    messages.success(request, f"{product_count} product(s) created successfully!")
    return redirect('/sitemap/')  # Assuming 'sitemap' is the URL name for the sitemap view
