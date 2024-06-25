from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView
from .models import Book
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import BookForm
from django.views.decorators.http import require_POST
from .models import BorrowRequest

from django.contrib.auth.mixins import LoginRequiredMixin


class HomePageView(TemplateView):
    template_name = 'base.html'

class UserLoginView(LoginView):
    template_name = 'login.html'

    def get_success_url(self):
        return reverse_lazy('catalog') 

class UserLogoutView(LogoutView):
    template_name = 'logout.html'

class UserRegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'register.html'
    success_url = reverse_lazy('catalog')

def book_catalog(request):
    books = Book.objects.all()
    return render(request, 'catalog.html', {'books': books})


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            book = form.save()
            return redirect('catalog')  
    else:
        form = BookForm()
    
    return render(request, 'add_book.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_detail', pk=pk)
    else:
        form = BookForm(instance=book)
    
    return render(request, 'edit_book.html', {'form': form, 'book': book})

@user_passes_test(lambda u: u.is_superuser or u.is_staff)
@require_POST
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('catalog')
    return render(request, 'delete_book.html', {'book': book})

def search_books(request):
    query = request.GET.get('query')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    
    context = {
        'books': books,
        'query': query,
    }
    return render(request, 'search_results.html', context)



@login_required
def borrow_requests(request):
    if request.user.is_staff:
        # Показуємо всі запити на позику для бібліотекарів
        borrow_requests = BorrowRequest.objects.all()
    else:
        # Показуємо тільки запити на позику користувача для звичайних користувачів
        borrow_requests = BorrowRequest.objects.filter(borrower=request.user)

    context = {
        'borrow_requests': borrow_requests,
    }
    return render(request, 'borrow_requests.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff)
def change_borrow_request_status(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    
    if request.method == 'POST':
        new_status = int(request.POST.get('status'))
        borrow_request.status = new_status
        borrow_request.save()
        return redirect('borrow_requests')

    context = {
        'borrow_request': borrow_request,
        'status_choices': BorrowRequest.STATUS_CHOICES,
    }
    return render(request, 'change_borrow_request_status.html', context)

@login_required
@require_POST
def create_borrow_request(request, pk):
    book = get_object_or_404(Book, pk=pk)

    # Перевіряємо, чи є вже запит на цю книгу від користувача
    existing_request = BorrowRequest.objects.filter(book=book, borrower=request.user, status=BorrowRequest.PENDING).exists()
    if existing_request:
        # Можна обробити цей випадок відповідно до бізнес-логіки
        return redirect('book_detail', pk=pk)

    # Створюємо новий запит на позику
    BorrowRequest.objects.create(book=book, borrower=request.user)

    # Можливо, додамо повідомлення про успіх
    messages.success(request, 'Запит на позику було створено.')
    return redirect('book_detail', pk=pk)

@login_required
@require_POST
def collect_book(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if borrow_request.status == BorrowRequest.APPROVED:
        borrow_request.status = BorrowRequest.COLLECTED
        borrow_request.save()
        borrow_request.book.available = False
        borrow_request.book.save()
    return redirect('borrow_requests')

@login_required
@require_POST
def return_book(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if borrow_request.status == BorrowRequest.COLLECTED:
        borrow_request.status = BorrowRequest.COMPLETE
        borrow_request.save()
        borrow_request.book.available = True
        borrow_request.book.save()
    return redirect('borrow_requests')


@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def approve_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if borrow_request.status == BorrowRequest.PENDING:
        borrow_request.status = BorrowRequest.APPROVED
        borrow_request.save()
    return redirect('borrow_requests')

@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def decline_borrow_request(request, request_id):
    borrow_request = get_object_or_404(BorrowRequest, pk=request_id)
    if borrow_request.status == BorrowRequest.PENDING:
        borrow_request.status = BorrowRequest.DECLINED
        borrow_request.save()
    return redirect('borrow_requests')
