# AutoTest AI - Complete Testing Guide

## Test Credentials
- **Email:** venki123@gmail.com
- **Password:** Venki@123

## Servers Status
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000

---

## Test Project: TodoMVC React Application

**GitHub Repository:** https://github.com/tastejs/todomvc/tree/master/examples/react

**Why This Project:**
- Well-documented and widely known
- Clear requirements (TodoMVC specification)
- Good complexity level for testing
- Real-world React application
- Active maintenance

---

## Step-by-Step Testing Process

### 1. Login to Application

1. Open browser: http://localhost:3000
2. Click "Try Now" or navigate to dashboard
3. If not logged in, register/login with:
   - Email: `venki123@gmail.com`
   - Password: `Venki@123`

### 2. Create Project

**Project Details:**
- **Name:** TodoMVC React App
- **Description:** A fully-featured todo application implementing the TodoMVC specification using React and modern JavaScript practices
- **GitHub URL:** https://github.com/tastejs/todomvc
- **Deployment URL:** https://todomvc.com/examples/react/

### 3. Upload Requirements Document

Create a comprehensive requirements document with the following content:

```markdown
# TodoMVC React Application - Requirements Specification

## 1. Functional Requirements

### FR-1: Task Management
- Users must be able to add new todo items by typing in the input field and pressing Enter
- Each todo item must display with a checkbox and editable text
- Users must be able to mark todos as complete by clicking the checkbox
- Users must be able to edit todo text by double-clicking on it
- Users must be able to delete individual todos using the delete button

### FR-2: Bulk Operations
- Users must be able to mark all todos as complete/incomplete using the toggle-all checkbox
- Users must be able to clear all completed todos at once
- The application must show the count of active (incomplete) todos

### FR-3: Filtering
- Users must be able to filter todos by status: All, Active, Completed
- The active filter must be visually indicated
- URL routing must reflect the current filter (/#/, /#/active, /#/completed)
- Filter state must persist on page refresh

### FR-4: Data Persistence
- All todo data must persist in browser localStorage
- Data must survive page refreshes and browser restarts
- Changes must be saved immediately without requiring manual save action

### FR-5: User Interface
- Input field must have placeholder text: "What needs to be done?"
- Completed todos must be visually distinguished (strikethrough text)
- Edit mode must show input with current todo text
- Empty todo list must hide the main section and footer

## 2. Non-Functional Requirements

### NFR-1: Performance
- Initial page load must complete in under 2 seconds
- Todo operations (add, complete, delete) must respond in under 100ms
- Application must remain responsive with 1000+ todos

### NFR-2: Usability
- Interface must follow TodoMVC specification exactly
- Keyboard navigation must work (Tab, Enter, Escape)
- Mobile-responsive design for touch devices
- Clear visual feedback for all user actions

### NFR-3: Browser Compatibility
- Must work on Chrome, Firefox, Safari, Edge (latest versions)
- Must support ES6+ JavaScript features
- Must gracefully handle localStorage unavailability

### NFR-4: Security
- Input must be sanitized to prevent XSS attacks
- localStorage data must not contain executable code
- No external API calls or data transmission

### NFR-5: Maintainability
- Code must follow React best practices
- Components must be modular and reusable
- PropTypes or TypeScript for type checking
- Comprehensive comments for complex logic

## 3. Test Objectives

1. **Functional Verification**
   - Verify all CRUD operations work correctly
   - Test bulk operations with multiple todos
   - Validate filter functionality and URL routing
   - Confirm data persistence across sessions

2. **Edge Cases**
   - Test with empty todo list
   - Test with single todo
   - Test with 100+ todos
   - Test with very long todo text (500+ characters)
   - Test with special characters and emojis

3. **User Interactions**
   - Verify keyboard shortcuts work
   - Test double-click to edit
   - Test Enter/Escape key behavior in edit mode
   - Verify checkbox toggle feedback

4. **Performance Testing**
   - Measure initial load time
   - Test operation speed with large dataset
   - Check memory usage over time
   - Verify no memory leaks

5. **Cross-Browser Testing**
   - Test core functionality on all major browsers
   - Verify localStorage works consistently
   - Check CSS rendering consistency

## 4. Known Risks

### High Priority Risks
- **localStorage Quota:** Browser may limit storage, causing data loss with many todos
- **XSS Vulnerability:** Improperly sanitized input could execute malicious scripts
- **Race Conditions:** Rapid user actions might cause state inconsistencies

### Medium Priority Risks
- **Browser Compatibility:** Older browsers may not support ES6 features
- **Mobile Touch Events:** Touch interactions might not work reliably
- **Performance Degradation:** Large todo lists may slow down rendering

### Low Priority Risks
- **URL Routing Issues:** History API may not work in all environments
- **Focus Management:** Tab order might be confusing for keyboard users
- **Accessibility:** Screen readers may not announce state changes properly

## 5. Acceptance Criteria

### Must Have (Critical)
✅ Add todo functionality works
✅ Complete/uncomplete todos works
✅ Delete todo works
✅ Data persists in localStorage
✅ Filters work correctly (All/Active/Completed)

### Should Have (Important)
✅ Edit todo by double-click works
✅ Toggle all checkbox works
✅ Clear completed button works
✅ Active todo count displays correctly
✅ URL routing matches filter state

### Nice to Have (Enhancement)
✅ Smooth animations for add/delete
✅ Loading states for slow operations
✅ Undo/redo functionality
✅ Keyboard shortcuts visible
✅ Dark mode support

## 6. Complexity Assessment

**Overall Complexity: MEDIUM**

**Breakdown:**
- State Management: Medium (multiple interdependent states)
- Data Persistence: Low (simple localStorage implementation)
- UI Interactions: Medium (edit mode, keyboard handling)
- Testing Coverage: High (many edge cases to consider)
- Performance Considerations: Medium (optimization needed for large lists)
```

