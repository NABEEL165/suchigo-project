# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect,get_object_or_404
# from authentication.models import CustomUser
# from waste_collector_dashboard.models import WasteCollection
# from customer_dashboard.models import CustomerWasteInfo
# from django.contrib import messages


# @login_required
# def admin_home(request):
#     return render(request, 'super_admin_dashboard.html')



# @login_required
# def user_list_view(request):
#     customers = CustomUser.objects.filter(role=0)
#     collectors = CustomUser.objects.filter(role=1)
#     admins = CustomUser.objects.filter(role=2)

#     return render(request, 'user_list.html', {
#         'customers': customers,
#         'collectors': collectors,
#         'admins': admins,
#     })
# @login_required
# def view_customers(request):
#     customers = CustomUser.objects.filter(role=0)
#     return render(request, 'view_customers.html', {'customers': customers})

# @login_required
# def view_waste_collectors(request):
#     collectors = CustomUser.objects.filter(role=1)
#     total_collectors = collectors.count()
#     return render(request, 'view_collectors.html', {'collectors': collectors, 'total_collectors': total_collectors})
# @login_required
# def view_super_admin(request):
#     super_admin = CustomUser.objects.filter(role=2)
#     return render(request, "view_super_admin.html", {"super_admin":super_admin})

# @login_required
# def view_admins(request):
#     admins = CustomUser.objects.filter(role=3)
#     return render(request, "view_admins.html", {"admins":admins})

# # \\\\\\\\\\\\\\\\\\\\\\\\\\\ user view //////////////////////

# from .forms import UserForm

# @login_required
# def user_list(request):
#     users = CustomUser.objects.all()
#     return render(request, "users_list.html", {"users": users})





# @login_required
# def user_create(request):
#     if request.method == 'POST':
#         form = UserForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Encrypt password before saving
#                 user.set_password(password)
#             else:  # Default password if none provided
#                 user.set_password("default123")
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm()
#     return render(request, 'user_form.html', {'form': form})

# # Update User
# @login_required
# def user_update(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == 'POST':
#         form = UserForm(request.POST, instance=user)
#         if form.is_valid():
#             user = form.save(commit=False)
#             password = form.cleaned_data.get('password')
#             if password:  # Reset password if admin entered new one
#                 user.set_password(password)
#             user.save()
#             return redirect('super_admin_dashboard:users_list')
#     else:
#         form = UserForm(instance=user)
#     return render(request, 'user_form.html', {'form': form, 'user': user})






# # Delete user
# @login_required
# def user_delete(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         user.delete()
#         messages.success(request, "User deleted successfully")
#         return redirect("super_admin_dashboard:users_list")
#     return render(request, "user_confirm_delete.html", {"user": user})



# from django.shortcuts import render
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser

# @login_required
# def view_customer_wasteinfo(request):
#     # Fetch all customer waste profiles with related fields
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         'state', 'district', 'localbody', 'assigned_collector', 'user'
#     ).all()

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     # Map waste_info_id → pickup date
#     pickup_dates = {}
#     pickups = CustomerPickupDate.objects.select_related('localbody_calendar', 'waste_info').all()
#     for pickup in pickups:
#         if pickup.waste_info:
#             pickup_dates[pickup.waste_info.id] = pickup.localbody_calendar.date

#     return render(request, 'view_customer_wasteinfo.html', {
#         'waste_infos': waste_infos,
#         'collectors': collectors,
#         'pickup_dates': pickup_dates,
#     })

# # Assign a waste collector to a CustomerWasteInfo entry
# @login_required
# def assign_waste_collector(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)
#     if request.method == 'POST':
#         collector_id = request.POST.get('collector')
#         collector = get_object_or_404(CustomUser, pk=collector_id, role=1)
#         waste_info.assigned_collector = collector
#         waste_info.save()
#         messages.success(request, "Assigned to collector successfully.")
#         return redirect('super_admin_dashboard:view_customer_waste_info')
#     collectors = CustomUser.objects.filter(role=1)
#     return render(request, 'assign_waste_collector.html', {
#         'waste_info': waste_info,
#         'collectors': collectors,
#     })


# #waste collector collect details from customer

# @login_required
# def view_collected_data(request):
#     all_data = WasteCollection.objects.all()
#     return render(request, 'view_collected_data.html', {
#         'all_data': all_data
#     })


# # ////// MAP_ROLE
# @login_required
# def map_role(request, user_id):
#     user = get_object_or_404(CustomUser, id=user_id)
#     if request.method == "POST":
#         new_role = request.POST.get("role")
#         if new_role is not None:
#             try:
#                 new_role = int(new_role)  # Convert string to int
#                 if new_role in dict(CustomUser.ROLE_CHOICES).keys():
#                     user.role = new_role
#                     user.save()
#                     return redirect("super_admin_dashboard:users_list")
#             except ValueError:
#                 pass  # Ignore invalid input
#     return render(request, "map_role.html", {"user": user, "roles": CustomUser.ROLE_CHOICES})







