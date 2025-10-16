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
