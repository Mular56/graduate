from django.db import models
from django.contrib.auth.models import User

class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True, null=True)
    isbn = models.CharField(max_length=13, unique=True)
    available = models.BooleanField(default=True)
    published_date = models.DateField(blank=True, null=True)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='books', blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='borrowed_books')

    def __str__(self):
        return self.title

class BorrowRequest(models.Model):
    PENDING = 1
    APPROVED = 2
    COLLECTED = 3
    COMPLETE = 4
    DECLINED = 5

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (COLLECTED, 'Collected'),
        (COMPLETE, 'Complete'),
        (DECLINED, 'Declined'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_requests')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    overdue = models.BooleanField(default=False)
    request_date = models.DateField(auto_now_add=True, editable=False)
    approval_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    complete_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.book.title} - {self.borrower.username}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status in [self.APPROVED, self.COLLECTED]:
            self.book.available = False
        else:
            if not BorrowRequest.objects.filter(book=self.book, status__in=[self.APPROVED, self.COLLECTED]).exists():
                self.book.available = True
        self.book.save()
