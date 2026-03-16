from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Count

from .models import ContactMessage, Service, Portfolio, BlogPost, Testimonial
from .forms import ContactForm, ServiceForm, PortfolioForm, BlogPostForm, TestimonialForm


def _staff_required(view_func):
    """Decorator: user must be staff to access admin panel."""
    def wrap(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('api:admin_login')
        if not request.user.is_staff:
            messages.error(request, 'Access denied. Staff only.')
            return redirect('api:admin_login')
        return view_func(request, *args, **kwargs)
    return wrap


# ---------- User-facing pages ----------

def index_1(request):
    return render(request, 'user_site/index-1.html')

def about(request):
    return render(request, 'user_site/about.html')

def service_list(request):
    services = Service.objects.filter(is_active=True).order_by('order', 'title')
    return render(request, 'user_site/service.html', {'services': services})

def service_single(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(request, 'user_site/service-single.html', {'service': service})

def case_list(request):
    portfolios = Portfolio.objects.filter(is_active=True).order_by('order', '-created_at')
    return render(request, 'user_site/case.html', {'portfolios': portfolios})

def portfolio_single(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug, is_active=True)
    return render(request, 'user_site/portfolio-single.html', {'portfolio': portfolio})

def blog_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'user_site/blog.html', {'posts': posts})

def blog_single(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'user_site/blog-single.html', {'post': post})

def faq(request):
    return render(request, 'user_site/faq.html')

def team_list(request):
    return render(request, 'user_site/team.html')

def team_single(request, pk):
    return render(request, 'user_site/team-single.html')

def contact(request):
    return render(request, 'user_site/contact.html', {'contact_form': ContactForm()})

def contact_submit(request):
    if request.method != 'POST':
        return redirect('api:contact')
    form = ContactForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Thank you! Your message has been sent.')
        return redirect('api:contact')
    messages.error(request, 'Please correct the errors below.')
    return render(request, 'user_site/contact.html', {'contact_form': form})


# ---------- Admin: Auth ----------

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('api:admin_dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff:
                login(request, user)
                next_url = request.GET.get('next', reverse('api:admin_dashboard'))
                return redirect(next_url)
            messages.error(request, 'Access denied. Staff account required.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'admin_panel/page-login.html', {'form': form})

def admin_logout(request):
    logout(request)
    return redirect('api:admin_login')


# ---------- Admin: Dashboard & Messages ----------

@_staff_required
def admin_dashboard(request):
    total_messages = ContactMessage.objects.count()
    total_services = Service.objects.filter(is_active=True).count()
    total_portfolio = Portfolio.objects.filter(is_active=True).count()
    recent_messages = ContactMessage.objects.all()[:5]
    return render(request, 'admin_panel/dashboard.html', {
        'total_messages': total_messages,
        'total_services': total_services,
        'total_portfolio': total_portfolio,
        'recent_messages': recent_messages,
    })

@_staff_required
def admin_messages(request):
    items = ContactMessage.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/message.html', {'messages_list': items})

@_staff_required
def admin_message_read(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save(update_fields=['is_read'])
    return redirect('api:admin_messages')

@_staff_required
def admin_message_delete(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, 'Message deleted.')
    return redirect('api:admin_messages')

@_staff_required
def admin_error_page(request):
    return render(request, 'admin_panel/page-error.html')


# ---------- Admin: Services CRUD ----------

@_staff_required
def admin_services(request):
    items = Service.objects.all().order_by('order', 'title')
    return render(request, 'admin_panel/service.html', {'services': items})

@_staff_required
def admin_service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service created.')
            return redirect('api:admin_services')
    else:
        form = ServiceForm()
    return render(request, 'admin_panel/form-service.html', {'form': form, 'title': 'Create Service'})

@_staff_required
def admin_service_edit(request, pk):
    obj = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service updated.')
            return redirect('api:admin_services')
    else:
        form = ServiceForm(instance=obj)
    return render(request, 'admin_panel/form-service.html', {'form': form, 'title': 'Edit Service', 'object': obj})

@_staff_required
def admin_service_delete(request, pk):
    obj = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Service deleted.')
        return redirect('api:admin_services')
    return render(request, 'admin_panel/confirm-delete.html', {'object': obj, 'cancel_url': 'api:admin_services'})


# ---------- Admin: Portfolio CRUD ----------

@_staff_required
def admin_portfolio(request):
    items = Portfolio.objects.all().order_by('order', '-created_at')
    return render(request, 'admin_panel/portfolio.html', {'portfolios': items})

@_staff_required
def admin_portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio item created.')
            return redirect('api:admin_portfolio')
    else:
        form = PortfolioForm()
    return render(request, 'admin_panel/form-portfolio.html', {'form': form, 'title': 'Create Portfolio'})

@_staff_required
def admin_portfolio_edit(request, pk):
    obj = get_object_or_404(Portfolio, pk=pk)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio updated.')
            return redirect('api:admin_portfolio')
    else:
        form = PortfolioForm(instance=obj)
    return render(request, 'admin_panel/form-portfolio.html', {'form': form, 'title': 'Edit Portfolio', 'object': obj})

@_staff_required
def admin_portfolio_delete(request, pk):
    obj = get_object_or_404(Portfolio, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Portfolio item deleted.')
        return redirect('api:admin_portfolio')
    return render(request, 'admin_panel/confirm-delete.html', {'object': obj, 'cancel_url': 'api:admin_portfolio'})


# ---------- Admin: Blog CRUD ----------

@_staff_required
def admin_blog(request):
    items = BlogPost.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/blog.html', {'posts': items})

@_staff_required
def admin_blog_create(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post created.')
            return redirect('api:admin_blog')
    else:
        form = BlogPostForm()
    return render(request, 'admin_panel/form-blog.html', {'form': form, 'title': 'Create Blog Post'})

@_staff_required
def admin_blog_edit(request, pk):
    obj = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated.')
            return redirect('api:admin_blog')
    else:
        form = BlogPostForm(instance=obj)
    return render(request, 'admin_panel/form-blog.html', {'form': form, 'title': 'Edit Blog Post', 'object': obj})

@_staff_required
def admin_blog_delete(request, pk):
    obj = get_object_or_404(BlogPost, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Blog post deleted.')
        return redirect('api:admin_blog')
    return render(request, 'admin_panel/confirm-delete.html', {'object': obj, 'cancel_url': 'api:admin_blog'})


# ---------- Admin: Testimonials CRUD ----------

@_staff_required
def admin_testimonials(request):
    items = Testimonial.objects.all().order_by('order', '-created_at')
    return render(request, 'admin_panel/testimonials.html', {'testimonials': items})

@_staff_required
def admin_testimonial_create(request):
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial created.')
            return redirect('api:admin_testimonials')
    else:
        form = TestimonialForm()
    return render(request, 'admin_panel/form-testimonial.html', {'form': form, 'title': 'Create Testimonial'})

@_staff_required
def admin_testimonial_edit(request, pk):
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        form = TestimonialForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Testimonial updated.')
            return redirect('api:admin_testimonials')
    else:
        form = TestimonialForm(instance=obj)
    return render(request, 'admin_panel/form-testimonial.html', {'form': form, 'title': 'Edit Testimonial', 'object': obj})

@_staff_required
def admin_testimonial_delete(request, pk):
    obj = get_object_or_404(Testimonial, pk=pk)
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'Testimonial deleted.')
        return redirect('api:admin_testimonials')
    return render(request, 'admin_panel/confirm-delete.html', {'object': obj, 'cancel_url': 'api:admin_testimonials'})
