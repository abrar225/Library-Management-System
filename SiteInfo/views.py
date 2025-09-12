from SiteInfo.models import Contact
from django.conf import settings
from django.shortcuts import render, HttpResponse
import requests

# Create your views here.
def contact(request):
    if request.method == "POST":
        fn = request.POST["first-name"]
        ln = request.POST["last-name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        msg = request.POST["msg"]
        screenshot = request.FILES["SS"]

        recaptcha_response = request.POST.get("g-recaptcha-response")
        data = {
            "secret": settings.RECAPTCHA_SECRET_KEY,
            "response": recaptcha_response

        }
        verify_url = "https://www.google.com/recaptcha/api/siteverify"
        response = requests.post(verify_url, data=data)
        final_result = response.json()
        print(final_result)

        if final_result.get("success"):
            new_contact = Contact.objects.create(
                fn=fn,
                ln=ln,
                email=email,
                phone=phone,
                msg=msg,
                ss=screenshot
            )
            new_contact.save()
            return HttpResponse("<script>alert('Query Submitted!!');window.location.href='/SiteInfo/contact/';</script>")
        else:
            return HttpResponse(
                "<script>alert('Captcha Verification Failed!!');window.location.href='/SiteInfo/contact/';</script>")
    else:
        return render(request, "SiteInfo/contact.html")
