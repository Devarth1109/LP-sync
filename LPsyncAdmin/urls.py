from django.urls import path
from LPsyncAdmin import views

from LPsyncAdmin.views.userview.user_view import signup, login, logout, fpswd, verify_otp, new_pswd

from LPsyncAdmin.views import base

# Correct import for project_view
from LPsyncAdmin.views.project_view import view, add, edit, delete as project_delete, scrape_sitemaps

from LPsyncAdmin.views.sitemap import run_external_script
from LPsyncAdmin.views.sitemap.scrape import scrape_view, scrape_all_view, scrape_selected_view
from LPsyncAdmin.views.sitemap import addsitemap
from LPsyncAdmin.views.sitemap import editsitemap
from LPsyncAdmin.views.sitemap.deletesitemap import delete as sitemap_delete
from LPsyncAdmin.views.sitemap.deleteall_sitemap import deleteall_sitemap

from LPsyncAdmin.views.authentication import home
from LPsyncAdmin.views.products_view import views as product_views
from LPsyncAdmin.views.products_view import product_add, product_delete, product_edit
from LPsyncAdmin.views.products_view.deleteall_products import deleteall_product

from LPsyncAdmin.views.product_errors.error_views import errors_view
from LPsyncAdmin.views.product_errors.error_delete import delete_error
from LPsyncAdmin.views.product_errors.deleteall_errors import deleteall_errors

from LPsyncAdmin.views.unauthorized import forbidden_view

from LPsyncAdmin.views.products_view.get_linenplus import get_linenplus_products

from LPsyncAdmin.views.products_view.views import sync

from LPsyncAdmin.views.sitemap.s_cards import s_cards
from LPsyncAdmin.views.products_view.p_cards import p_cards
from LPsyncAdmin.views.project_sync.project_sync_cards import project_sync_card
from LPsyncAdmin.views.project_sync.project_sync_add import project_sync_add
from LPsyncAdmin.views.project_sync.project_sync_delete import project_sync_delete

from LPsyncAdmin.views.project_sync.project_sync_v_pswd import project_sync_v_pswd
from LPsyncAdmin.views.project_sync.project_sync_change_email import project_sync_change_email

urlpatterns = [
    path('', base.BASE, name='base'),
    path('401_forbidden', forbidden_view, name='401_forbidden'),
    path('signup', signup, name='signup'),
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
    path('fpswd', fpswd, name='fpswd'),
    path('v_otp', verify_otp, name='v_otp'),
    path('new_pswd', new_pswd, name='new_pswd'),

    # Corrected project view path
    path('project/<int:pk>', view, name='project-view'),
    path('project_index/<int:pk>', add, name='project-index'),
    path('edit/<int:id>', edit, name='edit'),
    path('delete/<int:id>', project_delete),
    
    # New URL pattern for scraping sitemaps
    path('scrape-sitemaps/<int:project_id>', scrape_sitemaps, name='scrape-sitemaps'),

    # Corrected product view path
    path('products_card', p_cards, name='p_cards'),
    path('products-view/<int:pk>', product_views.products_view, name='products-view'),
    path('addproduct/<int:pk>', product_add.addproduct, name='addproduct'),
    path('product-delete/<int:id>', product_delete.delete_product, name='product-delete'), 
    path('deleteall-products/<int:pk>/', deleteall_product, name='deleteall-products'),
    path('edit-product/<int:id>/', product_edit.editproduct, name='edit-product'), 
    path('sync/<int:id>', sync, name='sync'),

    path('addsitemap/<int:pk>', views.sitemap.addsitemap, name='addsitemap'),
    path('editsitemap/<int:id>', views.sitemap.editsitemap, name='editsitemap'),
    path('deletesitemap/<int:id>', sitemap_delete, name="deletesitemap"),
    path('deleteallsitemap/<int:project_id>/', deleteall_sitemap, name='deleteall_sitemap'),
    path('run-script/<int:id>', views.sitemap.run_external_script, name='run_script'),
    
    path('sitemap_card', s_cards, name='s_cards'),
    path('sitemap/<int:pk>', views.sitemap.sitemap, name='site_map'),
    path('scrape/<int:id>', scrape_view, name='scrape'),
    path('scrape-all/', scrape_all_view, name='scrape_all'),
    path('scrape-selected/', scrape_selected_view, name='scrape_selected'),

    path('product_errors/<int:pk>', errors_view, name='product_errors'),
    path('error-delete/<int:id>', delete_error, name='error-delete'),
    path('deleteallerrors', deleteall_errors, name='deleteallerrors'),

    path('project_sync_card', project_sync_card, name='project_sync_card'),
    path('project_sync_add/<int:pk>', project_sync_add, name='project_sync_add'),
    path('project_sync_delete/<int:id>', project_sync_delete, name='project_sync_delete'),

    path('home', views.authentication.home, name='home'),

    path('get-linenplus-products/<int:pk>', get_linenplus_products, name='get_linenplus_products'),

    path('verify-password/<int:user_id>/', project_sync_v_pswd, name='project_sync_v_pswd'),
    path('change-email/<int:user_id>/', project_sync_change_email, name='project_sync_change_email'),

]