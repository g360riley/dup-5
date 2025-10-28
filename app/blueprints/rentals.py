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

    # Get status filter from query parameter (default to 'active')
    status_filter = request.args.get('status', 'active').lower()

    # Build WHERE clause based on filter
    if status_filter == 'completed':
        where_clause = "WHERE r.status = 'Completed'"
    else:
        where_clause = "WHERE r.status IN ('Active', 'Overdue')"

    # Get rentals with customer and employee information
    cursor.execute(f"""
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
        {where_clause}
        ORDER BY r.rental_date DESC
    """)

    filtered_rentals = cursor.fetchall()

    # Get customers for dropdown (only non-archived)
    cursor.execute("""
        SELECT customer_id, first_name, last_name, email
        FROM customer
        WHERE is_archived = FALSE
        ORDER BY last_name, first_name
    """)
    customers = cursor.fetchall()

    # Get available equipment for dropdown (only non-archived)
    cursor.execute("""
        SELECT equipment_id, equipment_name, equipment_type, daily_rate, availability_status
        FROM equipment
        WHERE availability_status = 'Available' AND is_archived = FALSE
        ORDER BY equipment_type, equipment_name
    """)
    equipment = cursor.fetchall()

    cursor.close()

    return render_template('rentals/list.html', rentals=filtered_rentals, customers=customers, equipment=equipment, status_filter=status_filter)

@rentals.route('/rentals/create', methods=['POST'])
@login_required
def create_rental():
    db = get_db()
    cursor = db.cursor()

    try:
        customer_id = request.form.get('customer_id')
        rental_date = request.form.get('rental_date')
        due_date = request.form.get('due_date')
        notes = request.form.get('notes', '')

        # Get selected equipment (can be multiple)
        equipment_ids = request.form.getlist('equipment_ids[]')
        days_rented = request.form.getlist('days_rented[]')

        if not customer_id or not rental_date or not due_date or not equipment_ids:
            flash('Please fill in all required fields and select at least one equipment item.', 'danger')
            return redirect(url_for('rentals.list_rentals'))

        # Calculate subtotal
        subtotal = 0
        rental_details = []

        for i, equip_id in enumerate(equipment_ids):
            cursor.execute("SELECT daily_rate FROM equipment WHERE equipment_id = %s", (equip_id,))
            equipment = cursor.fetchone()
            if equipment:
                daily_rate = float(equipment['daily_rate'])
                days = int(days_rented[i]) if i < len(days_rented) else 1
                line_total = daily_rate * days
                subtotal += line_total
                rental_details.append({
                    'equipment_id': equip_id,
                    'daily_rate': daily_rate,
                    'days_rented': days,
                    'line_total': line_total
                })

        # Create rental record
        cursor.execute("""
            INSERT INTO rental (customer_id, employee_id, rental_date, due_date, status, subtotal, late_fee, total_cost, notes)
            VALUES (%s, %s, %s, %s, 'Active', %s, 0.00, %s, %s)
        """, (customer_id, current_user.employee_id, rental_date, due_date, subtotal, subtotal, notes))

        rental_id = cursor.lastrowid

        # Create rental detail records
        for detail in rental_details:
            cursor.execute("""
                INSERT INTO rental_detail (rental_id, equipment_id, quantity, daily_rate, days_rented, line_total)
                VALUES (%s, %s, 1, %s, %s, %s)
            """, (rental_id, detail['equipment_id'], detail['daily_rate'], detail['days_rented'], detail['line_total']))

            # Update equipment availability
            cursor.execute("""
                UPDATE equipment
                SET availability_status = 'Rented'
                WHERE equipment_id = %s
            """, (detail['equipment_id'],))

        db.commit()
        flash(f'Rental #{rental_id} created successfully!', 'success')

    except Exception as e:
        db.rollback()
        flash(f'Error creating rental: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_rentals'))

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

    # Get status filter from query parameter (default to 'active')
    status_filter = request.args.get('status', 'active').lower()

    # Build WHERE clause based on filter
    if status_filter == 'archived':
        archive_filter = "WHERE c.is_archived = TRUE"
    else:
        archive_filter = "WHERE c.is_archived = FALSE"

    cursor.execute(f"""
        SELECT
            c.*,
            COUNT(r.rental_id) as total_rentals,
            COALESCE(SUM(r.total_cost), 0) as total_spent
        FROM customer c
        LEFT JOIN rental r ON c.customer_id = r.customer_id
        {archive_filter}
        GROUP BY c.customer_id
        ORDER BY c.last_name, c.first_name
    """)

    customers = cursor.fetchall()
    cursor.close()

    return render_template('rentals/customers.html', customers=customers, status_filter=status_filter)

