from django.shortcuts import render, redirect, get_object_or_404
from LPsyncAdmin.forms import ProjectForm
from django.contrib import messages
from LPsyncAdmin.models import Project, User
from django.urls import reverse

def add(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        try:
            project_name = request.POST.get('project_name')
            price_margin = request.POST.get('price_margin')
            uom = request.POST.get('uom')
            account_number = request.POST.get('account_number')
            type_erp = request.POST.get('type_erp')
            taxes_id = request.POST.get('taxes_id')
            property_account_income_id = request.POST.get('property_account_income_id')
            property_account_expense_id = request.POST.get('property_account_expense_id')
            attribute_set_code = request.POST.get('attribute_set_code')
            product_website = request.POST.get('product_website')
            meta_title_suffix = request.POST.get('meta_title_suffix')
            meta_description_suffix = request.POST.get('meta_description_suffix')
            status = request.POST.get('status')
            sitemap_json = request.POST.get('sitemap_json')  # <-- Add this line

            if not all([project_name, taxes_id, property_account_income_id, property_account_expense_id]):
                messages.error(request, 'Please fill in all required fields.')
                form = ProjectForm()
                return render(request, 'project/project-index.html', {'form': form, 'user': user})

            instance = Project(
                project_name=project_name,
                price_margin=price_margin,
                uom=uom,
                account_number=account_number,
                type_erp=type_erp,
                taxes_id=taxes_id,
                property_account_income_id=property_account_income_id,
                property_account_expense_id=property_account_expense_id,
                attribute_set_code=attribute_set_code,
                product_website=product_website,
                meta_title_suffix=meta_title_suffix,
                meta_description_suffix=meta_description_suffix,
                status=status,
                sitemap_json=sitemap_json,  # <-- Add this line
                user=user
            )
            instance.save()
            messages.success(request, 'Project created successfully!')
            
            return redirect(reverse('project-view', kwargs={'pk': pk}))
        
        except ValueError as e:
            messages.error(request, f'Invalid data provided: {str(e)}')
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')

    form = ProjectForm()  
    return render(request, 'project/project-index.html', {'form': form, 'user': user})