# 🧪 Admin Membership Testing Panel

## 🎯 Overview
Скрытая админ-панель для тестирования функциональности членства. Доступна только администраторам через прямой URL.

## 🔗 Access URL
```
http://localhost:5002/admin/membership-test
```

## 🛡️ Security Features
- **Admin Only**: Доступ только для пользователей с ролью `admin`
- **Hidden**: Нет ссылок в UI, только прямой URL
- **Testing Mode**: Четкие предупреждения о тестовом режиме

## 📊 Features

### 1. Statistics Dashboard
- **Total Users**: Общее количество пользователей
- **Premium Users**: Количество премиум пользователей
- **Users with QR**: Количество пользователей с QR-кодами
- **Free Users**: Количество бесплатных пользователей

### 2. User Management
- **Recent Users**: Список последних 20 пользователей
- **Membership Status**: Текущий статус членства каждого пользователя
- **Member ID**: Уникальный ID участника (если есть)
- **QR Code Status**: Статус генерации QR-кода

### 3. Test Actions
- **Activate Premium**: Активировать премиум для пользователя
- **Deactivate Premium**: Деактивировать премиум
- **View Member Card**: Просмотр карты участника
- **Test Upgrade Page**: Тестирование страницы обновления
- **Test Mollie Payment**: Тестирование платежей

## 🎮 How to Use

### Step 1: Access the Panel
1. Login as admin user
2. Navigate to: `http://localhost:5002/admin/membership-test`

### Step 2: Test Premium Activation
1. Find a user in the table
2. Click "Activate Premium" button
3. User will get:
   - `membership_type = 'premium'`
   - `membership_expires = 30 days from now`
   - `member_id` generated (format: MNT-XXXXX)
   - QR code generated automatically

### Step 3: Test Member Card
1. After activating premium, click "View Card"
2. Opens member card page with QR code
3. QR code links to verification page

### Step 4: Test Payment Flow
1. Click "Test Mollie Payment" button
2. Creates test payment with Mollie
3. Redirects to Mollie checkout page
4. Test payment completion

## 🔧 Technical Details

### Routes Added
```python
@admin_bp.route('/membership-test')
@admin_bp.route('/membership-test/activate/<int:user_id>')
@admin_bp.route('/membership-test/deactivate/<int:user_id>')
```

### Functions
- `membership_test()`: Main testing panel
- `test_activate_premium()`: Activate premium for user
- `test_deactivate_premium()`: Deactivate premium for user

### Database Changes
- Updates `membership_type` to 'premium'
- Sets `membership_expires` to 30 days from now
- Generates `member_id` if not exists
- Creates QR code via `generate_member_qr()`

## 🧪 Testing Scenarios

### Scenario 1: New User Premium Activation
1. Find a user with `membership_type = 'free'`
2. Click "Activate Premium"
3. Verify:
   - Status changed to 'premium'
   - Member ID generated
   - QR code created
   - Expiration date set

### Scenario 2: Member Card Viewing
1. Activate premium for a user
2. Click "View Card"
3. Verify:
   - Card displays correctly
   - QR code shows
   - User info is correct
   - Download buttons work

### Scenario 3: Payment Testing
1. Click "Test Mollie Payment"
2. Complete test payment
3. Verify:
   - Payment processed
   - User upgraded to premium
   - QR code generated
   - Webhook received

### Scenario 4: Premium Deactivation
1. Find a premium user
2. Click "Deactivate"
3. Verify:
   - Status changed to 'free'
   - QR code removed
   - Expiration cleared

## 🚨 Important Notes

### Testing Only
- This panel is for testing purposes only
- Do not use with production user data
- All actions are reversible

### Data Safety
- No user data is deleted
- Only membership fields are modified
- Original user information preserved

### Security
- Admin-only access
- No public links
- Direct URL access only

## 🔗 Related URLs

### Admin Panel
- Main Panel: `/admin/membership-test`
- Activate Premium: `/admin/membership-test/activate/<user_id>`
- Deactivate Premium: `/admin/membership-test/deactivate/<user_id>`

### Membership Pages
- Upgrade Page: `/membership/upgrade`
- Member Card: `/membership/card`
- Payment Checkout: `/membership/checkout`
- Verification: `/membership/verify/<member_id>`

## 📋 Testing Checklist

- [ ] Admin can access testing panel
- [ ] Statistics display correctly
- [ ] User list shows recent users
- [ ] Premium activation works
- [ ] Member ID generation works
- [ ] QR code generation works
- [ ] Member card displays correctly
- [ ] Payment testing works
- [ ] Premium deactivation works
- [ ] All buttons and links functional

## 🐛 Troubleshooting

### Panel Not Accessible
- Check user role is 'admin'
- Verify URL is correct
- Check server is running

### Premium Activation Fails
- Check database connection
- Verify user exists
- Check QR code generation

### Member Card Not Displaying
- Verify user has premium status
- Check QR code file exists
- Verify member_id is set

## 📞 Support

For issues with the testing panel:
1. Check application logs
2. Verify database state
3. Test with different users
4. Contact development team

**Created**: 2025-10-02  
**Status**: Ready for testing  
**Access**: Admin only via direct URL



