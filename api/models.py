from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject or 'No subject'}"


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title


class Portfolio(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    short_description = models.TextField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='portfolio/', blank=True, null=True)
    client_name = models.CharField(max_length=200, blank=True)
    project_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name_plural = 'Portfolio / Case Studies'

    def __str__(self):
        return self.title


class BlogPost(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    excerpt = models.TextField(blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author_name = models.CharField(max_length=200, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=200, blank=True)
    company = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.PositiveSmallIntegerField(default=5, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.name
