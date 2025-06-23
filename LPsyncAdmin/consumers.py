# import json, time
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from LPsyncAdmin.models import Product

# class ScrapeConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.sitemap_id = self.scope['url_route']['kwargs']['sitemap_id']
#         self.group_name = f"scrape_count_{self.sitemap_id}"
        
#         # Join group
#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )
        
#         await self.accept()
        
#         # Send confirmation message
#         await self.send(text_data=json.dumps({
#             'type': 'connection_established',
#             'message': f'Connected to sitemap {self.sitemap_id}'
#         }))
        
#         # Send initial product count
#         count = await self.get_product_count(self.sitemap_id)
#         await self.send(text_data=json.dumps({
#             'count': {
#                 'saved': 0,
#                 'updated': 0,
#                 'total': count,
#                 'timestamp': time.time()
#             }
#         }))
    
#     async def disconnect(self, close_code):
#         # Leave group
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )
    
#     # Receive message from WebSocket
#     async def receive(self, text_data):
#         try:
#             text_data_json = json.loads(text_data)
#             message = text_data_json.get('message', {})
            
#             # Send message to room group
#             await self.channel_layer.group_send(
#                 self.group_name,
#                 {
#                     'type': 'send_product_count',
#                     'count': message
#                 }
#             )
#         except Exception as e:
#             await self.send(text_data=json.dumps({
#                 'error': str(e)
#             }))
    
#     # Receive message from room group
#     async def send_product_count(self, event):
#         try:
#             count = event['count']
            
#             # Send message to WebSocket
#             await self.send(text_data=json.dumps({
#                 'count': count
#             }))
#         except Exception as e:
#             await self.send(text_data=json.dumps({
#                 'error': str(e)
#             }))
    
#     async def scrape_complete(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'scrape_complete',
#             'sitemap_id': event.get('sitemap_id'),
#             'timestamp': event.get('timestamp')
#         }))

#     async def send_processing_status(self, event):
#         await self.send(text_data=json.dumps({
#             'type': 'processing_status',
#             'status': event.get('status', {})
#         }))

#     @database_sync_to_async
#     def get_product_count(self, sitemap_id):
#         try:
#             return Product.objects.filter(sitemap_id=sitemap_id).count()
#         except Exception as e:
#             return 0

import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ScrapeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sitemap_id = self.scope['url_route']['kwargs']['sitemap_id']
        self.group_name = f"scrape_count_{self.sitemap_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

        # Send confirmation message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': f'Connected to sitemap {self.sitemap_id}'
        }))

        # Send initial product count
        count = await self.get_product_count(self.sitemap_id)
        await self.send(text_data=json.dumps({
            'count': {
                'saved': 0,
                'updated': 0,
                'total': count,
                'timestamp': time.time()
            }
        }))

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json.get('message', {})

            # Broadcast to group
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'send_product_count',
                    'count': message
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    # Receive from group
    async def send_product_count(self, event):
        try:
            count = event['count']
            await self.send(text_data=json.dumps({
                'count': count
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'error': str(e)
            }))

    async def scrape_complete(self, event):
        await self.send(text_data=json.dumps({
            'type': 'scrape_complete',
            'sitemap_id': event.get('sitemap_id'),
            'timestamp': event.get('timestamp')
        }))

    async def send_processing_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'processing_status',
            'status': event.get('status', {})
        }))

    @database_sync_to_async
    def get_product_count(self, sitemap_id):
        try:
            from LPsyncAdmin.models import Product  # ✅ Delayed import to prevent AppRegistryNotReady
            return Product.objects.filter(sitemap_id=sitemap_id).count()
        except Exception:
            return 0
