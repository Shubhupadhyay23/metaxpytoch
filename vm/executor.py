def run_code(code: str):
    try:
        local_env = {}
        exec(code, {}, local_env)
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
