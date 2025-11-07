# Mollie Payment Integration Setup Guide

## 🎯 Overview
This guide explains how to set up and test the Mollie payment integration for Mentora Premium membership.

## 📋 Prerequisites
- Mollie account (test or live)
- ngrok for local webhook testing
- Admin access to the application

## 🔧 Configuration

### 1. Environment Variables
Add to your `.env` file:
```bash
MOLLIE_API_KEY=test_dHar4XY7LxsDOtmnkVtjNVWXLSlXsM  # Test key
# MOLLIE_API_KEY=live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx  # Live key for production
```

### 2. Test Mode
The application is configured to run in test mode by default:
```python
MOLLIE_TEST_MODE = True
```

## 🧪 Testing Setup

### 1. Local Development with Webhooks
For testing webhooks locally, use ngrok:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com/

# Start ngrok tunnel
ngrok http 5002

# Note the HTTPS URL (e.g., https://abc123.ngrok.io)
```

### 2. Update Webhook URL
When testing, update the webhook URL in the payment creation:
```python
'webhookUrl': 'https://abc123.ngrok.io/membership/webhook'
```

## 🚀 Testing Flow

### 1. Admin Access
- Only admin users can access payment features during testing
- Check user role: `current_user.is_admin`

### 2. Payment Flow
1. **Upgrade Page**: `/membership/upgrade`
   - Shows pricing plans
   - Only accessible to admin users
   - Non-admin users see "Coming soon!" message

2. **Checkout**: `/membership/checkout`
   - Creates Mollie payment
   - Redirects to Mollie checkout page
   - Admin only during testing

3. **Callback**: `/membership/callback`
   - User returns after payment
   - Shows payment status
   - Redirects to appropriate page

4. **Webhook**: `/membership/webhook`
   - Mollie calls this endpoint
   - Activates premium membership
   - Generates QR code
   - Updates user status

### 3. Member Card
- **Card Page**: `/membership/card`
  - Shows digital membership card
  - Premium users only
  - Includes QR code for verification

## 💳 Payment Details

### Pricing
- **Amount**: €10.00 EUR
- **Period**: 1 month
- **Description**: "Mentora Premium - 1 month"

### Features Included
- Premium learning modules
- Digital membership card
- QR code verification
- Priority support
- Exclusive community access

## 🔒 Security Features

### Admin-Only Testing
```python
if not current_user.is_admin:
    flash('This feature is coming soon!', 'info')
    return redirect(url_for('index'))
```

### Payment Validation
- Webhook verifies payment status
- User ID validation
- Membership expiration handling

## 📱 QR Code Integration

### Automatic Generation
- QR codes generated automatically for premium users
- Stored in `static/qr_codes/`
- Verification URL: `https://mentora.nl/verify/{member_id}`

### Verification Page
- Public page for QR code scanning
- Shows member information
- Validates membership status

## 🐛 Troubleshooting

### Common Issues

1. **"This feature is coming soon!"**
   - User is not admin
   - Check user role in database

2. **Payment creation fails**
   - Check Mollie API key
   - Verify test mode settings
   - Check network connectivity

3. **Webhook not working**
   - Ensure ngrok is running
   - Check webhook URL in Mollie dashboard
   - Verify HTTPS URL (required by Mollie)

4. **QR code not generated**
   - Check file permissions
   - Verify static directory exists
   - Check qrcode package installation

### Debug Mode
Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Monitoring

### Payment Status
Check payment status in Mollie dashboard:
- Test payments: https://my.mollie.com/dashboard/test/payments
- Live payments: https://my.mollie.com/dashboard/payments

### Application Logs
Monitor application logs for:
- Payment creation
- Webhook calls
- Error messages
- User actions

## 🚀 Production Deployment

### 1. Switch to Live Mode
```python
MOLLIE_TEST_MODE = False
MOLLIE_API_KEY = 'live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
```

### 2. Update Webhook URL
```python
'webhookUrl': 'https://mentora.nl/membership/webhook'
```

### 3. Remove Admin Restrictions
Update routes to allow all users:
```python
# Remove this check for production
if not current_user.is_admin:
    abort(403)
```

### 4. SSL Certificate
Ensure HTTPS is enabled for webhook security.

## 📞 Support

For issues with:
- **Mollie API**: Check Mollie documentation
- **Application**: Check application logs
- **Webhooks**: Verify ngrok setup and URL configuration

## 🔗 Useful Links

- [Mollie API Documentation](https://docs.mollie.com/)
- [Mollie Test Cards](https://docs.mollie.com/payments/testing)
- [ngrok Documentation](https://ngrok.com/docs)
- [QR Code Generation](https://github.com/lincolnloop/python-qrcode)



