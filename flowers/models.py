from django.db import models

from django.contrib.auth.models import User



class Category(models.Model):
    
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/')
    is_active = models.BooleanField(default=True)
    
    
    def __str__(self):
        return self.title


class Flower(models.Model):
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='flower_images/')
    
    is_new = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'flower'],
                name='unique_user_flower_like'
            )
        ]
        

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    

class Order(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('canceled', 'Canceled')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS, max_length=50, default='pending')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    flower = models.ForeignKey(Flower, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    