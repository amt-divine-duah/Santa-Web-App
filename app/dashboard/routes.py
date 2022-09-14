from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Post
from app.dashboard import dashboard
from app.auth.utils.decorators import admin_required
from app.dashboard.forms import PostForm, ProfileForm, AdminPostForm
from app.dashboard.utils import save_profile_image, save_header_image

@dashboard.route('/')
@login_required
def dashboard_home():
    
    context = {
        'title': 'Home',
        'submenu': 'Home'
        
    }
    return render_template('dashboard/dashboard.html', **context)

@dashboard.route('/landing_page')
def landingpage():
    
    context = {
        'title': 'Landing Page'
    }
    return render_template('dashboard/landingpage.html', **context)

# Profile Page
@dashboard.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    # user = User.query.filter_by(email=current_user.email).first()
    
    if form.validate_on_submit():
        if request.files.get('profile_pic'):
            picture_file = save_profile_image(request.files.get('profile_pic'))
            current_user.image = picture_file 
        if request.files.get('header_image'):
            header_image = save_header_image(request.files.get('header_image'))
            current_user.header = header_image 
        current_user.country =  request.form.get('country')
        current_user.username = form.username.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.middle_name = form.middle_name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.job_title = form.job_title.data
        current_user.mobile_no = form.mobile_no.data
        current_user.address = form.address.data
        # current_user.address_no = form.address_no.data
        db.session.add(current_user)
        db.session.commit()
        flash("Profile updated successfully", "success")
        return redirect(url_for('dashboard.profile'))
    
    form.username.data = current_user.username
    form.first_name.data = current_user.first_name
    form.last_name.data = current_user.last_name
    form.middle_name.data = current_user.middle_name
    form.email.data = current_user.email
    form.bio.data = current_user.bio
    form.job_title.data = current_user.job_title
    form.mobile_no.data = current_user.mobile_no
    form.address.data = current_user.address
    
    context = {
        'title': 'Profile Page',
        'form': form,
        'submenu': 'Settings'
    }
    return render_template('dashboard/profile.html', **context)

# Post blog route
@dashboard.route('/post_blog', methods=['GET', 'POST'])
@login_required
def post_blog():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, body_html=form.body.data, 
                    author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        flash("New blog post has been added successfully", "success")
        return redirect(url_for('dashboard.post_blog'))
    
    context = {
        'title': 'Post Blog',
        'form': form,
        'submenu': 'Blog'
    }
    return render_template('dashboard/post_blog.html', **context)

# View Posts
@dashboard.route('/view_posts')
@login_required
def view_posts():
    
    posts = Post.query.filter_by(author=current_user._get_current_object()).all()
    
    context = {
        'title': 'View Posts',
        'posts': posts,
        'submenu': 'Blog'
    }
    return render_template('dashboard/view_posts.html', **context)

# Update Blog Post
@dashboard.route('/update_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def update_blog(blog_id):
    
    form = PostForm()
    # Get the post
    post = Post.query.filter_by(id=blog_id).first_or_404()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.body_html = form.body.data
        db.session.commit()
        flash("Blog post has been updated", "success")
        return redirect(url_for('dashboard.view_posts'))
    
    form.title.data = post.title
    form.body.data = post.body_html
    context = {
        'title': 'Update Blog',
        'form': form,
        'submenu': 'Blog',
    }
    return render_template('dashboard/update_blog.html', **context)

# Delete Blog post
@dashboard.route('/delete_post<int:blog_id>', methods=['POST'])
@login_required
def delete_post(blog_id):
    post = Post.query.filter_by(id=blog_id).first_or_404()
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted", "info")
        return redirect(url_for('dashboard.view_posts'))

# Manage blog posts
@dashboard.route('/admin_view_posts')
@login_required
@admin_required
def admin_view_posts():
    
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    
    context = {
        'title': 'Admin View Posts',
        'posts': posts,
        'submenu': 'Settings'
    }
    return render_template('dashboard/admin_view_posts.html', **context)

# Admin Update Blog Post
@dashboard.route('/admin_update_blog/<int:blog_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_update_blog(blog_id):
    
    form = AdminPostForm()
    # Get the post
    post = Post.query.filter_by(id=blog_id).first_or_404()
    
    if form.validate_on_submit():
        post.title = form.title.data
        post.author.username = form.author.data
        post.body_html = form.body.data
        db.session.commit()
        flash("Blog post has been updated", "success")
        return redirect(url_for('dashboard.admin_view_posts'))
    
    form.title.data = post.title
    form.author.data = post.author.username
    form.body.data = post.body_html
    context = {
        'title': 'Admin Update Blog',
        'form': form,
        'submenu': 'Settings',
    }
    return render_template('dashboard/admin_update_blog.html', **context)

# Admin Delete Blog post
@dashboard.route('/admin_delete_post<int:blog_id>', methods=['POST'])
@login_required
@admin_required
def admin_delete_post(blog_id):
    post = Post.query.filter_by(id=blog_id).first_or_404()
    if request.method == "POST":
        db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted", "info")
        return redirect(url_for('dashboard.admin_view_posts'))
