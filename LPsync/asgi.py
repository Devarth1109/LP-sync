# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# import LPsyncAdmin
# from LPsyncAdmin import routing

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LPsync.settings')

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     'http': django_asgi_app,
#     'websocket': AuthMiddlewareStack(
#         URLRouter(
#             LPsyncAdmin.routing.websocket_urlpatterns
#         )
#     ),
# })

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from LPsyncAdmin import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LPsync.settings')  # ✅ fixed

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
