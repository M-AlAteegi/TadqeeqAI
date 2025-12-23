# TadqeeqAI Release Notes

---

## v3.0 — December 2025

### 🎨 Major UI/UX Overhaul

This release features a complete redesign of the user interface, inspired by modern glassmorphic design principles and Apple's latest design language.

#### ✨ Visual Design
- **New Glassmorphic Theme**: Elegant frosted glass panels with subtle gradients and refined borders
- **Gradient Mesh Backgrounds**: Beautiful static gradient backgrounds in both light and dark modes
- **Improved Typography**: Better font weights, spacing, and hierarchy throughout
- **Polished Color Palette**: Refined teal accent colors with proper contrast ratios

#### 🎬 Animations & Interactions
- **Smooth Sidebar Toggle**: Fluid slide animation with the main panel elegantly covering the sidebar space
- **Chat Delete Animation**: Deleted chats slide out gracefully with collapse animation
- **Button Micro-interactions**: Subtle hover states and click feedback across all interactive elements
- **Toast Notifications**: iPhone-style notifications for actions (file upload, chat delete, report save)
- **Sidebar Toggle Icon Rotation**: Menu icon rotates 180° when sidebar state changes

#### 🏠 Welcome Screens
- **Redesigned Chat Welcome**: Floating animated icon, gradient title, hover-interactive stat cards
- **New Analysis Welcome**: Feature cards explaining Compliance Scan and Executive Brief capabilities
- **Unified Welcome System**: Single source of truth for welcome screens across the app

#### 📊 Header Improvements
- **Dynamic Header Title**: Shows "Saudi Financial Law Assistant" in Chat mode, "TadqeeqAI + Analysis badge" in Analysis mode
- **Theme Toggle Animation**: Icon rotates on click with smooth transitions
- **Improved Button Layout**: Better spacing and visual hierarchy for Export/New Chat/Save buttons

#### 🔧 Sidebar Polish
- **New Logo Design**: Gradient icon with subtle pulse animation
- **Status Indicator**: Pulsing green dot next to "Aya 8B · v3.0" showing system is active
- **Refined Section Headers**: Better typography for "Recent Chats" and "Try These"

#### 📄 Analysis Mode Enhancements
- **Operation Cancellation**: Exit button now properly cancels ongoing Brief/Compliance operations
- **Improved Loading States**: Centered loaders with descriptive text during processing
- **LIFO Export Logic**: Save button dynamically updates based on last generated report

#### ⚡ Performance Optimizations
- **Reduced GPU Usage**: Removed expensive `backdrop-filter` blur from large panels
- **Optimized Glass Effect**: Achieved glass aesthetic using gradients and opacity instead of blur
- **Kept Blur on Small Elements**: Dropdowns and toasts retain blur (minimal performance impact)

#### 🐛 Bug Fixes
- Fixed duplicate welcome screens causing inconsistent UI
- Fixed header buttons layout issues in Analysis mode
- Fixed dropdown menu being clipped by parent overflow
- Fixed sidebar content squishing during collapse animation
- Fixed chat export wrapper visibility toggling

---

## v2.2 — November 2025

### 📄 Document Analysis Features
- **PDF/DOCX Upload**: Drag & drop or click to upload documents
- **Compliance Checker**: Automated regulatory compliance scanning across 6 categories
- **Executive Brief Generation**: AI-powered strategic document summaries
- **Report Export**: Save compliance reports and briefs as PDF

### 💬 Chat Improvements
- **Chat Export**: Export conversations to Markdown or PDF format
- **Improved Input Bar**: Gemini-style bilateral button layout
- **Better Message Rendering**: Enhanced markdown support with syntax highlighting

### 🎨 UI Updates
- **Document Badge**: Shows loaded document name with quick actions
- **Analysis Mode UI**: Dedicated interface for document analysis workflow
- **Loading Indicators**: Progress feedback during document processing

---

## v2.1 — October 2025

### 🔍 Search Improvements
- **Hybrid Search**: Combined BM25 + semantic search with Reciprocal Rank Fusion
- **Better Arabic Support**: Improved tokenization for Arabic queries
- **Smart Regulator Detection**: Auto-routes queries to SAMA or CMA documents

### 💾 Data Management
- **Persistent Chat History**: Conversations saved locally as JSON
- **Chat Rename/Delete**: Manage saved conversations from sidebar

---

## v2.0 — September 2025

### 🚀 Initial Public Release
- **RAG System**: 1,350+ indexed articles from SAMA and CMA
- **Bilingual Support**: Full English and Arabic query/response support
- **PyWebView Desktop App**: Native desktop application experience
- **Aya 8B Integration**: Local LLM via Ollama for privacy

---

## v1.0 — August 2025

### 🧪 Internal Development
- Initial prototype with basic search functionality
- Command-line interface
- Single regulator support (SAMA only)

---

<p align="center">
  <b>Thank you for using TadqeeqAI!</b>
  <br>
  For issues or feature requests, please open a GitHub issue.
</p>
