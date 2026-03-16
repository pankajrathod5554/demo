from django.urls import path
from . import views

app_name = 'api'

# User-facing pages
urlpatterns = [
    path('', views.index_1, name='index_1'),
    path('index-1/', views.index_1, name='index_1_slash'),
    path('about/', views.about, name='about'),
    path('service/', views.service_list, name='service_list'),
    path('service/<slug:slug>/', views.service_single, name='service_single'),
    path('case/', views.case_list, name='case_list'),
    path('portfolio/<slug:slug>/', views.portfolio_single, name='portfolio_single'),
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_single, name='blog_single'),
    path('faq/', views.faq, name='faq'),
    path('team/', views.team_list, name='team_list'),
    path('team/<int:pk>/', views.team_single, name='team_single'),
    path('contact/', views.contact, name='contact'),
    path('contact/submit/', views.contact_submit, name='contact_submit'),
]

# Admin panel
urlpatterns += [
    path('admin-panel/login/', views.admin_login, name='admin_login'),
    path('admin-panel/logout/', views.admin_logout, name='admin_logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/messages/', views.admin_messages, name='admin_messages'),
    path('admin-panel/messages/<int:pk>/read/', views.admin_message_read, name='admin_message_read'),
    path('admin-panel/messages/<int:pk>/delete/', views.admin_message_delete, name='admin_message_delete'),
    path('admin-panel/services/', views.admin_services, name='admin_services'),
    path('admin-panel/services/create/', views.admin_service_create, name='admin_service_create'),
    path('admin-panel/services/<int:pk>/edit/', views.admin_service_edit, name='admin_service_edit'),
    path('admin-panel/services/<int:pk>/delete/', views.admin_service_delete, name='admin_service_delete'),
    path('admin-panel/portfolio/', views.admin_portfolio, name='admin_portfolio'),
    path('admin-panel/portfolio/create/', views.admin_portfolio_create, name='admin_portfolio_create'),
    path('admin-panel/portfolio/<int:pk>/edit/', views.admin_portfolio_edit, name='admin_portfolio_edit'),
    path('admin-panel/portfolio/<int:pk>/delete/', views.admin_portfolio_delete, name='admin_portfolio_delete'),
    path('admin-panel/blog/', views.admin_blog, name='admin_blog'),
    path('admin-panel/blog/create/', views.admin_blog_create, name='admin_blog_create'),
    path('admin-panel/blog/<int:pk>/edit/', views.admin_blog_edit, name='admin_blog_edit'),
    path('admin-panel/blog/<int:pk>/delete/', views.admin_blog_delete, name='admin_blog_delete'),
    path('admin-panel/testimonials/', views.admin_testimonials, name='admin_testimonials'),
    path('admin-panel/testimonials/create/', views.admin_testimonial_create, name='admin_testimonial_create'),
    path('admin-panel/testimonials/<int:pk>/edit/', views.admin_testimonial_edit, name='admin_testimonial_edit'),
    path('admin-panel/testimonials/<int:pk>/delete/', views.admin_testimonial_delete, name='admin_testimonial_delete'),
    path('admin-panel/error/', views.admin_error_page, name='admin_error'),
]
