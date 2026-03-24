from django import forms
from .models import ContactMessage, Service, Portfolio, BlogPost, Testimonial


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your full name', 'class': 'name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'name'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Enter your phone number', 'class': 'phone'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Enter your Subject', 'class': 'subject'}),
            'message': forms.Textarea(attrs={'placeholder': 'Enter your message', 'id': 'message'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Name must be at least 2 characters.')
        return name

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 10:
            raise forms.ValidationError('Message must be at least 10 characters.')
        return msg


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['title', 'slug', 'short_description', 'description', 'icon_class', 'order', 'is_active']


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = [
            'title',
            'slug',
            'category',
            'short_description',
            'description',
            'image',
            'client_name',
            'project_date',
            'order',
            'is_active',
        ]


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'slug', 'excerpt', 'content', 'image', 'author_name', 'published_at', 'is_published']


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ['name', 'role', 'company', 'content', 'image', 'rating', 'order', 'is_active']
