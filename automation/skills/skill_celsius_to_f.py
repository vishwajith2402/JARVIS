
def execute_skill(args: dict) -> dict:
    c = args.get("celsius", 25)
    f = (c * 9/5) + 32
    return {"success": True, "result": f, "message": f"{c}C is {f}F"}
