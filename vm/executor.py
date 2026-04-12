def run_code(code: str, test_code: str = ""):
    import sys
    try:
        shared_env = {}
        # Execute the fix code first in the shared environment
        exec(code, shared_env)
        
        # Execute the test verification code
        if test_code:
            exec(test_code, shared_env)
            
        return {"status": "success"}
    except Exception as e:
        print(f"Executor Error: {e}", file=sys.stderr)
        return {"status": "error", "error": str(e)}
