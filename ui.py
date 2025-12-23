"""
TadqeeqAI v3.0 - UI
===================
Complete HTML, CSS, and JavaScript for the PyWebView interface.
Merged: Spatial Glass UI + Original Full Logic
"""

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TadqeeqAI v3.0 | Spatial</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {
            /* --- DARK MODE (Deep Teal World + Navy Glass) --- */
            
            /* The Background: Rich Deep Teal */
            --bg-color: #0f172a; /* Fallback */
            --bg-gradient: linear-gradient(135deg, #115e59 0%, #022c22 100%);

            /* The Panels: Navy Blue, but 60% Opacity for Glass Effect */
            --glass-bg: rgba(2, 6, 23, 0.6); 
            
            /* The Blur: Standard blur, slight saturation boost for vibrancy */
            --glass-blur: blur(20px) saturate(140%);
            
            /* The Border: Thin white line defines the glass edge */
            --glass-border: 1px solid rgba(255, 255, 255, 0.1);
            --glass-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            
            /* Text & Accents */
            --text: #f8fafc;
            --text2: #cbd5e1;
            --text3: #64748b;
            --accent: #2dd4bf; /* Teal-400 */
            --accent-glow: rgba(45, 212, 191, 0.3);
            
            --sama: #60a5fa; /* Blue-400 */
            --cma: #4ade80;  /* Green-400 */
            --danger: #f87171;
            
            /* Components */
            --bubble-user: linear-gradient(135deg, #0d9488, #0f766e);
            --bubble-ai: rgba(255, 255, 255, 0.03);
            --bubble-ai-text: #e2e8f0;
            --bubble-ai-border: 1px solid rgba(255, 255, 255, 0.05);
            
            --card-bg: rgba(15, 23, 42, 0.6); /* Matches glass tint */
            --card-item-hover: rgba(255, 255, 255, 0.05);
            
            --dropdown-bg: #1e293b;
            --input-box-bg: rgba(15, 23, 42, 0.8);
            
            --scrollbar-thumb: rgba(255, 255, 255, 0.1);
            --bg2: rgba(255, 255, 255, 0.05);
            --bg3: rgba(255, 255, 255, 0.1);
            --bg4: rgba(255, 255, 255, 0.15);
            --border: rgba(255, 255, 255, 0.1);
            --score-color: #2dd4bf;
            --score-dim: rgba(45, 212, 191, 0.2);
        }

        [data-theme="light"] {
            /* --- LIGHT MODE (Teal World + White Glass) --- */
            
            /* 1. BACKGROUND: REMOVED to inherit Deep Teal from :root */
            /* --bg-color & --bg-gradient are now shared with Dark Mode */
            
            /* 2. PANELS: Milky White Glass */
            /* Increased opacity to 0.85 so dark text is readable against the dark teal background */
            --glass-bg: rgba(255, 255, 255, 0.85);
            
            /* Blur: Keeping it soft */
            --glass-blur: blur(25px) saturate(110%);
            
            /* Border: Crisp Dark Grey for definition */
            --glass-border: 1px solid rgba(0, 0, 0, 0.1); 
            
            /* Shadow: Soft lift */
            --glass-shadow: 0 20px 40px -5px rgba(0, 0, 0, 0.1);
            
            /* Text & Icons (Dark Navy) */
            --text: #0f172a;
            --text2: #334155;
            --text3: #64748b;
            
            --accent: #0d9488; /* Teal-600 */
            --accent-glow: rgba(13, 148, 136, 0.2);
            --sama: #2563eb;
            --cma: #16a34a;
            --danger: #dc2626;
            
            /* Components */
            --bubble-user: linear-gradient(135deg, #0d9488, #115e59);
            --bubble-ai: rgba(255, 255, 255, 0.6);
            --bubble-ai-text: #0f172a;
            --bubble-ai-border: 1px solid rgba(0, 0, 0, 0.08);
            
            --card-bg: rgba(255, 255, 255, 0.9);
            --card-item-hover: rgba(0, 0, 0, 0.04);
            
            --dropdown-bg: #ffffff;
            --input-box-bg: rgba(255, 255, 255, 0.8);
            
            --scrollbar-thumb: rgba(0, 0, 0, 0.2);
            
            /* UI Elements & Borders */
            --bg2: rgba(0, 0, 0, 0.04);
            --bg3: rgba(0, 0, 0, 0.08);
            --bg4: rgba(0, 0, 0, 0.12);
            
            /* Button Outlines */
            --border: rgba(0, 0, 0, 0.15); 
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            color: var(--text);
            height: 100vh;
            display: flex;
            overflow: hidden;
            background: var(--bg-gradient);
            background-size: 400% 400%;
            /*animation: meshFlow 25s ease infinite;*/
            transition: background 0.8s ease;
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { 
            background: var(--scrollbar-thumb); 
            border-radius: 10px; 
            border: 2px solid transparent;
            background-clip: content-box;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--text3); }

        @keyframes meshFlow {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }


        /* --- Master Layout & Visuals --- */
        .sidebar, .main {
            /* 1. Positioning (Native Window Mode) */
            margin: 12px;                 /* Equal gap on all sides */
            height: calc(100vh - 24px);   /* Full height minus top/bottom margins */
            
            /* 2. Visuals (The "Glass Card" Look) */
            border-radius: 24px;
            background: var(--glass-bg);
            backdrop-filter: var(--glass-blur);
            -webkit-backdrop-filter: var(--glass-blur);
            border: var(--glass-border);
            box-shadow: var(--glass-shadow);
            
            /* 3. GPU acceleration */
            transform: translateZ(0);
        }

        .sidebar { 
            width: 300px; 
            display: flex; 
            flex-direction: column; 
            margin-right: 6px; 
            flex-shrink: 0;
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
            position: relative;
            z-index: 10;
            /* Smooth slide transition */
            transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* Sidebar slides left - content stays intact, no squishing */
        .sidebar.collapsed { 
            transform: translateX(calc(-100% - 12px));
            pointer-events: none;
        }
        
        /* Main panel slides over to cover sidebar area */
        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            margin-left: 6px;
            overflow: hidden;
            position: relative;
            z-index: 20; /* Above sidebar so it covers it */
            transition: 
                margin-left 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        /* When sidebar is collapsed, main stretches to fill the space symmetrically */
        /* Sidebar width (300px) + sidebar left margin (12px) + gap (6px) - desired left margin (12px) = 306px */
        .sidebar.collapsed + .main {
            margin-left: calc(-300px - 12px + 6px); /* Results in 12px left margin, matching right */
        }
        
        .sidebar-header { padding: 24px 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.06); }
        [data-theme="light"] .sidebar-header { border-bottom: 1px solid rgba(0, 0, 0, 0.06); }
        .logo { display: flex; align-items: center; gap: 14px; margin-bottom: 20px; }
        .logo-icon-sidebar {
            width: 42px; height: 42px;
            background: linear-gradient(135deg, var(--accent), #0d9488);
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 8px 24px rgba(0, 212, 170, 0.25);
            animation: subtlePulse 3s ease-in-out infinite;
        }
        @keyframes subtlePulse {
            0%, 100% { box-shadow: 0 8px 24px rgba(0, 212, 170, 0.25); }
            50% { box-shadow: 0 8px 32px rgba(0, 212, 170, 0.35); }
        }
        .logo-icon-sidebar svg { width: 22px; height: 22px; fill: white; }
        .logo-text-group { display: flex; flex-direction: column; }
        .logo-text { 
            font-size: 17px; 
            font-weight: 800; 
            letter-spacing: -0.02em; 
            color: var(--text);
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
            background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .logo-sub { 
            font-size: 10px; 
            color: var(--text3); 
            text-transform: uppercase; 
            letter-spacing: 0.08em;
            font-weight: 600;
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
            margin-top: 2px;
        }
        
        .new-chat-btn {
            width: 100%; padding: 12px;
            background: var(--bg2);
            border-radius: 100px; 
            border: 1px solid var(--border);
            color: var(--text); font-weight: 600; font-size: 14px;
            display: flex; align-items: center; justify-content: center; gap: 10px;
            cursor: pointer; transition: 0.3s ease;
        }
        .new-chat-btn:hover { background: rgba(255, 255, 255, 0.18); border-color: var(--accent); transform: scale(1.02); }
        
        [data-theme="light"] .new-chat-btn:hover {
            border-color: var(--accent) !important;
            background: rgba(0, 212, 170, 0.1);
            color: var(--accent);
        }
        .new-chat-btn svg { stroke: currentColor; }

        /* History & Meatball Menu */
        .chat-history { flex: 1; overflow-y: auto; padding: 12px; }
        .history-title { font-size: 11px; color: var(--text3); text-transform: uppercase; letter-spacing: 0.15em; padding: 12px; font-weight: 700; }
        .history-item {
            padding: 10px 14px; border-radius: 14px; margin-bottom: 6px;
            color: var(--text2); font-size: 13.5px; cursor: pointer;
            transition: 0.2s ease; display: flex; align-items: center; justify-content: space-between;
            position: relative;
            background: transparent;
            border: 1px solid transparent;
        }
        .history-item:hover { background: rgba(255, 255, 255, 0.1); color: var(--text); }
        [data-theme="light"] .history-item:hover { background: rgba(0,0,0,0.05); }
        
        .history-item.active { background: rgba(0, 212, 170, 0.12); color: var(--text); border: 1px solid rgba(0, 212, 170, 0.2); }
        .history-item.active::before { display: none; } /* Remove old side bar */
        
        .history-item-menu {
            opacity: 0; width: 28px; height: 28px; border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: 0.2s ease;
        }
        .history-item:hover .history-item-menu { opacity: 1; }
        .history-item-menu:hover { background: rgba(255, 255, 255, 0.1); }
        .history-item-menu svg { width: 16px; height: 16px; fill: var(--text3); }

        .dropdown {
            position: absolute; right: 10px; top: 100%; 
            margin-top: 8px;
            background: var(--dropdown-bg); 
            backdrop-filter: blur(20px);
            border: var(--glass-border); border-radius: 12px;
            padding: 6px; z-index: 9999; display: none; min-width: 130px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        [data-theme="light"] .dropdown { box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
        .dropdown.show { display: block; }
        .dropdown-item {
            display: flex; align-items: center; gap: 8px; padding: 8px 12px;
            font-size: 12px; color: var(--danger); border-radius: 8px;
            cursor: pointer; transition: 0.15s ease;
        }
        .dropdown-item:hover { background: rgba(255, 81, 73, 0.1); }
        .dropdown-item svg { width: 14px; height: 14px; stroke: currentColor; fill: none; }

        /* Delete animation - completely separate, only applied via JS after modal confirm */
        @keyframes chatDeleteSlide {
            0% { transform: translateX(0); opacity: 1; }
            100% { transform: translateX(-40px); opacity: 0; }
        }
        .history-item.chat-deleting {
            animation: chatDeleteSlide 0.3s ease forwards;
            pointer-events: none;
        }

        .header {
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
        }

        /* Add this new rule below it to ensure buttons are still clickable */
        .header button,
        .header .header-btn,
        .header .menu-btn {
            -webkit-app-region: no-drag;
        }
        .header-title { 
            font-size: 14px; 
            font-weight: 700; 
            color: var(--text);
            letter-spacing: -0.02em; 
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .header-title-badge {
            font-size: 9px;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            line-height: 1;
            display: inline-flex;
            align-items: center;
            height: auto;
            flex-shrink: 0;
        }
        .header-title-badge.chat {
            background: rgba(45, 212, 191, 0.15);
            color: var(--accent);
        }
        .header-title-badge.analysis {
            background: rgba(139, 92, 246, 0.15);
            color: #a78bfa;
        }

        /* --- SIDEBAR TOGGLE (Updated) --- */
        .menu-btn {
            /* 1. Dimensions: Match the Theme Toggle size */
            width: 40px; 
            height: 40px; 
            min-width: 40px; /* Prevent squashing */
            
            /* 2. Shape: Perfect Circle */
            border-radius: 50% !important; 
            
            /* 3. Visuals */
            display: flex !important;
            align-items: center;
            justify-content: center;
            background: var(--bg2);
            border: 1px solid var(--border);
            cursor: pointer;
            color: var(--text);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        
        /* Hover Effect: Subtle scaling like the other buttons */
        .menu-btn:hover { 
            background: rgba(255, 255, 255, 0.1); 
            border-color: var(--accent);
            transform: scale(1.05);
        }
        
        /* --- ANIMATED MENU ICON --- */
        .menu-btn svg {
            width: 20px; 
            height: 20px; 
            stroke: currentColor; 
            display: block;
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            transform-origin: center center;
        }

        /* The Collapsed State - Flip 180° from left downward */
        .menu-btn.closed svg {
            transform: rotate(180deg);
        }

        /* Fixed Button Layout */
        .header-btn, .modal-btn {
            padding: 10px 20px; 
            border-radius: 100px; 
            font-size: 13px; 
            font-weight: 600;
            border: 1px solid var(--border); 
            background: var(--bg2);
            color: var(--text); 
            cursor: pointer; 
            transition: 0.3s ease; 
            display: flex; align-items: center; 
            gap: 8px;
            white-space: nowrap; /* Prevents text from wrapping */
            flex-shrink: 0;      /* Prevents button from getting squashed */
            user-select: none;
        }
        
        /* New Rule: Size the icons inside header buttons */
        .header-btn svg { 
            width: 16px; 
            height: 16px; 
            stroke: currentColor; 
            fill: none; 
        }
        .header-btn:hover { background: rgba(255, 255, 255, 0.15); border-color: var(--accent); }
        
        [data-theme="light"] .header-btn:hover,
        [data-theme="light"] .menu-btn:hover { 
            border-color: var(--accent) !important;
            background: rgba(0, 212, 170, 0.1);
            color: var(--accent);
        }
        .header-btn.primary { background: var(--bubble-user); border: none; color: white; box-shadow: 0 4px 15px rgba(0, 212, 170, 0.3); }
        
        /* Analysis Save Button - Animated Entry */
        #analysisSaveBtn {
            transform: translateX(20px) scale(0.8);
            opacity: 0;
            transition: 
                transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1),
                opacity 0.3s ease;
        }
        #analysisSaveBtn[style*="display: flex"] {
            transform: translateX(0) scale(1);
            opacity: 1;
            animation: saveButtonPop 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        @keyframes saveButtonPop {
            0% { transform: translateX(20px) scale(0.8); opacity: 0; }
            100% { transform: translateX(0) scale(1); opacity: 1; }
        }
        
        /* --- DYNAMIC HEADER ACTIONS --- */
        
        /* Wrapper to handle the sliding layout */
        .header-actions {
            display: flex;
            align-items: center;
            gap: 12px; /* Spacing between Export and New Chat */
        }

        /* The Header's "New Chat" Button (Hidden by default) */
        #newChatBtnHeader {
            /* 1. Layout: Zero width/padding means it takes no space */
            max-width: 0;
            padding: 0;
            border-width: 0;
            margin-left: 0;
            overflow: hidden;
            opacity: 0;
            white-space: nowrap;
            
            /* 2. Position: Start slightly right and small */
            transform: translateX(20px) scale(0.8);
            
            /* 3. The Spring Physics */
            transition: 
                max-width 0.5s cubic-bezier(0.2, 0.8, 0.2, 1),      /* Smooth slide for Export button */
                padding 0.5s cubic-bezier(0.2, 0.8, 0.2, 1),        /* Smooth resize */
                opacity 0.3s ease,
                transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);   /* The BOUNCE/JUMP effect */
        }

        /* The Visible State (Added via JS when sidebar hides) */
        #newChatBtnHeader.visible {
            max-width: 150px;       /* Enough space for text */
            padding: 10px 20px;     /* Restore original padding */
            border-width: 1px;      /* Restore border */
            opacity: 1;
            transform: translateX(0) scale(1); /* Land perfectly */
        }
        
        /* Export Menu */
        .export-menu {
            position: absolute; right: 0; top: 100%; margin-top: 8px;
            background: var(--dropdown-bg); backdrop-filter: blur(20px);
            border: var(--glass-border); border-radius: 12px;
            padding: 6px; z-index: 1000; display: none; min-width: 160px;
            box-shadow: var(--glass-shadow);
        }
        .export-menu.show { display: block; }
        .export-item {
            display: flex; align-items: center; gap: 8px; padding: 10px;
            font-size: 13px; color: var(--text); border-radius: 8px;
            cursor: pointer; transition: 0.15s ease;
        }
        .export-item:hover { background: var(--bg4); }
        .export-item svg { 
            width: 16px; 
            height: 16px; 
            stroke: currentColor; 
            fill: none; 
            stroke-width: 2;
        }

        /* Chat Layout */
        .chat { 
            flex: 1; 
            overflow-y: auto; 
            padding: 32px; 
            padding-bottom: 140px; 
            scroll-behavior: smooth;
            -webkit-mask-image: linear-gradient(to bottom, black 85%, transparent 100%);
            mask-image: linear-gradient(to bottom, black 85%, transparent 100%);
        }

        .msg { 
            display: flex; gap: 14px; margin-bottom: 28px; max-width: 75%; 
            width: fit-content;
            animation: springIn 0.5s var(--spring); 
            position: relative;
        }
        .msg.user { margin-left: auto; flex-direction: row-reverse; }
        .msg.assistant { margin-right: auto; text-align: left; }

        .msg-text {
            padding: 14px 20px; line-height: 1.6; font-size: 14px;
            border-radius: 18px; transition: background 0.3s ease;
            text-align: left;
        }
        .msg.user .msg-text {
            background: var(--bubble-user);
            color: #ffffff;
            border-radius: 20px 20px 4px 20px;
            box-shadow: 0 4px 15px rgba(0, 212, 170, 0.2);
        }
        .msg.assistant .msg-text {
            background: var(--bubble-ai);
            color: var(--bubble-ai-text);
            border: var(--bubble-ai-border);
            border-radius: 20px 20px 20px 4px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        /* Markdown Styles */
        .msg-text p { margin-bottom: 10px; }
        .msg-text p:last-child { margin-bottom: 0; }
        .msg-text strong { color: var(--accent); font-weight: 600; }
        .msg.user .msg-text strong { color: white; }
        .msg-text ul, .msg-text ol { margin: 10px 0; padding-left: 20px; }
        
        /* --- COPY BUTTON ANIMATIONS --- */
        .msg-copy {
            position: absolute; top: -10px; right: -10px; opacity: 0;
            width: 28px; height: 28px; 
            background: var(--bg3);
            border: 1px solid var(--border); border-radius: 8px;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
            color: var(--text3); /* Default Gray */
            z-index: 10;
        }
        /* Show on hover */
        .msg:hover .msg-copy { opacity: 1; transform: translateY(0); }
        .msg-copy:hover { background: var(--bg4); color: var(--text); }
        
        /* Active State (Clicked) */
        .msg-copy:active { transform: scale(0.9); }

        /* COPIED STATE (Teal Success) */
        .msg-copy.copied {
            background: rgba(45, 212, 191, 0.15) !important;
            border-color: var(--accent) !important;
            color: var(--accent) !important;
            animation: splash 0.6s ease forwards;
        }

        /* Icon Animation */
        .msg-copy svg {
            width: 14px; height: 14px; stroke-width: 2;
            transition: all 0.3s ease;
        }
        
        /* Splash Effect Ring */
        @keyframes splash {
            0% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(45, 212, 191, 0); }
            100% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0); }
        }

        /* Input Area Refinement */
        .input-area { 
            position: absolute; 
            bottom: 0; 
            left: 0; 
            width: 100%;
            padding: 20px 20px 32px;
            z-index: 100;
            background: transparent;
        }
        .input-area > div:last-child {
            user-select: none;
            cursor: default;
        }

        .input-box {
            max-width: 800px; margin: 0 auto;
            background: var(--input-box-bg);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 100px; 
            padding: 6px 6px 6px 8px; /* Fixed padding left */
            display: flex; align-items: center; 
            gap: 8px;
            box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            backdrop-filter: none; /* Removed distracting blur */
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
        }
        [data-theme="light"] .input-box {
            border-color: rgba(0, 0, 0, 0.15);
        }
        .input-box:focus-within { border-color: var(--accent); }

        .input-box textarea {
            flex: 1; background: transparent; border: none; color: var(--text);
            font-family: inherit; font-size: 14px; outline: none; resize: none; padding: 10px 0; max-height: 120px;
        }
        .send {
            width: 44px; height: 44px; border-radius: 50%; background: var(--accent);
            border: none; display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: 0.3s var(--spring);
            flex-shrink: 0;
        }
        .send svg { width: 22px; height: 22px; fill: #ffffff !important; }
        .send:hover:not(:disabled) { transform: scale(1.1); box-shadow: 0 0 20px rgba(0, 212, 170, 0.4); }

        .attach-btn {
            width: 36px; height: 36px; border-radius: 50%; background: rgba(255, 255, 255, 0.1);
            border: none; display: flex; align-items: center; justify-content: center;
            cursor: pointer; transition: 0.2s ease; color: var(--text2);
            flex-shrink: 0;
            margin: 0; /* Fixed Gap */
            padding: 0;
        }
        .attach-btn:hover { background: rgba(255, 255, 255, 0.2); transform: scale(1.05); }
        .attach-btn svg { width: 20px; height: 20px; stroke: var(--text2); stroke-width: 2.5; fill: none; }
        [data-theme="light"] .attach-btn { background: rgba(0,0,0,0.05); color: var(--text); }
        [data-theme="light"] .attach-btn svg { stroke: var(--text); }

        /* Theme Toggle & Avatar Icons */
        .theme-toggle-sidebar {
            background: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.1);
            width: 40px; height: 40px; border-radius: 50%; cursor: pointer;
            display: flex; align-items: center; justify-content: center; color: var(--text);
            transition: all 0.3s ease;
        }
        [data-theme="light"] .theme-toggle-sidebar { background: rgba(0,0,0,0.06); border-color: rgba(0,0,0,0.1); color: #1c1c1e; }
        .theme-toggle-sidebar:hover { transform: scale(1.1); border-color: var(--accent); }
        .theme-toggle-sidebar svg { 
            width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2.5; 
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .theme-toggle-sidebar:active svg { transform: rotate(360deg); }
        .avatar svg { width: 20px; height: 20px; fill: none; stroke: currentColor; stroke-width: 2.2; }
        
        /* Status Dot - Pulsing Green Light */
        .status-dot {
            width: 6px; height: 6px;
            background: #4ade80;
            border-radius: 50%;
            box-shadow: 0 0 8px #4ade80;
            animation: statusPulse 2s ease-in-out infinite;
        }
        @keyframes statusPulse {
            0%, 100% { opacity: 1; box-shadow: 0 0 8px #4ade80; }
            50% { opacity: 0.6; box-shadow: 0 0 4px #4ade80; }
        }

        /* Stats & Welcome */
        .welcome { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            height: 100%; 
            text-align: center;
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
            padding: 40px 20px;
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .welcome-icon {
            width: 100px; height: 100px;
            background: linear-gradient(135deg, var(--accent), #0d9488);
            border-radius: 32px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 32px;
            box-shadow: 0 20px 50px rgba(0, 212, 170, 0.3), 0 0 80px rgba(0, 212, 170, 0.15);
            animation: floatIcon 4s ease-in-out infinite;
        }
        .welcome-icon svg { width: 50px; height: 50px; fill: white; }
        .welcome-title {
            font-size: 38px; font-weight: 800; margin-bottom: 12px;
            background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
        }
        .welcome-subtitle {
            font-size: 15px; color: var(--text2); max-width: 480px; line-height: 1.7; margin-bottom: 8px;
        }
        .welcome-stats { 
            display: flex; 
            gap: 16px; 
            margin-top: 36px; 
            justify-content: center; 
            flex-wrap: wrap; 
        }
        .stat { 
            background: rgba(255, 255, 255, 0.04); 
            border: 1px solid rgba(255, 255, 255, 0.08); 
            border-radius: 20px; 
            padding: 20px 32px; 
            transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
            min-width: 100px;
        }
        .stat:hover {
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2), 0 0 20px rgba(45, 212, 191, 0.1);
        }
        [data-theme="light"] .stat {
            background: rgba(0, 0, 0, 0.03);
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        .stat-val { font-size: 32px; font-weight: 800; color: var(--accent); margin-bottom: 4px; }
        .stat-lbl { font-size: 10px; color: var(--text3); font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }

        /* Document Badge */
        .doc-badge {
            display: flex; align-items: center; gap: 10px;
            background: var(--bg3); padding: 10px 14px; border-radius: 100px;
            border: 1px solid var(--border);
            max-width: fit-content; margin: 0 auto;
        }
        .doc-badge svg { width: 18px; height: 18px; stroke: var(--accent); fill: none; flex-shrink: 0; }
        .doc-badge-info { flex: 1; min-width: 0; font-size: 12px; font-weight: 600; color: var(--text); }
        .doc-badge-btn {
            padding: 4px 10px; border-radius: 20px; font-size: 10px;
            cursor: pointer; border: 1px solid var(--border); transition: all 0.15s ease;
            -webkit-user-select: none;
            user-select: none;
        }
        .doc-badge-btn.check {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 10px;
            cursor: pointer;
            transition: all 0.15s ease;
    
            /* Base Styles (Dark Mode default) */
            background: var(--accent);
            color: #1a1a1a;            /* Dark text for the Bright Teal button in Dark Mode */
            border-color: var(--accent);
            font-weight: 700;
        }

        [data-theme="light"] .doc-badge-btn.check {color: #ffffff;
        }
        .doc-badge-btn.clear { background: transparent; color: var(--danger); border: none; font-size: 14px; }

        /* Executive Brief Button (Purple/Indigo Theme) */
        .doc-badge-btn.brief {
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 10px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
            
            /* Dark Mode: Purple Glow */
            background: rgba(139, 92, 246, 0.15); 
            color: #a78bfa; 
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        
        .doc-badge-btn.brief:hover {
            background: rgba(139, 92, 246, 0.25);
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
        }

        /* Light Mode Adaptation */
        [data-theme="light"] .doc-badge-btn.brief {
            background: rgba(124, 58, 237, 0.1);
            color: #7c3aed;
            border-color: rgba(124, 58, 237, 0.2);
        }

        /* IN ui.py `<style>` block */
        /* Find this rule around line 618 */
        .compliance-wrapper {
            max-width: 700px; /* <-- CHANGED from 650px to match Brief Card */
            margin: 20px auto; 
            animation: springIn 0.6s var(--spring);
        }
        
        /* The Main Card Container */
        .comp-card {
            background: var(--card-bg); /* <--- UPDATED: Dynamic Background */
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 30px;
            position: relative;
            overflow: hidden;
            /* Softer shadow in light mode if you want, or keep consistent */
            box-shadow: 0 20px 60px rgba(0,0,0,0.15); 
            transition: background 0.3s ease;
        }

        /* Top Light/Glow Bar (Color changes dynamically via JS) */
        .comp-card::before {
            content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
            background: var(--score-color);
            box-shadow: 0 0 30px 10px var(--score-color);
        }

        /* Header Section: Title & Score */
        .comp-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }
        
        .comp-title h2 { font-size: 20px; margin-bottom: 4px; color: var(--text); font-weight: 700; }
        .comp-title p { font-size: 12px; color: var(--text3); font-family: monospace; text-transform: uppercase; letter-spacing: 0.05em; }
        
        /* The Big Score Box */
        .score-box {
            text-align: center; padding: 10px 20px; border-radius: 16px;
            background: var(--bg2); /* <--- UPDATED: Uses existing theme variable */
            border: 1px solid var(--border);
            min-width: 120px;
        }
        .score-val { 
            font-size: 28px; font-weight: 800; color: var(--score-color); 
            text-shadow: 0 0 20px var(--score-dim); /* Glow text */
        }
        .score-lbl { font-size: 10px; font-weight: 700; color: var(--text3); text-transform: uppercase; letter-spacing: 0.1em; }

        /* The List of Checks */
        .comp-list { display: flex; flex-direction: column; gap: 12px; }
        
        .comp-item { 
            display: flex; gap: 16px; padding: 16px; 
            border-bottom: 1px solid var(--border);
            transition: 0.2s;
            border-radius: 12px;
        }
        .comp-item:hover { background: var(--card-item-hover); } /* <--- UPDATED: Dynamic Hover */
        .comp-item:last-child { border-bottom: none; }
        
        .comp-icon { 
            width: 32px; height: 32px; border-radius: 10px; 
            display: flex; align-items: center; justify-content: center; flex-shrink: 0; 
        }
        .comp-icon svg { width: 16px; height: 16px; stroke-width: 2.5; }
        
        .comp-name { font-weight: 700; font-size: 13px; color: var(--text); }
        .comp-reg { font-size: 11px; color: var(--text3); margin: 2px 0; font-family: monospace; }
        .comp-detail { font-size: 13px; color: var(--text2); line-height: 1.4; }

        /* Modals */
        .modal-overlay {
            position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(12px);
            display: none; align-items: center; justify-content: center; z-index: 600;
        }
        .modal-overlay.show { display: flex; }
        .modal {
            background: var(--glass-bg); border: var(--glass-border); border-radius: 28px;
            padding: 32px; width: 420px; box-shadow: var(--glass-shadow);
            backdrop-filter: blur(25px);
        }
        .modal-title { font-size: 20px; font-weight: 800; margin-bottom: 12px; color: var(--text); user-select: none; cursor: default;}
        .modal-text { font-size: 15px; color: var(--text2); margin-bottom: 28px; line-height: 1.6; user-select: none; cursor: default;}
        .modal-buttons { display: flex; gap: 12px; justify-content: flex-end; user-select: none; cursor: default;}
        .modal-btn { background: transparent; }
        .modal-btn.delete { background: var(--danger); border: none; color: white; }

        /* Toast Notification - iPhone Style */
        .toast-notification {
            position: fixed;
            top: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: var(--glass-bg);
            backdrop-filter: blur(30px) saturate(150%);
            -webkit-backdrop-filter: blur(30px) saturate(150%);
            border: var(--glass-border);
            border-radius: 100px;
            padding: 12px 24px;
            display: flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
            z-index: 700;
            opacity: 0;
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
            pointer-events: none;
        }
        .toast-notification.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
        .toast-notification .toast-icon {
            width: 20px;
            height: 20px;
            background: var(--accent);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .toast-notification .toast-icon svg {
            width: 12px;
            height: 12px;
            stroke: white;
            stroke-width: 3;
            fill: none;
        }
        .toast-notification .toast-text {
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
        }

        /* Drop Overlay Fix */
        .drop-overlay {
            position: absolute; inset: 0; 
            display: none; /* Hidden by default */
            align-items: center; justify-content: center; 
            background: rgba(0, 212, 170, 0.1); 
            border: 4px dashed var(--accent); 
            border-radius: 24px; 
            z-index: 200;
            pointer-events: none;
        }
        .drop-overlay.active { display: flex; pointer-events: auto; }
        
        .overlay { 
            position: fixed;
            inset: 0; 
            background: var(--glass-bg); 
            backdrop-filter: blur(40px); 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            justify-content: center; 
            z-index: 500; 
            -webkit-user-select: none;
            user-select: none;
            cursor: default;
        }
        .overlay.hidden { display: none; }
        /* --- AVATAR & LOGO STYLING --- */
        .avatar {
            width: 32px; 
            height: 32px; 
            border-radius: 50%; /* Circular */
            flex-shrink: 0; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: 800; 
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }

        /* 1. USER AVATAR (Always Bright Gradient) */
        .msg.user .avatar {
            background: var(--bubble-user);
            color: #ffffff;
            border: none;
            box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
        }

        /* 2. ASSISTANT AVATAR (DARK MODE) - White Glass */
        .msg.assistant .avatar {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
        }

        /* 3. ASSISTANT AVATAR (LIGHT MODE) - Teal Glass */
        [data-theme="light"] .msg.assistant .avatar {
            background: rgba(13, 148, 136, 0.12); /* Glassy Teal Background */
            color: var(--accent);                  /* Teal Icon */
            border-color: rgba(13, 148, 136, 0.2); /* Subtle Teal Border */
        }

        /* --- SOURCES STYLING --- */
        .sources-area {
            margin-top: 16px;
            padding-top: 12px;
            border-top: 1px solid var(--border); /* Adaptive border */
        }
        
        .sources-title {
            font-size: 10px;
            font-weight: 700;
            color: var(--text3);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        
        .sources-list {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }

        .source-tag {
            font-size: 10px; 
            font-weight: 600; 
            padding: 4px 10px; 
            border-radius: 6px;
            
            /* THEME ADAPTIVE COLORS */
            background: var(--bg2);          /* Glass in Dark, Light Grey in Light */
            border: 1px solid var(--border); /* Transparent in Dark, Grey in Light */
            color: var(--text2);             /* White in Dark, Dark Grey in Light */
            
            display: inline-block;
            transition: all 0.2s ease;
            cursor: default;
        }
        
        /* Optional: Hover effect */
        .source-tag:hover {
            background: var(--bg3);
            border-color: var(--accent);
            color: var(--text);
        }

        /* --- DYNAMIC HEADER EXTRAS --- */

        /* 1. The Vertical Divider (|) */
        #headerDivider {
            width: 1px; height: 24px; background: var(--border);
            margin: 0;
            display: none; /* Hide by default to remove gap */
            opacity: 0; transform: scaleY(0); transition: all 0.4s ease;
        }
        #headerDivider.visible {
            display: block; /* Show only when needed */
            opacity: 1; transform: scaleY(1);
            margin: 0 12px;
        }

        /* 2. The Emerging Theme Toggle */
        #themeToggleHeader {
            /* Hidden State */
            width: 0; 
            height: 40px;
            border-radius: 50%;
            border: none;
            background: transparent;
            overflow: hidden;
            opacity: 0;
            padding: 0;
            margin: 0;
            
            /* Visuals matching sidebar button */
            display: flex; align-items: center; justify-content: center;
            cursor: pointer;
            color: var(--text);
            
            /* Slide Animation */
            transform: translateX(10px) rotate(-90deg);
            transition: all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }

        #themeToggleHeader.visible {
            width: 40px; 
            opacity: 1;
            border: 1px solid var(--border);
            background: var(--bg2);
            transform: translateX(0) rotate(0deg);
        }
        
        #themeToggleHeader:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: var(--accent);
            transform: scale(1.1);
        }
        
        #themeToggleHeader.visible:hover {
            transform: scale(1.1);
        }

        /* CRITICAL FIX: Lock Icon Size */
        #themeToggleHeader svg {
            width: 20px;
            height: 20px;
            stroke: currentColor;
            flex-shrink: 0;
            transition: transform 0.5s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        
        #themeToggleHeader:active svg {
            transform: rotate(360deg);
        }

        /* 3. SOFT GLOW ANIMATION (No sizing changes) */
        .icon-sun {
            color: #facc15; 
            filter: drop-shadow(0 0 2px rgba(250, 204, 21, 0.5));
            animation: glowSoft 3s infinite ease-in-out;
        }
        
        .icon-moon {
            color: #60a5fa; 
            filter: drop-shadow(0 0 2px rgba(96, 165, 250, 0.5));
            animation: glowSoft 3s infinite ease-in-out;
        }

        @keyframes glowSoft {
            0%, 100% { filter: drop-shadow(0 0 2px rgba(currentColor, 0.3)); opacity: 0.85; }
            50% { filter: drop-shadow(0 0 8px rgba(currentColor, 0.6)); opacity: 1; }
        }

        /* --- ANALYSIS MODE STYLES --- */
        .doc-controls {
            width: 100%; max-width: 800px; margin: 0 auto;
            background: rgba(15, 23, 42, 0.65) !important;
            border: 1px solid var(--accent);
            border-radius: 20px;
            padding: 12px 20px;
            display: flex; align-items: center; justify-content: space-between;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(45px) saturate(120%) !important;
            animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            
            /* Disable Highlight */
            -webkit-user-select: none; user-select: none; cursor: default;
        }
        
        .doc-icon {
            width: 36px; height: 36px; border-radius: 10px;
            background: rgba(13, 148, 136, 0.15); color: var(--accent);
            display: flex; align-items: center; justify-content: center; margin-right: 12px;
        }
        .doc-icon svg { width: 18px; height: 18px; fill: none; stroke: currentColor; stroke-width: 2; }
        
        .doc-info { display: flex; align-items: center; }
        .doc-actions { display: flex; align-items: center; gap: 8px; }

        .action-btn {
            border: none; padding: 10px 16px; border-radius: 10px;
            font-size: 12px; font-weight: 700; cursor: pointer;
            display: flex; align-items: center; gap: 8px; transition: all 0.2s ease;
        }
        .action-btn svg { width: 14px; height: 14px; fill: none; stroke: currentColor; stroke-width: 2.5; }

        /* Button Variants */
        .action-btn.brief { background: rgba(139, 92, 246, 0.15); color: #a78bfa; border: 1px solid rgba(139, 92, 246, 0.2); }
        .action-btn.brief:hover { background: rgba(139, 92, 246, 0.25); transform: translateY(-1px); }

        .action-btn.check { background: rgba(45, 212, 191, 0.15); color: var(--accent); border: 1px solid rgba(45, 212, 191, 0.2); }
        .action-btn.check:hover { background: rgba(45, 212, 191, 0.25); transform: translateY(-1px); }

        .action-btn.back { 
            background: rgba(239, 68, 68, 0.1); 
            color: #ef4444; 
            border: 1px solid rgba(239, 68, 68, 0.2); 
            padding: 8px 16px; 
        }
        .action-btn.back:hover { color: #f87171; background: rgba(239, 68, 68, 0.2); }

        /* --- IPHONE STYLE NOTIFICATION TOAST --- */
        .notification-toast {
            position: fixed; top: -100px; left: 50%; transform: translateX(-50%);
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(0,0,0,0.1);
            color: #1a1a1a;
            padding: 12px 24px;
            border-radius: 100px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            z-index: 9999;
            display: flex; align-items: center; gap: 12px;
            font-size: 13px; font-weight: 600;
            transition: top 0.5s cubic-bezier(0.19, 1, 0.22, 1);
            
            /* Disable Highlight */
            -webkit-user-select: none; user-select: none; cursor: default;
        }
        :root:not([data-theme="light"]) .notification-toast {
            background: rgba(30, 41, 59, 0.9);
            border: 1px solid rgba(255,255,255,0.1);
            color: #fff;
        }
        .notification-toast.show { top: 30px; }
        .toast-icon { 
            width: 20px; height: 20px; border-radius: 50%; 
            background: #10b981; 
            display: flex; align-items: center; justify-content: center; 
            color: #fff; 
        }
        .toast-icon svg { width: 12px; height: 12px; stroke-width: 3; }

        /* --- FORCE VISIBILITY UTILITIES --- */
        .header-actions .icon-btn.force-visible,
        .header-divider.force-visible,
        #themeToggleHeader.force-visible {
            display: flex !important;
            opacity: 1 !important;
            visibility: visible !important;
            width: 40px !important;
            transform: none !important;
        }
        .force-hidden { display: none !important; }

        /* --- EXECUTIVE BRIEF CARD (Vibrant Dark Mode) --- */
        .brief-wrapper {
            padding: 20px 0; margin: 20px 0;
            display: flex; justify-content: center;
            animation: slideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1);
            width: 100%;
        }
        .brief-card {
            background: var(--card-bg); /* Deep Navy Background */
            border-radius: 24px;
            border: 1px solid var(--border);
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            width: 100%; max-width: 700px;
            transition: all 0.3s ease;
        }
        .brief-header {
            /* Vibrant Purple Gradient */
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.2), rgba(76, 29, 149, 0.3));
            padding: 24px 32px;
            border-bottom: 1px solid rgba(139, 92, 246, 0.2);
            display: flex; align-items: center; justify-content: space-between;
            
            /* Disable Highlight */
            -webkit-user-select: none; user-select: none; cursor: default;
        }
        .brief-title-group { display: flex; align-items: center; gap: 16px; }
        .brief-icon-large {
            width: 48px; height: 48px; border-radius: 14px;
            background: rgba(139, 92, 246, 0.25); 
            color: #c4b5fd;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(139, 92, 246, 0.3);
            flex-shrink: 0;
        }
        .brief-icon-large svg { width: 24px; height: 24px; stroke-width: 2; }
        .brief-heading h2 { font-size: 20px; font-weight: 800; margin: 0; color: var(--text); }
        .brief-heading p { margin: 4px 0 0 0; font-size: 12px; color: var(--text3); font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }

        .brief-content { padding: 32px; font-size: 15px; line-height: 1.7; color: var(--text2); }
        .brief-content h2 { font-size: 16px; font-weight: 700; color: var(--text); margin-top: 24px; margin-bottom: 12px; }
        .brief-content ul { padding-left: 20px; margin-bottom: 16px; }
        .brief-content li { margin-bottom: 8px; }
        .brief-content strong { color: var(--text); font-weight: 700; }

        /* --- COMPLIANCE CARD HEADER LOCK --- */
        /* Disable Highlight for Compliance Card Header too */
        .comp-header {
            -webkit-user-select: none; user-select: none; cursor: default;
        }

        /* --- LOADING STATES --- */
        .central-loader {
            -webkit-user-select: none; user-select: none; cursor: default;
        }
        .jumping-dots { display: inline-flex; align-items: center; }
        .jumping-dots span {
            display: inline-block; width: 5px; height: 5px; border-radius: 50%;
            background: var(--accent); margin: 0 2px;
            animation: jump 1.4s infinite ease-in-out both;
        }
        .jumping-dots span:nth-child(1) { animation-delay: -0.32s; }
        .jumping-dots span:nth-child(2) { animation-delay: -0.16s; }
        @keyframes jump { 0%, 80%, 100% { transform: scale(0); opacity: 0.5; } 40% { transform: scale(1); opacity: 1; } }
        @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        .hidden { display: none !important; }
        
        /* Fix Modal Text Overflow */
        .modal-text { word-wrap: break-word; overflow-wrap: break-word; word-break: break-all; max-width: 100%; }

        /* --- LIGHT MODE OVERRIDES --- */
        [data-theme="light"] .brief-card {
            background: #ffffff;
            border-color: rgba(0,0,0,0.1);
            box-shadow: 0 20px 40px rgba(0,0,0,0.08);
        }
        [data-theme="light"] .brief-header {
            background: linear-gradient(135deg, #f5f3ff, #ede9fe);
            border-bottom: 1px solid rgba(0,0,0,0.06);
        }
        [data-theme="light"] .brief-icon-large {
            background: #ddd6fe; color: #7c3aed;
            box-shadow: 0 8px 16px rgba(124, 58, 237, 0.15);
            border: none;
        }
        [data-theme="light"] .brief-heading h2 { color: #1e1b4b; }
        [data-theme="light"] .brief-heading p { color: #6d28d9; opacity: 0.7; }
        [data-theme="light"] .brief-content { color: #334155; }
        [data-theme="light"] .brief-content h2 { color: #1e1b4b; }
        [data-theme="light"] .brief-content strong { color: #0f172a; }
        [data-theme="light"] .ai-label {
            background: #ddd6fe !important;
            color: #7c3aed !important;
        }
        /* Fix Control Bar in Light Mode */
        [data-theme="light"] .doc-controls {
            background: rgba(255, 255, 255, 0.65) !important;
            border-color: rgba(0,0,0,0.1);
            box-shadow: 0 10px 40px rgba(0,0,0,0.05) !important;
        }

        /* --- ANALYSIS MODE WELCOME SCREEN (Paste at the end) --- */
        .analysis-welcome {
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            height: 100%; text-align: center;
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1);
            -webkit-user-select: none; user-select: none; cursor: default;
            padding: 40px 20px;
        }
        .analysis-icon-box {
            width: 90px; height: 90px; border-radius: 28px;
            background: linear-gradient(135deg, rgba(45, 212, 191, 0.15), rgba(139, 92, 246, 0.15));
            border: 1px solid rgba(45, 212, 191, 0.25);
            color: var(--accent);
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 28px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.25), 0 0 60px rgba(45, 212, 191, 0.15);
            animation: floatIcon 4s ease-in-out infinite;
        }
        @keyframes floatIcon {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-8px) rotate(2deg); }
        }
        .analysis-icon-box svg { width: 44px; height: 44px; stroke-width: 1.5; }
        
        .analysis-title { 
            font-size: 32px; font-weight: 800; color: var(--text); margin-bottom: 12px; letter-spacing: -0.03em;
            background: linear-gradient(135deg, var(--text) 0%, var(--accent) 100%);
            -webkit-background-clip: text; background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .analysis-subtitle {
            font-size: 15px; color: var(--text2); max-width: 460px; line-height: 1.7; margin-bottom: 32px;
        }
        
        /* Feature Cards */
        .analysis-features {
            display: flex; gap: 16px; margin-top: 8px;
            flex-wrap: wrap; justify-content: center;
        }
        .analysis-feature {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 20px 24px;
            width: 200px;
            text-align: left;
            transition: all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1);
        }
        .analysis-feature:hover {
            transform: translateY(-4px);
            border-color: var(--accent);
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2), 0 0 20px rgba(45, 212, 191, 0.1);
        }
        .analysis-feature-icon {
            width: 40px; height: 40px; border-radius: 12px;
            display: flex; align-items: center; justify-content: center;
            margin-bottom: 14px;
        }
        .analysis-feature-icon.scan {
            background: rgba(74, 222, 128, 0.15);
            color: #4ade80;
        }
        .analysis-feature-icon.brief {
            background: rgba(139, 92, 246, 0.15);
            color: #a78bfa;
        }
        .analysis-feature-icon svg { width: 22px; height: 22px; stroke-width: 2; }
        .analysis-feature-title {
            font-size: 14px; font-weight: 700; color: var(--text); margin-bottom: 6px;
        }
        .analysis-feature-desc {
            font-size: 12px; color: var(--text3); line-height: 1.5;
        }
        
        [data-theme="light"] .analysis-feature {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.08);
        }
        [data-theme="light"] .analysis-feature:hover {
            box-shadow: 0 12px 32px rgba(0, 0, 0, 0.1);
        }
        
        .analysis-tag {
            margin-top: 28px; font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;
            color: var(--accent); background: rgba(45, 212, 191, 0.1); 
            padding: 8px 16px; border-radius: 100px;
            border: 1px solid rgba(45, 212, 191, 0.2);
        }

        /* --- COPY BUTTON ANIMATIONS --- */
        .msg-copy {
            position: absolute; top: -10px; right: -10px; opacity: 0;
            width: 28px; height: 28px; 
            background: var(--bg3);
            border: 1px solid var(--border); border-radius: 8px;
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
            color: var(--text3); /* Default Gray */
            z-index: 10;
        }
        /* Show on hover */
        .msg:hover .msg-copy { opacity: 1; transform: translateY(0); }
        .msg-copy:hover { background: var(--bg4); color: var(--text); }
        
        /* Active State (Clicked) */
        .msg-copy:active { transform: scale(0.9); }

        /* COPIED STATE (Teal Success) */
        .msg-copy.copied {
            opacity: 1 !important; /* Stay visible even if mouse leaves */
            background: rgba(45, 212, 191, 0.15) !important;
            border-color: var(--accent) !important;
            color: var(--accent) !important;
            animation: splash 0.6s ease forwards;
        }

        /* Icon Animation */
        .msg-copy svg {
            width: 14px; height: 14px; stroke-width: 2;
            transition: all 0.3s ease;
        }
        
        /* Splash Effect Ring */
        @keyframes splash {
            0% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(45, 212, 191, 0); }
            100% { box-shadow: 0 0 0 0 rgba(45, 212, 191, 0); }
        }

    </style>
