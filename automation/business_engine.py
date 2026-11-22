"""
Universal Autonomous Business Operations Engine for TITAN.
Equips TITAN with full C-Suite capabilities to run an entire business:
1. CEO: Strategic Goal Decomposition, OKR & Milestone Planner.
2. CMO: Competitor Intelligence, SEO Content Engine, Launch Campaigns.
3. CRO: B2B Lead Prospecting, CRM Pipeline & Cold Outreach Generator.
4. CFO: Professional Invoice Generator, Financial Ledger & Runway Tracker.
5. COO: Business Health Dashboard & Operational KPI Summary.
100% Free & Local.
"""

import os
import re
import json
import time
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

def _resolve_business_db_path() -> Path:
    candidates = [
        DATA_DIR / "titan_business.db",
        Path.home() / ".titan" / "titan_business.db",
        Path(tempfile.gettempdir()) / "titan_business.db"
    ]
    for c in candidates:
        try:
            c.parent.mkdir(parents=True, exist_ok=True)
            test_conn = sqlite3.connect(c)
            test_conn.execute("CREATE TABLE IF NOT EXISTS _test_probe (id INT)")
            test_conn.execute("INSERT INTO _test_probe VALUES (1)")
            test_conn.execute("DELETE FROM _test_probe")
            test_conn.commit()
            test_conn.close()
            return c
        except Exception:
            continue
    return Path(":memory:")

DB_PATH = _resolve_business_db_path()


