"""
Odoo Time Logger Wrapper for Telegram Bot
Provides simplified interface to show recent time entries
"""

import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add odoo-logger to path
ODOO_LOGGER_PATH = "/Users/quentin/Projects/odoo-logger"
TIME_LOGGER_PATH = os.path.join(ODOO_LOGGER_PATH, "src", "time_logger")
if ODOO_LOGGER_PATH not in sys.path:
    sys.path.insert(0, ODOO_LOGGER_PATH)
if TIME_LOGGER_PATH not in sys.path:
    sys.path.insert(0, TIME_LOGGER_PATH)

# Import from main module
import main as odoo_main
OdooClient = odoo_main.OdooClient
load_env_config = odoo_main.load_env_config
select_company = odoo_main.select_company


def get_odoo_client() -> Optional[OdooClient]:
    """Get authenticated Odoo client."""
    try:
        # Load .env file from odoo-logger directory
        from dotenv import load_dotenv
        env_file = os.path.join(ODOO_LOGGER_PATH, '.env')
        load_dotenv(env_file, override=True)

        # Get configuration
        host = os.getenv('URL')
        port_str = os.getenv('PORT', '443')
        database = os.getenv('DB')
        username = os.getenv('USERNAME')
        api_key = os.getenv('API_KEY')

        # Validate required fields
        if not all([host, database, username, api_key]):
            return None

        # Remove http/https prefix if present
        if host and host.startswith(('http://', 'https://')):
            host = host.replace('http://', '').replace('https://', '')

        try:
            port = int(port_str)
        except (ValueError, TypeError):
            port = 443

        client = OdooClient(
            host=host,
            port=port,
            database=database,
            username=username,
            password=api_key
        )

        return client

    except Exception as e:
        print(f"Error connecting to Odoo: {e}")
        return None


def format_time_entry(entry) -> str:
    """Format a single time entry as a string."""
    date = str(entry.date) if entry.date else "No date"
    project = str(entry.project_id.name) if entry.project_id else "No Project"
    task = str(entry.task_id.name) if entry.task_id else "No Task"
    description = str(entry.name) if entry.name else ""
    hours = f"{float(entry.unit_amount):.2f}h" if entry.unit_amount else "0.00h"

    return f"📅 {date}\n📁 {project}\n📋 {task}\n💬 {description}\n⏱ {hours}"


def get_recent_time_entries(limit: int = 5) -> str:
    """
    Get recent time entries from Odoo and format them for Telegram.

    Args:
        limit: Number of recent entries to retrieve

    Returns:
        Formatted string with time entries or error message
    """
    try:
        client = get_odoo_client()

        if not client:
            return "❌ Could not connect to Odoo. Please check your configuration at:\n/Users/quentin/Projects/odoo-logger/.env"

        # Get all companies and select first one (or you can add company selection later)
        companies = client.get_companies()

        if not companies:
            return "❌ No companies found in your Odoo instance."

        # Use first company for now
        company_id = companies[0].id
        company_name = companies[0].name

        # Get recent entries
        entries = client.get_recent_entries(limit=limit, company_id=company_id)

        if not entries:
            return f"📊 No recent time entries found for {company_name}"

        # Format response
        result = f"📊 *Recent Time Entries* ({company_name})\n"
        result += "=" * 40 + "\n\n"

        for i, entry in enumerate(entries, 1):
            result += f"*Entry {i}:*\n"
            result += format_time_entry(entry)
            result += "\n" + "-" * 40 + "\n\n"

        # Calculate total hours
        total_hours = sum(float(e.unit_amount) if e.unit_amount else 0.0 for e in entries)
        result += f"*Total: {total_hours:.2f}h*"

        return result

    except Exception as e:
        return f"❌ Error fetching time entries: {str(e)}"


