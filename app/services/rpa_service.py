import time
import logging
import os

logger = logging.getLogger(__name__)

# Handle headless environments where pyautogui might fail to import
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except Exception as e:
    logger.warning(f"pyautogui not available (likely headless environment): {e}")
    PYAUTOGUI_AVAILABLE = False

def type_docstring(docstring: str):
    """
    Uses pyautogui to ghost-type the docstring directly into the active editor.
    """
    if not PYAUTOGUI_AVAILABLE:
        logger.error("RPA typing requested but pyautogui is not available.")
        return

    try:
        # 1. Move to the end of the selection/line
        # Pressing 'right' unselects highlighted text and puts cursor at end.
        pyautogui.press('right')
        time.sleep(0.1)
        
        # 2. Enter to create a new line inside the function
        pyautogui.press('enter')
        time.sleep(0.1)
        
        # 3. Type opening quotes
        pyautogui.write('"""\n', interval=0.01)
        time.sleep(0.1)
        
        # 4. Ghost type the generated docstring
        pyautogui.write(docstring, interval=0.01) 
        time.sleep(0.1)
        
        # 5. Type closing quotes
        pyautogui.write('\n"""\n', interval=0.01)
        
        logger.info("Successfully ghost-typed docstring.")
        
    except Exception as e:
        logger.error(f"Error during RPA typing: {e}")