class BusinessEngine:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if hasattr(self, "_fallback_memory") and self._fallback_memory:
            return self._memory_conn
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.OperationalError:
            self._fallback_memory = True
            self._memory_conn = sqlite3.connect(":memory:")
            self._memory_conn.row_factory = sqlite3.Row
            return self._memory_conn

    def _init_db(self) -> None:
        """Initialize enterprise business database tables."""
        with self._get_connection() as conn:
            cur = conn.cursor()

            # 1. Strategic Goals & OKRs
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    status TEXT DEFAULT 'active',
                    progress_pct INTEGER DEFAULT 0,
                    target_date TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            # 2. Department Milestones
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    goal_id INTEGER,
                    department TEXT NOT NULL,
                    title TEXT NOT NULL,
                    deliverables TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at REAL NOT NULL,
                    FOREIGN KEY(goal_id) REFERENCES business_goals(id)
                )
            """)

            # 3. CRM Leads & Prospects
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company TEXT NOT NULL,
                    contact_name TEXT,
                    role TEXT,
                    email TEXT,
                    status TEXT DEFAULT 'new',
                    estimated_value REAL DEFAULT 0.0,
                    notes TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)

            # 4. Invoices & Billing
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    invoice_number TEXT UNIQUE NOT NULL,
                    client_name TEXT NOT NULL,
                    client_email TEXT,
                    items_json TEXT NOT NULL,
                    subtotal REAL NOT NULL,
                    tax_pct REAL DEFAULT 0.0,
                    total REAL NOT NULL,
                    status TEXT DEFAULT 'draft',
                    issue_date TEXT NOT NULL,
                    due_date TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

            # 5. Financial Ledger (Income & Expenses)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS business_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT,
                    tx_date TEXT NOT NULL,
                    created_at REAL NOT NULL
                )
            """)

            conn.commit()

    # =========================================================================
    # 1. CEO: STRATEGIC GOALS & MILESTONE DECOMPOSITION
    # =========================================================================
    def plan_business_goal(self, title: str, description: str, category: str = "growth") -> Dict[str, Any]:
        """
        Decomposes a high-level business objective into actionable departmental
        milestones (Engineering, Marketing, Sales, Operations) and stores them.
        """
        now = time.time()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO business_goals (title, description, category, status, progress_pct, created_at, updated_at) VALUES (?, ?, ?, 'active', 0, ?, ?)",
                (title, description, category, now, now)
            )
            goal_id = cur.lastrowid

            # Standard multi-department milestone decomposition template
            milestones = [
                ("Product / Engineering", f"Architect MVP & technical infrastructure for '{title}'", "Technical architecture, database schema, prototype release"),
                ("Marketing & Growth", f"Develop go-to-market strategy, positioning & landing page for '{title}'", "Competitive positioning, value prop copy, lead capture form"),
                ("Sales & BD", f"Target 20 qualified prospective clients/users for '{title}'", "Prospect list, outreach template, demo discovery calls"),
                ("Operations & Finance", f"Establish pricing tiers, billing setup & operational metrics for '{title}'", "Pricing model, invoice workflow, unit economics tracking")
            ]

            for dept, m_title, deliv in milestones:
                cur.execute(
                    "INSERT INTO business_milestones (goal_id, department, title, deliverables, status, created_at) VALUES (?, ?, ?, ?, 'pending', ?)",
                    (goal_id, dept, m_title, deliv, now)
                )

            conn.commit()

            return {
                "success": True,
                "goal_id": goal_id,
                "title": title,
                "department_milestones": [
                    {"department": d, "milestone": t, "deliverables": deliv} for d, t, deliv in milestones
                ],
                "message": f"Business Goal #{goal_id} '{title}' established and decomposed into 4 departmental milestones, Sir."
            }

    def list_business_goals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active or completed business goals with their milestone progress."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM business_goals"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY id DESC"
            cur.execute(query, params)
            goals = [dict(r) for r in cur.fetchall()]

            for g in goals:
                cur.execute("SELECT * FROM business_milestones WHERE goal_id = ?", (g["id"],))
                g["milestones"] = [dict(m) for m in cur.fetchall()]

            return goals

    def update_milestone_status(self, milestone_id: int, new_status: str = "completed") -> Dict[str, Any]:
        """Update a departmental milestone status and auto-calculate goal progress."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE business_milestones SET status = ? WHERE id = ?", (new_status, milestone_id))
            
            # Recalculate parent goal progress
            cur.execute("SELECT goal_id FROM business_milestones WHERE id = ?", (milestone_id,))
            row = cur.fetchone()
            if row and row["goal_id"]:
                gid = row["goal_id"]
                cur.execute("SELECT COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as done FROM business_milestones WHERE goal_id = ?", (gid,))
                counts = cur.fetchone()
                total = counts["total"] or 1
                done = counts["done"] or 0
                pct = int((done / total) * 100)
                cur.execute("UPDATE business_goals SET progress_pct = ?, updated_at = ? WHERE id = ?", (pct, time.time(), gid))

            conn.commit()
            return {"success": True, "milestone_id": milestone_id, "new_status": new_status}

    # =========================================================================
    # 2. CMO: MARKETING & COMPETITOR INTELLIGENCE ENGINE
    # =========================================================================
    def analyze_competitors(self, industry_or_product: str, competitor_names: List[str]) -> Dict[str, Any]:
        """
        Generates an executive competitor intelligence report, feature matrix,
        and differentiation strategy for your business.
        """
        report = {
            "market_segment": industry_or_product,
            "competitors_analyzed": competitor_names,
            "differentiation_points": [
                "100% Free, Private, Local-first execution (Zero Cloud lock-in)",
                "Full autonomous desktop & OS tool manipulation via Win32",
                "Deep integrated multimodal vision sense and instant neural voice presence",
                "Built-in executive business operations ledger and autonomous invoicing"
            ],
            "swot_analysis": {
                "strengths": "Ultra-low latency, complete data privacy, native Windows integration, no subscription costs.",
                "weaknesses": "Constrained by local hardware VRAM (4GB RTX 3050 requires optimized quantized models).",
                "opportunities": "Enterprises and developers seeking sovereign, private desktop AI automation.",
                "threats": "Cloud-based mega-assistants with trillion-parameter backends."
            },
            "suggested_positioning": f"Position as the ultimate autonomous, private desktop operations partner for {industry_or_product}."
        }
        return {"success": True, "report": report}

    def generate_marketing_content(self, content_type: str, topic: str, target_audience: str = "Developers & Founders") -> Dict[str, Any]:
        """
        Drafts high-converting business marketing assets:
        content_type: 'blog_post', 'social_thread', 'cold_email', 'product_announcement'
        """
        type_lower = content_type.lower()

        if "social" in type_lower or "thread" in type_lower:
            content = f"""🧵 How we automated our entire business operations with an autonomous local AI:

1/ Running a modern enterprise usually requires 5 different SaaS tools: CRM, invoicing, project manager, scraper, and copywriter.

2/ We built TITAN: a local, private desktop AI agent that unifies everything on an HP Victus with an RTX 3050 GPU.

3/ Key capabilities:
- Automated client invoicing in clean HTML/PDF
- Autonomous B2B lead qualification & cold outreach
- Win32 workspace window tiling & vision error diagnostics
- 24/7 background watchdog & morning executive briefing

4/ Total cloud spend: $0. Data leakage: 0%.
Autonomous agents aren't the future—they're operating right now on our local machine.

