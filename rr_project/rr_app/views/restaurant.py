
from django.contrib.auth.decorators import login_required

from ..models import Reservation, Restaurant, Review, Customer
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from ..forms.restaurant import  ReservationForm, ReviewForm
from django.contrib import messages
from django import forms
from django.db.models import Avg, Count
from datetime import datetime, timedelta
from django.utils import timezone
from ..models import Cuisine, Tags

# @login_required
def dashboard_view(request):
    """User dashboard"""
    user = request.user
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).order_by('-avg_rating', '-created_at')[:6]

    context = {
        'user': user,
        'reservations': Reservation.objects.filter(user=user) if hasattr(user, 'reservations') else [],
        'restaurants': restaurants,
    }
    return render(request, 'rr_app/restaurant/dashboard/dashboard.html', context)

@login_required
def reservation_management_view(request):
    customer, created = Customer.objects.get_or_create(user=request.user)
    reservations = Reservation.objects.filter(customer=customer).order_by('-date')

    if request.method == 'POST':
        if 'cancel_reservation' in request.POST:
            reservation_id = request.POST.get('cancel_reservation')
            reason = request.POST.get('cancellation_reason', '').strip()

            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                restaurant_name = reservation.restaurant.name if reservation.restaurant else "Unknown Restaurant"
                reservation.status = 'CANCELLED'
                reservation.cancellation_reason = reason
                reservation.save()
                messages.success(request, f"Reservation at {restaurant_name} has been cancelled.")
            except Exception:
                messages.error(request, "Failed to cancel reservation. Please try again.")
            return redirect('rr_app:reservation_management')

        elif 'delete_reservation' in request.POST:
            reservation_id = request.POST.get('delete_reservation')
            try:
                reservation = get_object_or_404(Reservation, id=reservation_id, customer=customer)
                reservation.delete()
                messages.success(request, "Cancelled reservation has been deleted.")
            except Exception:
                messages.error(request, "Failed to delete reservation. Please try again.")
            return redirect('rr_app:reservation_management')

    context = {
        'reservations': reservations,
        'has_reservations': reservations.exists(),
    }
    return render(request, 'rr_app/reservation/reservation_list.html', context)




@login_required
def restaurant_detail_view(request, restaurant_id):
    """Restaurant detail page"""
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    reviews = Review.objects.filter(restaurant=restaurant)
    recent_reviews = reviews.filter(created_at__gte = timezone.now() - timedelta(days=30))
    avg_rating = reviews.aggregate(avg_rating=Avg('rating'))['avg_rating']
    review_form = None
    
    reserve_form = None

    if request.method == 'POST':
        reserve_form = ReservationForm(request.POST, restaurant=restaurant)
        if reserve_form.is_valid():
            try:
                customer = Customer.objects.filter(user=request.user).first()
                reservation = reserve_form.save(commit=False)
                reservation.customer = customer
                reservation.restaurant = restaurant
                reservation.save()

                messages.success(request, f'You will receive an email once your reservation has been confirmed')
                return redirect('rr_app:restaurant_detail', restaurant_id=restaurant.id)
            except Exception as e:
                messages.error(request, f'An error occured during reservation: {str(e)}')
    else:
        reserve_form = ReservationForm(initial={
            'name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email
        })


    context = {
        'restaurant': restaurant,
        'reviews': reviews,
        'recent_reviews': recent_reviews,
        'avg_rating': avg_rating,
        'review_form': review_form,
        'reserve_form': reserve_form,
    }
    return render(request, 'rr_app/restaurant/restaurant_detail.html', context)


def restaurants_view(request):
    restaurants = Restaurant.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).select_related().prefetch_related('cuisines', 'tags')
    
    # Get all cuisines and tags for filters
    cuisines = Cuisine.objects.all().order_by('name')
    tags = Tags.objects.all().order_by('tag')
    
    restaurant_list = [r.to_dict() for r in restaurants]
    context = {
        'restaurants': restaurant_list,
        'cuisines': cuisines,
        'tags': tags,
    }
    return render(request, 'rr_app/restaurant/restaurants.html', context)

