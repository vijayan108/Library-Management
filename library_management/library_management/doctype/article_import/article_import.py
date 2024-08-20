import frappe
from frappe.model.document import Document
import requests

class ArticleImport(Document):
    def validate(self):
        # Validate that the article limit doesn't exceed 30
        if self.limit and int(self.limit) > 30:
            frappe.throw("The limit cannot exceed 30.")

    def valid_books(self, book):
        article = frappe.db.exists('Article', {'isbn': book['isbn']})
        return article

    def after_insert(self):
        # Fetch books and insert them into the Article doctype
        limit = int(self.limit) if self.limit else 30  # Default limit if not specified
        title = self.fliter_title
        image_url = self.image

        added_articles = []
        self.fetch_books(limit, title, image_url, added_articles)

        frappe.msgprint(f"Successfully added {len(added_articles)} articles.")

    def fetch_books(self, limit, title, image_url, added_articles):
        books = []
        page = 1
        while len(added_articles) < limit:
            response = requests.get(f'https://frappe.io/api/method/frappe-library?page={page}&title={title}')
            if response.status_code != 200:
                frappe.throw("Failed to fetch books from the external API.")
            data = response.json().get('message', [])
            
            if not data:
                break  # No more data to fetch

            for book in data:
                if not frappe.db.exists('Article', {'isbn': book['isbn']}):
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

                if len(added_articles) >= limit:
                    break  # Stop if we've added enough articles

            page += 1