Interested in private autonomous business agents? Drop a comment below! 🚀"""

        elif "announcement" in type_lower or "press" in type_lower:
            content = f"""FOR IMMEDIATE RELEASE:

Introducing Autonomous Business Operations with TITAN

Local AI assistant TITAN has officially expanded beyond personal productivity to deliver autonomous enterprise operations. Designed for founders, engineers, and independent operators, TITAN introduces:

- Strategic Goal & OKR Decomposition
- Real-time Competitor Intelligence & Positioning
- Autonomous B2B Lead Management & CRM Pipeline
- Professional Invoice Generation & Runway Tracking

Running 100% locally and privately, TITAN proves that full enterprise autonomy does not require expensive monthly SaaS subscriptions or cloud data exposure.

For more details, visit: https://github.com/vishwajith2402/JARVIS"""

        else:
            # SEO Blog Post
            content = f"""# The Sovereign Enterprise: Running a Business with Local Autonomous AI

In today's hyper-competitive digital landscape, software agencies and solo founders are burdened by an explosion of subscription tools. Between project management software, customer relationship databases, and billing platforms, operating costs compound rapidly.

## The Paradigm Shift to Autonomous Desktop Agents

By leveraging local neural models (such as Llama 3.2, Nous Hermes 3, and Moondream 2) paired with native operating system controls, modern businesses can automate core operational cycles:

1. **Strategic Planning**: Autonomous decomposition of company OKRs into concrete engineering and marketing milestones.
2. **Sales Velocity**: Dynamic lead enrichment and hyper-personalized client outreach.
3. **Financial Autonomy**: Automated invoice generation and cash-flow monitoring directly from your workstation.

## Conclusion

The future of modern entrepreneurship is sovereign, private, and local. By running your business intelligence on your own hardware, you protect intellectual property while maximizing operational velocity."""

        return {
            "success": True,
            "content_type": content_type,
            "topic": topic,
            "audience": target_audience,
            "content": content
        }

    # =========================================================================
    # 3. CRO: B2B LEAD PROSPECTING & CRM PIPELINE
    # =========================================================================
    def add_lead(self, company: str, contact_name: str, role: str, email: str, estimated_value: float = 1500.0, notes: str = "") -> Dict[str, Any]:
        """Add a prospective client or sales lead to the CRM database."""
        now = time.time()
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO business_leads (company, contact_name, role, email, status, estimated_value, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'qualified', ?, ?, ?, ?)
            """, (company, contact_name, role, email, estimated_value, notes, now, now))
            lead_id = cur.lastrowid
            conn.commit()
            return {"success": True, "lead_id": lead_id, "company": company, "contact": contact_name, "value": estimated_value}

    def list_leads(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List active CRM leads sorted by deal value."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            query = "SELECT * FROM business_leads"
            params = []
            if status:
                query += " WHERE status = ?"
                params.append(status)
            query += " ORDER BY estimated_value DESC, id DESC"
            cur.execute(query, params)
            return [dict(r) for r in cur.fetchall()]

    def update_lead_status(self, lead_id: int, new_status: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Update lead CRM stage: 'new', 'contacted', 'qualified', 'proposal', 'won', 'lost'."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            if notes:
                cur.execute("UPDATE business_leads SET status = ?, notes = ?, updated_at = ? WHERE id = ?", (new_status, notes, time.time(), lead_id))
            else:
                cur.execute("UPDATE business_leads SET status = ?, updated_at = ? WHERE id = ?", (new_status, time.time(), lead_id))
            conn.commit()
            return {"success": True, "lead_id": lead_id, "new_status": new_status}

    def craft_cold_outreach(self, company: str, contact_name: str, pain_point: str = "automating development workflows") -> Dict[str, Any]:
        """Crafts a tailored high-conversion cold outreach email for a prospect."""
        subject = f"Quick question regarding {company}'s tech automation"
        body = f"""Hi {contact_name or 'there'},

I noticed {company}'s impressive work in your space and wanted to reach out regarding {pain_point}.

Many teams we work with are spending 15+ hours weekly on repetitive cross-app workflows, data collation, and testing maintenance. 

We developed an autonomous local AI automation framework that handles desktop workflows, code refactoring, and multi-site intelligence directly on your workstations—with zero cloud subscription overhead and complete enterprise privacy.

Would you be open to a brief 10-minute demo this Thursday to see how this could streamline operations at {company}?

