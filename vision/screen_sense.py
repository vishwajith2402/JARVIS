"""
Live Vision Screen Sense & Instant Screen Debugger for TITAN.
Captures screen/active window, inspects errors or code with Moondream vision model,
and automatically generates verified fixes using the CodingAgent.
100% Free & Local.
"""

from typing import Any, Dict, Optional
from vision.visual_analyzer import visual_analyzer
from automation.coding_agent import CodingAgent
from core.brain import brain
from voice.speaker import speaker


class ScreenSenseDebugger:
    def __init__(self):
        self.coding_agent = CodingAgent(brain)

    def debug_screen(self, user_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        End-to-end screen debugging:
        1. Captures current screen.
        2. Prompts local vision model to pinpoint errors, stack traces, and software state.
        3. Generates complete code/command fix and saves to sandbox.
        """
        prompt = (
            "Examine this screen screenshot closely. "
            "Identify any error messages, terminal exceptions, stack traces, compiler errors, or broken code. "
            "Transcribe the exact error text and indicate what file or application caused it."
        )
        if user_hint:
            prompt += f" User context hint: {user_hint}"

        # Step 1: Visual Inspection
        analysis_res = visual_analyzer.analyze_screen(prompt=prompt)
        if not analysis_res.get("success"):
            return {
                "success": False,
                "error": analysis_res.get("error", "Vision analysis failed.")
            }

        screen_diagnosis = analysis_res.get("analysis", "")
        file_path = analysis_res.get("image_path", "")

        # Step 2: Formulate solution using CodingAgent
        repair_prompt = (
            f"Based on the following visual screen diagnosis of an error on the user's PC, "
            f"explain the root cause and provide the complete corrected code or terminal command fix:\n\n"
            f"Screen Diagnosis:\n{screen_diagnosis}"
        )

        solution = self.coding_agent.generate_and_deliver_code(repair_prompt)

        feedback_msg = "Screen analyzed, Sir. I have identified the issue and formulated the solution."
        speaker.speak(feedback_msg)

        return {
            "success": True,
            "image_path": file_path,
            "diagnosis": screen_diagnosis,
            "solution": solution,
            "message": feedback_msg
        }


screen_sense = ScreenSenseDebugger()
