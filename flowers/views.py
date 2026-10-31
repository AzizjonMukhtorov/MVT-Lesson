from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required, login_required

from .forms import FlowersForm, CategoryForm

from .apps import FlowersConfig

from .models import Category, Flower, Likes

def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Username already exists"
            })

        if User.objects.filter(email=email).exists():
            return render(request, "register.html", {
                "error": "Email already exists"
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_active=False
        )
        # group = Group.objects.get(name='Users')
        # group.add(user)
        
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        verification_url = request.build_absolute_url(
            reverse(
                'activate',
                kwargs={
                    'uidb64': uid,
                    'token': token
                }
            )
        )
        
        send_mail(
            subject='Confirm email',
            message=(
                f"Hello {username}!\n\n"
                f"Click the link to activate your account:\n"
                f"{verification_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False
        )
        
        return render(request, "email_sent.html")
    render(request, 'register.html')


def login_user(request):
    
    if request.method == 'POST':
        
        data = request.POST
        
        username = data['username']
        password = data['password']
                
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user=user)    
                
            return redirect('home')
    
    return render(request, 'login.html')


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    return redirect('home')


def admin_access(func):
    
    def wrapper(request, *args, **kwargs):
        if request.user.is_staff:
            return func(request, *args, **kwargs)
        return HttpResponse('Permission denide!', status=403)
    return wrapper   


def home(request):
    print(request.user.has_perm('flowers.add_flower'))
    flowers = Flower.objects.filter(is_active=True).order_by('is_new')[:8]
    categories = Category.objects.all()[:4]
    
    return render(request, 'home.html',
                  context={'flowers': flowers, 'categories': categories})


@permission_required('flowers.view_flower', raise_exception=True)
def get_flowers(request):
    print(request.user.get_all_permissions())
    flowers = Flower.objects.filter(is_active=True).order_by('is_new')
    
    search = request.GET.get('search', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    is_new = request.GET.get('new', '')

    if search:
        flowers = flowers.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
        
    if min_price:
        flowers = flowers.filter(price__gte=min_price)
        
    if max_price:
        flowers = flowers.filter(price__lte=max_price)
        
    if is_new:
        flowers = flowers.filter(is_new=True)
        
    if request.user.is_authenticated:
        likes = set(
            Likes.objects.filter(
                user=request.user,
                status=True
            ).values_list('flower_id', flat=True)
        )
    else:
        likes = set()
        
    return render(request, 'flowers.html', context={'flowers': flowers, 'likes': likes})
    

def get_flower_by_id(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    return render(request, 'flower_detail.html', context={'flower': flower})


def admin_page(request):
    groups = Group.objects.all()
    print(groups[0].user_set.all())
    return render(request, 'admin_page.html', context={'groups': groups})

# def get_users_by_group(request, group_id):
    
#     groups = Group.objects.prefetch_related('user_set')
#     group = groups.get(pk=group_id)
    
#     group_users = [user for user in group.user_set.all()]
#     permissions = Permission.objects.prefetch_related(
#         'content_type').filter(content_type__app_label=FlowersConfig.name)
    
#     group_permissions = [permission for permission in permissions if permission in group.permissions.all()]
#     not_group_permissions = [permission for permission in permissions if permission not in group.permissions.all()]
    
#     # ['32', '25', '26', '28']
    
#     if request.method == 'POST':
#         data = request.POST        
#         assigned_permissions = data.getlist('permissions')
#         not_assigned_permissions = data.getlist('new_permissions')
        
#         to_delete_permissions = [permission for permission in group_permissions if str(permission.id) not in assigned_permissions]
#         to_add_permissions = [permission for permission in not_group_permissions if str(permission.id) in not_assigned_permissions]
        
#         group.permissions.remove(*to_delete_permissions)
#         group.permissions.add(*to_add_permissions)
        
        
    
#     return render(request, 'admin_page.html', 
#                   context={
#                       'groups': groups, 
#                       'group_users': group_users,
#                       'group_permissions': group_permissions,
#                       'not_group_permissions': not_group_permissions
#                       })

def get_users_by_group(request, group_id):

    groups = Group.objects.all()
    group = get_object_or_404(Group, pk=group_id)

    permissions = Permission.objects.filter(
        content_type__app_label=FlowersConfig.name
    )

    if request.method == 'POST':
        assigned_permissions = request.POST.getlist('permissions')
        new_permissions = request.POST.getlist('new_permissions')

        selected_permissions = (
            assigned_permissions + new_permissions
        )

        # Обновляем только разрешения приложения Flowers
        selected_ids = [
            int(pk) for pk in selected_permissions
            if pk.isdigit()
        ]

        selected_ids = list(
            permissions.filter(pk__in=selected_ids)
            .values_list('pk', flat=True)
        )

        current_ids = set(
            group.permissions.filter(
                pk__in=permissions
            ).values_list('pk', flat=True)
        )

        selected_ids = set(selected_ids)

        group.permissions.remove(*(current_ids - selected_ids))
        group.permissions.add(*(selected_ids - current_ids))

        return redirect('get_users_by_group', group_id=group_id)

    group_users = group.user_set.all()

    group_permissions = permissions.filter(
        group=group
    )

    not_group_permissions = permissions.exclude(
        group=group
    )

    return render(request, 'admin_page.html', {
        'groups': groups,
        'group_users': group_users,
        'group_permissions': group_permissions,
        'not_group_permissions': not_group_permissions,
    })
    
    

def create_like(request, flower_id):
    flower = get_object_or_404(Flower, pk=flower_id)
    updated = Likes.objects.filter(
        user=request.user,
        flower=flower
    ).update(status=True)

    if not updated:
        Likes.objects.create(
            user=request.user,
            flower=flower,
            status=True
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': True})

    return redirect('flowers')


def delete_like(request, flower_id):
    Likes.objects.filter(
        user=request.user,
        flower_id=flower_id
    ).update(status=False)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': False})

    return redirect('flowers')


def create_flower(request):
    
    form = FlowersForm()
    if request.method == 'POST':
        form = FlowersForm(request.data)
        
        if form.is_valid():
            form.save()
            return redirect('home')
        
    return render(request, 'create_flower.html', context={'form': form})

def create_category(request):
    
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
  
        if form.is_valid():
            data = form.cleaned_data
            print(data)
            Category.objects.create(
                title=data['title'],
                image=data['image']
            )
            return redirect('home')
        
    return render(request, 'create_flower.html', context={'form': form})