def get_weekly_summary() -> str:
    """Get weekly time summary."""
    try:
        from datetime import date, timedelta

        client = get_odoo_client()

        if not client:
            return "❌ Could not connect to Odoo."

        companies = client.get_companies()
        if not companies:
            return "❌ No companies found."

        company_id = companies[0].id
        company_name = companies[0].name

        # Get this week's date range
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Fetch entries
        entries = client.get_time_entries(week_start, week_end, company_id=company_id)

        if not entries:
            return f"📊 No time entries for this week\n({week_start} to {week_end})"

        # Calculate totals by project
        project_hours = {}
        total_hours = 0.0

        for entry in entries:
            project_name = str(entry.project_id.name) if entry.project_id else 'No Project'
            hours = float(entry.unit_amount) if entry.unit_amount else 0.0

            if project_name not in project_hours:
                project_hours[project_name] = 0.0

            project_hours[project_name] += hours
            total_hours += hours

        # Format response
        result = f"📊 *Week Summary* ({company_name})\n"
        result += f"📅 {week_start} to {week_end}\n"
        result += "=" * 40 + "\n\n"

        # Sort projects by hours (descending)
        sorted_projects = sorted(project_hours.items(), key=lambda x: x[1], reverse=True)

        for project, hours in sorted_projects:
            result += f"📁 {project}: *{hours:.2f}h*\n"

        result += "\n" + "=" * 40 + "\n"
        result += f"*Total: {total_hours:.2f}h*"

        return result

    except Exception as e:
        return f"❌ Error fetching weekly summary: {str(e)}"


def get_monthly_summary() -> str:
    """Get monthly time summary."""
    try:
        from datetime import date, timedelta

        client = get_odoo_client()

        if not client:
            return "❌ Could not connect to Odoo."

        companies = client.get_companies()
        if not companies:
            return "❌ No companies found."

        company_id = companies[0].id
        company_name = companies[0].name

        # Get this month's date range
        today = date.today()
        month_start = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        month_end = next_month.replace(day=1) - timedelta(days=1)

        # Fetch entries
        entries = client.get_time_entries(month_start, month_end, company_id=company_id)

        if not entries:
            return f"📊 No time entries for this month\n({month_start} to {month_end})"

        # Calculate totals by project
        project_hours = {}
        total_hours = 0.0

        for entry in entries:
            project_name = str(entry.project_id.name) if entry.project_id else 'No Project'
            hours = float(entry.unit_amount) if entry.unit_amount else 0.0

            if project_name not in project_hours:
                project_hours[project_name] = 0.0

            project_hours[project_name] += hours
            total_hours += hours

        # Format response
        result = f"📊 *Month Summary* ({company_name})\n"
        result += f"📅 {month_start.strftime('%B %Y')}\n"
        result += "=" * 40 + "\n\n"

        # Sort projects by hours (descending)
        sorted_projects = sorted(project_hours.items(), key=lambda x: x[1], reverse=True)

        for project, hours in sorted_projects:
            result += f"📁 {project}: *{hours:.2f}h*\n"

        result += "\n" + "=" * 40 + "\n"
        result += f"*Total: {total_hours:.2f}h*"

        return result

    except Exception as e:
        return f"❌ Error fetching monthly summary: {str(e)}"