@rentals.route('/equipment')
@login_required
def list_equipment():
    db = get_db()
    cursor = db.cursor()

    # Get status filter from query parameter (default to 'active')
    status_filter = request.args.get('status', 'active').lower()

    # Build WHERE clause based on filter
    if status_filter == 'archived':
        archive_filter = "WHERE e.is_archived = TRUE"
    else:
        archive_filter = "WHERE e.is_archived = FALSE"

    cursor.execute(f"""
        SELECT
            e.*,
            COUNT(rd.rental_detail_id) as times_rented,
            COALESCE(SUM(rd.line_total), 0) as total_revenue
        FROM equipment e
        LEFT JOIN rental_detail rd ON e.equipment_id = rd.equipment_id
        {archive_filter}
        GROUP BY e.equipment_id
        ORDER BY e.equipment_type, e.equipment_name
    """)

    equipment_list = cursor.fetchall()
    cursor.close()

    return render_template('rentals/equipment.html', equipment_list=equipment_list, status_filter=status_filter)

# Customer CRUD Operations
@rentals.route('/customers/create', methods=['POST'])
@login_required
def create_customer():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO customer (first_name, last_name, email, phone, address, city, state, zip_code, drivers_license)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form.get('first_name'),
            request.form.get('last_name'),
            request.form.get('email'),
            request.form.get('phone'),
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('state'),
            request.form.get('zip_code'),
            request.form.get('drivers_license')
        ))
        db.commit()
        flash('Customer created successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error creating customer: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_customers'))

@rentals.route('/customers/edit/<int:customer_id>', methods=['POST'])
@login_required
def edit_customer(customer_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE customer
            SET first_name = %s, last_name = %s, email = %s, phone = %s,
                address = %s, city = %s, state = %s, zip_code = %s, drivers_license = %s
            WHERE customer_id = %s
        """, (
            request.form.get('first_name'),
            request.form.get('last_name'),
            request.form.get('email'),
            request.form.get('phone'),
            request.form.get('address'),
            request.form.get('city'),
            request.form.get('state'),
            request.form.get('zip_code'),
            request.form.get('drivers_license'),
            customer_id
        ))
        db.commit()
        flash('Customer updated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error updating customer: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_customers'))

@rentals.route('/customers/archive/<int:customer_id>', methods=['POST'])
@login_required
def archive_customer(customer_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE customer SET is_archived = TRUE WHERE customer_id = %s", (customer_id,))
        db.commit()
        flash('Customer archived successfully! Historical rental data preserved.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error archiving customer: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_customers'))

@rentals.route('/customers/unarchive/<int:customer_id>', methods=['POST'])
@login_required
def unarchive_customer(customer_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE customer SET is_archived = FALSE WHERE customer_id = %s", (customer_id,))
        db.commit()
        flash('Customer restored successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error restoring customer: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_customers', status='active'))

@rentals.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
def delete_customer(customer_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Check if customer is archived
        cursor.execute("SELECT is_archived FROM customer WHERE customer_id = %s", (customer_id,))
        customer = cursor.fetchone()

        if not customer:
            flash('Customer not found.', 'danger')
        elif not customer['is_archived']:
            flash('Only archived customers can be deleted. Please archive the customer first.', 'warning')
        else:
            # Check if customer has any rentals
            cursor.execute("SELECT COUNT(*) as count FROM rental WHERE customer_id = %s", (customer_id,))
            rental_count = cursor.fetchone()['count']

            if rental_count > 0:
                flash('Cannot delete customer with existing rental history. Historical data must be preserved.', 'danger')
            else:
                cursor.execute("DELETE FROM customer WHERE customer_id = %s", (customer_id,))
                db.commit()
                flash('Customer deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting customer: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_customers', status='archived'))

# Equipment CRUD Operations
@rentals.route('/equipment/create', methods=['POST'])
@login_required
def create_equipment():
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            INSERT INTO equipment (equipment_name, equipment_type, description, daily_rate,
                                 condition_status, availability_status, serial_number, purchase_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form.get('equipment_name'),
            request.form.get('equipment_type'),
            request.form.get('description'),
            request.form.get('daily_rate'),
            request.form.get('condition_status'),
            request.form.get('availability_status'),
            request.form.get('serial_number'),
            request.form.get('purchase_date') if request.form.get('purchase_date') else None
        ))
        db.commit()
        flash('Equipment created successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error creating equipment: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_equipment'))

@rentals.route('/equipment/edit/<int:equipment_id>', methods=['POST'])
@login_required
def edit_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("""
            UPDATE equipment
            SET equipment_name = %s, equipment_type = %s, description = %s, daily_rate = %s,
                condition_status = %s, availability_status = %s, serial_number = %s, purchase_date = %s
            WHERE equipment_id = %s
        """, (
            request.form.get('equipment_name'),
            request.form.get('equipment_type'),
            request.form.get('description'),
            request.form.get('daily_rate'),
            request.form.get('condition_status'),
            request.form.get('availability_status'),
            request.form.get('serial_number'),
            request.form.get('purchase_date') if request.form.get('purchase_date') else None,
            equipment_id
        ))
        db.commit()
        flash('Equipment updated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error updating equipment: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_equipment'))

@rentals.route('/equipment/archive/<int:equipment_id>', methods=['POST'])
@login_required
def archive_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Check if equipment is in active rentals
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM rental_detail rd
            JOIN rental r ON rd.rental_id = r.rental_id
            WHERE rd.equipment_id = %s AND r.status IN ('Active', 'Overdue')
        """, (equipment_id,))
        active_count = cursor.fetchone()['count']

        if active_count > 0:
            flash('Cannot archive equipment with active rentals.', 'danger')
        else:
            cursor.execute("UPDATE equipment SET is_archived = TRUE WHERE equipment_id = %s", (equipment_id,))
            db.commit()
            flash('Equipment archived successfully! Historical data preserved.', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error archiving equipment: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_equipment'))

@rentals.route('/equipment/unarchive/<int:equipment_id>', methods=['POST'])
@login_required
def unarchive_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE equipment SET is_archived = FALSE WHERE equipment_id = %s", (equipment_id,))
        db.commit()
        flash('Equipment restored successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error restoring equipment: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_equipment', status='active'))

