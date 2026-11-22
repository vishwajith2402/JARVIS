"""
Unit Test Suite for TITAN Autonomous Business Operations Engine.
Tests:
1. CEO Strategic Goal Decomposition & Milestones
2. CMO Competitor Intelligence & Marketing Content Generation
3. CRO B2B Lead Prospecting, CRM Pipeline & Cold Outreach
4. CFO Invoicing, Financial Ledger & Business Health Metrics
"""

import os
import unittest
from automation.business_engine import business_engine
from core.brain import brain


class TestBusinessEngine(unittest.TestCase):
    def test_01_strategic_goal_decomposition(self):
        """Test CEO strategic planning & departmental milestone breakdown."""
        res = business_engine.plan_business_goal(
            title="Launch Enterprise AI Consulting Retainer",
            description="Secure 5 enterprise retainer contracts at $5,000/mo",
            category="revenue"
        )
        self.assertTrue(res.get("success", False))
        self.assertIn("goal_id", res)
        self.assertEqual(len(res["department_milestones"]), 4)

        goals = business_engine.list_business_goals()
        self.assertGreater(len(goals), 0)
        first_goal = goals[0]
        self.assertIn("milestones", first_goal)
        self.assertEqual(len(first_goal["milestones"]), 4)

        # Update milestone status
        first_milestone = first_goal["milestones"][0]
        res_update = business_engine.update_milestone_status(first_milestone["id"], "completed")
        self.assertTrue(res_update["success"])

    def test_02_competitor_intelligence_and_marketing(self):
        """Test CMO competitor SWOT analysis and marketing campaign generation."""
        # Competitor report
        res_comp = business_engine.analyze_competitors(
            industry_or_product="Desktop AI Assistants",
            competitor_names=["CloudMegaAI", "EnterpriseSaaSBot"]
        )
        self.assertTrue(res_comp["success"])
        self.assertIn("swot_analysis", res_comp["report"])

        # Marketing content
        res_mkt = business_engine.generate_marketing_content(
            content_type="social_thread",
            topic="Autonomous Local AI Agents for Enterprise"
        )
        self.assertTrue(res_mkt["success"])
        self.assertIn("TITAN", res_mkt["content"])

    def test_03_crm_lead_pipeline_and_cold_outreach(self):
        """Test CRO B2B lead CRM operations and personalized outreach generation."""
        res_lead = business_engine.add_lead(
            company="Apex Innovations Corp",
            contact_name="Marcus Vance",
            role="Chief Technology Officer",
            email="marcus@apexinnovations.io",
            estimated_value=6000.0,
            notes="Interested in local workstation automation"
        )
        self.assertTrue(res_lead["success"])
        lead_id = res_lead["lead_id"]

        # Update CRM status
        res_st = business_engine.update_lead_status(lead_id, "proposal", "Sent proposal draft")
        self.assertTrue(res_st["success"])

        # Cold outreach email
        res_email = business_engine.craft_cold_outreach(
            company="Apex Innovations Corp",
            contact_name="Marcus Vance",
            pain_point="cross-app manual data entry"
        )
        self.assertTrue(res_email["success"])
        self.assertIn("Marcus", res_email["email_body"])
        self.assertIn("Apex Innovations Corp", res_email["email_body"])

    def test_04_cfo_invoicing_and_ledger(self):
        """Test CFO invoice generation, financial ledger and business metrics."""
        line_items = [
            {"description": "Autonomous Agent Architecture", "quantity": 1, "rate": 3500.0},
            {"description": "Local Model Fine-Tuning & Quantization", "quantity": 2, "rate": 750.0}
        ]
        res_inv = business_engine.generate_invoice(
            client_name="Apex Innovations Corp",
            client_email="billing@apexinnovations.io",
            line_items=line_items,
            tax_pct=0.0
        )
        self.assertTrue(res_inv["success"])
        self.assertEqual(res_inv["total"], 5000.0)
        self.assertTrue(os.path.isfile(res_inv["file_path"]))

        # Record expense
        res_tx = business_engine.record_transaction("expense", "hardware", 250.0, "NVMe SSD Cache Upgrade")
        self.assertTrue(res_tx["success"])

        # Business summary metrics
        summary = business_engine.get_business_summary()
        self.assertTrue(summary["success"])
        self.assertGreater(summary["metrics"]["total_revenue"], 0.0)
        self.assertGreater(summary["metrics"]["pipeline_value"], 0.0)

    def test_05_brain_business_tools_dispatch(self):
        """Test Universal Agent Brain dispatching business tools."""
        res_summary = brain.execute_tool("get_business_summary", {})
        self.assertTrue(res_summary.get("success", False))

        res_outreach = brain.execute_tool("craft_cold_outreach", {
            "company": "NeuralEdge Ltd",
            "contact_name": "Elena Rostova",
            "pain_point": "manual code verification"
        })
        self.assertTrue(res_outreach.get("success", False))
        self.assertIn("Elena", res_outreach["email_body"])


if __name__ == "__main__":
    unittest.main()
