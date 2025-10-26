from flask import Blueprint, render_template, g
from flask_login import login_required, current_user
from app.db_connect import get_db
from datetime import date

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@dashboard.route('/dashboard')
@login_required
def index():
    db = get_db()

    # Get total revenue
    cursor = db.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(total_cost), 0) as total_revenue
        FROM rental
        WHERE status IN ('Completed', 'Overdue', 'Active')
    """)
    total_revenue = cursor.fetchone()['total_revenue']

    # Get most rented equipment
    cursor.execute("""
        SELECT
            e.equipment_name,
            e.equipment_type,
            COUNT(rd.rental_detail_id) as rental_count,
            SUM(rd.line_total) as total_revenue
        FROM equipment e
        JOIN rental_detail rd ON e.equipment_id = rd.equipment_id
        JOIN rental r ON rd.rental_id = r.rental_id
        GROUP BY e.equipment_id, e.equipment_name, e.equipment_type
        ORDER BY rental_count DESC
        LIMIT 5
    """)
    most_rented_equipment = cursor.fetchall()

    # Get overdue rentals with calculated late fees
    cursor.execute("""
        SELECT
            r.rental_id,
            r.rental_date,
            r.due_date,
            r.subtotal,
            r.late_fee,
            r.total_cost,
            DATEDIFF(CURDATE(), r.due_date) as days_overdue,
            c.first_name,
            c.last_name,
            c.phone,
            c.email,
            GROUP_CONCAT(e.equipment_name SEPARATOR ', ') as equipment_list
        FROM rental r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN rental_detail rd ON r.rental_id = rd.rental_id
        JOIN equipment e ON rd.equipment_id = e.equipment_id
        WHERE r.status = 'Overdue'
        GROUP BY r.rental_id
        ORDER BY r.due_date ASC
    """)
    overdue_rentals = cursor.fetchall()

    # Get active rentals count
    cursor.execute("""
        SELECT COUNT(*) as active_count
        FROM rental
        WHERE status = 'Active'
    """)
    active_rentals_count = cursor.fetchone()['active_count']

    # Get completed rentals count
    cursor.execute("""
        SELECT COUNT(*) as completed_count
        FROM rental
        WHERE status = 'Completed'
    """)
    completed_rentals_count = cursor.fetchone()['completed_count']

    # Get overdue rentals count
    cursor.execute("""
        SELECT COUNT(*) as overdue_count
        FROM rental
        WHERE status = 'Overdue'
    """)
    overdue_rentals_count = cursor.fetchone()['overdue_count']

    # Get total late fees collected
    cursor.execute("""
        SELECT COALESCE(SUM(late_fee), 0) as total_late_fees
        FROM rental
        WHERE late_fee > 0
    """)
    total_late_fees = cursor.fetchone()['total_late_fees']

    # Get recent rentals
    cursor.execute("""
        SELECT
            r.rental_id,
            r.rental_date,
            r.due_date,
            r.status,
            r.total_cost,
            c.first_name,
            c.last_name,
            e_emp.first_name as employee_first_name,
            e_emp.last_name as employee_last_name
        FROM rental r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN employee e_emp ON r.employee_id = e_emp.employee_id
        ORDER BY r.rental_date DESC
        LIMIT 10
    """)
    recent_rentals = cursor.fetchall()

    cursor.close()

    return render_template('dashboard/index.html',
                         total_revenue=total_revenue,
                         most_rented_equipment=most_rented_equipment,
                         overdue_rentals=overdue_rentals,
                         active_rentals_count=active_rentals_count,
                         completed_rentals_count=completed_rentals_count,
                         overdue_rentals_count=overdue_rentals_count,
                         total_late_fees=total_late_fees,
                         recent_rentals=recent_rentals,
                         current_date=date.today())
