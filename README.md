# Equipment Rental Management System

A complete Flask-based equipment rental management system with employee authentication, dynamic dashboards, and comprehensive rental tracking featuring automated late fee calculation.

## Features

### Database Architecture - 5 Related Tables
- **employee** - Employee authentication and staff management
- **customer** - Customer information and contact details
- **equipment** - Equipment inventory catalog and specifications
- **rental** - Rental transactions with dates, costs, and status
- **rental_detail** - Individual equipment items per rental (junction table)

### Authentication System
- Flask-Login integration for secure session management
- Employee-only access with username/password authentication
- Protected routes requiring login
- Session timeout and security features

### Dynamic Dashboard with Metrics
- **Total Revenue** - Sum of all completed and active rental costs
- **Active Rentals** - Currently ongoing rentals
- **Overdue Rentals** - Rentals past due date with calculated late fees
- **Late Fees Collected** - Total 10% late fees applied
- **Most Rented Equipment** - Top 5 most popular items by rental count
- **Recent Rentals** - Last 10 rental transactions with status

### Late Fee System (10% Automatic)
- Automatic 10% late fee calculation for overdue returns
- Applied when rental is returned after due date
- Clearly displayed on dashboard and rental details
- Included in total cost summaries
- Calculated in real-time during return processing

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Database Setup
Database credentials are configured in `.env` file:
- Host: AWS RDS MySQL
- Already configured and ready to use

### 3. Deploy Database Schema
```bash
python deploy_schema.py
```

### 4. Deploy Seed Data
```bash
python deploy_seed_data.py
```

## Running the Application

Start the Flask development server:
```bash
python app.py
```

Access the application at: **http://127.0.0.1:5000**

## Login Credentials

### Test Employee Accounts
- **Manager**: Username: `admin` / Password: `password123`
- **Rental Agent 1**: Username: `jsmith` / Password: `password123`
- **Rental Agent 2**: Username: `mjones` / Password: `password123`

## Application Structure

```
dup-5/
├── app/
│   ├── blueprints/
│   │   ├── auth.py           # Authentication (login/logout)
│   │   ├── dashboard.py      # Dashboard with metrics
│   │   └── rentals.py        # Rental management & late fees
│   ├── templates/
│   │   ├── auth/login.html
│   │   ├── dashboard/index.html
│   │   ├── rentals/
│   │   │   ├── list.html
│   │   │   ├── view.html
│   │   │   ├── customers.html
│   │   │   └── equipment.html
│   │   └── base.html
│   ├── models.py             # Employee model (Flask-Login)
│   ├── db_connect.py         # Database connection
│   ├── app_factory.py        # Flask app factory
│   └── routes.py             # Main routes
├── database/
│   ├── schema.sql            # 5-table schema
│   └── seed_data.sql         # Sample data
├── deploy_schema.py
├── deploy_seed_data.py
├── .env                      # Environment config
└── app.py                    # Entry point
```

## Key Implementation Details

### Late Fee Calculation (rentals.py:17)
```python
def calculate_late_fee(subtotal, due_date, return_date=None):
    """Calculate 10% late fee if rental is overdue"""
    check_date = return_date if return_date else date.today()
    if check_date > due_date:
        return round(subtotal * 0.10, 2)
    return 0.00
```

### Dashboard Metrics (dashboard.py:13-95)
Real-time queries for:
- Total revenue from all rentals
- Most rented equipment with counts
- Overdue rentals with days overdue
- Total late fees collected
- Active and completed rental statistics

### Return Processing (rentals.py:147-179)
When processing a return:
1. Checks rental status
2. Calculates late fee (10% of subtotal if overdue)
3. Updates rental record with return date and fees
4. Changes equipment status back to Available
5. Commits transaction
6. Displays confirmation with fee details

## Database Relationships

### Foreign Keys
- rental.customer_id → customer.customer_id
- rental.employee_id → employee.employee_id
- rental_detail.rental_id → rental.rental_id
- rental_detail.equipment_id → equipment.equipment_id

### Status Values
- **Rental Status**: Active, Completed, Overdue
- **Equipment Availability**: Available, Rented, Maintenance, Retired
- **Equipment Condition**: Excellent, Good, Fair, Poor

## Sample Data Included

- 3 employees (1 manager, 2 rental agents)
- 8 customers with full contact information
- 12 equipment items (drills, saws, mowers, etc.)
- 12 rentals in various states (active, completed, overdue)
- Mix of on-time and late returns for testing late fees

## Testing the Application

### Test Authentication
1. Navigate to http://127.0.0.1:5000
2. Login: admin / password123
3. Should redirect to dashboard

### Test Dashboard Metrics
1. View total revenue (sum of all rentals)
2. Check "Most Rented Equipment" table
3. Review "Overdue Rentals" with 10% late fees
4. Verify metric cards (revenue, active, overdue, late fees)

### Test Late Fee Calculation
1. Go to "Rentals" page
2. Find an overdue rental
3. Click "Return" button
4. Verify 10% late fee is calculated and applied
5. Check total cost includes subtotal + late fee

### Test Rental Views
1. Browse all rentals with status indicators
2. Click a rental to view full details
3. Review customer information
4. See equipment items listed
5. Verify cost summary shows late fees

## Production Deployment

For production:
1. Update `SECRET_KEY` in `.env` with cryptographically secure key
2. Use Gunicorn WSGI server:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```
3. Enable HTTPS for secure authentication
4. Set proper database backup schedule
5. Monitor late fee calculations and revenue metrics

## Technologies

- **Flask 3.1.0** - Web framework
- **Flask-Login 0.6.3** - Session management
- **PyMySQL 1.1.1** - MySQL connector
- **Bootstrap 5.3** - Frontend UI
- **Font Awesome 6.0** - Icons
- **Werkzeug 3.1.3** - Password hashing

---

Complete multi-table rental management system with authentication, metrics dashboard, and automated 10% late fee calculation.