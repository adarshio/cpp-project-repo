from django.shortcuts import render,get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from house_rent_app.forms import UserRegistrationForm, HouseForm
from house_rent_app.models import UserProfile, House, Booking,Request
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count

from django.shortcuts import render
from .models import House
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import House, Request, Booking
from django.utils.dateparse import parse_date
# how to manage login required in class based views
# from django.contrib.auth.mixins import LoginRequiredMixin
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError


from export_to_csv_lib.exporter import export_queryset_to_csv




def s3_upload(file_path, object_name=None):

    bucket_name = "s3-bucket-x24220591" 
    if object_name is None:
        object_name = file_path.split('/')[-1]

    s3_client = boto3.client('s3', region_name="us-east-1")

    try:
        with open(file_path, "rb") as file_data:
            s3_client.upload_fileobj(file_data, bucket_name, object_name)
        print(f"Successfully uploaded {object_name} to {bucket_name}")
        return True

    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return False



def email_sns(subject, message, name, email, phone):
    
    full_message = f"""Property Enquiry :\n
        Sender Name: {name}\t
        Email: {email}\t
        Phone: {phone}\n
        Message: {message}\n
    """

    SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:637357743739:x24220591-sns"

    try:
        sns_client = boto3.client("sns", region_name="us-east-1")  
        
        response = sns_client.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=full_message,
            Subject=subject
        )
        
        print(f"Email sent successfully! Message ID: {response['MessageId']}")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False










#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

