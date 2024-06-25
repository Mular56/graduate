from django.urls import path
from .views import HomePageView, UserLoginView, UserLogoutView, UserRegisterView, \
    book_catalog, book_detail, add_book, edit_book, delete_book, \
        search_books, borrow_requests, change_borrow_request_status, \
            create_borrow_request, collect_book, return_book, approve_borrow_request, \
                decline_borrow_request

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    
    path('catalog/', book_catalog, name='catalog'),
    path('book/<int:pk>/', book_detail, name='book_detail'),
    path('add_book/', add_book, name='add_book'),
    path('edit_book/<int:pk>/', edit_book, name='edit_book'),
    path('delete_book/<int:pk>/', delete_book, name='delete_book'),
    path('search/', search_books, name='search_books'),
    
    path('book/<int:pk>/borrow_request/', create_borrow_request, name='create_borrow_request'),
    
    path('borrow_requests/', borrow_requests, name='borrow_requests'),
    path('borrow_request/<int:request_id>/collect/', collect_book, name='collect_book'),
    path('borrow_request/<int:request_id>/return/', return_book, name='return_book'),
    path('borrow_request/<int:request_id>/approve/', approve_borrow_request, name='approve_borrow_request'),
    path('borrow_request/<int:request_id>/decline/', decline_borrow_request, name='decline_borrow_request'),
]
