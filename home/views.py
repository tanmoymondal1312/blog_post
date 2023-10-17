from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth  import authenticate,  login, logout
from .models import *
from django.contrib.auth.decorators import login_required
from .models import BlogPost, Favorite
from django.shortcuts import get_object_or_404
from .forms import ProfileForm, BlogPostForm
from django.views.generic import UpdateView
from django.contrib import messages
from .forms import RatingForm,CommentForm


def blogs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    posts = BlogPost.objects.all()
    posts = BlogPost.objects.filter().order_by('-dateTime')
    favorite_blogs = Favorite.objects.filter(user=request.user).values_list('blog', flat=True)
    
    return render(request, "blog.html", {'posts': posts, 'favorite_blogs': favorite_blogs})

def blog_details(request, blog_id):
    blog = get_object_or_404(BlogPost, pk=blog_id)
    
    ratings = Rating.objects.filter(blog=blog)
    total_ratings = ratings.count()   
    if total_ratings > 0:
        average_rating = round(sum(rating.rating for rating in ratings) / total_ratings, 1)
    else:
        average_rating = 0.0
        
    comments = Comment.objects.filter(blog = blog)
    
        
    if request.method == 'POST':
        rating_form = RatingForm(request.POST)
        comment_form = CommentForm(request.POST)  # Assuming you have a CommentForm defined
        
        if rating_form.is_valid():
            rating = rating_form.save(commit=False)
            rating.blog = blog
            rating.user = request.user
            rating.save()
            return redirect('blog_details', blog_id=blog_id)
        
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.blog = blog
            comment.user = request.user
            comment.save()
            return redirect('blog_details', blog_id=blog_id)
    else:
        rating_form = RatingForm()
        comment_form = CommentForm()
    
    return render(request, 'blog_details.html', {
        'blog': blog,
        'rating_form': rating_form,
        'comment_form': comment_form,
        'average_rating': average_rating,
        'comments':comments,
    })

def Delete_Blog_Post(request, blog_id):
    

    posts = BlogPost.objects.get(id=blog_id)
    print(posts)
    posts.delete()
    return redirect('favorite_blogs')



def search(request):
    if request.method == "POST":
        searched = request.POST['searched']
        blogs = BlogPost.objects.filter(title__contains=searched)
        return render(request, "search.html", {'searched':searched, 'blogs':blogs})
    else:
        return render(request, "search.html", {})

@login_required(login_url = '/login')
def add_blogs(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but commit=False to set the category later
            blog_post = form.save(commit=False)
            
            # Set the category directly from the form
            category = form.cleaned_data['category']
            slug = form.cleaned_data['slug']
            blog_post.category = category
            blog_post.author = request.user
            blog_post.slug = slug
            
            blog_post.save()
            return redirect('blog')  # Replace 'success_page' with the actual URL name for the success page
    else:
        form = BlogPostForm()
    return render(request, 'add_blogs.html', {'form': form})

class UpdatePostView(UpdateView):
    model = BlogPost
    template_name = 'edit_blog_post.html'
    fields = ['title', 'slug', 'content', 'image']


def user_profile(request, myid):
    post = BlogPost.objects.filter(id=myid)
    return render(request, "user_profile.html", {'post':post})

def Profile(request):
    return render(request, "profile.html")

def edit_profile(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
    if request.method=="POST":
        form = ProfileForm(data=request.POST, files=request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            alert = True
            return render(request, "edit_profile.html", {'alert':alert})
    else:
        form=ProfileForm(instance=profile)
    return render(request, "edit_profile.html", {'form':form})


def Register(request):
    if request.method=="POST":  
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/register')
        
        user = User.objects.create_user(username, email, password1)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return render(request, 'login.html')   
    return render(request, "register.html")

def Login(request):
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect("/")
        else:
            messages.error(request, "Invalid Credentials")
        return render(request, 'blog.html')   
    return render(request, "login.html")

def Logout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('/login')

@login_required(login_url='/login')
def save_favorite(request, blog_id):
    post = BlogPost.objects.get(pk=blog_id)

    favorite = Favorite()
    favorite.user = request.user
    favorite.blog = post
    favorite.save()
    return redirect('blog')
    
    
    
@login_required(login_url='/login')
def favorite_blogs(request):
    favorite_posts = Favorite.objects.filter(user=request.user)
    return render(request, 'favorite_blogs.html', {'favorite_posts': favorite_posts})

def delete_from_fv(request,blog_id):
    posts = Favorite.objects.get(id=blog_id)
    print(posts)
    posts.delete()
    return redirect('favorite_blogs')