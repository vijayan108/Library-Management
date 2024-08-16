import frappe
import requests

def get_context(context):
    context.success = False  # Initialize success as False
    context.added_articles = []  # Initialize an empty list for added articles

    if frappe.request.method == "POST":
        image_url = frappe.form_dict.get('image_url')
        limit = int(frappe.form_dict.get('limit'))
        title = frappe.form_dict.get('filer_title')
        
        data = fetch_books(limit, title)
        
        for book in data:
            article = frappe.get_doc({
                'doctype': 'Article',
                'title': book['title'],
                'authors': book['authors'],
                'image_url': image_url,
                'publication_date': book['publication_date'],
                'isbn': book['isbn'],
                'publisher': book['publisher'],
            })
            article.insert()
            context.added_articles.append(book['title'])  # Add title to the context list

        context.success = True  # Set success to True after adding articles

def fetch_books(limit, title):
    books = []
    page = 1
    while len(books) < limit:
        response = requests.get(f'https://frappe.io/api/method/frappe-library?page={page}&title={title}')
        data = response.json().get('message', [])
        books.extend(data)
        if len(data) == 0 or len(books) >= limit:
            break
        page += 1
    return books[:limit]
