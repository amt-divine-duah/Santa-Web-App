from flask import redirect, url_for, render_template, request, current_app
from app.main import main
from models import Post, User

# Homepage route
@main.route('/')
def home():
    
    context = {
        'title': 'Blog Page'
    }
    return render_template('main/index.html', **context)

# Blog page
@main.route('/blog')
def blog():
    
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).\
                paginate(page=page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'])
    posts = pagination.items
    recent_posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    context = {
        'title': 'Blog Page',
        'posts': posts,
        'pagination': pagination,
        'recent_posts': recent_posts,
    }
    return render_template('main/blog.html', **context)

# Get user posts
@main.route('/user_posts/<username>')
def user_posts(username):
    
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(author=user).\
                order_by(Post.timestamp.desc()).\
                paginate(page=page, per_page=current_app.config['BLOG_POSTS_PER_PAGE'])
    posts = pagination.items
    recent_posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    context = {
        'title': f'{user.username}\'s Posts',
        'posts': posts,
        'pagination': pagination,
        'recent_posts': recent_posts,
        'user': user,
    }
    return render_template('main/user_posts.html', **context)