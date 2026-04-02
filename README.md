# Library Service Project

## Setup
pip install django djangorestframework
python manage.py migrate
python manage.py runserver

## Endpoints
GET /api/books/
POST /api/books/
POST /api/books/{id}/borrow/
POST /api/books/{id}/return_book/
