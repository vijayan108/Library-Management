import frappe
from frappe.model.document import Document
import requests

class ArticleImport(Document):
    def validate(self):
        # Validate that the article doesn't already exist
        pass
    def after_insert(self):
        # Fetch books and insert them into the Artic le doctype
        limit = int(self.limit) if self.limit else 30  # Default limit if not specified
        title = self.fliter_title
        image_url = self.image

        data = self.fetch_books(limit, title)

        added_articles = []
        for book in data:
            # Create and insert a new article document
            article = frappe.get_doc({
                'doctype': 'Article',
                'article_name': book['title'],
                'author': book['authors'],
                'isbn': book['isbn'],
                'publisher': book['publisher'],
                'image': image_url,  # Assuming this is the field for the image URL in Article
                'status': "Available",  # Assuming status should be set to "Available" by default
                'description': f"<div class=\"ql-editor read-mode\"><p>{book['title']} by {book['authors']}</p></div>",  # Using title and author as description
                'route': f"articles/{book['title'].lower().replace(' ', '-')}",  # Generating a route based on the title
                'published': 1,  # Assuming published is a boolean field
            })
            article.insert()
            added_articles.append(book['title'])  # Collect added articles' titles

        frappe.msgprint(f"Successfully added {len(added_articles)} articles.")

    def fetch_books(self, limit, title):
        books = []
        page = 1
        while len(books) < limit:
            response = requests.get(f'https://frappe.io/api/method/frappe-library?page={page}&title={title}')
            if response.status_code != 200:
                frappe.throw("Failed to fetch books from the external API.")
            data = response.json().get('message', [])
            books.extend(data)
            if len(data) == 0 or len(books) >= limit:
                break
            page += 1
        return books[:limit]
