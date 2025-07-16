from django.shortcuts import render, redirect, get_object_or_404
from .models import Bus, Booking
from datetime import datetime,date
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.db.models import Q


def home(request):
    buses = Bus.objects.filter(date__gte=date.today()) 

    departure = request.GET.get('departure')
    arrival = request.GET.get('arrival')
    travel_date = request.GET.get('date')
    bus_type = request.GET.get('bus_type')
    max_price = request.GET.get('max_price')

    if departure:
        buses = buses.filter(source__icontains=departure)

    if arrival:
        buses = buses.filter(destination__icontains=arrival)

    if travel_date:
        buses = buses.filter(date=travel_date)

    if bus_type:
        buses = buses.filter(bus_type__iexact=bus_type)

    if max_price:
        try:
            buses = buses.filter(price__lte=float(max_price))
        except ValueError:
            pass  

    context = {
        'buses': buses
    }
    return render(request, 'home.html', context)

    return render(request, 'home.html', {'buses': buses})


def view_buses(request):
    buses = Bus.objects.filter(date__gte=date.today())
    return render(request, 'buses.html', {'buses': buses})



@login_required
def book_ticket(request, bus_id):
    bus = get_object_or_404(Bus, id=bus_id)

    if request.method == 'POST':
        date_input = request.POST.get('date')
        pickup = request.POST.get('pickup')
        drop = request.POST.get('drop')
        bus_type = request.POST.get('bus_type')
        seat_count = int(request.POST.get('seats'))
        travelers = []

        try:
            selected_date = datetime.strptime(date_input, '%Y-%m-%d').date()

        except ValueError:
            return render(request, 'book_ticket.html', {'bus': bus, 'error': 'Invalid date format'})

        for i in range(1, seat_count + 1):
            name = request.POST.get(f'traveler_name_{i}')
            seat_no = request.POST.get(f'seat_number_{i}')
            if name and seat_no:
                travelers.append({'name': name, 'seat_no': seat_no})

        bookings = []
        for traveler in travelers:
            booking = Booking.objects.create(
                user=request.user,
                bus=bus,
                passenger_name=traveler['name'],
                pickup=pickup,
                drop=drop,
                seat_number=traveler['seat_no'],
                bus_type=bus_type,
                date=selected_date
            )
            bookings.append(booking)

        bus.available_seats -= seat_count
        bus.save()

        context = {
            'bookings': bookings,
            'success_message': f"Congratulations! {seat_count} ticket(s) confirmed from {bus.source} to {bus.destination} on {selected_date}."
        }
        return render(request, 'booking_success.html', context)

    return render(request, 'book_ticket.html', {'bus': bus})

@login_required
def view_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'ticket.html', {'booking': booking})

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.bus.available_seats += booking.seats_booked
    booking.bus.save()
    booking.delete()
    return redirect('view_bookings')

def signup_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('home')
    return render(request, 'signup.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid login credentials.")
            return redirect('login')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def view_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('bus').order_by('-booking_date')
    return render(request, 'bookings.html', {'bookings': bookings})

def search_buses(request):
    if request.method == 'POST':
        source = request.POST.get('source')
        destination = request.POST.get('destination')
        travel_date = request.POST.get('date')

        buses = Bus.objects.filter(
            source__icontains=source,
            destination__icontains=destination,
            date=travel_date
        )
        return render(request, 'search_results.html', {'buses': buses})
    
    return render(request, 'search.html')

def ticket_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    context = {
        'passenger_name': booking.user.username,
        'bus_name': booking.bus.name,
        'source': booking.bus.source,
        'destination': booking.bus.destination,
        'bus_type': booking.bus.bus_type,
        'date': booking.date,
        'seat_number': booking.seat_number,
    }

    return render(request, 'booking_sucess.html', context)


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id,user=request.user)

    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Your booking has been canceled.')
        return redirect('view_bookings')

    return render(request, 'confirm_cancel.html', {'booking': booking})

def download_ticket(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "Bus Ticket Confirmation")

    p.setFont("Helvetica", 12)
    y = 750
    p.drawString(50, y, f"Passenger Name: {booking.passenger_name}")
    p.drawString(50, y - 20, f"Bus: {booking.bus}")
    p.drawString(50, y - 40, f"From: {booking.bus.source}")
    p.drawString(50, y - 60, f"To: {booking.bus.destination}")
    p.drawString(50, y - 80, f"Seat Number: {booking.seat_number}")
    p.drawString(50, y - 100, f"Bus Type: {booking.bus_type}")
    p.drawString(50, y - 120, f"Pickup Point: {booking.pickup}")
    p.drawString(50, y - 140, f"Drop Point: {booking.drop}")
    p.drawString(50, y - 160, f"Journey Date: {booking.date}")
    p.drawString(50, y - 180, f"Booking Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}")

    p.showPage()
    p.save()

    return response