# # ////////////////////////////      CALENDAR SET UP     ///////////////////////////////////


# import json
# from datetime import date, datetime, timedelta

# from django.shortcuts import render, get_object_or_404, redirect
# from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest
# from django.views.decorators.http import require_POST, require_GET
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.dateparse import parse_date

# from .models import State, District, LocalBody, LocalBodyCalendar
# from .utils import is_super_admin





# @login_required
# @user_passes_test(is_super_admin)
# def calendar_view(request):
#     """Main page where admin picks state/district/localbody and sees FullCalendar."""
#     states = State.objects.all().order_by("name")
#     return render(request, "calendar.html", {"states": states})


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_districts(request, state_id):
#     districts = District.objects.filter(state_id=state_id).values("id", "name")
#     return JsonResponse(list(districts), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def load_localbodies(request, district_id):
#     lbs = LocalBody.objects.filter(district_id=district_id).values("id", "name", "body_type")
#     return JsonResponse(list(lbs), safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_GET
# def get_calendar_dates(request, localbody_id):
#     events = LocalBodyCalendar.objects.filter(localbody_id=localbody_id).values("id", "date")
#     # FullCalendar expects events with at least id and start
#     data = [{"id": e["id"], "title": "Assigned", "start": e["date"].isoformat(), "color": "green"} for e in events]
#     return JsonResponse(data, safe=False)


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def create_calendar_date(request, localbody_id):
#     """Create one date or range. Expects 'date' in YYYY-MM-DD or 'start' & 'end' for ranges."""
#     lb = get_object_or_404(LocalBody, pk=localbody_id)

#     # support single-date or start/end
#     start = request.POST.get("start")
#     end = request.POST.get("end")
#     single = request.POST.get("date")

#     created = []
#     if single:
#         d = parse_date(single)
#         if not d:
#             return HttpResponseBadRequest("Invalid date")
#         entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=d)
#         if created_flag:
#             created.append({"id": entry.id, "date": entry.date.isoformat()})
#         return JsonResponse({"status": "created", "created": created})

#     if start and end:
#         s = parse_date(start)
#         e = parse_date(end)
#         if not s or not e:
#             return HttpResponseBadRequest("Invalid start/end")
#         cur = s
#         while cur <= e:
#             entry, created_flag = LocalBodyCalendar.objects.get_or_create(localbody=lb, date=cur)
#             if created_flag:
#                 created.append({"id": entry.id, "date": entry.date.isoformat()})
#             cur += timedelta(days=1)
#         return JsonResponse({"status": "created_range", "created": created})

#     return HttpResponseBadRequest("Provide 'date' or 'start' and 'end'.")


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def update_calendar_date(request, pk):
#     """Change date for an existing LocalBodyCalendar entry. Expect 'new_date' YYYY-MM-DD"""
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     new_date_raw = request.POST.get("new_date")
#     if not new_date_raw:
#         return HttpResponseBadRequest("Missing new_date")
#     new_date = parse_date(new_date_raw.split("T")[0])
#     if not new_date:
#         return HttpResponseBadRequest("Invalid date")
#     # prevent duplicates: if another entry exists for that localbody on same date -> reject
#     exists = LocalBodyCalendar.objects.filter(localbody=entry.localbody, date=new_date).exclude(pk=entry.pk).exists()
#     if exists:
#         return JsonResponse({"status": "conflict", "message": "Date already assigned"}, status=409)
#     entry.date = new_date
#     entry.save()
#     return JsonResponse({"status": "updated", "id": entry.id, "date": entry.date.isoformat()})


# @login_required
# @user_passes_test(is_super_admin)
# @require_POST
# def delete_calendar_date(request, pk):
#     entry = get_object_or_404(LocalBodyCalendar, pk=pk)
#     entry.delete()
#     return JsonResponse({"status": "deleted", "id": pk})






# # /////////////// super admin create waste oder


# from django.contrib import messages
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from customer_dashboard.models import CustomerWasteInfo, CustomerPickupDate
# from authentication.models import CustomUser
# from super_admin_dashboard.models import State, District, LocalBody
# @login_required
# def create_waste_profile(request):
#     if request.method == "POST":
#         contact_number = request.POST.get("contact_number")

#         # Step 1: Check if customer exists
#         try:
#             customer = CustomUser.objects.get(contact_number=contact_number, role=0)
#         except CustomUser.DoesNotExist:
#             messages.error(request, "No registered customer found with this contact number.")
#             return redirect("super_admin_dashboard:create_waste_profile")

#         # Step 2: Collect waste info details from form
#         full_name = request.POST.get("full_name")
#         secondary_number = request.POST.get("secondary_number")
#         pickup_address = request.POST.get("pickup_address")
#         landmark = request.POST.get("landmark")
#         pincode = request.POST.get("pincode")
#         state_id = request.POST.get("state")
#         district_id = request.POST.get("district")
#         localbody_id = request.POST.get("localbody")
#         waste_type = request.POST.get("waste_type")
#         number_of_bags = request.POST.get("number_of_bags")
#         ward = request.POST.get("ward")
#         selected_date_id = request.POST.get("selected_date")  # calendar selected date

