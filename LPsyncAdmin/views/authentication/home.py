from django.shortcuts import render,redirect
# from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.models import User

from LPsyncAdmin.models import Project
from LPsyncAdmin.models import Product
from LPsyncAdmin.models import Sitemap


# @login_required
def home(request):
    # user_count = User.objects.count()
    project_count = Project.objects.count()
    product_count = Product.objects.count()
    sitemap_count = Sitemap.objects.count()

    context = {
    # 'user_count' : user_count,
    'project_count' : project_count,
    'product_count' : product_count,
    'sitemap_count' : sitemap_count,
    }
    return render(request,'base.html',context)