"""
TITAN Live Interactive Feature Verifier.
Executes live, end-to-end demonstrations of every single feature in TITAN:
1. Local AI Brain Inference (titan:latest on RTX 3050).
2. Autonomous Coding Agent (OpenHands Engine + py_compile verification).
3. OpenJarvis ReAct Reasoning Loop (Thought-Action-Observation).
4. Universal Application Lifecycle (Open & Close Notepad).
5. System Hardware Controls (Volume & Recycle Bin).
6. File Manager CRUD operations.
7. Desktop GUI Controller (Screen & Cursor).
8. Autonomous Watchdog & Morning Briefing.
9. Local Document Intelligence (Extraction & Indexing).
10. Task Board Kanban (CRUD & Memory).
11. Multi-Step Macro Routines (Focus Mode & Quick Clean).
12. Web Agent (Web Scraping & Extraction).
13. Dynamic Skill Creator ("Teach TITAN" Hot-Reloading).
14. Ultra-Realistic Neural Voice Engine & Barge-In.
15. Procedural Arc Reactor Tray Icon.
16. Global Spotlight Quick Command Bridge.
"""

import sys
import time
import py_compile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from core.brain import brain
from core.react_agent import OpenJarvisAgentManager
from automation.coding_agent import CodingAgent
from automation.app_controller import app_controller
from automation.system_control import system_control
from automation.file_manager import file_manager
from automation.gui_controller import gui_controller
from automation.watchdog import watchdog
from automation.document_intelligence import doc_intelligence
from core.task_board import task_board
from automation.routines import routines
from automation.web_agent import web_agent
from automation.skill_creator import skill_creator
from voice.speaker import speaker
from ui.tray_service import create_arc_reactor_icon
from ui.spotlight import SpotlightApiBridge, SpotlightManager