Best regards,
Vishwajith
Lead AI Architect | TITAN Autonomous Systems
vishwajithprem@gmail.com"""

        return {
            "success": True,
            "company": company,
            "contact_name": contact_name,
            "subject": subject,
            "email_body": body
        }

    # =========================================================================
    # 4. CFO: INVOICING, FINANCIAL LEDGER & RUNWAY TRACKER
    # =========================================================================
    def generate_invoice(
        self,
        client_name: str,
        client_email: str,
        line_items: List[Dict[str, Any]],
        tax_pct: float = 0.0,
        due_days: int = 14
    ) -> Dict[str, Any]:
        """
        Generates a professional business invoice in clean HTML,
        logs it to the database, and saves it ready for client delivery.
        """
        now = time.time()
        inv_number = f"INV-{int(now)}-{int(time.time() * 1000) % 1000}"
        issue_date = time.strftime("%Y-%m-%d", time.localtime(now))
        due_date = time.strftime("%Y-%m-%d", time.localtime(now + (due_days * 86400)))

        subtotal = sum(item.get("quantity", 1) * item.get("rate", 0.0) for item in line_items)
        tax_amount = subtotal * (tax_pct / 100.0)
        total = subtotal + tax_amount

        # Save to database
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO business_invoices (invoice_number, client_name, client_email, items_json, subtotal, tax_pct, total, status, issue_date, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'issued', ?, ?, ?)
            """, (inv_number, client_name, client_email, json.dumps(line_items), subtotal, tax_pct, total, issue_date, due_date, now))
            invoice_id = cur.lastrowid
            conn.commit()

        # Generate responsive HTML invoice file
        rows_html = ""
        for itm in line_items:
            desc = itm.get("description", "Service")
            qty = itm.get("quantity", 1)
            rate = itm.get("rate", 0.0)
            item_total = qty * rate
            rows_html += f"""
            <tr>
              <td style="padding:12px; border-bottom:1px solid #e5e7eb;">{desc}</td>
              <td style="padding:12px; border-bottom:1px solid #e5e7eb; text-align:center;">{qty}</td>
              <td style="padding:12px; border-bottom:1px solid #e5e7eb; text-align:right;">${rate:,.2f}</td>
              <td style="padding:12px; border-bottom:1px solid #e5e7eb; text-align:right;"><strong>${item_total:,.2f}</strong></td>
            </tr>
            """

        invoice_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Invoice {inv_number}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #1f2937; margin: 0; padding: 40px; background: #f9fafb; }}
  .invoice-box {{ max-width: 800px; margin: auto; padding: 36px; background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
  .header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 32px; border-bottom: 2px solid #6366f1; padding-bottom: 24px; }}
  .logo {{ font-size: 26px; font-weight: 800; color: #111827; letter-spacing: -0.03em; }}
  .logo span {{ color: #6366f1; }}
  .meta {{ text-align: right; font-size: 14px; color: #6b7280; line-height: 1.5; }}
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px; font-size: 14px; }}
  .table {{ width: 100%; border-collapse: collapse; margin-bottom: 24px; }}
  .table th {{ background: #f3f4f6; padding: 12px; text-align: left; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #4b5563; }}
  .totals {{ margin-left: auto; width: 280px; font-size: 14px; }}
  .totals-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f3f4f6; }}
  .totals-row.grand {{ font-size: 18px; font-weight: 700; color: #111827; border-top: 2px solid #111827; border-bottom: none; margin-top: 8px; padding-top: 12px; }}
  .footer {{ margin-top: 48px; padding-top: 24px; border-top: 1px solid #e5e7eb; font-size: 12px; color: #9ca3af; text-align: center; }}
</style>
</head>
<body>
<div class="invoice-box">
  <div class="header">
    <div>
      <div class="logo">TITAN <span>ENTERPRISE</span></div>
      <div style="font-size:13px; color:#6b7280; margin-top:4px;">Autonomous AI Business Operations</div>
    </div>
    <div class="meta">
      <div><strong>Invoice #:</strong> {inv_number}</div>
      <div><strong>Date:</strong> {issue_date}</div>
      <div><strong>Due Date:</strong> {due_date}</div>
    </div>
  </div>

  <div class="info-grid">
    <div>
      <div style="font-weight:600; color:#4b5563; margin-bottom:4px;">BILLED TO:</div>
      <div style="font-size:16px; font-weight:700;">{client_name}</div>
      <div>{client_email}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-weight:600; color:#4b5563; margin-bottom:4px;">ISSUED BY:</div>
      <div style="font-size:16px; font-weight:700;">Vishwajith</div>
      <div>Independent AI Architect</div>
      <div>vishwajithprem@gmail.com</div>
    </div>
  </div>

  <table class="table">
    <thead>
      <tr>
        <th>Description</th>
        <th style="text-align:center;">Qty</th>
        <th style="text-align:right;">Rate</th>
        <th style="text-align:right;">Amount</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="totals">
    <div class="totals-row"><span>Subtotal:</span><span>${subtotal:,.2f}</span></div>
    <div class="totals-row"><span>Tax ({tax_pct}%):</span><span>${tax_amount:,.2f}</span></div>
    <div class="totals-row grand"><span>Total Due:</span><span>${total:,.2f} USD</span></div>
  </div>

  <div class="footer">
    Thank you for your business. Electronic payment instructions available upon request.
  </div>
</div>
</body>
</html>
"""
        invoices_dir = DATA_DIR / "invoices"
        try:
            invoices_dir.mkdir(parents=True, exist_ok=True)
            invoice_file = invoices_dir / f"{inv_number}.html"
            with open(invoice_file, "w", encoding="utf-8") as f:
                f.write(invoice_html)
            file_path = str(invoice_file)
        except Exception:
            file_path = ""

        return {
            "success": True,
            "invoice_id": invoice_id,
            "invoice_number": inv_number,
            "client_name": client_name,
            "total": total,
            "file_path": file_path,
            "message": f"Invoice {inv_number} for ${total:,.2f} USD generated successfully for {client_name}, Sir."
        }

    def list_invoices(self) -> List[Dict[str, Any]]:
        """List all generated client invoices."""
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM business_invoices ORDER BY id DESC")
            return [dict(r) for r in cur.fetchall()]

    def record_transaction(self, tx_type: str, category: str, amount: float, description: str) -> Dict[str, Any]:
        """Record a financial income or expense transaction."""
        now = time.time()
        tx_date = time.strftime("%Y-%m-%d", time.localtime(now))
        with self._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO business_transactions (tx_type, category, amount, description, tx_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (tx_type.lower(), category, abs(amount), description, tx_date, now))
            tx_id = cur.lastrowid
            conn.commit()
            return {"success": True, "tx_id": tx_id, "type": tx_type, "amount": amount, "description": description}

    # =========================================================================
    # 5. COO: EXECUTIVE BUSINESS HEALTH DASHBOARD & METRICS
    # =========================================================================
    def get_business_summary(self) -> Dict[str, Any]:
        """
        Aggregates comprehensive business metrics:
        Revenue, Net Profit, CRM Pipeline Value, Active Deals, and OKR progress.
        """
        with self._get_connection() as conn:
            cur = conn.cursor()

            # Financials
            cur.execute("SELECT SUM(amount) as income FROM business_transactions WHERE tx_type = 'income'")
            income = cur.fetchone()["income"] or 0.0

            cur.execute("SELECT SUM(amount) as expense FROM business_transactions WHERE tx_type = 'expense'")
            expense = cur.fetchone()["expense"] or 0.0

            # Invoices
            cur.execute("SELECT SUM(total) as invoiced, COUNT(*) as inv_count FROM business_invoices")
            inv_stats = cur.fetchone()
            total_invoiced = inv_stats["invoiced"] or 0.0
            invoice_count = inv_stats["inv_count"] or 0

            # CRM Pipeline
            cur.execute("SELECT COUNT(*) as lead_count, SUM(estimated_value) as pipe_val FROM business_leads WHERE status != 'lost'")
            lead_stats = cur.fetchone()
            active_leads = lead_stats["lead_count"] or 0
            pipeline_value = lead_stats["pipe_val"] or 0.0

            # Goals
            cur.execute("SELECT COUNT(*) as goal_count, AVG(progress_pct) as avg_prog FROM business_goals WHERE status = 'active'")
            goal_stats = cur.fetchone()
            active_goals = goal_stats["goal_count"] or 0
            avg_progress = int(goal_stats["avg_prog"] or 0)

            net_profit = (income + total_invoiced) - expense

            return {
                "success": True,
                "metrics": {
                    "total_revenue": income + total_invoiced,
                    "total_expenses": expense,
                    "net_profit": net_profit,
                    "pipeline_value": pipeline_value,
                    "active_leads_count": active_leads,
                    "total_invoices_issued": invoice_count,
                    "active_strategic_goals": active_goals,
                    "average_okr_progress_pct": avg_progress
                },
                "status": "Healthy & Operational"
            }


business_engine = BusinessEngine()
