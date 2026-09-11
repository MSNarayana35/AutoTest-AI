# AutoTest AI - Visual Diagrams and Graphs

This directory contains professional, high-resolution graphs and diagrams that visualize the AutoTest AI system architecture, workflows, and analytics.

## 📊 Generated Graphs

### 1. System Architecture (`01_system_architecture.png`)
**Complete platform architecture overview**
- Frontend Layer (Next.js + TypeScript)
- API Gateway (FastAPI + JWT)
- Backend Services (Requirements, Test Generation, Execution)
- AI Agent Layer (GPT-4 Integration)
- Database Layer (SQLite with 17 tables)
- File Storage System
- Test Execution Engine (Playwright/Selenium)
- Monitoring & Analytics

### 2. Test Execution Flow (`02_test_execution_flow.png`)
**End-to-end test execution pipeline**
- 9-step process from user action to dashboard update
- Real-time timing annotations
- Color-coded by function:
  - Blue: User actions
  - Green: Pre-execution setup
  - Purple: Test execution
  - Orange: Result capture
  - Pink: Self-healing
  - Cyan: Data storage
  - Red: Notifications
  - Brown: Bug creation
  - Gray: Dashboard updates

### 3. AI Agent Workflow (`03_ai_agent_workflow.png`)
**Multi-agent AI processing system**
- Requirement Agent: PRD analysis
- Test Generator Agent: Playwright script creation
- Execution Engine: Browser automation
- Self-Healing Agent: Automatic failure fixes
- Evaluation Agent: Quality assessment
- Shows LLM integration points and data flow

### 4. Data Flow Diagram (`04_data_flow.png`)
**How data moves through the system**
- Input Layer: PRD Files, GitHub, User Input, CI/CD Webhooks
- API Endpoints Layer (100+ routes)
- Processing Layer (Business Logic + AI)
- Storage Layer (Database + File Storage)
- Output Layer (Dashboard, Reports, Alerts, Notifications)
- Includes data volume annotations

### 5. Statistics Dashboard (`05_statistics_dashboard.png`)
**Analytics and metrics visualization**
- Test Success Rate Trend (30-day line chart)
- Test Distribution by Type (pie chart)
- Execution Time Comparison (bar chart)
- Bug Discovery Over Time (stacked area chart)
- Flaky Test Detection Matrix (scatter plot)
- Self-Healing Success Rate (horizontal bar chart)

### 6. CI/CD Pipeline (`06_cicd_pipeline.png`)
**GitHub Actions integration flow**
- GitHub Event Trigger
- GitHub Actions Workflow
- Setup & Dependency Installation
- Fetch Tests from AutoTest AI
- Run Playwright Tests
- Upload Results
- Multi-channel Notifications
- PR Comment with Test Results
- Timing annotations at each step

### 7. Database Schema (`07_database_schema.png`)
**Complete database structure (17 tables)**
- Core Tables (users, projects, requirements, test_cases, test_executions)
- Bug Tracking (bug_reports)
- Visual Testing (visual_tests, visual_baselines, visual_comparisons, visual_test_runs)
- CI/CD (cicd_configs, workflow_runs)
- Integrations (integrations, notifications)
- Platform & Tags (platforms, tags, test_case_tags)
- Self-Healing (self_healing_logs)
- Color-coded by category with relationship arrows

### 8. User Journey (`08_user_journey.png`)
**Timeline from onboarding to production**
- Day 1: Sign Up & Project Setup
- Day 2: AI Test Generation
- Week 1: CI/CD Integration
- Week 2: Visual Testing
- Month 1: Production Ready
- Progress indicators (20% → 100%)
- User experience sentiment indicators

## 🎨 Design Features

All graphs feature:
- **White background** for professional presentations
- **High resolution** (300 DPI) for print quality
- **Color-coded elements** for easy comprehension
- **Clear typography** for readability
- **Consistent styling** across all diagrams

## 🔧 Technical Details

- **Format**: PNG
- **Resolution**: 300 DPI
- **Color Space**: RGB
- **Background**: White (#FFFFFF)
- **Generated with**: matplotlib + numpy
- **Font**: Sans-serif (system default)

## 📦 Usage

These graphs can be used in:
- Technical documentation
- Architecture review presentations
- Stakeholder meetings
- Developer onboarding materials
- Marketing collateral
- Blog posts and articles
- Academic papers
- Pitch decks

## 🔄 Regeneration

To regenerate all graphs:

```bash
# Activate virtual environment
cd backend
.\venv\Scripts\activate

# Run generator
cd ..
python generate_graphs.py
```

The script will recreate all 8 graphs with the latest data and styling.

## 📝 Notes

- Some emoji characters may show warnings due to font limitations but won't affect the visual output
- Graphs are optimized for both digital display and print
- All colors follow Material Design color palette for accessibility
- Timing annotations use realistic estimates based on typical execution times

## 📄 License

These diagrams are part of the AutoTest AI project and follow the same license terms.

---

**Generated**: January 2025  
**Version**: 1.0  
**Total Graphs**: 8 professional visualizations
