from django.shortcuts import render

# Render the home page
def index(request):
    return render(request, 'index.html')

# Render the review page
def review(request):
    return render(request, 'review.html') 