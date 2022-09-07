from flask import redirect, url_for, render_template, request, current_app, flash
from app import db
from app.main import main
from flask_login import current_user, login_required
from app.auth.utils.decorators import permission_required
from models import Post, User, Permission

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

# User Profile page
@main.route('/user_profile/<username>')
def user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    
    context = {
        'title': f'{user.username}\'s Profile Page',
        'user': user
    }
    return render_template('main/user_profile.html', **context)

# Follow route
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user', "warning")
        return redirect(url_for('main.user_profile', username=username))
    if current_user.username == username:
        flash('You cannot follow yourself', "warning")
        return redirect(url_for('main.user_profile', username=username))
    if current_user.is_following(user):
        flash('You are already following this user', "info")
        return redirect(url_for('main.user_profile', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {username}', 'success')
    return redirect(url_for('main.user_profile', username=username))

# Unfollow user route
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user', 'warning')
        return redirect(url_for('main.user_profile', username=username))
    if not current_user.is_following(user):
        flash("You are not following this user", "warning")
        return redirect(url_for('main.user_profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You have unfollowed {username}', 'info')
    return redirect(url_for('main.user_profile', username=username))

# Get Followers of a particular user
@main.route('/followers/<username>')
def followers(username):
    # Get user
    user = User.query.filter_by(username=username).first() 
    if user is None:
        flash('Invalid user', 'warning')
        return redirect(url_for('main.user_profile', username=username))
    followers = user.followers.all()
    follows = [{'user':item.follower, 'date_followed':item.date_followed} for item in followers]
    
    context = {
        'title': f'Followers of {username}',
        'follows':follows,
        'user':user,
        'followers':'followers'
    }
    return render_template('main/followers.html', **context)

# Get followed users
@main.route('/following/<username>')
def following(username):
    
    # Get user
    user = User.query.filter_by(username=username).first() 
    if user is None:
        flash('Invalid user', 'warning')
        return redirect(url_for('main.user_profile', username=username))
    followed = user.followed.all()
    follows = [{'user':item.followed, 'date_followed':item.date_followed} for item in followed]
    
    context = {
        'title': f'Users Followed by {username}',
        'follows':follows,
        'user':user,
        'following':'following'
    }
    return render_template('main/followers.html', **context)


        