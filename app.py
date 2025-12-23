#!/usr/bin/env python3
"""
TadqeeqAI v3.0 - Application Entry Point
=========================================
Minimal entry point that imports backend and UI, then launches the app.
Includes Windows-specific fix for frameless window maximization.
"""

import webview
import ctypes
from ctypes import windll
from backend import API
from ui import HTML

def fix_window_behavior(window):
    try:
        import ctypes
        from ctypes import windll
        
        # FIX: Convert .NET Handle to Python Integer
        hwnd = window.native.Handle.ToInt64()
        
        # Windows Style Constants
        GWL_STYLE = -16
        WS_THICKFRAME = 0x00040000 
        WS_CAPTION = 0x00C00000
        
        current_style = windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
        new_style = (current_style | WS_THICKFRAME) & ~WS_CAPTION
        windll.user32.SetWindowLongW(hwnd, GWL_STYLE, new_style)
        
        # Force Redraw
        windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0237)
        print("Window style patched successfully.")
    except Exception as e:
        print(f"Window patch failed: {e}")

def main():
    """Launch TadqeeqAI application."""
    print("\n" + "=" * 50)
    print("   TadqeeqAI v3.0")
    print("   Hybrid Search: BM25 + Semantic")
    print("   SAMA + CMA · English + Arabic")
    print("   Document Analysis · Export")
    print("=" * 50 + "\n")
    
    # Create API instance
    api = API()
    
    # Create window
    window = webview.create_window(
        title='TadqeeqAI',
        html=HTML,
        js_api=api,
        width=1200,
        height=800,
        min_size=(900, 600),
        background_color='#0f172a',
        text_select=True,
    )
    
    # Set window reference for file dialogs
    api.set_window(window)
    
    # Start the application with the fix function
    # Passing 'window' as an argument to the fix function
    webview.start(fix_window_behavior, window, debug=False)

if __name__ == '__main__':
    main()