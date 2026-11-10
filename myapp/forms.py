from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(max_length=5000)


class NewsletterForm(forms.Form):
    email = forms.EmailField()
