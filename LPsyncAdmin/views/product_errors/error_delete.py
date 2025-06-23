from django.shortcuts import render, redirect
from LPsyncAdmin.models import ProductWithErrors, User

def delete_error(request, id):
    error = ProductWithErrors.objects.get(id=id)
    user_pk = error.user.pk
    error.delete()
    return redirect('product_errors', pk=user_pk)