class SignupView(View):
    def get(self, request):
        return render(request, template_name='signup.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')
        user_type = request.POST.get('type')
        address = request.POST.get('address')
        city = request.POST.get('city')
        if user_type == 'True':
            user_type = True
        else:
            user_type = False

        if User.objects.filter(username=username).exists():
            return render(request, template_name='signup.html', context={'error': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, template_name='signup.html', context={'error': 'Email already exists.'})
        
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(username=username, email=email, password=password)
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()
            return redirect('login')

        return render(request, template_name='signup.html')


class LoginView(View):
    def get(self, request):
        return render(request, template_name='login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username == "admin" and password == "admin":
            # Get or create a real Django user for admin
            admin_user, created = User.objects.get_or_create(username="admin", is_superuser=True, is_staff=True)
            admin_user.set_password("admin")  # ensure password is set
            admin_user.save()

            user = authenticate(request, username="admin", password="admin")
            if user:
                login(request, user)
                return redirect("admin_home")

        user = authenticate(request, username=username, password=password)
        usertype = UserProfile.objects.filter(user=user).first()

        if user is not None and usertype and usertype.type is True:
            login(request, user)
            return redirect('owner_home')
        elif user is not None and usertype and usertype.type is False:
            login(request, user)
            return redirect('tenant_home')
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect("login")


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('login')
    
    def post(self, request):
        logout(request)
        return redirect('login')


def export_houses(request):
    queryset = House.objects.all()
    fields = ['id', 'title', 'description','rent','city']
    return export_queryset_to_csv(queryset, fields, filename="houses_export.csv")


class AdminHome(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        total_owners = UserProfile.objects.filter(type=True).count()
        total_tenants = UserProfile.objects.filter(type=False).count()
        total_houses = House.objects.all().count()
        total_available_houses = House.objects.filter(is_available=True).count()
        return render(request, template_name="admin_home.html", context={"total_owners":total_owners, "total_tenants":total_tenants, "total_houses":total_houses, "total_available_houses":total_available_houses})
    
    def post(self, request):
        return render(request, template_name="admin_home.html")

class AdminHouseList(LoginRequiredMixin, View):

    login_url = 'login'  
    redirect_field_name = 'next'
    
    def get(self, request):
        house_list = House.objects.all()
        print("--------------------> HOUSES : ",house_list.values())
        return render(request, template_name="admin_houses.html", context={"houses":house_list})
    
    def post(self, request):
        delete = request.POST.get("delete")
        edit = request.POST.get("edit")

        if edit is not None:
            house = House.objects.get(id=edit)
            return render(request, template_name="admin_edit_property.html", context={"house":house})
        
        if delete is not None:
            house = House.objects.get(id=delete)
            house.delete()
            return redirect('admin_houses')
        return render(request, template_name="admin_houses.html")

class AdminOwnerList(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        owners_list = UserProfile.objects.filter(type=True).annotate(house_count=Count('user__houses')).all()
        print("--------------------> OWNERS : ",owners_list.values())
        return render(request, template_name="admin_owners.html", context={"owners":owners_list})
    
    def post(self, request):
        delete = request.POST.get("delete")
        edit = request.POST.get("edit")

        # edit owner
        if edit is not None:
            print("EDIT : ",edit)
            owner = UserProfile.objects.get(user_id=edit)
            print("OWNER : ",owner)
            return render(request, template_name="admin_edit_owner.html", context={"owner":owner})

        if delete is not None:
            owner = User.objects.get(id=delete)
            owner.delete()
            return redirect('admin_owners') 
        return render(request, template_name="admin_owners.html")

class AdminTenantList(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'

    def get(self, request):
        tenants_list = UserProfile.objects.filter(type=False).all()
        cities = []
        for tenant in tenants_list:
            if tenant.city not in cities:
                cities.append(tenant.city)
        print("--------------------> TENANTS : ",tenants_list.values())
        print("--------------------> CITIES : ",cities)

        return render(request, template_name="admin_tenants.html", context={"tenants":tenants_list, "cities":cities})
    
    def post(self, request):
        delete = request.POST.get("delete")
        edit = request.POST.get("edit")

        if edit is not None:
            print("EDIT : ",edit)
            tenant = UserProfile.objects.get(user_id=edit)
            print("TENANT : ",tenant)
            return render(request, template_name="admin_edit_tenant.html", context={"tenant":tenant})

        if delete is not None:
            owner = User.objects.get(id=delete)
            owner.delete()
            return redirect('admin_tenants')
        return render(request, template_name="admin_tenants.html")

class AdminEditProprty(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request,template_name="admin_edit_property.html")
    
    def post(self, request):
        house_id = request.POST.get("house_id")
        title = request.POST.get("title")
        description = request.POST.get("description")
        rent = request.POST.get("rent")
        address = request.POST.get("address")
        city = request.POST.get("city")
        rooms = request.POST.get("rooms")
        image = request.FILES.get("image")
        is_furnished = request.POST.get("is_furnished")
        area = request.POST.get("area")
        if is_furnished == "on":
            is_furnished = True 
        else:
            is_furnished = False

        #edit house
        house = House.objects.get(id=house_id)
        house.title = title
        house.description = description
        house.rent = rent
        house.address = address
        house.city = city
        house.image = image
        house.area = area
        house.furnished = is_furnished
        house.no_of_rooms = rooms
        house.save()
        return redirect('admin_houses')

class AdminEditOwner(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, template_name="admin_edit_owner.html")
    
    def post(self, request):
        owner_id = request.POST.get("owner_id")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")

        owner = UserProfile.objects.get(id=owner_id)
        owner.user.username = username
        owner.user.email = email
        owner.phone_number = phone_number
        owner.address = address
        owner.city = city
        owner.user.save()
        owner.save()
        return redirect("admin_owners")

class AdminEditTenant(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, template_name="admin_edit_tenant")
    
    def post(self, request):
        tenant_id = request.POST.get("tenant_id")
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")

        tenant = UserProfile.objects.get(id=tenant_id)
        tenant.user.username = username
        tenant.user.email = email
        tenant.phone_number = phone_number
        tenant.address = address
        tenant.city = city
        tenant.user.save()
        tenant.save()
        return redirect("admin_tenants")


#<------------------ OWNER VIEWS ------------------>
import requests
from django.conf import settings
import requests
import json

class OwnerHome(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'next'

    def get(self, request):
        owner_houses = House.objects.filter(owner=request.user).all()

        # Collect rents
        rents = [house.rent for house in owner_houses]

        # Call Lambda to calculate total rent
        total_rent = self.get_total_rent_from_lambda(rents)

        return render(request, template_name="owner_home.html", context={
            "houses": owner_houses,
            "total_rent": total_rent
        })

    def post(self, request):
        delete = request.POST.get("delete")
        edit = request.POST.get("edit")

        if edit is not None:
            house = House.objects.get(id=edit)
            return render(request, template_name="owner_add_property.html", context={"house": house})

        if delete is not None:
            owner = House.objects.get(id=int(delete))
            owner.delete()
            return redirect('owner_home')

        return render(request, template_name="owner_home.html")

    # def get_total_rent_from_lambda(self, rents):
    #     """Calls Lambda function via API Gateway to calculate total rent"""
    #     try:
    #         response = requests.post(
    #             "https://k8qr82fcrg.execute-api.us-east-1.amazonaws.com/default/lambda-x24220591",
    #             json={"rents": rents},
    #             timeout=5
    #         )
    #         if response.status_code == 200:
    #             lambda_body = json.loads(response.json()['body'])  # <-- parse nested JSON string
    #             return lambda_body.get("total_rent", 0)
    #         else:
    #             print("Lambda Error Response:", response.text)
    #             return 0
    #     except Exception as e:
    #         print("Error calling Lambda:", e)
    #         return 0

    
    
    def get_total_rent_from_lambda(self, rents):
        """Calls Lambda function via API Gateway to calculate total rent"""
        try:
            response = requests.post(
                "https://0iqlrx5ax1.execute-api.us-east-1.amazonaws.com/default/lambda-x24220591",
                json={"rents": rents},
                timeout=5
            )
            if response.status_code == 200:
                # The response is already a JSON object, not a string
                lambda_body = response.json()
                
                # Check if it's the nested API Gateway format
                if 'body' in lambda_body:
                    # Parse the nested body if it exists
                    nested_body = json.loads(lambda_body['body'])
                    return nested_body.get("total_rent", 0)
                else:
                    # Direct response format
                    return lambda_body.get("total_rent", 0)
            else:
                print("Lambda Error Response:", response.text)
                return 0
        except Exception as e:
            print("Error calling Lambda:", e)
            return 0


class OwnerAddProperty(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request,template_name="owner_add_property.html")
    
    def post(self, request):
        title = request.POST.get("title")
        description = request.POST.get("description")
        rent = request.POST.get("rent")
        address = request.POST.get("address")
        city = request.POST.get("city")
        image = request.FILES.get("image")
        area = request.POST.get("area")
        is_furnished = request.POST.get("is_furnished")
        rooms = request.POST.get("rooms")

        house_id = request.POST.get("house_id")

        if is_furnished == "on":
            is_furnished = True 
        else:
            is_furnished = False

        if house_id is not None and len(house_id) > 0:
            edit_house = House.objects.get(id=house_id)
            edit_house.title = title
            edit_house.description = description
            edit_house.rent = rent
            edit_house.address = address
            edit_house.city = city
            edit_house.image = image
            edit_house.area = area
            edit_house.furnished = is_furnished
            edit_house.no_of_rooms = rooms
            edit_house.save()
            return redirect('owner_home')

        add_house = House.objects.create(
            title=title,
            description=description,
            rent=rent,
            address=address,
            city=city,
            image=image,
            area=area,
            owner=request.user,
            furnished=is_furnished,
            no_of_rooms=rooms
        )
        print("House Created Successfully")
        add_house.save()
        s3_upload(add_house.image.path, f"houses/{add_house.image.name}")
        return redirect('owner_home')
        
class OwnerInfo(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        owner_id = request.user.id
        owners_info = UserProfile.objects.filter(user_id=owner_id).first()
        print("--------------------> OWNERSsssssss : ",owners_info)
        return render(request, template_name="owner_info.html", context={"owner":owners_info})

    def post(self, request):
        owner_id = request.user.id
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")

        owner = UserProfile.objects.get(user_id=owner_id)
        owner.user.username = username
        owner.user.email = email
        owner.phone_number = phone_number
        owner.address = address
        owner.city = city
        owner.user.save()
        owner.save()
        return redirect("owner_home")


from rental_agreement_lib import generate_rental_agreement
import os
from django.core.mail import EmailMessage

class OwnerRequests(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = 'next'

    def get(self, request):
        owner_houses = House.objects.filter(owner=request.user)
        requests = Request.objects.filter(house__in=owner_houses)
        booking_dates = []

        for req in requests:
            booking = Booking.objects.filter(house=req.house, tenant=req.tenant).first()
            if booking:
                booking_dates.append({
                    'house': req.house,
                    'tenant': req.tenant,
                    'start_date': booking.start_date,
                    'end_date': booking.end_date
                })

        return render(request, "owner_requests.html", {"requests": requests, "booking_dates": booking_dates})

    # def post(self, request):
    #     accept = request.POST.get("accept")
    #     reject = request.POST.get("reject")
    #     req_id = request.POST.get("id")
        

    #     if accept is not None and len(accept) > 0: 
    #         req = Request.objects.get(id=accept)
    #         start_date = parse_date(request.POST.get("start_date"))
    #         end_date = parse_date(request.POST.get("end_date"))

    #         if not start_date or not end_date:
    #             return JsonResponse({"success": False, "message": "Invalid dates"})

    #         req.status = True
    #         req.save()

    #         Booking.objects.create( 
    #             house=req.house,
    #             tenant=req.tenant,
    #             start_date=start_date,
    #             end_date=end_date
    #         )

    #         req.house.is_available = False
    #         req.house.save()

    #         return redirect('owner_requests')

    #     elif reject is not None and len(reject) > 0:
    #         req = Request.objects.get(id=reject)
    #         req.delete()
    #         return redirect('owner_requests')
    
    def post(self, request):
        accept = request.POST.get("accept")
        reject = request.POST.get("reject")
    
        if accept is not None and len(accept) > 0:
            req = Request.objects.get(id=accept)
            start_date = parse_date(request.POST.get("start_date"))
            end_date = parse_date(request.POST.get("end_date"))
    
            if not start_date or not end_date:
                return JsonResponse({"success": False, "message": "Invalid dates"})
    
            # Update request status
            req.status = True
            req.save()
    
            # Create booking
            Booking.objects.create(
                house=req.house,
                tenant=req.tenant,
                start_date=start_date,
                end_date=end_date
            )
    
            # Mark house unavailable
            req.house.is_available = False
            req.house.save()
    
            # --------- Generate Rental Agreement PDF ----------
            file_name = f"agreement_{req.tenant.username}_{req.house.id}.pdf"
            output_path = os.path.join(settings.MEDIA_ROOT, file_name)
    
            pdf_path = generate_rental_agreement(
                tenant_name=req.tenant.username,
                tenant_email=req.tenant.email,
                start_date=start_date,
                end_date=end_date,
                output_path=output_path
            )
            
            # --------- Send Email with Attachment ----------
            email = EmailMessage(
                subject="Rental Agreement Confirmation",
                body="Your rental agreement has been generated. Please find the attachment.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[req.tenant.email],
            )
    
            email.attach_file(pdf_path)
            email.send()
    
            return redirect('owner_requests')
    
        elif reject is not None and len(reject) > 0:
            req = Request.objects.get(id=reject)
            req.delete()
            return redirect('owner_requests')


class OwnerChangePassword(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, "owner_info.html")
    
    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  
            messages.success(request, 'Your password is successfully updated!')
            return redirect('owner_info')

        return render(request, "owner_info.html")

#<------------------ TENANT VIEWS ------------------>

class TenantHome(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        houses = House.objects.filter(is_available=True)  
        return render(request, 'tenant_home.html', {'houses': houses})
    
    def post(self, request):
        return render(request, template_name="tenant_home.html")

class TenantRequests(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        requested_houses = Request.objects.filter(tenant=request.user).all()
        print("--------------------> REQUESTS : ",requested_houses.values())
        return render(request, 'tenant_requests.html', {'houses': requested_houses})
    
    def post(self, request):
        return render(request, template_name="tenant_requests.html")
    
class TenantInfo(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        tenant_id = request.user.id
        tenant_info = UserProfile.objects.filter(user_id=tenant_id).first()
        print("--------------------> TENANT : ",tenant_info)
        return render(request, template_name="tenant_info.html", context={"tenant":tenant_info})
    
    def post(self, request):
        tenant_id = request.user.id
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")
        address = request.POST.get("address")
        city = request.POST.get("city")

        tenant = UserProfile.objects.get(user_id=tenant_id)
        tenant.user.username = username
        tenant.user.email = email
        tenant.phone_number = phone_number
        tenant.address = address
        tenant.city = city
        tenant.user.save()
        tenant.save()
        return redirect("tenant_home")
    
class TenantPropDetails(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request, pk):
        house = get_object_or_404(House, pk=pk)

        # check if request already sent
        request_obj = Request.objects.filter(house=house, tenant=request.user).first()
        print("REQUEST OBJ : ",request_obj)
        return render(request, 'tenant_property_details.html', {'house': house, "request_obj": request_obj})

    def post(self, request, pk):
        tenant=request.user
        print("tenant: ",tenant)
        house = get_object_or_404(House, pk=pk)
        send_request = Request.objects.create(
            house=house,
            tenant=request.user,
            status=False
        )
        send_request.save()

        email_sns("New Request for House","A new request has been made for your house.",tenant.username, tenant.email, tenant.userprofile.phone_number)
        return redirect('tenant_home')

class TenantChangePassword(LoginRequiredMixin, View):
    login_url = 'login'  
    redirect_field_name = 'next'
    def get(self, request):
        return render(request, "tenant_info.html")
    
    def post(self, request):
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  
            messages.success(request, 'Your password is successfully updated!')
            return redirect('tenant_info')

        return render(request, "tenant_info.html")




