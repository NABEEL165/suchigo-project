

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_GET
from django.contrib import messages
from decimal import Decimal, InvalidOperation
from .models import CustomerWasteInfo, CustomerPickupDate, CustomerLocationHistory
from super_admin_dashboard.models import State, District, LocalBody, LocalBodyCalendar
from .utils import is_customer


# Role checking
class CustomerRoleRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 0


@login_required
def customer_dashboard(request):
    if request.user.role != 0:
        return redirect('authentication:login')
    return render(request, 'customer_dashboard.html')


@login_required
@user_passes_test(is_customer)
def waste_profile_list(request):
    profiles = CustomerWasteInfo.objects.filter(user=request.user)
    return render(request, "waste_profile_list.html", {"profiles": profiles})


@login_required
@user_passes_test(is_customer)
def waste_profile_detail(request, pk):
    info = get_object_or_404(CustomerWasteInfo, pk=pk, user=request.user)
    selected_dates = CustomerPickupDate.objects.filter(user=request.user).values_list("localbody_calendar__date", flat=True)

    # Get location history for this waste info
    location_history = CustomerLocationHistory.objects.filter(waste_info=info).order_by('-changed_at')[:5]

    return render(request, "waste_profile_detail.html", {
        "info": info,
        "selected_dates": selected_dates,
        "location_history": location_history,
    })


def validate_coordinates(latitude, longitude):
    """Validate latitude and longitude values"""
    try:
        if latitude and longitude:
            lat = Decimal(latitude)
            lng = Decimal(longitude)

            # Check valid range
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return lat, lng
    except (InvalidOperation, ValueError, TypeError):
        pass

    return None, None


@login_required
@user_passes_test(lambda u: u.role == 0)
def waste_profile_create(request):
    states = State.objects.all()
    ward_range = range(1, 16)
    bag_range = range(1, 11)

    if request.method == "POST":
        # Get and validate coordinates
        latitude_raw = request.POST.get("latitude")
        longitude_raw = request.POST.get("longitude")
        latitude, longitude = validate_coordinates(latitude_raw, longitude_raw)

        # Create waste info with location data
        info = CustomerWasteInfo.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            secondary_number=request.POST.get("secondary_number"),
            pickup_address=request.POST.get("pickup_address"),
            landmark=request.POST.get("landmark"),
            latitude=latitude,
            longitude=longitude,
            state_id=request.POST.get("state"),
            district_id=request.POST.get("district"),
            localbody_id=request.POST.get("localbody"),
            ward=request.POST.get("ward"),
            number_of_bags=request.POST.get("number_of_bags"),
            waste_type=request.POST.get("waste_type"),
            comments=request.POST.get("comments"),
            pincode=request.POST.get("pincode")
        )

        # Save location history if coordinates provided
        if latitude and longitude:
            CustomerLocationHistory.objects.create(
                waste_info=info,
                latitude=latitude,
                longitude=longitude,
                changed_by=request.user
            )
            messages.success(request, "Waste profile created with location tracking!")
        else:
            messages.warning(request, "Waste profile created without location data. Please update location later.")

        # Handle pickup date
        selected_date_id = request.POST.get("selected_date")
        if selected_date_id:
            try:
                cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
                CustomerPickupDate.objects.create(
                    user=request.user,
                    waste_info=info,
                    localbody_calendar=cal
                )
            except LocalBodyCalendar.DoesNotExist:
                messages.error(request, "Selected pickup date is invalid.")

        return render(request, "waste_success.html", {"info": info})

    return render(request, "waste_form.html", {
        "states": states,
        "ward_range": ward_range,
        "bag_range": bag_range,
        "selected_dates": [],
        "districts": [],
        "localbodies": [],
        "info": None,
    })


@login_required
@user_passes_test(lambda u: u.role == 0)
def waste_profile_update(request, pk):
    info = get_object_or_404(CustomerWasteInfo, pk=pk, user=request.user)
    states = State.objects.all()
    ward_range = range(1, 16)
    bag_range = range(1, 11)

    # Preload districts & localbodies for the selected state/district
    districts = District.objects.filter(state=info.state) if info.state else []
    localbodies = LocalBody.objects.filter(district=info.district) if info.district else []

    # Preload existing selected dates
    selected_dates = CustomerPickupDate.objects.filter(waste_info=info)

    if request.method == "POST":
        # Store old coordinates for comparison
        old_latitude = info.latitude
        old_longitude = info.longitude

        # Get and validate new coordinates
        latitude_raw = request.POST.get("latitude")
        longitude_raw = request.POST.get("longitude")
        new_latitude, new_longitude = validate_coordinates(latitude_raw, longitude_raw)

        # Update main waste info
        info.full_name = request.POST.get("full_name")
        info.secondary_number = request.POST.get("secondary_number")
        info.pickup_address = request.POST.get("pickup_address")
        info.landmark = request.POST.get("landmark")
        info.latitude = new_latitude
        info.longitude = new_longitude
        info.state_id = request.POST.get("state")
        info.district_id = request.POST.get("district")
        info.localbody_id = request.POST.get("localbody")
        info.ward = request.POST.get("ward")
        info.number_of_bags = request.POST.get("number_of_bags")
        info.waste_type = request.POST.get("waste_type")
        info.comments = request.POST.get("comments")
        info.pincode = request.POST.get("pincode")
        info.save()

        # Track location change if coordinates changed
        if new_latitude and new_longitude:
            if old_latitude != new_latitude or old_longitude != new_longitude:
                CustomerLocationHistory.objects.create(
                    waste_info=info,
                    latitude=new_latitude,
                    longitude=new_longitude,
                    changed_by=request.user
                )
                messages.success(request, "Waste profile and location updated successfully!")
            else:
                messages.success(request, "Waste profile updated successfully!")
        else:
            messages.warning(request, "Waste profile updated without location data.")

        # Handle pickup date update (replace old one with new if given)
        selected_date_id = request.POST.get("selected_date")
        if selected_date_id:
            try:
                cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
                # Remove old pickup dates for this profile
                CustomerPickupDate.objects.filter(waste_info=info).delete()
                # Create new pickup date
                CustomerPickupDate.objects.create(
                    user=request.user,
                    waste_info=info,
                    localbody_calendar=cal
                )
            except LocalBodyCalendar.DoesNotExist:
                messages.error(request, "Selected pickup date is invalid.")

        return redirect("customer:waste_profile_detail", pk=info.id)

    return render(request, "waste_form.html", {
        "states": states,
        "ward_range": ward_range,
        "bag_range": bag_range,
        "selected_dates": selected_dates,
        "districts": districts,
        "localbodies": localbodies,
        "info": info,
    })


