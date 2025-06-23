from django.shortcuts import render, redirect
from LPsyncAdmin.models import ProductWithErrors, User

def deleteall_errors(request):
    user = User.objects.get(email=request.session['email'])
    ProductWithErrors.objects.filter(user=user).delete()
    return redirect('product_errors', pk=user.pk)