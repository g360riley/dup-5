from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db_connect import get_db
from datetime import datetime, date

rentals = Blueprint('rentals', __name__)

def calculate_late_fee(subtotal, due_date, return_date=None):
    """
    Calculate 10% late fee if rental is overdue
    Returns the late fee amount
    """
    check_date = return_date if return_date else date.today()

    if check_date > due_date:
        # Apply 10% late fee
        return round(subtotal * 0.10, 2)
    return 0.00

@rentals.route('/rentals')
@login_required
def list_rentals():
    db = get_db()
    cursor = db.cursor()

    # Get all rentals with customer and employee information
    cursor.execute("""
        SELECT
            r.rental_id,
            r.rental_date,
            r.due_date,
            r.return_date,
            r.status,
            r.subtotal,
            r.late_fee,
            r.total_cost,
            r.notes,
            c.first_name as customer_first_name,
            c.last_name as customer_last_name,
            c.phone as customer_phone,
            c.email as customer_email,
            e.first_name as employee_first_name,
            e.last_name as employee_last_name,
            DATEDIFF(CURDATE(), r.due_date) as days_overdue
        FROM rental r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN employee e ON r.employee_id = e.employee_id
        ORDER BY r.rental_date DESC
    """)

    all_rentals = cursor.fetchall()
    cursor.close()

    return render_template('rentals/list.html', rentals=all_rentals)

@rentals.route('/rentals/<int:rental_id>')
@login_required
def view_rental(rental_id):
    db = get_db()
    cursor = db.cursor()

    # Get rental information
    cursor.execute("""
        SELECT
            r.rental_id,
            r.rental_date,
            r.due_date,
            r.return_date,
            r.status,
            r.subtotal,
            r.late_fee,
            r.total_cost,
            r.notes,
            c.customer_id,
            c.first_name as customer_first_name,
            c.last_name as customer_last_name,
            c.phone as customer_phone,
            c.email as customer_email,
            c.address as customer_address,
            c.city as customer_city,
            c.state as customer_state,
            c.zip_code as customer_zip,
            c.drivers_license,
            e.employee_id,
            e.first_name as employee_first_name,
            e.last_name as employee_last_name,
            DATEDIFF(CURDATE(), r.due_date) as days_overdue
        FROM rental r
        JOIN customer c ON r.customer_id = c.customer_id
        JOIN employee e ON r.employee_id = e.employee_id
        WHERE r.rental_id = %s
    """, (rental_id,))

    rental = cursor.fetchone()

    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('rentals.list_rentals'))

    # Get rental details (equipment items)
    cursor.execute("""
        SELECT
            rd.rental_detail_id,
            rd.quantity,
            rd.daily_rate,
            rd.days_rented,
            rd.line_total,
            e.equipment_id,
            e.equipment_name,
            e.equipment_type,
            e.description
        FROM rental_detail rd
        JOIN equipment e ON rd.equipment_id = e.equipment_id
        WHERE rd.rental_id = %s
    """, (rental_id,))

    rental_items = cursor.fetchall()
    cursor.close()

    return render_template('rentals/view.html', rental=rental, rental_items=rental_items)

@rentals.route('/rentals/<int:rental_id>/return', methods=['POST'])
@login_required
def return_rental(rental_id):
    db = get_db()
    cursor = db.cursor()

    # Get rental information
    cursor.execute("""
        SELECT rental_id, due_date, subtotal, status
        FROM rental
        WHERE rental_id = %s
    """, (rental_id,))

    rental = cursor.fetchone()

    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('rentals.list_rentals'))

    if rental['status'] == 'Completed':
        flash('This rental has already been returned.', 'warning')
        return redirect(url_for('rentals.view_rental', rental_id=rental_id))

    return_date = date.today()
    due_date = rental['due_date']
    subtotal = rental['subtotal']

    # Calculate late fee (10% if overdue)
    late_fee = calculate_late_fee(subtotal, due_date, return_date)
    total_cost = subtotal + late_fee

    # Determine status
    status = 'Completed'

    # Update rental
    cursor.execute("""
        UPDATE rental
        SET return_date = %s,
            status = %s,
            late_fee = %s,
            total_cost = %s
        WHERE rental_id = %s
    """, (return_date, status, late_fee, total_cost, rental_id))

    # Update equipment availability
    cursor.execute("""
        UPDATE equipment e
        JOIN rental_detail rd ON e.equipment_id = rd.equipment_id
        SET e.availability_status = 'Available'
        WHERE rd.rental_id = %s
    """, (rental_id,))

    db.commit()
    cursor.close()

    if late_fee > 0:
        flash(f'Rental returned successfully. Late fee of ${late_fee:.2f} applied (10% of subtotal).', 'warning')
    else:
        flash('Rental returned successfully. No late fees.', 'success')

    return redirect(url_for('rentals.view_rental', rental_id=rental_id))

@rentals.route('/customers')
@login_required
def list_customers():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            c.*,
            COUNT(r.rental_id) as total_rentals,
            COALESCE(SUM(r.total_cost), 0) as total_spent
        FROM customer c
        LEFT JOIN rental r ON c.customer_id = r.customer_id
        GROUP BY c.customer_id
        ORDER BY c.last_name, c.first_name
    """)

    customers = cursor.fetchall()
    cursor.close()

    return render_template('rentals/customers.html', customers=customers)

@rentals.route('/equipment')
@login_required
def list_equipment():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            e.*,
            COUNT(rd.rental_detail_id) as times_rented,
            COALESCE(SUM(rd.line_total), 0) as total_revenue
        FROM equipment e
        LEFT JOIN rental_detail rd ON e.equipment_id = rd.equipment_id
        GROUP BY e.equipment_id
        ORDER BY e.equipment_type, e.equipment_name
    """)

    equipment_list = cursor.fetchall()
    cursor.close()

    return render_template('rentals/equipment.html', equipment_list=equipment_list)
