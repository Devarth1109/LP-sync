from django.shortcuts import render, redirect
from LPsyncAdmin.models import Product, User, Project
from django.urls import reverse

def deleteall_product(request, pk):
    user = User.objects.get(email=request.session['email'])
    project = Project.objects.get(pk=pk, user=user)
    # Delete only products for this user and project
    Product.objects.filter(user=user, sitemap__project=project).delete()
    return redirect(reverse('products-view', kwargs={'pk': pk}))