def get_time_summary_tables() -> str:
    """
    Get comprehensive time summary with MD tables for weeks, months, and quarters.

    Returns:
        Formatted markdown tables with time data or error message
    """
    try:
        from datetime import date, timedelta

        client = get_odoo_client()

        if not client:
            return "❌ Could not connect to Odoo. Please check your configuration."

        companies = client.get_companies()
        if not companies:
            return "❌ No companies found."

        company_id = companies[0].id
        company_name = companies[0].name

        today = date.today()

        # Expected hours
        EXPECTED_WEEK_HOURS = 40.0
        EXPECTED_MONTH_HOURS = 160.0
        EXPECTED_QUARTER_HOURS = 480.0

        # Helper functions
        def get_week_number(d: date) -> int:
            return d.isocalendar()[1]

        def get_week_range(d: date) -> tuple:
            week_start = d - timedelta(days=d.weekday())
            week_end = week_start + timedelta(days=6)
            return week_start, week_end

        def get_month_range(year: int, month: int) -> tuple:
            month_start = date(year, month, 1)
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            month_end = next_month - timedelta(days=1)
            return month_start, month_end

        def get_quarter(d: date) -> int:
            return (d.month - 1) // 3 + 1

        def get_quarter_range(year: int, quarter: int) -> tuple:
            start_month = (quarter - 1) * 3 + 1
            quarter_start = date(year, start_month, 1)
            end_month = start_month + 2
            if end_month == 12:
                quarter_end = date(year, 12, 31)
            else:
                next_quarter = date(year, end_month + 1, 1)
                quarter_end = next_quarter - timedelta(days=1)
            return quarter_start, quarter_end

        # Calculate weeks (current + previous 3)
        weeks_data = []
        for i in range(4):
            week_date = today - timedelta(weeks=i)
            week_start, week_end = get_week_range(week_date)
            week_num = get_week_number(week_date)
            year = week_date.year

            entries = client.get_time_entries(week_start, week_end, company_id=company_id)
            total_hours = sum(float(e.unit_amount) if e.unit_amount else 0.0 for e in entries)
            weeks_data.append((year, week_num, total_hours))

        # Calculate months (current + previous 3)
        months_data = []
        for i in range(4):
            if today.month - i >= 1:
                month = today.month - i
                year = today.year
            else:
                month = 12 + (today.month - i)
                year = today.year - 1

            month_start, month_end = get_month_range(year, month)
            entries = client.get_time_entries(month_start, month_end, company_id=company_id)
            total_hours = sum(float(e.unit_amount) if e.unit_amount else 0.0 for e in entries)
            months_data.append((month_start, total_hours))

        # Calculate quarters (current + previous 3)
        quarters_data = []
        current_quarter = get_quarter(today)
        current_year = today.year

        for i in range(4):
            quarter = current_quarter - i
            year = current_year
            while quarter < 1:
                quarter += 4
                year -= 1

            quarter_start, quarter_end = get_quarter_range(year, quarter)
            entries = client.get_time_entries(quarter_start, quarter_end, company_id=company_id)
            total_hours = sum(float(e.unit_amount) if e.unit_amount else 0.0 for e in entries)
            quarters_data.append((year, quarter, total_hours))

        # Format as markdown tables
        result = f"📊 *Time Summary* ({company_name})\n\n"

        # Weeks table
        result += "*Weeks*\n```\n"
        result += "| Week   | Hours |    % |\n"
        result += "|--------|-------|------|\n"
        for year, week_num, hours in weeks_data:
            percentage = (hours / EXPECTED_WEEK_HOURS * 100) if EXPECTED_WEEK_HOURS > 0 else 0
            result += f"| KW {week_num:02d}  | {hours:5.1f} | {percentage:3.0f}% |\n"
        result += "```\n\n"

        # Months table
        result += "*Months*\n```\n"
        result += "| Month     | Hours |    % |\n"
        result += "|-----------|-------|------|\n"
        for month_start, hours in months_data:
            percentage = (hours / EXPECTED_MONTH_HOURS * 100) if EXPECTED_MONTH_HOURS > 0 else 0
            result += f"| {month_start.strftime('%b %Y')}  | {hours:5.1f} | {percentage:3.0f}% |\n"
        result += "```\n\n"

        # Quarters table
        result += "*Quarters*\n```\n"
        result += "| Quarter  | Hours |    % |\n"
        result += "|----------|-------|------|\n"
        for year, quarter, hours in quarters_data:
            percentage = (hours / EXPECTED_QUARTER_HOURS * 100) if EXPECTED_QUARTER_HOURS > 0 else 0
            result += f"| Q{quarter} {year}  | {hours:5.1f} | {percentage:3.0f}% |\n"
        result += "```"

        return result

    except Exception as e:
        return f"❌ Error fetching time summary: {str(e)}"