### 4. Expected Test Cases Generated

The AI should generate test cases similar to:

**Functional Tests:**
1. ✅ Add New Todo Item
2. ✅ Mark Todo as Complete
3. ✅ Delete Todo Item
4. ✅ Edit Existing Todo
5. ✅ Toggle All Todos
6. ✅ Clear Completed Todos
7. ✅ Filter Active Todos
8. ✅ Filter Completed Todos
9. ✅ Data Persistence After Refresh

**Boundary Tests:**
10. ✅ Add Empty Todo (should fail)
11. ✅ Add Todo with 500+ Characters
12. ✅ Add Todo with Special Characters
13. ✅ Delete Last Remaining Todo
14. ✅ Toggle All with Empty List

**Negative Tests:**
15. ✅ Invalid Input Handling
16. ✅ XSS Attack Prevention
17. ✅ localStorage Unavailable Scenario

**Performance Tests:**
18. ✅ Initial Load Time Under 2s
19. ✅ Operation Response Time Under 100ms
20. ✅ Handling 100+ Todos

### 5. Run All Tests

1. Navigate to **Test Cases** tab
2. Click **"Run All Tests"** button
3. Enter deployment URL: `https://todomvc.com/examples/react/`
4. Wait for all tests to execute
5. Review results:
   - ✅ Passed tests (green)
   - ❌ Failed tests (red)
   - ⏸️ Pending tests (yellow)

### 6. Generate PDF Report

1. Navigate to **Reports** tab
2. Review the live project summary:
   - Total Requirements
   - Total Test Cases
   - Execution Results
   - Pass Rate
   - Bugs Logged
3. Click **"Download PDF"** button
4. PDF will be generated and downloaded with filename: `TestReport_TodoMVC_React_App_YYYYMMDD_HHMMSS.pdf`

---

## PDF Report Contents

The generated PDF report includes:

### 📄 Page 1: Title Page
- Report title: "AutoTest AI - Test Execution Report"
- Project name
- Project description
- Repository URL
- Report generation date/time

### 📊 Page 2: Executive Summary
- Metrics table:
  - Total Requirements
  - Total Test Cases
  - Total Executions
  - Passed/Failed/Pending counts
  - Success Rate
  - Bugs Reported
- Overall status assessment (Excellent/Good/Fair/Critical)
- Color-coded status interpretation

### 📋 Page 3: Requirements Analysis
- List of all requirements
- Requirement titles and descriptions
- Status badges (analyzed/pending/error)
- Content previews (first 500 characters)

### 🧪 Page 4: Test Cases
- Grouped by test type (functional, boundary, negative, performance)
- Test case titles and descriptions
- Total count per type
- Detailed test steps (if applicable)

### ✅ Page 5: Execution Results
- Table format with columns:
  - Test number
  - Test case name
  - Status (color-coded: green=passed, red=failed)
  - Execution time
  - Execution date
- Summary statistics

### 🐛 Page 6: Reported Bugs (if any)
- Bug titles and descriptions
- Severity levels (Critical/High/Medium/Low)
- Color-coded severity badges
- Creation dates

---

## Expected Results

