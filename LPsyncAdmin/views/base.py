from django.shortcuts import render, redirect
from LPsyncAdmin.models import Project
from LPsyncAdmin.models import Product
from LPsyncAdmin.models import Sitemap
from LPsyncAdmin.models.usermodel import User

def BASE(request):
    user = None
    if 'email' in request.session:
        try:
            user = User.objects.get(email=request.session['email'])
        except User.DoesNotExist:
            return redirect('login')
    else:
        return redirect('login')

    # Filter by user
    project_count = Project.objects.filter(user=user).count()
    product_count = Product.objects.filter(user=user).count()
    sitemap_count = Sitemap.objects.filter(user=user).count()
    user_count = User.objects.all().count()
    return render(request, 'base.html', {
        'user': user,
        'project_count': project_count,
        'product_count': product_count,
        'sitemap_count': sitemap_count,
        'user_count': user_count
    })