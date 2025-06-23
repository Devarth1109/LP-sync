from django.shortcuts import render, redirect
from LPsyncAdmin.models import Project, User
from django.db.models import Count

def p_cards(request):
    if 'email' in request.session:
        current_user = User.objects.get(email=request.session['email'])
        projects = Project.objects.filter(user=current_user).annotate(
            product_count=Count('sitemap__product', distinct=True)
        )
        return render(request, 'products/product_card.html', {'projects': projects, 'user': current_user})
    else:
        return redirect('login')