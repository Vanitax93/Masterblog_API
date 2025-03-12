from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

# Create Flask app first
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

# Swagger configuration
SWAGGER_URL = "/api/docs"  # swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL = "/static/masterblog.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API'
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]


@app.route('/api/posts', methods=['GET'])
def get_posts():
    sort_field = request.args.get('sort')
    direction = request.args.get('direction')

    valid_sort_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_sort_fields:
        return jsonify({
            "error": f"Invalid sort field. Must be one of {valid_sort_fields}"
        }), 400

    if direction and direction not in valid_directions:
        return jsonify({
            "error": f"Invalid sort direction. Must be one of {valid_directions}"
        }), 400

    posts_to_return = POSTS.copy()

    if sort_field:
        reverse = direction == 'desc'
        posts_to_return.sort(key=lambda x: x[sort_field].lower(), reverse=reverse)

    return jsonify(posts_to_return)


@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        missing_fields = []
        if not data or 'title' not in data:
            missing_fields.append('title')
        if not data or 'content' not in data:
            missing_fields.append('content')
        return jsonify({
            'error': 'Missing required fields',
            'missing': missing_fields
        }), 400

    new_id = max(post['id'] for post in POSTS) + 1 if POSTS else 1
    new_post = {
        'id': new_id,
        'title': data['title'],
        'content': data['content']
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route('/api/posts/<int:id>', methods=['DELETE'])
def delete_post(id):
    for i, post in enumerate(POSTS):
        if post['id'] == id:
            del POSTS[i]
            return jsonify({
                "message": f"Post with id {id} has been deleted successfully."
            }), 200
    return jsonify({
        "error": f"Post with id {id} not found."
    }), 404


@app.route('/api/posts/<int:id>', methods=['PUT'])
def update_post(id):
    data = request.get_json()
    for post in POSTS:
        if post['id'] == id:
            post['title'] = data.get('title', post['title'])
            post['content'] = data.get('content', post['content'])
            return jsonify({
                'id': post['id'],
                'title': post['title'],
                'content': post['content']
            }), 200
    return jsonify({
        "error": f"Post with id {id} not found."
    }), 404


@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_search = request.args.get('title', '').lower()
    content_search = request.args.get('content', '').lower()
    matching_posts = [
        post for post in POSTS
        if (title_search in post['title'].lower() if title_search else True) and
           (content_search in post['content'].lower() if content_search else True)
    ]
    return jsonify(matching_posts)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)