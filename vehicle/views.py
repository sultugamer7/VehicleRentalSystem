# Required imports
from django.shortcuts import render, HttpResponseRedirect, reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import *
from .DAL import *
import datetime
from datetime import date, timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.core.paginator import Paginator


# Create your views here.


# HOME
@require_http_methods(["GET", "POST"])
@login_required(login_url="login")
def index(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # SEARCH VEHICLES FOR SELECTED TIME
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = BookingForm(request.POST)
        # Get form fields
        from_date = datetime.datetime.strptime(
            request.POST["from_date"], '%Y-%m-%d')
        from_time = int(request.POST["from_time"])
        to_date = datetime.datetime.strptime(
            request.POST["to_date"], '%Y-%m-%d')
        to_time = int(request.POST["to_time"])
        # Ensure booking date & time is in future
        now = datetime.datetime.now()
        today = datetime.datetime.strptime(
            (str(now.strftime("%Y-%m-%d"))), "%Y-%m-%d")
        if from_date < today:
            messages.success(request, "Pick up date cannot be in past!")
            return render(request, "vehicle/index.html", {'form': form})
        if from_date == today:
            if from_time - now.hour < 1:
                messages.success(request, "Pick up time cannot be in past!")
                return render(request, "vehicle/index.html", {'form': form})
        # Ensure pick up date is not greater than return date
        if from_date > to_date:
            messages.success(
                request, "Pick up date cannot be greater than return date!")
            return render(request, "vehicle/index.html", {'form': form})
        # Ensure min booking time period is 5 hours
        if from_date == to_date:
            if to_time - from_time < 5:
                messages.success(
                    request, "Minimum booking time period is 5 hours!")
                return render(request, "vehicle/index.html", {'form': form})
        # Ensure max booking time period is 2 weeks
        if abs((to_date - from_date).days) > 14 or (abs((to_date - from_date).days) == 14 and to_time - from_time > 0):
            messages.success(
                request, "Maximum booking time period is 2 weeks!")
            return render(request, "vehicle/index.html", {'form': form})
        # Ensure user has not already booked for the selected time period
        try:
            bookings = get_user_bookings(request.user)
        except:
            bookings = ""
        if bookings != "":
            for booking in bookings:
                from_date1 = datetime.datetime.strptime(
                    str(booking.from_date), '%Y-%m-%d')
                to_date1 = datetime.datetime.strptime(
                    str(booking.to_date), '%Y-%m-%d')
                # Ensure time does not conflict on return date
                if to_date == from_date1:
                    from_time1 = int(str(booking.from_time)[0:2])
                    if from_time1 - to_time < 1:
                        messages.success(
                            request, f"Already booked for the selected time period or part of it!\nConsider checking your bookings.")
                        return render(request, "vehicle/index.html", {'form': form})
                # Ensure time does not conflict on pickup date
                elif from_date == to_date1:
                    to_time1 = int(str(booking.to_time)[0:2])
                    if from_time - to_time1 < 1:
                        messages.success(
                            request, f"Already booked for the selected time period or part of it!\nConsider checking your bookings.")
                        return render(request, "vehicle/index.html", {'form': form})
                # Ensure dates does not conflict
                elif not ((from_date < from_date1 and to_date < from_date1) or (from_date > to_date1 and to_date > to_date1)):
                    messages.success(
                        request, f"Already booked for the selected time period or part of it!\nConsider checking your bookings.")
                    return render(request, "vehicle/index.html", {'form': form})
        # Store important values in session
        request.session["from_date"] = str(from_date.date())
        request.session["from_time"] = str(from_time)
        request.session["to_date"] = str(to_date.date())
        request.session["to_time"] = str(to_time)
        request.session["today"] = str(today.date())
        # Go to search view
        return HttpResponseRedirect(reverse("search"))
    # DISPLAY BOOKING FORM
    else:
        # Clear sessions if exists
        try:
            request.session["from_date"] = ""
            request.session["from_time"] = ""
            request.session["to_date"] = ""
            request.session["to_time"] = ""
            request.session["today"] = ""
        except:
            pass
        form = BookingForm()
        return render(request, 'vehicle/index.html', {'form': form})


# REGISTER
@require_http_methods(["GET", "POST"])
def register_view(request):
    # REGISTER USER
    if request.method == "POST":
        # Create a form instance and populate it with data from the request
        form = RegisterForm(request.POST)
        # Get form fields
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        username = request.POST["username"]
        email = request.POST["email"]
        birth = request.POST["birth"]
        password = request.POST["password"]
        # Ensure form fields are not empty/unselected
        if not first_name:
            messages.success(request, "Must provide first name!")
            return render(request, "vehicle/register.html", {'form': form})
        if not last_name:
            messages.success(request, "Must provide last name!")
            return render(request, "vehicle/register.html", {'form': form})
        if not username:
            messages.success(request, "Must provide username!")
            return render(request, "vehicle/register.html", {'form': form})
        if not email:
            messages.success(request, "Must provide e-mail address!")
            return render(request, "vehicle/register.html", {'form': form})
        if not birth:
            messages.success(request, "Must provide birth date!")
            return render(request, "vehicle/register.html", {'form': form})
        if not password:
            messages.success(request, "Must provide password!")
            return render(request, "vehicle/register.html", {'form': form})
        # Ensure first name and last name are valid
        if not first_name.isalpha():
            messages.success(request, "Must provide a proper first name!")
            return render(request, "vehicle/register.html", {'form': form})
        if not last_name.isalpha():
            messages.success(request, "Must provide a proper last name!")
            return render(request, "vehicle/register.html", {'form': form})
        # Ensure username > 3 characters
        if len(username) < 4:
            messages.success(
                request, "Username must contain at least 4 characters!")
            return render(request, "vehicle/register.html", {'form': form})
        # Ensure password > 7 characters
        if len(password) < 8:
            messages.success(
                request, "Password must contain at least 8 characters!")
            return render(request, "vehicle/register.html", {'form': form})
        # Ensure email and username are unique
        user = get_username(username)
        if len(user) != 0:
            messages.success(request, "Username already exists!")
            return render(request, "vehicle/register.html", {'form': form})
        user = get_email(email)
        if len(user) != 0:
            messages.success(request, "E-mail address already exists!")
            return render(request, "vehicle/register.html", {'form': form})
        # If everything is fine, register & log user in
        user = add_user(first_name, last_name, username, email, password)
        user = authenticate(request, username=username, password=password)
        login(request, user)
        add_client(request.user, birth)
        # Send mail to the user
        subject = 'Registration Confirmation'
        message = f"""
Thank you for registering with us!
We hope you'll enjoy the services that we provide and we also hope that you'll enjoy booking with us and recommend us to your friends and family.

Sincerely,
Banger & Co.
        """
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [request.user.email, ]
        send_mail(subject, message, email_from, recipient_list)
        # Redirect to home page
        messages.success(request, "Account created!")
        return HttpResponseRedirect(reverse("index"))
    # DISPLAY REGISTER FORM
    else:
        # Render register.html with RegisterForm
        form = RegisterForm()
        return render(request, "vehicle/register.html", {'form': form})


# LOGIN
@require_http_methods(["GET", "POST"])
def login_view(request):
    # LOG USER IN
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request
        form = LoginForm(request.POST)
        # Get form fields
        username = request.POST["username"]
        password = request.POST["password"]
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        # Ensure if authentication is successful
        if user is None:
            messages.success(request, "Invalid username/password!")
            return render(request, 'vehicle/login.html', {'form': form})
        # Ensure user is not blacklisted
        if is_blacklisted(user):
            messages.success(request, "You're blacklisted!")
            return render(request, 'vehicle/login.html', {'form': form})
        # If authentication is successful, log user in
        login(request, user)
        # Redirect to home page
        return HttpResponseRedirect(reverse("index"))
    # DISPLAY LOGIN FORM
    else:
        # Render login.html with LoginForm
        form = LoginForm()
        return render(request, 'vehicle/login.html', {'form': form})


# LOGOUT
@require_http_methods(["GET"])
@login_required(login_url="login")
def logout_view(request):
    # LOG USER OUT
    logout(request)
    # Redirect to login page
    messages.success(request, "Logged out!")
    return HttpResponseRedirect(reverse("login"))


# SEARCH
@require_http_methods(["GET"])
@login_required(login_url="login")
def search_view(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # SEARCH VEHICLES
    # Get values from session or else raise error
    try:
        if request.session["from_date"] != "" and request.session["from_time"] != "" and request.session[
                "to_date"] != "" and request.session["to_time"] != "" and request.session["today"] != "":
            from_date = datetime.datetime.strptime(
                (request.session["from_date"]), "%Y-%m-%d")
            from_time = int(request.session["from_time"])
            to_date = datetime.datetime.strptime(
                (request.session["to_date"]), "%Y-%m-%d")
            to_time = int(request.session["to_time"])
            today = datetime.datetime.strptime(
                (request.session["today"]), "%Y-%m-%d")
        else:
            # Go to index page
            messages.success(request, "Error occurred!\nPlease try again")
            return HttpResponseRedirect(reverse("index"))
    except:
        # Go to index page
        messages.success(request, "Error occurred!\nPlease try again")
        return HttpResponseRedirect(reverse("index"))
    # Get user's birthdate and calculate age
    # Algorithm from - https://stackoverflow.com/questions/2217488/age-from-birthdate-in-python
    birthdate = datetime.datetime.strptime(
        (str(get_birthdate(request.user))), '%Y-%m-%d')
    age = (today - birthdate) // timedelta(days=365.2425)
    # Get booked vehicles
    bookings = get_bookings()
    # Add vehicles that are already booked for the time period in booking1 list
    booking1 = []
    for booking in bookings:
        from_date1 = datetime.datetime.strptime(
            str(booking.from_date), '%Y-%m-%d')
        to_date1 = datetime.datetime.strptime(str(booking.to_date), '%Y-%m-%d')
        from_time1 = str(booking.from_time)
        to_time1 = str(booking.to_time)
        index = from_time1.index(':')
        from_time1 = int(from_time1[0:index])
        index = to_time1.index(':')
        to_time1 = int(to_time1[0:index])
        if not ((from_date > to_date1 or from_date < from_date1) and (to_date < from_date1 or to_date > to_date1)):
            if from_date >= from_date1 or to_date <= to_date1:
                if from_date == to_date1:
                    if from_time - to_time1 < 1:
                        booking1.append(booking)
                elif to_date == from_date1:
                    if from_time1 - to_time < 1:
                        booking1.append(booking)
                else:
                    booking1.append(booking)
        elif from_date < from_date1 and to_date > to_date1:
            booking1.append(booking)
    # Get only small town cars if age < 25
    if age < 25:
        vehicles = get_small_vehicles(booking1)
    else:
        vehicles = get_vehicles(booking1)
    # Get vehicle cost multiplier
    multiplier = 1
    no_of_days = abs((to_date - from_date).days)
    if no_of_days == 0:
        # Get hours
        # Algorithm from - https://stackoverflow.com/questions/1345827/how-do-i-find-the-time-difference-between-two-datetime-objects-in-python
        hours = divmod((to_time - from_time), 3600)[1]
        if hours < 6:
            multiplier = 0.5
    else:
        multiplier = no_of_days
    # Store multiplier in session
    request.session["multiplier"] = multiplier
    # Multiply rental cost of vehicles by multiplier
    for vehicle in vehicles:
        vehicle.total_cost = str(float(int(vehicle.hire_cost) * multiplier)) + "0"
    # Show 10 vehicles per page
    paginator = Paginator(vehicles, 10)
    page = request.GET.get("page")
    vehicles_per_page = paginator.get_page(page)
    # Render search.html and display search results
    context = {"vehicles": vehicles_per_page}
    return render(request, 'vehicle/search.html', context)


# VEHICLE DETAILS
@require_http_methods(["GET"])
@login_required(login_url="login")
def vehicle_view(request, brand, model):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # Fetch vehicle or else raise error
    try:
        vehicle = get_vehicle(brand, model)
    except:
        # Raise 404
        raise Http404("Vehicle does not exist!")
    # Get values from session or else raise error
    try:
        if request.session["from_date"] != "" and request.session["from_time"] != "" and request.session[
                "to_date"] != "" and request.session["to_time"] != "" and request.session["multiplier"] != "":
            from_date = datetime.datetime.strptime(request.session["from_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            from_time = request.session["from_time"] + ":00"
            to_date = datetime.datetime.strptime(request.session["to_date"], "%Y-%m-%d").strftime("%d-%m-%Y")
            to_time = request.session["to_time"] + ":00"
            multiplier = request.session["multiplier"]
        else:
            # Go to index page
            messages.success(request, "Error occurred!\nPlease try again")
            return HttpResponseRedirect(reverse("index"))
    except:
        # Go to index page
        messages.success(request, "Error occurred!\nPlease try again")
        return HttpResponseRedirect(reverse("index"))
    # Calc total cost
    vehicle.total_cost = str(float(int(vehicle.hire_cost) * multiplier)) + "0"
    # Render vehicle.html with vehicle details
    context = {
        "vehicle": vehicle,
        "from_date": from_date,
        "from_time": from_time,
        "to_date": to_date,
        "to_time": to_time
    }
    return render(request, 'vehicle/vehicle.html', context)


# BOOK
@require_http_methods(["POST"])
@login_required(login_url="login")
def book_view(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # BOOK VEHICLE
    # Get values from session or else raise error
    try:
        if request.session["from_date"] != "" and request.session["from_time"] != "" and request.session[
                "to_date"] != "" and request.session["to_time"] != "" and request.session["multiplier"] != "":
            from_date = request.session["from_date"]
            from_time = request.session["from_time"] + ":00:00"
            to_date = request.session["to_date"]
            to_time = request.session["to_time"] + ":00:00"
            multiplier = request.session["multiplier"]
        else:
            # Go to index page
            messages.success(request, "Error occurred!\nPlease try again")
            return HttpResponseRedirect(reverse("index"))
    except:
        # Go to index page
        messages.success(request, "Error occurred!\nPlease try again")
        return HttpResponseRedirect(reverse("index"))
    # Get form's hidden input values
    brand = request.POST["brand"]
    model = request.POST["model"]
    # Get vehicle
    vehicle = get_vehicle(brand, model)
    # Calculate booking cost
    cost = float(vehicle.hire_cost) * multiplier
    # Add booking info to db
    book_vehicle(request.user, vehicle, from_date,
                 from_time, to_date, to_time, cost)
    # Convert dates in dd-mm-yyy
    from_date = datetime.datetime.strptime(
        from_date, '%Y-%m-%d').strftime('%d-%m-%Y')
    to_date = datetime.datetime.strptime(
        to_date, '%Y-%m-%d').strftime('%d-%m-%Y')
    # Get times in hh format
    index = from_time.index(':')
    from_time = from_time[0:index]
    index = to_time.index(':')
    to_time = to_time[0:index]
    # Send mail to the user
    subject = 'Booking Confirmation'
    message = f"""
Thank you for booking with us!
You've booked {brand} {model} from {from_time}:00 on {from_date} to {to_time}:00 on {to_date} 
Your total cost is: £{cost}
Please bring your photocard driving licence, 1 other form of identity from either a recent utility bill (within 3 months) or council tax statement, and this e-mail on the pickup date for confirmation.
We hope you'll enjoy your trip!

Sincerely,
Banger & Co.
    """
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.user.email, ]
    send_mail(subject, message, email_from, recipient_list)
    # Clear sessions
    request.session["from_date"] = ""
    request.session["from_time"] = ""
    request.session["to_date"] = ""
    request.session["to_time"] = ""
    request.session["today"] = ""
    request.session["multiplier"] = ""
    # Redirect to index page
    messages.success(request, "Booking done!")
    return HttpResponseRedirect(reverse("index"))


# BOOKINGS
@require_http_methods(["GET"])
@login_required(login_url="login")
def bookings_view(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # DISPLAY LOGGED IN USER's BOOKINGS
    # Get user's bookings
    try:
        bookings = get_user_bookings(request.user)
    except:
        bookings = ""
    # Show 10 bookings per page
    paginator = Paginator(bookings, 10)
    page = request.GET.get("page")
    bookings_per_page = paginator.get_page(page)
    # Render bookings.html
    context = {
        "bookings": bookings_per_page,
    }
    return render(request, 'vehicle/bookings.html', context)


# BOOKING DETAILS
@require_http_methods(["GET"])
@login_required(login_url="login")
def booking_details_view(request, booking_id):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # DISPLAY LOGGED IN USER's BOOKING DETAILS
    # Ensure booking_id exists
    if not booking_id:
        # Raise 404
        raise Http404("Booking does not exists!")
    # Get user's booking details
    booking = get_booking_details(booking_id)
    # Ensure booking is of logged in user
    if booking.user != request.user:
        raise Http404("Booking does not exists!")
    # Cancel booking functionality
    # Get pick up date
    from_date = datetime.datetime.strptime(
        str(booking.from_date), '%Y-%m-%d')
    # Get today's date
    today = date.today()
    today = datetime.datetime.strptime(str(today), "%Y-%m-%d")
    # Ensure booking is eligible to be cancelled
    eligible = False
    if abs((from_date - today).days) > 0 and booking.from_date > today.date():
        eligible = True
    # Extend return time functionality
    # Get booking time of the same vehicle on return date if vehicle is booked on the same day
    try:
        booking1 = get_vehicle_booking(booking.to_date, booking.vehicle)
    except:
        booking1 = ""
    # Generate a list of times to display on the extend time form
    times = []
    from_time = str(booking.to_time)
    index = from_time.index(':')
    from_time = int(from_time[0:index])
    if booking.from_date > today.date():
        try:
            to_time = str(booking1.from_time)
            index = to_time.index(':')
            to_time = int(to_time[0:index])
        except:
            # Ensure if user is eligible for late return (that is if he has already booked for more than 3 times in the past)
            # Set cout to 0
            count = 0
            # Get all user's bookings
            all_bookings = get_user_bookings(request.user)
            for all_booking in all_bookings:
                if all_booking.to_date < today.date():
                    count += 1
            if count > 3:
                to_time = 24
            else:
                to_time = 17
        for i in range(from_time + 1, to_time):
            times.append(str(i) + ":00")
    # Render booking details page
    return render(request, 'vehicle/booking_details.html', {'booking': booking, 'times': times, 'eligible': eligible})


# EXTEND TIME
@require_http_methods(["POST"])
@login_required(login_url="login")
def extend_view(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # EXTEND RETURN TIME
    # Get form data
    booking_id = request.POST["booking_id"]
    time = request.POST["time"]
    # Extend return time
    extend_time(booking_id, time)
    # Get new booking details
    booking_details = get_booking_details(booking_id)
    to_time = str(booking_details.to_time)
    index = to_time.index(':')
    to_time = to_time[0:index]
    # Convert dates in dd-mm-yyy
    to_date = datetime.datetime.strptime(
        str(booking_details.to_date), '%Y-%m-%d').strftime('%d-%m-%Y')
    # Send mail to the user
    subject = 'Return Time Extension Confirmation'
    message = f"""
Your return time for {booking_details.vehicle.brand} {booking_details.vehicle.model} has been extended till {to_time}:00 on {to_date}.
    """
    if int(to_time) > 18:
        message += f"""
        
Since you're our regular customer and returning the vehicle after the garage closes, be sure to return the vehicle to the garage on the return time and drop the keys through office letterbox.
"""
    message += """
We hope you'll enjoy your journey!

Sincerely,
Banger & Co.
    """
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.user.email, ]
    send_mail(subject, message, email_from, recipient_list)
    # Redirect back to booking details page
    messages.success(request, "Vehicle return time extended!")
    return HttpResponseRedirect(reverse("booking_details", args=(booking_id,)))


# CANCEL BOOKING
@require_http_methods(["POST"])
@login_required(login_url="login")
def cancel_booking_view(request):
    # Ensure user is not blacklisted
    if is_blacklisted(request.user):
        logout(request)
        messages.success(request, "You're blacklisted!")
        return HttpResponseRedirect(reverse("index"))
    # Get form fields
    booking_id = request.POST["booking_id"]
    password = request.POST["password"]
    # Ensure password is correct
    if not request.user.check_password(password):
        messages.success(request, "Incorrect password!")
        return HttpResponseRedirect(reverse("booking_details", args=(booking_id,)))
    # Get booking details
    booking_details = get_booking_details(booking_id)
    # Get pickup and return time in hh format
    from_time = str(booking_details.from_time)
    index = from_time.index(':')
    from_time = from_time[0:index]
    to_time = str(booking_details.to_time)
    index = to_time.index(':')
    to_time = to_time[0:index]
    # Convert dates in dd-mm-yyy
    from_date = datetime.datetime.strptime(
        str(booking_details.from_date), '%Y-%m-%d').strftime('%d-%m-%Y')
    to_date = datetime.datetime.strptime(
        str(booking_details.to_date), '%Y-%m-%d').strftime('%d-%m-%Y')
    # Cancel booking
    cancel_booking(booking_id)
    # Send mail to the user
    subject = 'Booking Cancelled'
    message = f"""
Your booking for {booking_details.vehicle.brand} {booking_details.vehicle.model} from {from_time}:00 on {from_date} to {to_time}:00 on {to_date} has been cancelled.

Sincerely,
Banger & Co.
    """
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [request.user.email, ]
    send_mail(subject, message, email_from, recipient_list)
    # Redirect to bookings page
    messages.success(request, "Booking cancelled!")
    return HttpResponseRedirect(reverse("bookings"))