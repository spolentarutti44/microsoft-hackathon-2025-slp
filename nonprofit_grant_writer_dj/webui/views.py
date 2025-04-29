from django.shortcuts import render

# Serve the main form page
def index(request):
    return render(request, 'index.html')

# Serve the review/edit page
def review(request):
    return render(request, 'review.html') 