def get_invoice_summary() -> str:
    """
    Get invoice summary with amounts invoiced and paid per month and quarter.

    Returns:
        Formatted markdown tables with invoice data or error message
    """
    try:
        from datetime import date, timedelta
        from typing import Tuple

        client = get_odoo_client()

        if not client:
            return "❌ Could not connect to Odoo. Please check your configuration."

        companies = client.get_companies()
        if not companies:
            return "❌ No companies found."

        company_id = companies[0].id
        company_name = companies[0].name

        today = date.today()

        def get_month_range(year: int, month: int) -> Tuple[date, date]:
            month_start = date(year, month, 1)
            if month == 12:
                next_month = date(year + 1, 1, 1)
            else:
                next_month = date(year, month + 1, 1)
            month_end = next_month - timedelta(days=1)
            return month_start, month_end

        def format_thousands(amount: float) -> str:
            return f"{amount / 1000:.1f}k"

        def get_quarter(d: date) -> int:
            return (d.month - 1) // 3 + 1

        def get_quarter_range(year: int, quarter: int) -> Tuple[date, date]:
            start_month = (quarter - 1) * 3 + 1
            quarter_start = date(year, start_month, 1)
            end_month = start_month + 2
            if end_month == 12:
                quarter_end = date(year, 12, 31)
            else:
                next_quarter = date(year, end_month + 1, 1)
                quarter_end = next_quarter - timedelta(days=1)
            return quarter_start, quarter_end

        # Calculate last 3 months
        months_data = []
        for i in range(3):
            if today.month - i >= 1:
                month = today.month - i
                year = today.year
            else:
                month = 12 + (today.month - i)
                year = today.year - 1

            month_start, month_end = get_month_range(year, month)

            invoice_domain = [
                ('company_id', '=', company_id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', month_start.isoformat()),
                ('invoice_date', '<=', month_end.isoformat()),
                ('state', '=', 'posted')
            ]

            invoice_ids = client.odoo.env['account.move'].search(invoice_domain)

            total_invoiced = 0.0
            total_paid = 0.0

            if invoice_ids:
                invoice_data = client.odoo.env['account.move'].read(
                    invoice_ids,
                    ['amount_untaxed', 'amount_residual', 'amount_total']
                )

                for invoice in invoice_data:
                    invoice_amount = float(invoice.get('amount_untaxed', 0.0))
                    residual_amount = float(invoice.get('amount_residual', 0.0))
                    total_with_tax = float(invoice.get('amount_total', 0.0))

                    if total_with_tax > 0:
                        paid_with_tax = total_with_tax - residual_amount
                        paid_amount = (paid_with_tax / total_with_tax) * invoice_amount
                    else:
                        paid_amount = 0.0

                    total_invoiced += invoice_amount
                    total_paid += paid_amount

            percentage_paid = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0.0
            months_data.append((month_start, total_invoiced, total_paid, percentage_paid))

        # Calculate monthly totals
        total_invoiced_m = sum(invoiced for _, invoiced, _, _ in months_data)
        total_paid_m = sum(paid for _, _, paid, _ in months_data)
        total_percentage_m = (total_paid_m / total_invoiced_m * 100) if total_invoiced_m > 0 else 0.0

        # Calculate quarters
        quarters_data = []
        current_quarter = get_quarter(today)
        current_year = today.year

        for i in range(4):
            quarter = current_quarter - i
            year = current_year

            while quarter < 1:
                quarter += 4
                year -= 1

            quarter_start, quarter_end = get_quarter_range(year, quarter)

            invoice_domain = [
                ('company_id', '=', company_id),
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', quarter_start.isoformat()),
                ('invoice_date', '<=', quarter_end.isoformat()),
                ('state', '=', 'posted')
            ]

            invoice_ids = client.odoo.env['account.move'].search(invoice_domain)

            total_invoiced_q = 0.0
            total_paid_q = 0.0

            if invoice_ids:
                invoice_data = client.odoo.env['account.move'].read(
                    invoice_ids,
                    ['amount_untaxed', 'amount_residual', 'amount_total']
                )

                for invoice in invoice_data:
                    invoice_amount = float(invoice.get('amount_untaxed', 0.0))
                    residual_amount = float(invoice.get('amount_residual', 0.0))
                    total_with_tax = float(invoice.get('amount_total', 0.0))

                    if total_with_tax > 0:
                        paid_with_tax = total_with_tax - residual_amount
                        paid_amount = (paid_with_tax / total_with_tax) * invoice_amount
                    else:
                        paid_amount = 0.0

                    total_invoiced_q += invoice_amount
                    total_paid_q += paid_amount

            percentage_paid_q = (total_paid_q / total_invoiced_q * 100) if total_invoiced_q > 0 else 0.0
            quarters_data.append((year, quarter, total_invoiced_q, total_paid_q, percentage_paid_q))

        # Calculate quarterly totals
        total_invoiced_q_all = sum(invoiced for _, _, invoiced, _, _ in quarters_data)
        total_paid_q_all = sum(paid for _, _, _, paid, _ in quarters_data)
        total_percentage_q = (total_paid_q_all / total_invoiced_q_all * 100) if total_invoiced_q_all > 0 else 0.0

        # Format as markdown
        result = f"💰 *Invoice Summary* ({company_name})\n\n"

        # Months table
        result += "*Invoices (excl. VAT)*\n```\n"
        result += "| Month     | Invoiced | Paid    | Paid % |\n"
        result += "|-----------|----------|---------|--------|\n"
        for month_start, invoiced, paid, percentage in months_data:
            invoiced_fmt = format_thousands(invoiced)
            paid_fmt = format_thousands(paid)
            result += f"| {month_start.strftime('%b %Y')}  | {invoiced_fmt:>8} | {paid_fmt:>7} | {percentage:5.0f}% |\n"
        result += "|-----------|----------|---------|--------|\n"
        total_inv_fmt = format_thousands(total_invoiced_m)
        total_paid_fmt = format_thousands(total_paid_m)
        result += f"| Total     | {total_inv_fmt:>8} | {total_paid_fmt:>7} | {total_percentage_m:5.0f}% |\n"
        result += "```\n\n"

        # Quarters table
        result += "*Quarters*\n```\n"
        result += "| Quarter  | Invoiced | Paid    | Paid % |\n"
        result += "|----------|----------|---------|--------|\n"
        for year, quarter, invoiced, paid, percentage in quarters_data:
            invoiced_fmt = format_thousands(invoiced)
            paid_fmt = format_thousands(paid)
            result += f"| Q{quarter} {year}  | {invoiced_fmt:>8} | {paid_fmt:>7} | {percentage:5.0f}% |\n"
        result += "|----------|----------|---------|--------|\n"
        total_inv_fmt_q = format_thousands(total_invoiced_q_all)
        total_paid_fmt_q = format_thousands(total_paid_q_all)
        result += f"| Total    | {total_inv_fmt_q:>8} | {total_paid_fmt_q:>7} | {total_percentage_q:5.0f}% |\n"
        result += "```"

        return result

    except Exception as e:
        return f"❌ Error fetching invoice summary: {str(e)}"


def get_projects_list(company_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get list of active projects for selection."""
    try:
        client = get_odoo_client()
        if not client:
            return []

        if company_id:
            projects = client.get_projects_by_company(company_id)
        else:
            companies = client.get_companies()
            if companies:
                company_id = companies[0].id
                projects = client.get_projects_by_company(company_id)
            else:
                return []

        return [{"id": p.id, "name": p.name} for p in projects]
    except Exception:
        return []


def get_tasks_list(project_id: int) -> List[Dict[str, Any]]:
    """Get list of tasks for a project."""
    try:
        client = get_odoo_client()
        if not client:
            return []

        tasks = client.get_tasks(project_id)
        return [{"id": t.id, "name": t.name} for t in tasks]
    except Exception:
        return []


def log_time_entry(
    project_id: int,
    task_id: int,
    description: str,
    hours: float,
    log_date: Optional[str] = None
) -> str:
    """
    Log a time entry to Odoo.

    Args:
        project_id: Project ID
        task_id: Task ID
        description: Work description
        hours: Hours spent
        log_date: Date in YYYY-MM-DD format (defaults to today)

    Returns:
        Success or error message
    """
    try:
        from datetime import date as dt_date

        client = get_odoo_client()
        if not client:
            return "❌ Could not connect to Odoo."

        companies = client.get_companies()
        if not companies:
            return "❌ No companies found."

        company_id = companies[0].id

        # Use today if no date specified
        if not log_date:
            log_date = dt_date.today().isoformat()

        # Validate employee exists
        if not client.check_employee_exists(company_id):
            return ("❌ You don't have an active employee record in the selected company.\n"
                   "Please contact your Odoo administrator.")

        # Create the time entry
        timesheet_id = client.log_time(
            project_id=project_id,
            task_id=task_id,
            description=description,
            time_spent=hours,
            log_date=log_date,
            company_id=company_id
        )

        return f"✅ Time logged successfully!\n📝 {hours}h on {log_date}\n🆔 Entry ID: {timesheet_id}"

    except Exception as e:
        return f"❌ Error logging time: {str(e)}"