@login_required
@user_passes_test(is_customer)
def waste_profile_delete(request, pk):
    info = get_object_or_404(CustomerWasteInfo, pk=pk, user=request.user)
    if request.method == "POST":
        info.delete()
        messages.success(request, "Waste profile deleted successfully!")
        return redirect("customer:waste_profile_list")
    return render(request, "waste_profile_delete.html", {"info": info})


@login_required
@user_passes_test(is_customer)
@require_GET
def get_available_dates(request, localbody_id):
    """Get available pickup dates for a local body"""
    all_dates = LocalBodyCalendar.objects.filter(localbody_id=localbody_id)
    data = []
    for d in all_dates:
        data.append({
            "id": d.id,
            "date": d.date.isoformat(),
            "title": "Available",
        })
    return JsonResponse(data, safe=False)


@login_required
@user_passes_test(is_customer)
@require_GET
def load_districts_customer(request, state_id):
    """Load districts based on selected state"""
    districts = District.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)


@login_required
@user_passes_test(is_customer)
@require_GET
def load_localbodies_customer(request, district_id):
    """Load local bodies based on selected district"""
    localbodies = LocalBody.objects.filter(district_id=district_id).values('id', 'name', 'body_type')
    return JsonResponse(list(localbodies), safe=False)


@login_required
@user_passes_test(is_customer)
def save_pickup_date(request):
    """Save or update pickup date"""
    if request.method == "POST":
        user = request.user
        date_id = request.POST.get("pickup_date")
        localbody_calendar = get_object_or_404(LocalBodyCalendar, pk=date_id)

        # Create or update
        pickup_date, created = CustomerPickupDate.objects.update_or_create(
            user=user,
            defaults={"localbody_calendar": localbody_calendar}
        )

        if created:
            messages.success(request, "Pickup date saved successfully!")
        else:
            messages.info(request, "Pickup date updated successfully!")

        return JsonResponse({"status": "success", "created": created})

    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)


@login_required
@user_passes_test(is_customer)
@require_GET
def validate_location(request):
    """
    API endpoint to validate coordinates from frontend
    Usage: GET /validate-location/?lat=10.5276&lng=76.2144
    """
    latitude = request.GET.get('lat')
    longitude = request.GET.get('lng')

    lat, lng = validate_coordinates(latitude, longitude)

    if lat and lng:
        return JsonResponse({
            "valid": True,
            "latitude": str(lat),
            "longitude": str(lng),
            "message": "Coordinates are valid"
        })
    else:
        return JsonResponse({
            "valid": False,
            "message": "Invalid coordinates. Latitude must be between -90 and 90, Longitude between -180 and 180."
        }, status=400)


@login_required
@user_passes_test(is_customer)
def location_history(request, pk):
    """
    View location change history for a waste profile
    """
    info = get_object_or_404(CustomerWasteInfo, pk=pk, user=request.user)
    history = CustomerLocationHistory.objects.filter(waste_info=info).order_by('-changed_at')

    return render(request, "location_history.html", {
        "info": info,
        "history": history
    })


@login_required
@user_passes_test(is_customer)
@require_GET
def get_location_by_address(request):
    """
    API endpoint for geocoding - convert address to coordinates
    This would typically call Google Geocoding API from backend
    For now, returns a placeholder response
    """
    address = request.GET.get('address')

    if not address:
        return JsonResponse({"error": "Address parameter is required"}, status=400)

    # TODO: Implement actual Google Geocoding API call here
    # For now, return placeholder
    return JsonResponse({
        "success": False,
        "message": "Geocoding should be done on frontend using Google Maps JavaScript API"
    })


@login_required
@user_passes_test(is_customer)
def export_locations(request):
    """
    Export all customer locations as JSON for mapping/analytics
    """
    profiles = CustomerWasteInfo.objects.filter(
        user=request.user,
        latitude__isnull=False,
        longitude__isnull=False
    ).values(
        'id',
        'full_name',
        'pickup_address',
        'latitude',
        'longitude',
        'waste_type',
        'status',
        'created_at'
    )

    return JsonResponse(list(profiles), safe=False)


