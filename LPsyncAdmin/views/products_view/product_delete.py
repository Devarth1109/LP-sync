from django.shortcuts import render, redirect
from django.urls import reverse
from LPsyncAdmin.models import Product
from django.shortcuts import get_object_or_404

def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    project_id = product.sitemap.project.id  # Get the project id before deleting
    product.delete()
    return redirect('products-view', pk=project_id)