### Success Metrics
- ✅ **20+ test cases generated** automatically from requirements
- ✅ **Test execution completes** in 2-5 minutes
- ✅ **Success rate:** 70-90% (depending on implementation quality)
- ✅ **PDF report generated** in under 5 seconds
- ✅ **PDF file size:** 100-500 KB

### Common Issues and Solutions

**Issue 1: All Tests Fail**
- **Cause:** Incorrect deployment URL or site is down
- **Solution:** Verify URL is accessible, check CORS settings

**Issue 2: Tests Time Out**
- **Cause:** Selectors not found or page loads slowly
- **Solution:** Review test scripts, check selector accuracy

**Issue 3:** PDF Generation Fails**
- **Cause:** reportlab not installed or import error
- **Solution:** Run `pip install reportlab` in backend venv

**Issue 4: No Test Cases Generated**
- **Cause:** LLM/Ollama not available, fallback triggered
- **Solution:** Verify requirement content has clear objectives

**Issue 5: Empty PDF or Missing Sections**
- **Cause:** No executions recorded or data not saved
- **Solution:** Ensure tests were run and results saved to database

---

## Manual Testing Checklist

After automated tests, perform manual verification:

### Frontend UI
- [ ] Login/Register works
- [ ] Project creation works
- [ ] Requirement upload works (file + text)
- [ ] Test cases display correctly
- [ ] Filters work (All/Active/Completed)
- [ ] Run All Tests button works
- [ ] Progress indicator shows during execution
- [ ] Results update in real-time
- [ ] Reports tab shows statistics
- [ ] PDF download button works
- [ ] PDF opens and displays correctly

### Backend API
- [ ] POST /api/v1/auth/register works
- [ ] POST /api/v1/auth/login returns JWT token
- [ ] GET /api/v1/projects/ returns user's projects
- [ ] POST /api/v1/requirements/ accepts file upload
- [ ] GET /api/v1/tests/project/{id} returns test cases
- [ ] POST /api/v1/tests/project/{id}/run-all executes tests
- [ ] GET /api/v1/reports/project/{id}/pdf generates PDF

### Database
- [ ] Projects saved with correct owner_id
- [ ] Requirements stored with structured_data
- [ ] Test cases linked to requirements
- [ ] Executions recorded with status and logs
- [ ] Bugs can be created and retrieved

---

## Performance Benchmarks

### Expected Timings
- **Login:** < 500ms
- **Load Dashboard:** < 1s (with cache), < 2s (without)
- **Create Project:** < 300ms
- **Upload Requirement:** 3-15s (with AI analysis)
- **Generate Test Cases:** 5-20s (depends on LLM)
- **Run All Tests (20 tests):** 2-5 minutes
- **Generate PDF:** 2-5s
- **Download PDF:** < 1s

### Resource Usage
- **Backend Memory:** 200-500 MB (with LLM loaded)
- **Frontend Bundle:** ~2 MB (minified)
- **Database Size:** ~10 MB per project (with 100 tests)
- **PDF File Size:** 100-500 KB per report

---

## Troubleshooting

### Backend Won't Start
```bash
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Won't Start
```bash
cd frontend
npm install
npm run dev
```

### Database Locked
```bash
# Stop backend
# Delete autotest.db
# Restart backend (will recreate DB)
```

### Ollama Not Working
```bash
# Install Ollama manually from https://ollama.com
ollama serve
ollama pull llama3.2
# Restart backend
```

---

## Success Criteria

✅ **All Features Working:**
- User authentication
- Project management
- Requirement analysis
- Test case generation
- Test execution
- Bug tracking
- Report generation
- PDF export

✅ **Performance Targets Met:**
- Dashboard loads in < 2s
- Test generation in < 20s
- PDF generation in < 5s

✅ **Quality Metrics:**
- 70%+ test pass rate
- Detailed PDF with all sections
- No server errors
- Smooth user experience

---

## Test Report Template

After completing tests, document results:

```markdown
# Test Execution Report

**Date:** [DATE]
**Tester:** [NAME]
**Project:** TodoMVC React App

## Summary
- Total Test Cases: [X]
- Passed: [X]
- Failed: [X]
- Success Rate: [X]%

## Issues Found
1. [Issue description]
2. [Issue description]

## Observations
- [Positive/negative observations]

## Recommendations
- [Improvements needed]
```

---

## Contact & Support

If you encounter issues:
1. Check backend logs: `backend/backend.log`
2. Check frontend console (F12 in browser)
3. Review this guide's troubleshooting section
4. Check `PERFORMANCE_OPTIMIZATIONS.md` for system requirements

**App is ready for testing!** 🚀
