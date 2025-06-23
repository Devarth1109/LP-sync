from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from LPsyncAdmin.models import Sitemap, Product
from LPsyncAdmin.tasks import scrape_products_task, scrape_all_sitemaps_task, scrape_selected_sitemaps_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
import json

def site_map(request):
    sitemaps = Sitemap.objects.all()
    for sitemap in sitemaps:
        sitemap.product_count = Product.objects.filter(sitemap=sitemap).count()
    return render(request, 'sitemap.html', {'sitemaps': sitemaps})

def scrape_view(request, id):
    try:
        sitemap = get_object_or_404(Sitemap, id=id)
        channel_layer = get_channel_layer()
        current_count = Product.objects.filter(sitemap=sitemap).count()
        
        # Send a clear update to ensure the websocket connection is active
        async_to_sync(channel_layer.group_send)(
            f"scrape_count_{sitemap.id}",
            {
                'type': 'send_product_count',
                'count': {
                    'saved': 0,
                    'updated': 0,
                    'total': current_count,
                    'timestamp': time.time()
                }
            }
        )
        
        # Short delay to ensure the message is processed
        time.sleep(0.5)
        
        task = scrape_products_task.delay(sitemap.id)
        
        return JsonResponse({
            'success': True,
            'success_message': f'Started scraping products from {sitemap.url}. You will see real-time updates on the page.',
            'task_id': task.id,
            'saved_count': 0,
            'updated_count': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error_message': str(e)
        }, status=500)

def scrape_all_view(request):
    try:
        sitemaps = Sitemap.objects.all()
        channel_layer = get_channel_layer()
        
        # Send initial status to all sitemap WebSocket groups
        for sitemap in sitemaps:
            current_count = Product.objects.filter(sitemap=sitemap).count()
            async_to_sync(channel_layer.group_send)(
                f"scrape_count_{sitemap.id}",
                {
                    'type': 'send_product_count',
                    'count': {
                        'saved': 0,
                        'updated': 0,
                        'total': current_count,
                        'timestamp': time.time()
                    }
                }
            )
        
        # Start the scraping task
        task = scrape_all_sitemaps_task.delay()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'success_message': 'Started scraping all sitemaps. Each sitemap will be processed with a 90-second delay between them.',
                'task_id': task.id
            })
        
        else:
            request.session['scrape_all_message'] = 'Started scraping all sitemaps. Each sitemap will be processed with a 90-second delay between them.'
            return redirect('site_map')
            
    except Exception as e:
        error_message = str(e)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error_message': error_message
            }, status=500)
        
        else:
            request.session['scrape_all_error'] = f'Error starting scrape: {error_message}'
            return redirect('site_map')
        
def scrape_selected_view(request):
    if request.method == 'POST':
        try:
            # Get selected sitemap IDs from POST data
            selected_ids_raw = request.POST.get('selected_ids')
            if selected_ids_raw:
                selected_ids = json.loads(selected_ids_raw)
            else:
                selected_ids = []
            
            if not selected_ids:
                return JsonResponse({
                    'success': False,
                    'error_message': 'No sitemaps selected.'
                }, status=400)
                
            # Convert string IDs to integers
            selected_ids = [int(id) for id in selected_ids]
            
            # Get the selected sitemaps
            sitemaps = Sitemap.objects.filter(id__in=selected_ids)
            
            if not sitemaps.exists():
                return JsonResponse({
                    'success': False,
                    'error_message': 'No valid sitemaps found for the selected IDs.'
                }, status=404)
            
            # Initialize channel layer for websocket communications
            channel_layer = get_channel_layer()
            
            # Reset counts for each selected sitemap via websocket
            for sitemap in sitemaps:
                current_count = Product.objects.filter(sitemap=sitemap).count()
                async_to_sync(channel_layer.group_send)(
                    f"scrape_count_{sitemap.id}",
                    {
                        'type': 'send_product_count',
                        'count': {
                            'saved': 0,
                            'updated': 0,
                            'total': current_count,
                            'timestamp': time.time()
                        }
                    }
                )
            
            # Start the task to scrape selected sitemaps
            task = scrape_selected_sitemaps_task.delay(selected_ids)
            
            return JsonResponse({
                'success': True,
                'success_message': f'Started scraping {len(selected_ids)} selected sitemaps. Each sitemap will be processed with a 90-second delay between them.',
                'task_id': task.id,
                'selected_count': len(selected_ids)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error_message': str(e)
            }, status=500)
    
    # If not POST, return method not allowed
    return JsonResponse({
        'success': False,
        'error_message': 'Method not allowed'
    }, status=405)