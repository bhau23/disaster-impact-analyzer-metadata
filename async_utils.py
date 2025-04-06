import asyncio
import os
import nest_asyncio
import platform
import sys

def get_or_create_eventloop():
    """Get the current event loop or create a new one if needed."""
    try:
        return asyncio.get_event_loop()
    except RuntimeError as ex:
        if "There is no current event loop in thread" in str(ex):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop
        else:
            raise

def setup_asyncio_patch():
    """Apply nest_asyncio patch if running in a Jupyter/IPython or Streamlit environment.
    This allows nested event loops to run."""
    try:
        nest_asyncio.apply()
        print("✓ nest_asyncio patch applied successfully")
        return True
    except Exception as e:
        print(f"× Failed to apply nest_asyncio patch: {e}")
        return False

def diagnose_asyncio_environment():
    """Print helpful diagnostics about the current asyncio environment."""
    print("\n=== AsyncIO Environment Diagnostics ===")
    print(f"Python version: {platform.python_version()}")
    print(f"OS: {platform.system()} {platform.release()}")
    
    try:
        loop = asyncio.get_event_loop()
        print(f"Current event loop: {loop}")
        print(f"Loop is running: {loop.is_running()}")
        print(f"Loop is closed: {loop.is_closed()}")
    except RuntimeError as e:
        print(f"Event loop error: {e}")
    
    # Check for IPython/Jupyter environment
    is_ipython = 'IPython' in sys.modules
    print(f"Running in IPython/Jupyter: {is_ipython}")
    
    # Check for Streamlit
    is_streamlit = 'streamlit' in sys.modules
    print(f"Running in Streamlit: {is_streamlit}")
    
    print("=" * 40)
