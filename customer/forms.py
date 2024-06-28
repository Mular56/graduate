from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'summary', 'isbn', 'available', 'published_date', 'publisher', 'genres', 'authors', 'borrower']