</head>
<body>
    <div id="notificationToast" class="notification-toast">
        <div class="toast-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="20 6 9 17 4 12"/></svg>
        </div>
        <span id="toastMessage">File Uploaded Successfully</span>
    </div>
    
    <aside class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <div class="logo-icon-sidebar">
                    <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                </div>
                <div class="logo-text-group">
                    <div class="logo-text">TadqeeqAI</div>
                    <div class="logo-sub">Regulatory Intelligence</div>
                </div>
            </div>
            <button class="new-chat-btn" id="newChatBtn">
                <svg viewBox="0 0 24 24" width="18" height="18" stroke="currentColor" stroke-width="2.5" fill="none"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                New Chat
            </button>
        </div>
        <div class="chat-history" id="chatHistory">
            <div class="history-title">Recent Chats</div>
        </div>
        <div class="examples" style="padding: 20px; border-top: 1px solid var(--border);">
            <div class="history-title" style="padding: 0 0 12px 0;">Try These</div>
            <div class="history-item ex" data-q="What are the licensing fees for finance companies?">
                <span>Licensing fees</span><span style="padding: 3px 8px; background: var(--sama); color: white; border-radius: 8px; font-weight: 700; font-size: 9px;">SAMA</span>
            </div>
            <div class="history-item ex" data-q="What is a qualified investor?">
                <span>Qualified investor</span><span style="padding: 3px 8px; background: var(--cma); color: white; border-radius: 8px; font-weight: 700; font-size: 9px;">CMA</span>
            </div>
        </div>
        <div class="sidebar-footer" style="padding: 20px; border-top: 1px solid rgba(255,255,255,0.06);">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <button class="theme-toggle-sidebar" id="themeToggle" title="Toggle Theme">
                    <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
                </button>
                <div style="display: flex; align-items: center; gap: 8px; font-size: 10px; color: var(--text3); font-weight: 700; letter-spacing: 0.05em;">
                    <span class="status-dot"></span>
                    Aya 8B · v3.0
                </div>
            </div>
        </div>
    </aside>

    <main class="main" style="position: relative;">
        <header class="header">
            <div style="display: flex; align-items: center; gap: 16px;">
                <button id="menuBtn" class="menu-btn" title="Toggle Sidebar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <line x1="9" y1="3" x2="9" y2="21"></line>
                    </svg>
                </button>
                <span class="header-title" id="headerTitle">Saudi Financial Law Assistant</span>
            </div>
            <div class="header-actions">
                <button id="themeToggleHeader" title="Switch Theme">
                </button>

                <div id="headerDivider"></div>

                <div style="position: relative;">
                    <div id="chatExportWrapper">
                        <button class="header-btn" id="exportBtn">
                            <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2.5" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
                            Export
                        </button>
                        <div class="export-menu" id="exportMenu">
                            <div class="export-item" id="exportMd">
                                <svg viewBox="0 0 24 24" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                                Markdown (.md)
                            </div>
                            <div class="export-item" id="exportPdf">
                                <svg viewBox="0 0 24 24" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
                                PDF (.pdf)
                            </div>
                        </div>
                    </div>

                    <button class="header-btn primary" id="analysisSaveBtn" style="display: none;">
                        <svg viewBox="0 0 24 24" stroke-width="2" fill="none" stroke="currentColor"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                        <span id="analysisSaveText">Save Report</span>
                    </button>
                </div>
                
                <button class="header-btn primary" id="newChatBtnHeader">
                    <svg viewBox="0 0 24 24" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                    New Chat
                </button>
            </div>
        </header>

        <div class="drop-overlay" id="dropOverlay">
            <div style="text-align: center;">
                <h3 style="font-size: 24px; font-weight: 800; color: var(--text);">Drop Document</h3>
                <p style="color: var(--text2); font-size: 15px; margin-top: 8px;">PDF or DOCX (max 50 pages)</p>
            </div>
        </div>

        <div class="chat" id="chat">
            <!-- Welcome screen injected by JS using getWelcomeHTML() -->
        </div>

        <div class="input-area">
            <div id="chatInputBox" class="input-box">
                <button class="attach-btn" id="attachBtn" title="Attach Document">
                    <svg viewBox="0 0 24 24"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                </button>
                <textarea id="input" placeholder="Ask about regulations..." rows="1" disabled></textarea>
                <button class="send" id="send" disabled>
                    <svg viewBox="0 0 24 24"><path d="M2 21L23 12 2 3 2 10 17 12 2 14z"/></svg>
                </button>
            </div>

            <div id="docControls" class="doc-controls" style="display: none;">
                <div class="doc-info">
                    <div class="doc-icon">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                    </div>
                    <div style="display:flex; flex-direction:column;">
                        <span style="font-size:10px; color:var(--text3); font-weight:700; letter-spacing:0.05em; text-transform:uppercase;">Analysis Mode</span>
                        <span id="docNameDisplay" style="font-weight:700; color:var(--text); max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">Document.pdf</span>
                    </div>
                </div>
                
                <div class="doc-actions">
                    <button class="action-btn check" onclick="window.runComplianceCheck()">
                        <svg viewBox="0 0 24 24"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                        Scan Compliance
                    </button>
                    <button class="action-btn brief" onclick="window.generateBrief()">
                        <svg viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                        Executive Brief
                    </button>
                    <div style="width:1px; height:24px; background:var(--border); margin:0 8px;"></div>
                    <button class="action-btn back" onclick="window.exitAnalysisMode()">
                        Exit
                    </button>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 12px; font-size: 10px; color: var(--text3); font-weight: 600;">AI can make mistakes. Verify important information.</div>
        </div>
        <input type="file" id="fileInput" accept=".pdf,.docx,.doc" style="display: none;">
    </main>

    <div class="overlay" id="overlay">
        <div style="width: 80px; height: 80px; background: var(--accent); border-radius: 20px; display: flex; align-items: center; justify-content: center; margin-bottom: 24px; box-shadow: 0 20px 50px rgba(0, 212, 170, 0.4);">
            <svg viewBox="0 0 24 24" style="width: 40px; height: 40px; fill: white;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
        </div>
        <h2 style="font-size: 32px; font-weight: 800; margin-bottom: 8px;">TadqeeqAI</h2>
        <div class="progress-container" style="width: 300px; max-width: 80vw;">
            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 100px; overflow: hidden;">
                <div id="progressBar" style="width: 0%; height: 100%; background: var(--accent); transition: width 0.3s ease;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 12px; font-size: 12px;">
                <span id="progressStage" style="color: var(--text3); font-weight: 600;">Initializing...</span>
                <span id="progressPercent" style="color: var(--accent); font-weight: 800;">0%</span>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="deleteModal">
        <div class="modal">
            <div class="modal-title">Delete Chat</div>
            <div class="modal-text">Are you sure you want to delete this chat? This action is permanent and cannot be undone.</div>
            <div class="modal-buttons">
                <button class="modal-btn cancel" id="cancelDelete" style="color: var(--text2);">Cancel</button>
                <button class="modal-btn delete" id="confirmDelete">Delete</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="errorModal">
        <div class="modal">
            <div class="modal-title" id="errorTitle">Error</div>
            <div class="modal-text" id="errorText"></div>
            <div class="modal-buttons">
                <button class="modal-btn cancel" id="errorClose" style="color: var(--text);">OK</button>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast-notification" id="toastNotification">
        <div class="toast-icon">
            <svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>
        </div>
        <span class="toast-text" id="toastText">Success</span>
    </div>

    <script>

        // --- 1. SAFE MARKDOWN STRIPPER ---
        function stripMarkdown(text) {
            if (!text) return '';
            // Remove headers (# )
            text = text.replace(/^#+\s+/gm, '');
            // Remove bold/italic asterisks/underscores (just remove the markers)
            text = text.replace(/\*\*/g, '').replace(/__/g, '');
            // Remove links ([text](url) -> text)
            text = text.replace(/\[([^\]]+)\]\([^\)]+\)/g, '$1');
            // Remove code backticks
            text = text.replace(/`/g, '');
            // Remove blockquotes (>)
            text = text.replace(/^>\s+/gm, '');
            
            // NOTE: We purposely DO NOT remove "starting hyphens" (- ) 
            // so your lists remain readable.
            
            return text.trim();
        }

        // --- 2. ROBUST COPY HELPER ---
        function copyToClipboard(text, onSuccess) {
            const cleanText = stripMarkdown(text);
            
            // Try Modern API first
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(cleanText)
                    .then(onSuccess)
                    .catch(() => fallbackCopy(cleanText, onSuccess));
            } else {
                // Fallback for PyWebView
                fallbackCopy(cleanText, onSuccess);
            }
        }

        // --- 3. FALLBACK COPY ---
        function fallbackCopy(text, onSuccess) {
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            try {
                if (document.execCommand('copy')) {
                    if (onSuccess) onSuccess();
                }
            } catch (err) {
                console.error('Copy failed', err);
            }
            document.body.removeChild(textArea);
        }
    
        const chat=document.getElementById('chat'),input=document.getElementById('input'),sendBtn=document.getElementById('send');
        const chatHistoryEl=document.getElementById('chatHistory');
        const deleteModal=document.getElementById('deleteModal');
        let ready=false,busy=false,currentChatId=null,chatToDelete=null;
        
        // Store stats globally so they persist
        let appStats = { sama: '-', cma: '-', total: '-' };
        
        // Unified Welcome Screen Generator
        function getWelcomeHTML() {
            return `<div class="welcome" id="welcome">
                <div class="welcome-icon">
                    <svg viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
                </div>
                <div class="welcome-title">TadqeeqAI</div>
                <div class="welcome-subtitle">Your AI-powered regulatory assistant for SAMA and CMA compliance.<br>Ask questions in English or Arabic to explore financial regulations.</div>
                <div class="welcome-stats">
                    <div class="stat"><div class="stat-val">${appStats.sama}</div><div class="stat-lbl">SAMA Articles</div></div>
                    <div class="stat"><div class="stat-val">${appStats.cma}</div><div class="stat-lbl">CMA Articles</div></div>
                    <div class="stat"><div class="stat-val">${appStats.total}</div><div class="stat-lbl">Total Indexed</div></div>
                </div>
            </div>`;
        }
        
        marked.setOptions({breaks:true,gfm:true});
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if(!e.target.closest('.history-item-menu') && !e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown.show').forEach(d => d.classList.remove('show'));
            }
        });
        
        // Modal handlers
        document.getElementById('cancelDelete').addEventListener('click', () => {
            deleteModal.classList.remove('show');
            chatToDelete = null;
        });
        
        document.getElementById('confirmDelete').addEventListener('click', async () => {
            if(chatToDelete) {
                const chatIdToDelete = chatToDelete;
                
                // 1. Close modal FIRST
                deleteModal.classList.remove('show');
                chatToDelete = null;
                
                // 2. Find the chat element and apply animation
                const chatElement = document.querySelector(`.history-item[data-id="${chatIdToDelete}"]`);
                if(chatElement) {
                    chatElement.classList.add('chat-deleting');
                    // 3. Wait for animation to complete
                    await new Promise(resolve => setTimeout(resolve, 300));
                }
                
                // 4. Actually delete
                await deleteChat(chatIdToDelete);
                
                // 5. Show notification
                showNotification('Chat Deleted');
            }
        });
        
        async function deleteChat(chatId) {
            try {
                const r = await window.pywebview.api.delete_chat(chatId);
                if(r.success) {
                    renderChatHistory(r.chats);
                    if(chatId === currentChatId) {
                        await newChat(true);
                    }
                }
            } catch(e) {
                console.error('deleteChat error:', e);
            }
        }
        
        function showDeleteConfirm(chatId) {
            chatToDelete = chatId;
            deleteModal.classList.add('show');
        }
        
        // Progress bar elements
        const progressBar = document.getElementById('progressBar');
        const progressStage = document.getElementById('progressStage');
        const progressPercent = document.getElementById('progressPercent');
        
        function updateProgress(progress, stage) {
            if (progressBar) progressBar.style.width = progress + '%';
            if (progressPercent) progressPercent.textContent = progress + '%';
            if (progressStage) progressStage.textContent = stage || 'Initializing...';
        }
        
        async function pollProgress() {
            try {
                const status = await window.pywebview.api.get_init_status();
                updateProgress(status.progress || 0, status.stage_text || 'Initializing...');
                
                if (status.status === 'ready') {
                    return status;
                } else if (status.status === 'error') {
                    throw new Error(status.error || 'Initialization failed');
                }
                // Still loading, poll again
                await new Promise(resolve => setTimeout(resolve, 200));
                return pollProgress();
            } catch (e) {
                throw e;
            }
        }
        
        async function init(){
            try{
                // Start initialization in background
                window.pywebview.api.initialize();
                
                // Poll for progress
                const r = await pollProgress();
                
                if(r.status==='ready'){
                    ready=true;
                    // Store stats globally
                    appStats.sama = r.sama;
                    appStats.cma = r.cma;
                    appStats.total = r.total;
                    
                    // Inject welcome screen with stats
                    chat.innerHTML = getWelcomeHTML();
                    
                    input.disabled=false;
                    sendBtn.disabled=false;
                    document.getElementById('overlay').classList.add('hidden');
                    input.focus();
                    // Load chat history
                    if(r.chats) renderChatHistory(r.chats);
                    // Start new chat
                    await newChat(false);
                }else{
                    updateProgress(0, 'Error: ' + (r.message || 'Unknown error'));
                }
            }catch(e){
                updateProgress(0, 'Error: ' + e.message);
            }
        }
        window.addEventListener('pywebviewready',init);
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Ctrl+N or Cmd+N - New Chat
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                newChat(true);
            }
            // Ctrl+/ or Cmd+/ - Focus input
            if ((e.ctrlKey || e.metaKey) && e.key === '/') {
                e.preventDefault();
                input.focus();
            }
            // Escape - Close sidebar
            if (e.key === 'Escape') {
                const sidebar = document.getElementById('sidebar');
                if (sidebar && !sidebar.classList.contains('collapsed')) {
                    sidebar.classList.add('collapsed');
                    try { localStorage.setItem('tadqeeq-sidebar', 'collapsed'); } catch(e) {}
                }
            }
        });
        
        function renderChatHistory(chats){
            let html='<div class="history-title">Recent Chats</div>';
            chats.forEach(c=>{
                const isActive=c.id===currentChatId?' active':'';
                html+=`<div class="history-item${isActive}" data-id="${c.id}">
                    <span class="history-item-text" style="flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${escHtml(c.preview)}</span>
                    <div class="history-item-menu" data-id="${c.id}">
                        <svg viewBox="0 0 24 24"><circle cx="12" cy="6" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="18" r="1.5"/></svg>
                    </div>
                    <div class="dropdown" data-id="${c.id}">
                        <div class="dropdown-item delete-chat" data-id="${c.id}">
                            <svg viewBox="0 0 24 24" stroke-width="2"><path d="M3 6h18M8 6V4a2 2 0 012-2h4a2 2 0 012 2v2m3 0v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6h14"/></svg>
                            Delete
                        </div>
                    </div>
                </div>`;
            });
            chatHistoryEl.innerHTML=html;
            
            // Add click handlers for chat items
            chatHistoryEl.querySelectorAll('.history-item').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    if(!e.target.closest('.history-item-menu') && !e.target.closest('.dropdown')) {
                        loadChat(el.dataset.id);
                    }
                });
            });
            
            // Add click handlers for menu buttons
            chatHistoryEl.querySelectorAll('.history-item-menu').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    e.stopPropagation();
                    const dropdown = el.nextElementSibling;
                    document.querySelectorAll('.dropdown.show').forEach(d => {
                        if(d !== dropdown) d.classList.remove('show');
                    });
                    dropdown.classList.toggle('show');
                });
            });
            
            // Add click handlers for delete buttons
            chatHistoryEl.querySelectorAll('.delete-chat').forEach(el=>{
                el.addEventListener('click',(e)=>{
                    e.stopPropagation();
                    showDeleteConfirm(el.dataset.id);
                });
            });
        }
        
        async function newChat(updateUI=true){
            try{
                const r=await window.pywebview.api.new_chat();
                currentChatId=r.id;
                if(updateUI){
                    // Restore welcome screen using unified function
                    chat.innerHTML = getWelcomeHTML();
                    renderChatHistory(r.chats);
                    // Clear document badge
                    const docBadge = document.getElementById('docBadge');
                    if (docBadge) { docBadge.style.display = 'none'; docBadge.innerHTML = ''; }
                }
            }catch(e){
                console.error('newChat error:',e);
            }
        }
        
        async function loadChat(chatId){
            try{
                const r=await window.pywebview.api.load_chat(chatId);
                currentChatId=chatId;
                // Clear and render messages
                chat.innerHTML='';
                r.messages.forEach(m=>{
                    addMsg(m.role,m.content,m.sources||null,m.regulator||null);
                });
                // Update active state
                chatHistoryEl.querySelectorAll('.history-item').forEach(el=>{
                    el.classList.toggle('active',el.dataset.id===chatId);
                });
            }catch(e){
                console.error('loadChat error:',e);
            }
        }
        
        document.getElementById('newChatBtn').addEventListener('click',()=>newChat(true));
        document.getElementById('newChatBtnHeader').addEventListener('click',()=>newChat(true));
        
        input.addEventListener('input',()=>{input.style.height='auto';input.style.height=Math.min(input.scrollHeight,120)+'px';});
        input.addEventListener('keydown',e=>{if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();}});
        sendBtn.addEventListener('click',send);
        document.querySelectorAll('.ex').forEach(el=>{el.addEventListener('click',()=>{input.value=el.dataset.q;send();});});
        
        function escHtml(t){const d=document.createElement('div');d.textContent=t;return d.innerHTML;}
        function renderMd(text){try{return marked.parse(text);}catch(e){return escHtml(text);}}
        function isArabic(text){return /[\u0600-\u06FF]/.test(text)&&(text.match(/[\u0600-\u06FF]/g)||[]).length>text.length*0.3;}
        
        const logoSvg='<svg viewBox="0 0 24 24" style="width:14px; height:14px; fill:white;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>';
        const userSvg='<svg viewBox="0 0 24 24"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
        const sunSvg = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
        const moonSvg = '<svg viewBox="0 0 24 24"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';

        // UPDATED addMsg FUNCTION
        function addMsg(role, text, sources, reg) {
            const w = document.getElementById('welcome');
            if (w) w.style.display = 'none';
            
            const div = document.createElement('div');
            div.className = 'msg ' + role;
            
            // Regulator Badge
            let regHtml = reg && reg !== 'NONE' ? '<span style="font-size:9px; font-weight:800; color:var(--' + reg.toLowerCase() + '); padding:3px 10px; border:1px solid; border-radius:100px; margin-left:8px; background:rgba(255,255,255,0.05);">' + reg + '</span>' : '';
            
            // Sources
            let srcHtml = '';
            if (sources && sources.length > 0) {
                srcHtml = `<div class="sources-area"><div class="sources-title">Sources</div><div class="sources-list">${sources.map(s => `<span class="source-tag">${escHtml(s.article)}</span>`).join('')}</div></div>`;
            }

            const textHtml = role === 'assistant' ? renderMd(text) : escHtml(text);
            const rtlClass = isArabic(text) ? ' style="direction:rtl; text-align:right;"' : '';
            
            // Icons
            const logoSvg = '<svg viewBox="0 0 24 24" style="width:14px; height:14px; fill:white;"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>';
            const userSvg = '<svg viewBox="0 0 24 24" stroke="currentColor" fill="none" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
            const avatarContent = role === 'user' ? userSvg : logoSvg;

            // Copy Button (Only for Assistant)
            const copyBtnHtml = role === 'assistant' 
                ? `<button class="msg-copy" title="Copy">
                     <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                   </button>` 
                : '';

            div.innerHTML = copyBtnHtml + `
                <div class="avatar">${avatarContent}</div>
                <div class="msg-body" style="flex:1; min-width:0;">
                    <div style="display:flex; align-items:center; margin-bottom:6px; gap:8px;">
                        <span style="font-size:12px; font-weight:700; color:var(--text2);">${role === 'user' ? 'You' : 'TadqeeqAI'}</span>
                        ${regHtml}
                    </div>
                    <div class="msg-text"${rtlClass}>${textHtml}${srcHtml}</div>
                </div>`;

            // --- EVENT LISTENER ---
            const copyBtn = div.querySelector('.msg-copy');
            if (copyBtn) {
                copyBtn.addEventListener('click', () => {
                    // Call the helper from Step 1
                    copyToClipboard(text, () => {
                        // 1. Force Visible & Teal
                        copyBtn.classList.add('copied');
                        
                        // 2. Swap to Checkmark
                        copyBtn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
                        
                        // 3. Revert after 2s
                        setTimeout(() => {
                            copyBtn.classList.remove('copied');
                            copyBtn.innerHTML = `<svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
                        }, 2000);
                    });
                });
            }

            chat.appendChild(div);
            chat.scrollTo({ top: chat.scrollHeight, behavior: 'smooth' });
        }
        
        function addLoading(){
            const w=document.getElementById('welcome');if(w)w.style.display='none';
            const div=document.createElement('div');
            div.className='msg assistant';
            div.id='loading';
            div.innerHTML='<div class="avatar" style="width:32px; height:32px; border-radius:50%; background:rgba(255,255,255,0.1); flex-shrink:0; display:flex; align-items:center; justify-content:center; font-weight:800; border:1px solid rgba(255,255,255,0.1); color:white;">'+logoSvg+'</div><div class="msg-body"><div class="msg-header" style="font-size:12px; font-weight:700; color:var(--text2); margin-bottom:6px;">TadqeeqAI</div><div class="loading-msg"><div class="typing-indicator"><span></span><span></span><span></span></div><span class="loading-text">Searching regulations...</span></div></div>';
            chat.appendChild(div);
            chat.scrollTop=chat.scrollHeight;
        }
        
        async function send(){
            const q=input.value.trim();
            if(!q||busy||!ready)return;
            busy=true;
            sendBtn.disabled=true;
            input.disabled=true;
            input.value='';
            input.style.height='auto';
            addMsg('user',q,null,null);
            addLoading();
            try{
                const r=await window.pywebview.api.query(q);
                document.getElementById('loading')?.remove();
                addMsg('assistant',r.answer,r.sources,r.regulator);
                // Refresh chat history
                const chats=await window.pywebview.api.get_chats();
                renderChatHistory(chats.chats);
            }catch(e){
                document.getElementById('loading')?.remove();
                addMsg('assistant','An error occurred while processing your request.',null,null);
            }
            busy=false;
            sendBtn.disabled=false;
            input.disabled=false;
            input.focus();
        }
        
        // Error modal helper
        function showError(title, message) {
            const modal = document.getElementById('errorModal');
            document.getElementById('errorTitle').textContent = title;
            document.getElementById('errorText').textContent = message;
            modal.classList.add('show');
        }
        document.getElementById('errorClose').addEventListener('click', () => {
            document.getElementById('errorModal').classList.remove('show');
        });
        
        // Toast notification helper
        function showNotification(message) {
            const toast = document.getElementById('toastNotification');
            const toastText = document.getElementById('toastText');
            if (toast && toastText) {
                toastText.textContent = message;
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }
        }
        
        (function initV22() {
            // --- DOM ELEMENTS ---
            const exportBtn = document.getElementById('exportBtn');
            const exportMenu = document.getElementById('exportMenu');
            const exportMd = document.getElementById('exportMd');
            const exportPdf = document.getElementById('exportPdf');
            const dropOverlay = document.getElementById('dropOverlay');
            const fileInput = document.getElementById('fileInput');
            const attachBtn = document.getElementById('attachBtn');
            const docBadge = document.getElementById('docBadge');
            const mainEl = document.querySelector('.main');
            
            // UI Areas
            const chatInputBox = document.getElementById('chatInputBox');
            const docControls = document.getElementById('docControls');
            const docNameDisplay = document.getElementById('docNameDisplay');
            const headerTitle = document.getElementById('headerTitle');
            
            // Sidebar & Header Controls
            const themeToggle = document.getElementById('themeToggle');
            const menuBtn = document.getElementById('menuBtn');
            const sidebar = document.getElementById('sidebar');
            const headerNewChat = document.getElementById('newChatBtnHeader');
            const themeHeaderBtn = document.getElementById('themeToggleHeader');
            const headerDivider = document.getElementById('headerDivider');

            // --- NEW ELEMENTS & STATE ---
            const chatExportWrapper = document.getElementById('chatExportWrapper');
            const analysisSaveBtn = document.getElementById('analysisSaveBtn');
            const analysisSaveText = document.getElementById('analysisSaveText');
            const switchFileBtn = document.getElementById('switchFileBtn');

            // LIFO State: null, 'brief', or 'compliance'
            let lastActiveReport = null;
            
            // Cancellation flag for long-running analysis operations
            let analysisAborted = false;

            // --- CENTRAL HEADER STATE MANAGER ---
            function updateHeaderState() {
                const isAnalysisMode = docControls && docControls.style.display === 'flex';

                if (isAnalysisMode) {
                    // --- ANALYSIS MODE RULES ---
                    if(headerNewChat) headerNewChat.classList.remove('visible');
                    if(themeHeaderBtn) themeHeaderBtn.classList.add('visible');

                    // EXPORT BUTTON LOGIC (LIFO)
                    if(chatExportWrapper) chatExportWrapper.style.display = 'none'; // Hide Chat Export
                    
                    if (lastActiveReport) {
                        // Show Analysis Save Button with correct text
                        if(analysisSaveBtn) {
                            analysisSaveBtn.style.display = 'flex';
                        }
                        if (analysisSaveText) {
                            // Both show "Save Report" but call different backend functions based on lastActiveReport
                            analysisSaveText.textContent = "Save Report";
                        }
                        // Show divider ONLY when save button is visible
                        if(headerDivider) headerDivider.classList.add('visible');
                    } else {
                        // No report yet -> Hide save button AND divider
                        if(analysisSaveBtn) analysisSaveBtn.style.display = 'none';
                        if(headerDivider) headerDivider.classList.remove('visible');
                    }

                } else {
                    // --- NORMAL CHAT MODE RULES ---
                    if(chatExportWrapper) chatExportWrapper.style.display = 'block';
                    if(analysisSaveBtn) analysisSaveBtn.style.display = 'none';
                    
                    if (sidebar && sidebar.classList.contains('collapsed')) {
                        if(headerNewChat) headerNewChat.classList.add('visible');
                        if(headerDivider) headerDivider.classList.add('visible');
                        if(themeHeaderBtn) themeHeaderBtn.classList.add('visible');
                    } else {
                        if(headerNewChat) headerNewChat.classList.remove('visible');
                        if(headerDivider) headerDivider.classList.remove('visible');
                        if(themeHeaderBtn) themeHeaderBtn.classList.remove('visible');
                    }
                }
            }
            
            window.updateHeaderState = updateHeaderState;

            // --- 1. MODE SWITCHING LOGIC ---
            
            window.enterAnalysisMode = function(filename) {
                chatInputBox.classList.add('hidden');
                docControls.style.display = 'flex'; 
                if (docNameDisplay) docNameDisplay.textContent = filename;
                if(headerTitle) headerTitle.innerHTML = 'TadqeeqAI <span class="header-title-badge analysis">Analysis</span>';
                
                if (sidebar && !sidebar.classList.contains('collapsed')) {
                    sidebar.classList.add('collapsed');
                }
                if (menuBtn) menuBtn.classList.add('force-hidden');
                if (headerNewChat) headerNewChat.classList.add('force-hidden');
                
                // RESET STATE
                lastActiveReport = null;
                analysisAborted = false; // Reset cancellation flag
                if (docBadge) docBadge.style.display = 'none';

                // INJECT IMPRESSIVE WELCOME SCREEN
                const chatContainer = document.getElementById('chat');
                chatContainer.innerHTML = `
                    <div class="analysis-welcome">
                        <div class="analysis-icon-box">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                <path d="M9 12h6M9 16h6M17 21H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5.586a1 1 0 0 1 .707.293l5.414 5.414a1 1 0 0 1 .293.707V19a2 2 0 0 1-2 2z"/>
                                <polyline points="14 2 14 8 20 8"/>
                            </svg>
                        </div>
                        <div class="analysis-title">Document Analysis</div>
                        <div class="analysis-subtitle">
                            Your document is loaded and ready for intelligent analysis.<br>
                            Choose an action below to extract strategic insights.
                        </div>
                        
                        <div class="analysis-features">
                            <div class="analysis-feature">
                                <div class="analysis-feature-icon scan">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                                        <polyline points="22 4 12 14.01 9 11.01"/>
                                    </svg>
                                </div>
                                <div class="analysis-feature-title">Compliance Scan</div>
                                <div class="analysis-feature-desc">Audit against SAMA & CMA regulations with pass/fail scoring</div>
                            </div>
                            <div class="analysis-feature">
                                <div class="analysis-feature-icon brief">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                        <line x1="16" y1="13" x2="8" y2="13"/>
                                        <line x1="16" y1="17" x2="8" y2="17"/>
                                    </svg>
                                </div>
                                <div class="analysis-feature-title">Executive Brief</div>
                                <div class="analysis-feature-desc">AI-generated summary of risks, financials & deadlines</div>
                            </div>
                        </div>
                        
                        <div class="analysis-tag">🔒 Secure Environment Active</div>
                    </div>`;

                updateHeaderState();
            };

            window.exitAnalysisMode = async function() {
                // SET ABORT FLAG to cancel any running analysis
                analysisAborted = true;
                busy = false; // Allow new operations
                
                try { await window.pywebview.api.clear_document(); } catch(e){}
                
                docControls.style.display = 'none';
                chatInputBox.classList.remove('hidden');
                if(headerTitle) headerTitle.textContent = 'Saudi Financial Law Assistant';
                
                if (menuBtn) {
                    menuBtn.classList.remove('force-hidden');
                    menuBtn.classList.remove('closed');
                    menuBtn.classList.remove('flipped');
                }
                if (headerNewChat) headerNewChat.classList.remove('force-hidden');
                
                if (sidebar && sidebar.classList.contains('collapsed')) {
                    sidebar.classList.remove('collapsed');
                }

                // RESTORE CHAT WELCOME
                const chatContainer = document.getElementById('chat');
                chatContainer.innerHTML = getWelcomeHTML();

                lastActiveReport = null;
                updateHeaderState();
            };

            // --- 2. ACTION HANDLERS ---

            window.generateBrief = async function() {
                if (busy) return;
                busy = true;
                analysisAborted = false; // Reset flag at start
                const chatContainer = document.getElementById('chat');
                
                // Central Loader
                chatContainer.innerHTML = `
                    <div class="central-loader" style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; animation: fadeIn 0.5s ease;">
                        <div class="jumping-dots" style="transform: scale(1.5); margin-bottom: 24px;"><span></span><span></span><span></span></div>
                        <div style="font-size:18px; font-weight:700; color:var(--text); letter-spacing:-0.01em;">Synthesizing Executive Brief</div>
                        <div style="font-size:13px; color:var(--text3); margin-top:8px; font-weight:500;">Analyzing risks, financials, and deadlines</div>
                    </div>`;
                
                try {
                    const r = await window.pywebview.api.generate_brief();
                    
                    // CHECK IF USER EXITED - Don't render if aborted
                    if (analysisAborted) {
                        busy = false;
                        return;
                    }

                    if (r.error) {
                        chatContainer.innerHTML = `<div style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--danger); font-weight:700;">Generation Failed<div style="font-size:13px; opacity:0.8; margin-top:4px;">${r.error}</div></div>`;
                    } else {
                        // RENDER BRIEF CARD
                        const renderedMarkdown = marked.parse(r.report);
                        const filename = document.getElementById('docNameDisplay').textContent || "Document";
                        const cardHtml = `
                        <div class="brief-wrapper" style="margin-top: 40px;">
                            <div class="brief-card">
                                <div class="brief-header">
                                    <div class="brief-title-group">
                                        <div class="brief-icon-large">
                                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                                        </div>
                                        <div class="brief-heading">
                                            <h2>Executive Strategic Brief</h2>
                                            <p>${escHtml(filename)}</p>
                                        </div>
                                    </div>
                                    <div class="ai-label" style="font-size:11px; font-weight:800; color:#a78bfa; background:rgba(139,92,246,0.15); padding:6px 14px; border-radius:100px; border:1px solid rgba(139,92,246,0.2); letter-spacing:0.05em;">AI GENERATED</div>
                                </div>
                                <div class="brief-content markdown-body">${renderedMarkdown}</div>
                            </div>
                        </div>`;
                        chatContainer.innerHTML = cardHtml;
                        
                        // SET LIFO STATE
                        lastActiveReport = 'brief';
                        updateHeaderState();
                    }
                } catch (e) { 
                    if (!analysisAborted) {
                        chatContainer.innerHTML = `<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--danger);">❌ Error: ${e.message}</div>`; 
                    }
                }
                busy = false;
            };

            window.runComplianceCheck = async function() {
                if (busy) return;
                busy = true;
                analysisAborted = false; // Reset flag at start
                const chatContainer = document.getElementById('chat');
                
                chatContainer.innerHTML = `
                    <div class="central-loader" style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; animation: fadeIn 0.5s ease;">
                        <div class="jumping-dots" style="transform: scale(1.5); margin-bottom: 24px;"><span></span><span></span><span></span></div>
                        <div style="font-size:18px; font-weight:700; color:var(--text); letter-spacing:-0.01em;">Running Compliance Audit</div>
                    </div>`;

                try {
                    const r = await window.pywebview.api.run_compliance_check();
                    
                    // CHECK IF USER EXITED - Don't render if aborted
                    if (analysisAborted) {
                        busy = false;
                        return;
                    }
                    
                    if (r.error) {
                         chatContainer.innerHTML = `<div style="height:100%; display:flex; flex-direction:column; align-items:center; justify-content:center; color:var(--danger); font-weight:700;">Scan Failed<div style="font-size:13px; opacity:0.8; margin-top:4px;">${r.error}</div></div>`;
                    } else {
                        // Render Compliance Report directly to chat container (replacing loader)
                        renderComplianceReportCentrally(r, chatContainer);
                        
                        // SET LIFO STATE
                        lastActiveReport = 'compliance';
                        updateHeaderState();
                    }
                } catch (e) { 
                    if (!analysisAborted) {
                        chatContainer.innerHTML = `<div style="height:100%; display:flex; align-items:center; justify-content:center; color:var(--danger);">❌ Error: ${e.message}</div>`; 
                    }
                }
                busy = false;
            };

            function renderComplianceReportCentrally(r, container) {
                let color = '#ff453a'; let dim = 'rgba(255, 69, 58, 0.2)';
                if (r.score >= 80) { color = '#3fb950'; dim = 'rgba(63, 185, 80, 0.2)'; } 
                else if (r.score >= 50) { color = '#ffbd2e'; dim = 'rgba(255, 189, 46, 0.2)'; }

                let itemsHtml = '';
                r.checks.forEach(c => {
                    const isPass = c.status === 'compliant';
                    const iconStyle = isPass ? 'color:#3fb950; background:rgba(63,185,80,0.15);' : 'color:#ffbd2e; background:rgba(255,189,46,0.15);';
                    const iconSvg = isPass ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><polyline points="20 6 9 17 4 12"/></svg>' : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12" y2="16"/></svg>';
                    itemsHtml += `<div class="comp-item"><div class="comp-icon" style="${iconStyle}">${iconSvg}</div><div><div class="comp-name">${c.name}</div><div class="comp-reg">${c.regulation}</div><div class="comp-detail">${c.detail}</div></div></div>`;
                });

                const reportHtml = `
                <div class="compliance-wrapper" style="margin-top:40px;">
                    <div class="comp-card" style="--score-color: ${color}; --score-dim: ${dim};">
                        <div class="comp-header">
                            <div class="comp-title"><h2>Compliance Scan</h2><p>${escHtml(r.filename)}</p></div>
                            <div class="score-box"><div class="score-val">${r.score}%</div><div class="score-lbl">Compliant</div></div>
                        </div>
                        <div class="comp-list">${itemsHtml}</div>
                    </div>
                </div>`;
                container.innerHTML = reportHtml;
            }

            // --- 3. EXPORT LOGIC (Handling new LIFO logic) ---
            if (analysisSaveBtn) {
                analysisSaveBtn.addEventListener('click', async () => {
                    if (!lastActiveReport) return;
                    try {
                        let r;
                        if (lastActiveReport === 'brief') r = await window.pywebview.api.export_brief_pdf();
                        else if (lastActiveReport === 'compliance') r = await window.pywebview.api.export_compliance_pdf();

                        if (r.error) showError('Export Failed', r.error);
                        else if (r.success) {
                            const reportType = lastActiveReport === 'brief' ? 'Executive Brief' : 'Compliance Report';
                            showNotification(`${reportType} Saved Successfully`);
                        }
                    } catch (e) { showError('Error', e.message); }
                });
            }

            // Keep standard export logic for chat
            if (exportMd) exportMd.addEventListener('click', async () => { if (exportMenu) exportMenu.classList.remove('show'); try { let r = await window.pywebview.api.export_markdown(); if (r.error) showError('Export Failed', r.error); else if (r.success) showError('Export Complete', 'Saved to: ' + r.path); } catch(e) { showError('Error', e.message); } });
            if (exportPdf) exportPdf.addEventListener('click', async () => { if (exportMenu) exportMenu.classList.remove('show'); try { let r = await window.pywebview.api.export_pdf(); if (r.error) showError('Export Failed', r.error); else if (r.success) showError('Export Complete', 'Saved to: ' + r.path); } catch(e) { showError('Error', e.message); } });

            // --- 4. FILE HANDLING ---
            async function handleFile(file) {
                const ext = file.name.split('.').pop().toLowerCase();
                if (!['pdf', 'docx', 'doc'].includes(ext)) { showError('Invalid File', 'PDF or DOCX only.'); return; }
                const reader = new FileReader();
                reader.onload = async (e) => {
                    try {
                        const base64 = e.target.result.split(',')[1];
                        const r = await window.pywebview.api.upload_document(base64, file.name);
                        if (r.error) { showError('Upload Failed', r.error); return; }
                        window.enterAnalysisMode(r.filename);
                        showNotification("Document Loaded Successfully");
                    } catch (err) { showError('Error', err.message); }
                };
                reader.readAsDataURL(file);
            }
            
            // Switch File Button Listener
            if (switchFileBtn && fileInput) {
                switchFileBtn.addEventListener('click', () => fileInput.click());
            }

            // --- 5. EVENT LISTENERS (Keep existing) ---
            if (mainEl && dropOverlay) { mainEl.addEventListener('dragenter', (e) => { e.preventDefault(); dropOverlay.classList.add('active'); }); mainEl.addEventListener('dragover', (e) => { e.preventDefault(); dropOverlay.classList.add('active'); }); dropOverlay.addEventListener('dragleave', (e) => { e.preventDefault(); dropOverlay.classList.remove('active'); }); dropOverlay.addEventListener('drop', (e) => { e.preventDefault(); dropOverlay.classList.remove('active'); if (e.dataTransfer.files[0]) handleFile(e.dataTransfer.files[0]); }); }
            if (attachBtn && fileInput) { attachBtn.addEventListener('click', () => fileInput.click()); fileInput.addEventListener('change', (e) => { if (e.target.files[0]) { handleFile(e.target.files[0]); fileInput.value = ''; } }); }
            if (exportBtn && exportMenu) { exportBtn.addEventListener('click', (e) => { e.stopPropagation(); exportMenu.classList.toggle('show'); }); document.addEventListener('click', (e) => { if (exportMenu && !e.target.closest('#exportBtn') && !e.target.closest('#exportMenu')) exportMenu.classList.remove('show'); }); }

            // --- 6. SIDEBAR LOGIC (Keep existing) ---
             if (menuBtn && sidebar) {
                const sunIcon = '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';
                const moonIcon = '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
                function updateThemeIcons() {
                    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
                    const icon = isLight ? moonIcon : sunIcon;
                    const sbToggle = document.getElementById('themeToggle');
                    if (sbToggle) sbToggle.innerHTML = icon;
                    if (themeHeaderBtn) themeHeaderBtn.innerHTML = icon;
                }
                function toggleTheme(e) {
                    if(e) e.stopPropagation();
                    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
                    const newTheme = isLight ? 'dark' : 'light';
                    document.documentElement.setAttribute('data-theme', newTheme);
                    try { localStorage.setItem('tadqeeq-theme', newTheme); } catch(err){}
                    updateThemeIcons();
                }
                const sbToggle = document.getElementById('themeToggle');
                if (sbToggle) sbToggle.onclick = toggleTheme;
                if (themeHeaderBtn) themeHeaderBtn.onclick = toggleTheme;
                updateThemeIcons();

                try {
                    const savedState = localStorage.getItem('tadqeeq-sidebar');
                    if (savedState === 'collapsed') {
                        sidebar.classList.add('collapsed');
                        menuBtn.classList.add('closed');
                    }
                } catch(e) {}
                
                // Initial Header State
                updateHeaderState();

                menuBtn.onclick = function() {
                    sidebar.classList.toggle('collapsed');
                    menuBtn.classList.toggle('closed'); 
                    updateHeaderState(); 
                    try { localStorage.setItem('tadqeeq-sidebar', sidebar.classList.contains('collapsed') ? 'collapsed' : 'expanded'); } catch(e) {}
                };
                
                sidebar.addEventListener('transitionend', () => { updateHeaderState(); });
            }
        })();
    </script>
</body>
</html>'''