@rentals.route('/equipment/delete/<int:equipment_id>', methods=['POST'])
@login_required
def delete_equipment(equipment_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Check if equipment is archived
        cursor.execute("SELECT is_archived FROM equipment WHERE equipment_id = %s", (equipment_id,))
        equipment = cursor.fetchone()

        if not equipment:
            flash('Equipment not found.', 'danger')
        elif not equipment['is_archived']:
            flash('Only archived equipment can be deleted. Please archive the equipment first.', 'warning')
        else:
            # Check if equipment has any rental history
            cursor.execute("SELECT COUNT(*) as count FROM rental_detail WHERE equipment_id = %s", (equipment_id,))
            rental_count = cursor.fetchone()['count']

            if rental_count > 0:
                flash('Cannot delete equipment with existing rental history. Historical data must be preserved.', 'danger')
            else:
                cursor.execute("DELETE FROM equipment WHERE equipment_id = %s", (equipment_id,))
                db.commit()
                flash('Equipment deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting equipment: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_equipment', status='archived'))

# Rental Delete Operation
@rentals.route('/rentals/delete/<int:rental_id>', methods=['POST'])
@login_required
def delete_rental(rental_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Check if rental is active
        cursor.execute("SELECT status FROM rental WHERE rental_id = %s", (rental_id,))
        rental = cursor.fetchone()

        if rental and rental['status'] == 'Active':
            flash('Cannot delete active rental. Please return it first.', 'danger')
        else:
            cursor.execute("DELETE FROM rental WHERE rental_id = %s", (rental_id,))
            db.commit()
            flash('Rental deleted successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error deleting rental: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_rentals', status='completed'))

# Rental Change Status Operation
@rentals.route('/rentals/reactivate/<int:rental_id>', methods=['POST'])
@login_required
def reactivate_rental(rental_id):
    db = get_db()
    cursor = db.cursor()

    try:
        # Get rental information
        cursor.execute("SELECT status, return_date FROM rental WHERE rental_id = %s", (rental_id,))
        rental = cursor.fetchone()

        if not rental:
            flash('Rental not found.', 'danger')
        elif rental['status'] != 'Completed':
            flash('Only completed rentals can be reactivated.', 'warning')
        else:
            # Clear return date and reset status to Active
            cursor.execute("""
                UPDATE rental
                SET status = 'Active',
                    return_date = NULL,
                    late_fee = 0.00,
                    total_cost = subtotal
                WHERE rental_id = %s
            """, (rental_id,))

            # Set equipment back to rented status
            cursor.execute("""
                UPDATE equipment e
                JOIN rental_detail rd ON e.equipment_id = rd.equipment_id
                SET e.availability_status = 'Rented'
                WHERE rd.rental_id = %s
            """, (rental_id,))

            db.commit()
            flash('Rental reactivated successfully!', 'success')
    except Exception as e:
        db.rollback()
        flash(f'Error reactivating rental: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('rentals.list_rentals', status='active'))