#         # Step 3: Create Waste Profile
#         waste_info = CustomerWasteInfo.objects.create(
#             user=customer,
#             full_name=full_name,
#             secondary_number=secondary_number,
#             pickup_address=pickup_address,
#             landmark=landmark,
#             pincode=pincode,
#             state_id=state_id,
#             district_id=district_id,
#             localbody_id=localbody_id,
#             waste_type=waste_type,
#             number_of_bags=number_of_bags,
#             ward=ward
#         )

#         # Step 4: Save pickup date if given
#         if selected_date_id:
#             try:
#                 cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                 CustomerPickupDate.objects.create(
#                     user=customer,
#                     waste_info=waste_info,
#                     localbody_calendar=cal
#                 )
#             except LocalBodyCalendar.DoesNotExist:
#                 messages.warning(request, "Invalid pickup date selected.")

#         messages.success(request, f"Waste profile created for {customer.first_name}")
#         return redirect("super_admin_dashboard:view_customer_waste_info")

#     # GET request
#     states = State.objects.all()
#     ward_range = range(1, 16)  # Wards 1–15
#     bag_range = range(1, 11)   # Bags 1–10

#     return render(request, "superadmin_waste_form.html", {
#         "states": states,
#         "ward_range": ward_range,
#         "bag_range": bag_range,
#     })




# from .forms import WasteProfileForm  # we'll create this form



# @login_required
# def view_waste_profile(request, pk):
#     waste_info = get_object_or_404(
#         CustomerWasteInfo.objects.select_related(
#             "user", "state", "district", "localbody", "assigned_collector"
#         ),
#         pk=pk
#     )

#     # pickup dates for this profile
#     pickup_dates = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     return render(request, "superadmin_view_waste.html", {
#         "info": waste_info,
#         "pickup_dates": pickup_dates,
#     })



# @login_required
# def edit_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     existing_pickups = waste_info.customerpickupdate_set.select_related("localbody_calendar")

#     if request.method == "POST":
#         form = WasteProfileForm(request.POST, instance=waste_info)
#         if form.is_valid():
#             waste_info = form.save()

#             selected_date_id = request.POST.get("selected_date")
#             if selected_date_id:
#                 try:
#                     cal = LocalBodyCalendar.objects.get(pk=int(selected_date_id))
#                     CustomerPickupDate.objects.update_or_create(
#                         waste_info=waste_info,
#                         user=waste_info.user,
#                         defaults={"localbody_calendar": cal}
#                     )
#                 except LocalBodyCalendar.DoesNotExist:
#                     messages.warning(request, "⚠️ Invalid pickup date selected.")

#             messages.success(request, "✅ Waste profile updated successfully.")
#             return redirect("super_admin_dashboard:waste_info_list")
#     else:
#         form = WasteProfileForm(instance=waste_info)

#     available_dates = LocalBodyCalendar.objects.filter(localbody=waste_info.localbody).order_by("date")
#     districts = District.objects.all()
#     localbodies = LocalBody.objects.filter(district=waste_info.district)

#     return render(request, "superadmin_edit_waste.html", {
#         "form": form,
#         "info": waste_info,
#         "existing_pickups": existing_pickups,
#         "available_dates": available_dates,
#         "districts": districts,
#         "localbodies": localbodies
#     })



# @login_required
# def delete_waste_profile(request, pk):
#     waste_info = get_object_or_404(CustomerWasteInfo, pk=pk)

#     if request.method == "POST":
#         waste_info.delete()
#         messages.success(request, "🗑️ Waste profile deleted successfully.")
#         return redirect("super_admin_dashboard:waste_info_list")  # ✅ updated

#     return render(request, "superadmin_confirm_delete.html", {
#         "info": waste_info
#     })


# from django.core.paginator import Paginator
# from django.db.models import Q

# @login_required
# def waste_info_list(request):
#     search_query = request.GET.get("q", "")   # search input
#     page_number = request.GET.get("page", 1)  # current page

#     # Fetch all customer waste profiles
#     waste_infos = CustomerWasteInfo.objects.select_related(
#         "state", "district", "localbody", "assigned_collector", "user"
#     ).prefetch_related("customerpickupdate_set__localbody_calendar")

#     # ✅ Search filter (name / phone / address)
#     if search_query:
#         waste_infos = waste_infos.filter(
#             Q(user__first_name__icontains=search_query) |
#             Q(user__last_name__icontains=search_query) |
#             Q(user__contact_number__icontains=search_query) |
#             Q(pickup_address__icontains=search_query)
#         )

#     # ✅ Pagination (10 profiles per page)
#     paginator = Paginator(waste_infos.order_by("-id"), 10)
#     page_obj = paginator.get_page(page_number)

#     # Fetch all collectors
#     collectors = CustomUser.objects.filter(role=1)

#     return render(request, "waste_info_list.html", {
#         "page_obj": page_obj,
#         "collectors": collectors,
#         "search_query": search_query,
#     })
