# Email Setup — Lumiere

Booking & contact forms send automatic emails via **EmailJS** (free tier:
200 emails/month). Setup takes ~5 minutes.

## 1. Create an EmailJS account

Go to https://www.emailjs.com and sign up (free).

## 2. Add an Email Service

Dashboard → **Email Services** → **Add New Service**. Pick Gmail,
Outlook, or whatever you use. Connect your inbox. You'll get a **Service ID**
(looks like `service_xxxxxxx`).

## 3. Create the Booking Confirmation template

Dashboard → **Email Templates** → **Create New Template**.

**Settings tab:**
- **Subject**: `Your {{salon_name}} appointment is confirmed`
- **To Email**: `{{to_email}}`
- **From Name**: `{{salon_name}}`
- **Reply To**: your salon's email

**Content tab — paste the HTML from `email-template-booking.html`** (included
in this folder).

Save → copy the **Template ID** (looks like `template_xxxxxxx`).

## 4. Create the Contact Reply template (optional)

Same flow:
- **Subject**: `Thank you for contacting {{salon_name}}`
- **To Email**: `{{to_email}}`
- Paste `email-template-contact.html` as the body.
- Copy the **Template ID**.

## 5. Get your Public Key

Dashboard → **Account** → **General** → **Public Key** (looks like
`abcDEFghi123XYZ`).

## 6. Paste into `lumiere.html`

Open `lumiere.html` and find this block near the top of the `<script>`:

```js
const EMAIL_CONFIG = {
  publicKey:         'YOUR_PUBLIC_KEY',
  serviceId:         'YOUR_SERVICE_ID',
  bookingTemplateId: 'YOUR_BOOKING_TEMPLATE_ID',
  contactTemplateId: 'YOUR_CONTACT_TEMPLATE_ID',
  salonName:         'Lumiere Studio',
  salonEmail:        'hello@lumiere.studio',
  studioAddress:     '184 Mercer Street, SoHo, New York',
  studioPhone:       '(212) 555-0184'
};
```

Replace the four `YOUR_*` strings with your real keys. Save.

## 7. Test

Open `lumiere.html`, scroll to **Reserve your visit**, submit a booking
with your own email. Check your inbox.

## Behavior

- **If EmailJS is configured** → confirmation email sends automatically.
- **If not configured** → form still works, booking saves locally,
  success message reads "We will email you a confirmation shortly."

That's it.
