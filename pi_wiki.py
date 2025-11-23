
import os
import markdown
from flask import Flask, render_template_string, request, redirect, url_for, escape

# --- Configuration ---
WIKI_PAGES_DIR = "wiki_pages"
SERVER_PORT = 8080

# --- Flask App Initialization ---
app = Flask(__name__)

# --- HTML Templates ---
# Using string templates keeps this as a single, easy-to-run file.

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - Pi Wiki</title>
    <style>
        body { font-family: sans-serif; line-height: 1.6; margin: 0; background-color: #fdfdfd; }
        .container { max-width: 800px; margin: 20px auto; padding: 20px; background-color: #fff; border: 1px solid #e0e0e0; border-radius: 5px; }
        .actions { margin-bottom: 20px; }
        .actions a { text-decoration: none; padding: 8px 12px; background-color: #007bff; color: white; border-radius: 3px; }
        .actions a:hover { background-color: #0056b3; }
        textarea { width: 98%; height: 60vh; font-family: monospace; font-size: 14px; }
        .content h1, .content h2, .content h3 { border-bottom: 1px solid #eee; padding-bottom: 5px; }
        pre { background-color: #f4f4f4; padding: 15px; border-radius: 4px; overflow-x: auto; }
        code { font-family: monospace; }
        .home-link { float: right; text-decoration: none; color: #007bff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>{{ title }} <a href="/" class="home-link">Home</a></h1>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
    </div>
</body>
</html>
"""

VIEW_TEMPLATE = """
{% extends "layout" %}
{% block content %}
    <div class="actions">
        <a href="{{ url_for('edit_page', page_name=page_name) }}">Edit this page</a>
    </div>
    {{ body|safe }}
{% endblock %}
"""

EDIT_TEMPLATE = """
{% extends "layout" %}
{% block content %}
    <form method="post">
        <textarea name="content">{{ content }}</textarea>
        <br><br>
        <div class="actions">
            <button type="submit" style="border:none; cursor:pointer;">
                <a>Save Page</a>
            </button>
        </div>
    </form>
{% endblock %}
"""

# --- Helper Functions ---
def get_page_path(page_name):
    """Constructs the full path for a given wiki page name."""
    # Sanitize page_name to prevent directory traversal attacks
    safe_page_name = "".join(c for c in page_name if c.isalnum() or c in (' ', '_', '-')).rstrip()
    return os.path.join(WIKI_PAGES_DIR, f"{safe_page_name}.md")

# --- Flask Routes ---
@app.route('/')
def home():
    """Redirects to the default 'Home' page."""
    return redirect(url_for('view_page', page_name='Home'))

@app.route('/view/<page_name>')
def view_page(page_name):
    """Displays a wiki page."""
    filepath = get_page_path(page_name)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert Markdown to HTML
        html_content = markdown.markdown(content, extensions=['fenced_code', 'tables'])
        
        return render_template_string(
            VIEW_TEMPLATE,
            title=escape(page_name),
            page_name=escape(page_name),
            body=html_content,
            layout=LAYOUT_TEMPLATE
        )
    else:
        # If page doesn't exist, redirect to the edit view to create it
        return redirect(url_for('edit_page', page_name=page_name))

@app.route('/edit/<page_name>', methods=['GET', 'POST'])
def edit_page(page_name):
    """Handles both displaying the edit form and saving the page content."""
    filepath = get_page_path(page_name)
    
    if request.method == 'POST':
        # Save the submitted content
        content = request.form['content']
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return redirect(url_for('view_page', page_name=page_name))
    
    # For a GET request, show the edit page
    content = ""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
    return render_template_string(
        EDIT_TEMPLATE,
        title=f"Editing {escape(page_name)}",
        page_name=escape(page_name),
        content=escape(content),
        layout=LAYOUT_TEMPLATE
    )

# --- Main Execution Block ---
if __name__ == '__main__':
    # Ensure the directory for wiki pages exists
    if not os.path.exists(WIKI_PAGES_DIR):
        print(f"Creating directory for wiki pages at: '{WIKI_PAGES_DIR}'")
        os.makedirs(WIKI_PAGES_DIR)

    # Create a default Home page if it doesn't exist
    home_path = get_page_path('Home')
    if not os.path.exists(home_path):
        print("Creating default 'Home.md' page.")
        with open(home_path, 'w', encoding='utf-8') as f:
            f.write("# Welcome to your Pi Wiki!\n\n")
            f.write("This is your new wiki, running on a Raspberry Pi.\n\n")
            f.write("To create a new page, simply edit the URL. For example, to create a page named 'My_New_Page', navigate to:\n")
            f.write("`/view/My_New_Page`\n\n")
            f.write("Click the 'Edit this page' link to get started.")

    print(f"Starting Pi Wiki server...")
    print(f"Access the wiki from your browser at http://<your_pi_ip>:{SERVER_PORT}")
    app.run(host='0.0.0.0', port=SERVER_PORT)