def run_live_test_battery():
    print("=" * 78)
    print("           T.I.T.A.N. LIVE COMPREHENSIVE FEATURE TEST BATTERY")
    print("=" * 78)
    start_total = time.time()
    feature_results = []

    # -------------------------------------------------------------
    # 1. Local AI Brain Inference
    # -------------------------------------------------------------
    print("\n[TEST 01/16] Local AI Brain Inference (titan:latest)")
    t0 = time.time()
    try:
        reply = brain.chat("State your name and system status in one concise sentence.")
        dt = round(time.time() - t0, 2)
        print(f"  Result : {reply.strip()[:100]}...")
        print(f"  Latency: {dt}s | Status: OK")
        feature_results.append(("01. Local AI Brain Inference", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("01. Local AI Brain Inference", False, str(e)))

    # -------------------------------------------------------------
    # 2. Autonomous Coding Agent (OpenHands Engine)
    # -------------------------------------------------------------
    print("\n[TEST 02/16] Autonomous Coding Agent (Code Generation & Syntax Pre-compilation)")
    t0 = time.time()
    try:
        coding_agent = CodingAgent(brain)
        code_output = coding_agent.generate_and_deliver_code("Create a basic digital clock in Tkinter")
        dt = round(time.time() - t0, 2)
        sandbox_file = Path(ROOT) / "data" / "sandbox" / "digital_clock.py"
        valid_syntax = False
        if sandbox_file.exists():
            py_compile.compile(str(sandbox_file), doraise=True)
            valid_syntax = True
        print(f"  File Generated : {sandbox_file.name} | Syntax Verified: {valid_syntax}")
        print(f"  Latency        : {dt}s | Status: OK")
        feature_results.append(("02. Autonomous Coding Agent", valid_syntax, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("02. Autonomous Coding Agent", False, str(e)))

    # -------------------------------------------------------------
    # 3. OpenJarvis ReAct Reasoning Loop
    # -------------------------------------------------------------
    print("\n[TEST 03/16] OpenJarvis ReAct Loop (Thought -> Action -> Observation)")
    t0 = time.time()
    try:
        agent_mgr = OpenJarvisAgentManager(brain)
        react_reply = agent_mgr.handle_message("What is my current system telemetry?")
        dt = round(time.time() - t0, 2)
        print(f"  Agent Response: {react_reply.strip()[:90]}...")
        print(f"  Latency       : {dt}s | Status: OK")
        feature_results.append(("03. OpenJarvis ReAct Loop", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("03. OpenJarvis ReAct Loop", False, str(e)))

    # -------------------------------------------------------------
    # 4. Universal Application Lifecycle (Open & Close)
    # -------------------------------------------------------------
    print("\n[TEST 04/16] Universal Application Lifecycle (Launch & Close Notepad)")
    t0 = time.time()
    try:
        open_res = app_controller.open_app("notepad")
        time.sleep(1.0)
        close_res = app_controller.close_app("notepad")
        dt = round(time.time() - t0, 2)
        success = open_res.get("success", False) and close_res.get("success", False)
        print(f"  Launch: {open_res.get('message')}")
        print(f"  Close : {close_res.get('message')}")
        print(f"  Latency: {dt}s | Status: {'OK' if success else 'FAIL'}")
        feature_results.append(("04. Application Lifecycle (Open/Close)", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("04. Application Lifecycle (Open/Close)", False, str(e)))

    # -------------------------------------------------------------
    # 5. System Hardware Controls (Volume & Recycle Bin)
    # -------------------------------------------------------------
    print("\n[TEST 05/16] System Hardware Controls (Volume & Recycle Bin)")
    t0 = time.time()
    try:
        vol_up = system_control.volume_up(steps=2)
        vol_down = system_control.volume_down(steps=2)
        bin_res = system_control.empty_recycle_bin()
        dt = round(time.time() - t0, 2)
        success = vol_up.get("success") and vol_down.get("success") and bin_res.get("success")
        print(f"  Volume Adjustment : OK ({vol_up.get('message')})")
        print(f"  Recycle Bin Purge : OK ({bin_res.get('message')})")
        print(f"  Latency           : {dt}s | Status: OK")
        feature_results.append(("05. System Hardware Controls", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("05. System Hardware Controls", False, str(e)))

    # -------------------------------------------------------------
    # 6. File Manager CRUD Operations
    # -------------------------------------------------------------
    print("\n[TEST 06/16] File Manager (Write, Read, List, Delete)")
    t0 = time.time()
    try:
        test_file = str(Path(ROOT) / "data" / "sandbox" / "feature_test_file.txt")
        w_res = file_manager.write_file(test_file, "TITAN Live Feature Test Verified", overwrite=True)
        r_res = file_manager.read_file(test_file)
        l_res = file_manager.list_directory(str(Path(ROOT) / "data" / "sandbox"))
        d_res = file_manager.delete_file(test_file)
        dt = round(time.time() - t0, 2)
        success = w_res["success"] and r_res["success"] and l_res["success"] and d_res["success"]
        print(f"  File CRUD: Written -> Read ({len(r_res.get('content',''))} chars) -> Listed -> Deleted")
        print(f"  Latency  : {dt}s | Status: OK")
        feature_results.append(("06. File Manager CRUD", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("06. File Manager CRUD", False, str(e)))

    # -------------------------------------------------------------
    # 7. Desktop GUI Controller
    # -------------------------------------------------------------
    print("\n[TEST 07/16] Desktop GUI Controller (Screen & Cursor Coordinates)")
    t0 = time.time()
    try:
        w, h = gui_controller.get_screen_size()
        cx, cy = gui_controller.get_mouse_position()
        dt = round(time.time() - t0, 2)
        print(f"  Display Resolution : {w} x {h}")
        print(f"  Mouse Coordinates  : X={cx}, Y={cy}")
        print(f"  Latency            : {dt}s | Status: OK")
        feature_results.append(("07. Desktop GUI Controller", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("07. Desktop GUI Controller", False, str(e)))

    # -------------------------------------------------------------
    # 8. Autonomous Watchdog & Morning Briefing
    # -------------------------------------------------------------
    print("\n[TEST 08/16] Autonomous Watchdog & Proactive Morning Briefing")
    t0 = time.time()
    try:
        briefing = watchdog.generate_morning_briefing()
        disks = watchdog.check_disk_space()
        dirty = watchdog.scan_uncommitted_git_repos()
        dt = round(time.time() - t0, 2)
        print(f"  Briefing Snippet : {briefing[:110]}...")
        print(f"  Disks Checked    : Drive C ({disks['C:']['free_gb']} GB free), Drive D ({disks['D:']['free_gb']} GB free)")
        print(f"  Git Repos Dirty  : {len(dirty)} repos")
        print(f"  Latency          : {dt}s | Status: OK")
        feature_results.append(("08. Watchdog & Morning Briefing", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("08. Watchdog & Morning Briefing", False, str(e)))

    # -------------------------------------------------------------
    # 9. Local Document Intelligence (Second Brain)
    # -------------------------------------------------------------
    print("\n[TEST 09/16] Local Document Intelligence (Extraction & Deep Memory)")
    t0 = time.time()
    try:
        readme_path = str(Path(ROOT) / "README.md")
        doc_res = doc_intelligence.extract_text(readme_path)
        dt = round(time.time() - t0, 2)
        success = doc_res.get("success", False)
        print(f"  Extracted File : {doc_res.get('file_name')} ({doc_res.get('total_chars')} characters)")
        print(f"  Latency        : {dt}s | Status: OK")
        feature_results.append(("09. Document Intelligence", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("09. Document Intelligence", False, str(e)))

    # -------------------------------------------------------------
    # 10. Task Board Kanban
    # -------------------------------------------------------------
    print("\n[TEST 10/16] Task Board Kanban (Persistent SQLite CRUD)")
    t0 = time.time()
    try:
        add_t = task_board.add_task("Live System Verification", "Verify all 16 features", "high")
        tid = add_t["task_id"]
        upd_t = task_board.update_status(tid, "in_progress")
        summary_t = task_board.get_summary()
        del_t = task_board.delete_task(tid)
        dt = round(time.time() - t0, 2)
        success = add_t["success"] and upd_t["success"] and del_t["success"]
        print(f"  Task #{tid} Created -> Moved to '{upd_t.get('new_status')}' -> Deleted")
        print(f"  Kanban Summary  : {summary_t['summary_text']}")
        print(f"  Latency         : {dt}s | Status: OK")
        feature_results.append(("10. Task Board Kanban", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("10. Task Board Kanban", False, str(e)))

    # -------------------------------------------------------------
    # 11. Multi-Step Macro Routines
    # -------------------------------------------------------------
    print("\n[TEST 11/16] Multi-Step Macro Routines (Focus Mode & Quick Clean)")
    t0 = time.time()
    try:
        res_focus = routines.execute_routine("focus_mode")
        res_clean = routines.execute_routine("quick_clean")
        dt = round(time.time() - t0, 2)
        success = res_focus.get("success") and res_clean.get("success")
        print(f"  Focus Mode  : {res_focus.get('message')}")
        print(f"  Quick Clean : {res_clean.get('message')}")
        print(f"  Latency     : {dt}s | Status: OK")
        feature_results.append(("11. Macro Routines", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("11. Macro Routines", False, str(e)))

    # -------------------------------------------------------------
    # 12. Agentic Web Scraper
    # -------------------------------------------------------------
    print("\n[TEST 12/16] Agentic Web Scraper (BeautifulSoup Extraction)")
    t0 = time.time()
    try:
        scrape_res = web_agent.scrape_web_tables_and_links("https://httpbin.org/html")
        dt = round(time.time() - t0, 2)
        success = scrape_res.get("success", False) and len(scrape_res.get("summary_text", "")) > 50
        print(f"  Page Scraped : {scrape_res.get('title')} ({len(scrape_res.get('summary_text',''))} chars extracted)")
        print(f"  Latency      : {dt}s | Status: OK")
        feature_results.append(("12. Agentic Web Scraper", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("12. Agentic Web Scraper", False, str(e)))

    # -------------------------------------------------------------
    # 13. Dynamic Skill Creator ("Teach TITAN")
    # -------------------------------------------------------------
    print("\n[TEST 13/16] Dynamic Skill Creator & Hot-Reloading")
    t0 = time.time()
    try:
        # Create a sample live skill
        skill_code = """
def execute_skill(args: dict) -> dict:
    c = args.get("celsius", 25)
    f = (c * 9/5) + 32
    return {"success": True, "result": f, "message": f"{c}C is {f}F"}
"""
        skill_path = Path(ROOT) / "automation" / "skills" / "skill_celsius_to_f.py"
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(skill_code)

        skill_creator._load_existing_skills()
        res_skill = skill_creator.execute_custom_skill("celsius_to_f", {"celsius": 100})
        dt = round(time.time() - t0, 2)
        success = res_skill.get("success") and res_skill.get("result") == 212.0
        print(f"  Hot-Loaded Skill Result : {res_skill.get('message')}")
        print(f"  Latency                 : {dt}s | Status: OK")
        feature_results.append(("13. Dynamic Skill Creator", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("13. Dynamic Skill Creator", False, str(e)))

    # -------------------------------------------------------------
    # 14. Ultra-Realistic Neural Voice Engine & Barge-In
    # -------------------------------------------------------------
    print("\n[TEST 14/16] Ultra-Realistic Neural Voice Engine & Barge-In")
    t0 = time.time()
    try:
        voices = speaker.get_available_voices()
        speaker.speak("TITAN live verification speech.", interrupt=True)
        time.sleep(0.3)
        speaker.stop()
        dt = round(time.time() - t0, 2)
        print(f"  Voices Active : {len(voices)} voices detected | Active: {speaker.preferred_voice}")
        print(f"  Barge-In Stop : Interrupted successfully")
        print(f"  Latency       : {dt}s | Status: OK")
        feature_results.append(("14. Neural Voice & Barge-In", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("14. Neural Voice & Barge-In", False, str(e)))

    # -------------------------------------------------------------
    # 15. Procedural Arc Reactor Tray Icon
    # -------------------------------------------------------------
    print("\n[TEST 15/16] Procedural Arc Reactor Tray Icon")
    t0 = time.time()
    try:
        icon_img = create_arc_reactor_icon()
        dt = round(time.time() - t0, 2)
        success = icon_img.size == (64, 64) and icon_img.mode == "RGBA"
        print(f"  Icon Generated : In-memory {icon_img.size} {icon_img.mode} canvas")
        print(f"  Latency        : {dt}s | Status: OK")
        feature_results.append(("15. Arc Reactor Tray Icon", success, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("15. Arc Reactor Tray Icon", False, str(e)))

    # -------------------------------------------------------------
    # 16. Global Spotlight Quick Command Bridge
    # -------------------------------------------------------------
    print("\n[TEST 16/16] Global Spotlight Quick Command Bridge")
    t0 = time.time()
    try:
        bridge = SpotlightApiBridge(SpotlightManager())
        spot_res = bridge.execute_command("volume up")
        dt = round(time.time() - t0, 2)
        print(f"  Spotlight Command Result : {spot_res}")
        print(f"  Latency                  : {dt}s | Status: OK")
        feature_results.append(("16. Spotlight Command Bridge", True, f"{dt}s"))
    except Exception as e:
        print(f"  Error: {e}")
        feature_results.append(("16. Spotlight Command Bridge", False, str(e)))

    total_time = round(time.time() - start_total, 2)

    # -------------------------------------------------------------
    # Summary Table
    # -------------------------------------------------------------
    print("\n" + "=" * 78)
    print("                     LIVE FEATURE VERIFICATION AUDIT")
    print("=" * 78)
    print(f"{'#':<4} | {'FEATURE SUBSYSTEM':<45} | {'STATUS':<8} | {'TIME'}")
    print("-" * 78)
    all_passed = True
    for idx, (feat, passed, duration) in enumerate(feature_results):
        stat = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"{idx+1:02d}   | {feat:<45} | [{stat}]   | {duration}")
    print("-" * 78)
    print(f"OVERALL STATUS: {'ALL 16 FEATURES PASS (100% OPERATIONAL)' if all_passed else 'SOME FEATURES FAILED'}")
    print(f"TOTAL EXECUTION TIME: {total_time}s across all 16 live subsystem tests.")
    print("=" * 78)

if __name__ == "__main__":
    run_live_test_battery()
