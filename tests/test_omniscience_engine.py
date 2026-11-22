"""
Unit Test Suite for TITAN Omniscience & Generative Studio Engine.
Tests:
1. Lovable / v0 Generative Interactive Full-Stack Web Apps
2. Figma Generative UI/UX Design Tokens & Component Layouts
3. Perplexity Real-time Search with Numbered Citations
4. Universal Agent Brain Tool Dispatch
"""

import os
import unittest
from automation.omniscience_engine import omniscience_engine
from core.brain import brain


class TestOmniscienceEngine(unittest.TestCase):
    def test_01_lovable_generative_app(self):
        """Test Lovable/v0 interactive single-file web app creation."""
        res = omniscience_engine.generate_lovable_app("Focus Pomodoro Timer with Sound Alert")
        self.assertTrue(res["success"])
        self.assertIn("artifact_id", res)
        self.assertTrue(os.path.isfile(res["file_path"]))
        self.assertIn("timer", res["html_code"].lower())

    def test_02_figma_design_system(self):
        """Test Figma design tokens and component canvas generation."""
        res = omniscience_engine.generate_figma_design(
            component_name="Biometric Security Shield",
            style_theme="futuristic_glass"
        )
        self.assertTrue(res["success"])
        self.assertIn("design_system", res)
        self.assertIn("tokens", res["design_system"])
        self.assertTrue(os.path.isfile(res["file_path"]))

    def test_03_perplexity_search(self):
        """Test Perplexity-style synthesized response with numbered citations."""
        res = omniscience_engine.perplexity_search("Open source local LLMs 2026")
        self.assertTrue(res["success"])
        self.assertIn("sources", res)
        self.assertIn("answer_with_citations", res)
        self.assertIn("[1]", res["answer_with_citations"])

    def test_04_brain_omniscience_dispatch(self):
        """Test Universal Agent Brain dispatching all 3 omniscience tools."""
        res_lovable = brain.execute_tool("generate_lovable_app", {
            "prompt": "SaaS Churn and MRR Calculator"
        })
        self.assertTrue(res_lovable.get("success", False))

        res_figma = brain.execute_tool("generate_figma_design", {
            "component_name": "Analytics KPI Card"
        })
        self.assertTrue(res_figma.get("success", False))

        res_perp = brain.execute_tool("perplexity_search", {
            "query": "Quantum computing hardware"
        })
        self.assertTrue(res_perp.get("success", False))


if __name__ == "__main__":
    unittest.main()
