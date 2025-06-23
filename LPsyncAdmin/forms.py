from django import forms
from LPsyncAdmin.models import Project
from LPsyncAdmin.models import Sitemap
from LPsyncAdmin.models import Product
from LPsyncAdmin.models.usermodel import User
from LPsyncAdmin.models.project_syncing import ProjectSyncing

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'pswd': forms.PasswordInput(attrs={'class': 'form-control'}),
            'cpswd': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),  # Changed from 'username' to 'user'
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'price_margin': forms.TextInput(attrs={'class': 'form-control'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control'}),
            'type_erp': forms.TextInput(attrs={'class': 'form-control'}),
            'taxes_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Changed to NumberInput
            'property_account_income_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Changed to NumberInput
            'property_account_expense_id': forms.NumberInput(attrs={'class': 'form-control'}),  # Changed to NumberInput
            'attribute_set_code': forms.TextInput(attrs={'class': 'form-control'}),
            'product_website': forms.URLInput(attrs={'class': 'form-control'}),  # Changed to URLInput
            'meta_title_suffix': forms.TextInput(attrs={'class': 'form-control'}),
            'meta_description_suffix': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(choices=((0, 'Disabled'), (1, 'Enabled')), attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()
        self.fields['user'].empty_label = "Select user"

class SitemapForm(forms.ModelForm):
    class Meta:
        model = Sitemap
        fields = "__all__"
        widgets = {
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'sitemap': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.TextInput(attrs={'class': 'form-control'}),
            'project_name': forms.Select(attrs={'class': 'form-control'}),
            'username': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['project_name'].choices = [('', 'Select project')] + [
            (project.id, project.project_name) for project in Project.objects.all()
        ]
        self.fields['username'].choices = [('', 'Select user')] + [
            (user.id, user.username) for user in User.objects.all()
        ]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            'username': forms.Select(attrs={'class': 'form-control'}),
            'sitemap_name': forms.Select(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'uom': forms.TextInput(attrs={'class': 'form-control'}),
            'product_title': forms.TextInput(attrs={'class': 'form-control'}),
            'product_price': forms.TextInput(attrs={'class': 'form-control'}),
            'update_flag': forms.TextInput(attrs={'class': 'form-control'}),
            'product_description': forms.TextInput(attrs={'class': 'form-control'}),
            'base_product_image': forms.TextInput(attrs={'class': 'form-control'}),
            'additional_images': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = [('', 'Select user')] + [
            (user.id, user.username) for user in User.objects.all()
        ]
        self.fields['sitemap_name'].choices = [('', 'Select sitemap')] + [
            (sitemap.id, sitemap.sitemap_name) for sitemap in Sitemap.objects.all()
        ]

class ProjectSyncingForm(forms.ModelForm):
    class Meta:
        model = ProjectSyncing
        fields = "__all__"
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'platform': forms.Select(attrs={'class': 'form-control'}),
            'endpoint_url': forms.TextInput(attrs={'class': 'form-control'}),
            'token_url': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_username': forms.TextInput(attrs={'class': 'form-control'}),
            'admin_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'admin_password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = User.objects.all()
        self.fields['user'].empty_label = "Select user"
        self.fields['project'].queryset = Project.objects.all()
        self.fields['project'].empty_label = "Select project"