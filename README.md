# Shop Management System

A comprehensive Django-based shop management system with advanced features for transaction management, financial analysis, and reporting.

## 🚀 Features

### ✅ **Delete Functionality**
- **Hover Effects**: Transaction logs slide left on hover, revealing delete button
- **Confirmation Dialog**: User-friendly confirmation before deletion
- **Reverse Transaction Logic**: Automatically reverses financial effects when deleting
- **Real-time Updates**: Holdings and balances update immediately after deletion

### ✅ **Advanced Analytics & Charts**
- **Monthly Reports**: Daily trend analysis with line charts
- **Yearly Reports**: Monthly trend analysis with line charts
- **Payment Mode Analysis**: Separate tracking for GPay and Cash transactions
- **Interactive Charts**: Beautiful Chart.js visualizations
- **Comprehensive Coverage**: Sales and bills analysis for all areas

### ✅ **PDF Report Generation**
- **Monthly PDF Reports**: Complete transaction summaries
- **Yearly PDF Reports**: Annual financial summaries
- **Professional Formatting**: Clean, structured PDF output
- **Download Functionality**: One-click PDF downloads

### ✅ **Transaction Management**
- **Sales Tracking**: GPay and Cash sales with date tracking
- **Bill Management**: Multiple bill categories (Restocking, Rent, EB Bills, etc.)
- **Credit System**: Advanced credit/lending management
- **Real-time Holdings**: Live updates of GPay, Cash, and Credit balances

## 🛠️ Technical Implementation

### **Backend Features**
- **Django 5.2+**: Modern web framework
- **SQLite Database**: Lightweight, file-based database
- **ReportLab**: Professional PDF generation
- **Chart.js**: Interactive data visualization
- **AJAX Integration**: Seamless delete operations

### **Frontend Features**
- **Tailwind CSS**: Modern, responsive design
- **JavaScript**: Dynamic interactions and chart rendering
- **CSRF Protection**: Secure form handling
- **Responsive Design**: Works on all devices

### **Security Features**
- **User Authentication**: Login/signup system
- **CSRF Protection**: Secure form submissions
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Graceful error management

## 📦 Dependencies

```txt
Django>=5.2,<6.0
gunicorn
whitenoise
psycopg2-binary
reportlab
```

## 🚀 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd management
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open browser to `http://localhost:8000`
   - Sign up or log in to start using the system

## 📊 Usage Guide

### **Adding Transactions**
1. **Sales**: Navigate to Sales page, enter GPay/Cash amounts and date
2. **Bills**: Navigate to Bills page, select categories and payment modes
3. **Credits**: Navigate to Credits page, manage lending/receiving

### **Deleting Transactions**
1. **Hover** over any transaction log
2. **Click** the red "Delete" button that appears
3. **Confirm** the deletion in the dialog
4. **Watch** as holdings update automatically

### **Viewing Reports**
1. **Monthly Reports**: Enter month/year, view charts and download PDF
2. **Yearly Reports**: Enter year, view monthly trends and download PDF
3. **Search**: Find transactions by date

### **Chart Analysis**
- **Sales Charts**: Daily/monthly GPay vs Cash sales trends
- **Bills Charts**: Daily/monthly GPay vs Cash bills trends
- **Interactive**: Hover over chart points for details
- **Responsive**: Charts adapt to screen size

## 🔧 API Endpoints

### **Delete Operations**
- `POST /delete_transaction/<id>/` - Delete transaction
- `POST /delete_credit_log/<id>/` - Delete credit log

### **Report Operations**
- `GET /monthly_report/?download=pdf` - Download monthly PDF
- `GET /yearly_report/?download=pdf` - Download yearly PDF

## 🧪 Testing

Run the feature test script to verify all functionality:

```bash
python test_features.py
```

This will test:
- ✅ Model functionality
- ✅ Transaction operations
- ✅ Credit management
- ✅ Chart data generation
- ✅ PDF generation
- ✅ Delete operations

## 📁 Project Structure

```
management/
├── accounts/
│   ├── models.py          # Data models
│   ├── views.py           # Business logic
│   ├── urls.py            # URL routing
│   ├── forms.py           # Form definitions
│   └── templates/         # HTML templates
├── management/
│   ├── settings.py        # Django settings
│   └── urls.py           # Main URL config
├── requirements.txt       # Dependencies
├── test_features.py      # Feature testing
└── README.md            # This file
```

## 🎯 Key Features Summary

| Feature | Status | Description |
|---------|--------|-------------|
| Delete Transactions | ✅ | Hover effects, confirmation, reverse logic |
| Delete Credit Logs | ✅ | Same functionality for credit operations |
| Monthly Charts | ✅ | Daily sales/bills trends with GPay/Cash |
| Yearly Charts | ✅ | Monthly sales/bills trends with GPay/Cash |
| PDF Downloads | ✅ | Professional monthly/yearly reports |
| Real-time Updates | ✅ | Holdings update after deletions |
| CSRF Protection | ✅ | Secure form handling |
| Error Handling | ✅ | Comprehensive error management |
| Responsive Design | ✅ | Works on all devices |

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **User Authentication**: Login required for all operations
- **Input Validation**: Comprehensive data validation
- **SQL Injection Protection**: Django ORM prevents SQL injection
- **XSS Protection**: Template escaping prevents XSS attacks

## 🚀 Performance Features

- **Database Optimization**: Efficient queries with aggregation
- **Static File Handling**: Optimized static file serving
- **Chart.js CDN**: Fast chart rendering
- **Responsive Images**: Optimized for all screen sizes

## 📞 Support

For issues or questions:
1. Check the Django documentation
2. Review the test script for feature verification
3. Check browser console for JavaScript errors
4. Verify database migrations are applied

---

**Built with ❤️ using Django, Chart.js, and Tailwind CSS**
