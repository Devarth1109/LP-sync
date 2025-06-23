from django.shortcuts import render, redirect
from LPsyncAdmin.models import ProductWithErrors, User

def errors_view(request, pk):
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])
        if user.pk != pk:
            return redirect('401_forbidden')

        products_with_errors = ProductWithErrors.objects.filter(user=user)
        return render(request, "producterrors/product_errors.html", {
            'products_with_errors': products_with_errors,
            'user': user
        })
    else:
        return redirect('login')