from django.shortcuts import render, redirect
from LPsyncAdmin.models import Project, User

def edit(request, id):
    project = Project.objects.get(id=id)
    user = None
    if 'email' in request.session:
        user = User.objects.get(email=request.session['email'])

    if request.method == 'POST':
        project.project_name = request.POST.get('project_name')
        project.price_margin = request.POST.get('price_margin')
        project.uom = request.POST.get('uom')
        project.account_number = request.POST.get('account_number')
        project.type_erp = request.POST.get('type_erp')
        project.taxes_id = request.POST.get('taxes_id')
        project.property_account_income_id = request.POST.get('property_account_income_id')
        project.property_account_expense_id = request.POST.get('property_account_expense_id')
        project.attribute_set_code = request.POST.get('attribute_set_code')
        project.product_website = request.POST.get('product_website')
        project.meta_title_suffix = request.POST.get('meta_title_suffix')
        project.meta_description_suffix = request.POST.get('meta_description_suffix')
        project.status = request.POST.get('status')
        project.save()
        return redirect('project-view', pk=user.pk)

    return render(request, "project/edit.html", {'project': project, 'user': user})