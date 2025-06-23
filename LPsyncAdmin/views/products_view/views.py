from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from LPsyncAdmin.models import Product, User, Sitemap, Project
from LPsyncAdmin.views.sitemap.sitemap import run_external_script


def products_view(request, pk):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        try:
            project = Project.objects.get(pk=pk, user=current_user)
        except Project.DoesNotExist:
            return redirect('401_forbidden')
        products = Product.objects.filter(user=current_user, sitemap__project=project)
        return render(request, "products/products-view.html", {'products': products, 'user': current_user, 'project': project})
    else:
        messages.error(request, "You need to be logged in to view products.")
        return redirect('login')
    
def sync(request, id):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        product = Product.objects.get(pk=id, user=current_user)
        if product:
            run_external_script(request, product.sitemap_id)
            messages.success(request, "Product synced successfully.")
            return redirect('products_view', pk=current_user.pk)
        else:
            messages.error(request, "Product not found.")
            return redirect('products_view', pk=current_user.pk)
    else:
        messages.error(request, "You need to be logged in to sync products.")
        return redirect('login')
