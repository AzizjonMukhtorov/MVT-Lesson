from django.urls import path

from .views import (home, get_flowers, 
                    get_flower_by_id, 
                    create_like, delete_like, 
                    login_user, logout_user, admin_page,
                    get_users_by_group)


urlpatterns = [
    path('', home, name='home'),
    path('flowers/', get_flowers, name='flowers'),
    path('flower/<int:pk>/', get_flower_by_id, name='flower_detail'),
    path('create_like/<int:flower_id>/', create_like, name='create_like'),
    path('delete_like/<int:flower_id>/', delete_like, name='delete_like'),
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('admin-page/', admin_page, name='admin_page'),
    path('admin-page/<int:group_id>/', get_users_by_group, name='get_users_by_group')
]
