from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils.html import escape
from mongoengine.errors import ValidationError
import json

from resourceFinder.medical_ai.contactModel import Contact
from resourceFinder.utility.email_sender import send_email


@csrf_exempt
def createContact(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method allowed"}, status=405)
    
    try:
        data = json.loads(request.body)
        full_name = data.get("full_name")
        email = data.get("email")
        content = data.get("content")

        if not all([full_name, email, content]):
            return JsonResponse({"error": "All fields are required"}, status=400)

        # Save contact
        contact = Contact(
            full_name=full_name,
            email=email,
            content=content
        )
        contact.save()

        # Confirmation email content (tailwind style: blue-500, black, white)
        thank_you_html = f"""
<div style="background-color:#ffffff; color:#000000; padding:20px; font-family:Arial, sans-serif;">
    <h2 style="color:#3B82F6;">Thank You for Reaching Out to MediConnect AI-RWA-CST </h2>
    <p>Dear <strong>{escape(full_name)}</strong>,</p>

    <p>Thank you for contacting MediConnectAI-RWA-CST. We truly appreciate you taking the time to share your thoughts with us.</p>
    
    <p>Your message has been received, and our dedicated support team is already reviewing it. We strive to respond as quickly and helpfully as possible, and you can expect a reply shortly.</p>

    <p>If your inquiry is urgent, please feel free to call our support line directly at <strong>+250 787 239 952</strong>.</p>

    <p style="margin-top:20px;">In the meantime, thank you again for trusting MediAI-RWA-CST. We’re here to support you.</p>

    <p style="margin-top:30px;">Warm regards,<br/>
    <strong>The MediConnect AI-RWA-CST Support Team</strong></p>
</div>
"""



        # Send confirmation email
        send_email(
            to_email=email,
            subject="Thank You for Contacting Mediconnect AI-RWA",
            message=thank_you_html  # Make sure your helper accepts 'message' or rename this to 'body'
        )

        return JsonResponse({"message": "Contact saved and email sent successfully."}, status=201)

    except (json.JSONDecodeError, ValidationError) as e:
        return JsonResponse({"error": f"Invalid input: {str(e)}"}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)
