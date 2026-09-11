"""
AutoTest AI - Graph Generator
Generates professional graphs and diagrams with white background
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
import numpy as np
import os

# Create output directory
os.makedirs('graphs', exist_ok=True)

# Set white background style
plt.style.use('default')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['savefig.facecolor'] = 'white'
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def create_system_architecture():
    """Create System Architecture Diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'AutoTest AI - System Architecture', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # Frontend Layer
    frontend = FancyBboxPatch((0.5, 7.5), 4, 1.5, boxstyle="round,pad=0.1", 
                             edgecolor='#2196F3', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(frontend)
    ax.text(2.5, 8.6, 'Frontend Layer', ha='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 8.2, 'Next.js 14 + TypeScript', ha='center', fontsize=9)
    ax.text(2.5, 7.9, 'React Components', ha='center', fontsize=8)
    
    # API Gateway
    api = FancyBboxPatch((5.5, 7.5), 3, 1.5, boxstyle="round,pad=0.1",
                        edgecolor='#4CAF50', facecolor='#E8F5E9', linewidth=2)
    ax.add_patch(api)
    ax.text(7, 8.6, 'API Gateway', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 8.2, 'FastAPI + CORS', ha='center', fontsize=9)
    ax.text(7, 7.9, 'JWT Authentication', ha='center', fontsize=8)
    
    # External Services
    external = FancyBboxPatch((9.5, 7.5), 4, 1.5, boxstyle="round,pad=0.1",
                             edgecolor='#FF9800', facecolor='#FFF3E0', linewidth=2)
    ax.add_patch(external)
    ax.text(11.5, 8.6, 'External Services', ha='center', fontsize=11, fontweight='bold')
    ax.text(11.5, 8.2, 'GitHub • Slack • Discord', ha='center', fontsize=9)
    ax.text(11.5, 7.9, 'Email SMTP', ha='center', fontsize=8)
    
    # Backend Services
    backend = FancyBboxPatch((0.5, 5.2), 6, 1.8, boxstyle="round,pad=0.1",
                            edgecolor='#9C27B0', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(backend)
    ax.text(3.5, 6.7, 'Backend Services', ha='center', fontsize=11, fontweight='bold')
    ax.text(3.5, 6.3, 'Requirements • Test Generation • Execution', ha='center', fontsize=9)
    ax.text(3.5, 5.9, 'Visual Testing • Bug Tracking • Reports', ha='center', fontsize=9)
    ax.text(3.5, 5.5, 'CI/CD Integration • Notifications', ha='center', fontsize=9)
    
    # AI Agent Layer
    ai = FancyBboxPatch((7.5, 5.2), 6, 1.8, boxstyle="round,pad=0.1",
                       edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2)
    ax.add_patch(ai)
    ax.text(10.5, 6.7, 'AI Agent Layer', ha='center', fontsize=11, fontweight='bold')
    ax.text(10.5, 6.3, 'RequirementAgent • TestGeneratorAgent', ha='center', fontsize=9)
    ax.text(10.5, 5.9, 'SelfHealingAgent • EvaluationAgent', ha='center', fontsize=9)
    ax.text(10.5, 5.5, 'OpenAI GPT-4 Integration', ha='center', fontsize=8, style='italic')
    
    # Database Layer
    db = FancyBboxPatch((0.5, 2.8), 4, 1.8, boxstyle="round,pad=0.1",
                       edgecolor='#00BCD4', facecolor='#E0F7FA', linewidth=2)
    ax.add_patch(db)
    ax.text(2.5, 4.3, 'Database Layer', ha='center', fontsize=11, fontweight='bold')
    ax.text(2.5, 3.9, 'SQLite Database', ha='center', fontsize=9)
    ax.text(2.5, 3.5, '17 Tables', ha='center', fontsize=9)
    ax.text(2.5, 3.1, 'Users • Projects • Tests • Bugs', ha='center', fontsize=8)
    
    # File Storage
    storage = FancyBboxPatch((5.5, 2.8), 4, 1.8, boxstyle="round,pad=0.1",
                            edgecolor='#795548', facecolor='#EFEBE9', linewidth=2)
    ax.add_patch(storage)
    ax.text(7.5, 4.3, 'File Storage', ha='center', fontsize=11, fontweight='bold')
    ax.text(7.5, 3.9, 'Local File System', ha='center', fontsize=9)
    ax.text(7.5, 3.5, 'Screenshots • Traces • Reports', ha='center', fontsize=8)
    ax.text(7.5, 3.1, 'PRD Files • Visual Baselines', ha='center', fontsize=8)
    
    # Test Execution Engine
    execution = FancyBboxPatch((10.5, 2.8), 3, 1.8, boxstyle="round,pad=0.1",
                              edgecolor='#607D8B', facecolor='#ECEFF1', linewidth=2)
    ax.add_patch(execution)
    ax.text(12, 4.3, 'Test Execution', ha='center', fontsize=11, fontweight='bold')
    ax.text(12, 3.9, 'Playwright', ha='center', fontsize=9)
    ax.text(12, 3.5, 'Selenium', ha='center', fontsize=9)
    ax.text(12, 3.1, 'Browsers', ha='center', fontsize=8)
    
    # Monitoring & Analytics
    monitor = FancyBboxPatch((3, 0.5), 8, 1.5, boxstyle="round,pad=0.1",
                            edgecolor='#FF5722', facecolor='#FBE9E7', linewidth=2)
    ax.add_patch(monitor)
    ax.text(7, 1.6, 'Monitoring & Analytics', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 1.2, 'Real-time Dashboard • Test Metrics • Success Rates', ha='center', fontsize=9)
    ax.text(7, 0.8, 'Flaky Test Detection • Performance Analytics', ha='center', fontsize=9)
    
    # Arrows - Frontend to API
    arrow1 = FancyArrowPatch((4.5, 8.25), (5.5, 8.25), 
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow1)
    
    # Arrows - API to Backend
    arrow2 = FancyArrowPatch((7, 7.5), (3.5, 7.0), 
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow2)
    
    # Arrows - API to AI
    arrow3 = FancyArrowPatch((8, 7.5), (10.5, 7.0), 
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow3)
    
    # Arrows - Backend to Database
    arrow4 = FancyArrowPatch((2.5, 5.2), (2.5, 4.6), 
                            arrowstyle='<->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow4)
    
    # Arrows - Backend to Storage
    arrow5 = FancyArrowPatch((6.5, 5.2), (7.5, 4.6), 
                            arrowstyle='<->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow5)
    
    # Arrows - AI to Execution
    arrow6 = FancyArrowPatch((11.5, 5.2), (12, 4.6), 
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow6)
    
    # Arrows - All to Monitoring
    arrow7 = FancyArrowPatch((3.5, 2.8), (5, 2.0), 
                            arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow7)
    
    plt.tight_layout()
    plt.savefig('graphs/01_system_architecture.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 01_system_architecture.png")


def create_test_execution_flow():
    """Create Test Execution Flow Diagram"""
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Title
    ax.text(5, 13.5, 'Test Execution Pipeline', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    steps = [
        (12.5, 'User Action', 'Select Test & Click Execute', '#2196F3'),
        (11.3, 'Pre-Execution', 'Initialize Browser\nLoad Configuration\nSet Viewport', '#4CAF50'),
        (9.8, 'Test Execution', 'Run Playwright Script\nNavigate • Click • Type\nAssertions', '#9C27B0'),
        (8.3, 'Result Capture', 'Screenshot on Fail\nTrace Collection\nLog Recording', '#FF9800'),
        (6.8, 'Self-Healing', 'AI Analyzes Failure\nSuggest Fixes\nUpdate Selectors', '#E91E63'),
        (5.3, 'Data Storage', 'Save Execution Record\nStore Artifacts\nUpdate Statistics', '#00BCD4'),
        (3.8, 'Notifications', 'Email Alert\nSlack Message\nIn-App Notification', '#FF5722'),
        (2.3, 'Bug Creation', 'Auto-Create Bug Report\nAssign to Developer\nAttach Evidence', '#795548'),
        (0.8, 'Dashboard Update', 'Refresh Metrics\nUpdate Charts\nShow Results', '#607D8B'),
    ]
    
    for i, (y_pos, title, desc, color) in enumerate(steps):
        # Box
        box = FancyBboxPatch((1, y_pos-0.4), 8, 0.9, boxstyle="round,pad=0.1",
                            edgecolor=color, facecolor=color+'20', linewidth=2.5)
        ax.add_patch(box)
        
        # Step number
        circle = Circle((1.5, y_pos+0.05), 0.25, facecolor=color, edgecolor='white', linewidth=2)
        ax.add_patch(circle)
        ax.text(1.5, y_pos+0.05, str(i+1), ha='center', va='center', 
               fontsize=10, fontweight='bold', color='white')
        
        # Title and description
        ax.text(2.2, y_pos+0.25, title, fontsize=11, fontweight='bold', va='top')
        ax.text(2.2, y_pos-0.15, desc, fontsize=8, va='top', style='italic')
        
        # Arrow to next step
        if i < len(steps) - 1:
            arrow = FancyArrowPatch((5, y_pos-0.4), (5, steps[i+1][0]+0.5),
                                  arrowstyle='->', mutation_scale=25, linewidth=3, color='#666')
            ax.add_patch(arrow)
    
    # Add timing annotations
    timings = ['0s', '1s', '2-30s', '30s', '31s', '31.5s', '32s', '32.5s', '33s']
    for i, time in enumerate(timings):
        ax.text(9.5, steps[i][0]+0.05, f'⏱ {time}', fontsize=8, color='#666', style='italic')
    
    plt.tight_layout()
    plt.savefig('graphs/02_test_execution_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 02_test_execution_flow.png")


def create_ai_agent_workflow():
    """Create AI Agent Workflow Diagram"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'AI Agent Multi-Processing Workflow', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # Input
    input_box = FancyBboxPatch((5.5, 8), 3, 0.8, boxstyle="round,pad=0.1",
                              edgecolor='#2196F3', facecolor='#E3F2FD', linewidth=2)
    ax.add_patch(input_box)
    ax.text(7, 8.5, 'Input: PRD Document', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 8.15, 'Product Requirements', ha='center', fontsize=8)
    
    # Arrow down
    arrow1 = FancyArrowPatch((7, 8), (7, 7.2), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow1)
    
    # Requirement Agent
    req_agent = FancyBboxPatch((5, 6.2), 4, 1, boxstyle="round,pad=0.1",
                              edgecolor='#4CAF50', facecolor='#E8F5E9', linewidth=2)
    ax.add_patch(req_agent)
    ax.text(7, 6.9, '1. Requirement Agent', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 6.5, 'Extract & Parse Requirements', ha='center', fontsize=9)
    
    # Arrow down
    arrow2 = FancyArrowPatch((7, 6.2), (7, 5.4), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow2)
    
    # Test Generator Agent
    test_agent = FancyBboxPatch((5, 4.4), 4, 1, boxstyle="round,pad=0.1",
                               edgecolor='#9C27B0', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(test_agent)
    ax.text(7, 5.1, '2. Test Generator Agent', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 4.7, 'Generate Playwright Scripts', ha='center', fontsize=9)
    
    # Branching arrows
    arrow3a = FancyArrowPatch((7, 4.4), (3, 3.6), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow3a)
    arrow3b = FancyArrowPatch((7, 4.4), (11, 3.6), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow3b)
    
    # Execution Engine (Left)
    exec_box = FancyBboxPatch((0.5, 2.6), 3.5, 1, boxstyle="round,pad=0.1",
                             edgecolor='#FF9800', facecolor='#FFF3E0', linewidth=2)
    ax.add_patch(exec_box)
    ax.text(2.25, 3.3, '3a. Execute Tests', ha='center', fontsize=10, fontweight='bold')
    ax.text(2.25, 2.9, 'Run in Browser', ha='center', fontsize=8)
    
    # Self-Healing Agent (Right)
    heal_box = FancyBboxPatch((10, 2.6), 3.5, 1, boxstyle="round,pad=0.1",
                             edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2)
    ax.add_patch(heal_box)
    ax.text(11.75, 3.3, '3b. Self-Healing', ha='center', fontsize=10, fontweight='bold')
    ax.text(11.75, 2.9, 'Fix Failed Tests', ha='center', fontsize=8)
    
    # Converging arrows
    arrow4a = FancyArrowPatch((2.25, 2.6), (6, 1.8), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow4a)
    arrow4b = FancyArrowPatch((11.75, 2.6), (8, 1.8), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow4b)
    
    # Evaluation Agent
    eval_agent = FancyBboxPatch((5, 0.8), 4, 1, boxstyle="round,pad=0.1",
                               edgecolor='#00BCD4', facecolor='#E0F7FA', linewidth=2)
    ax.add_patch(eval_agent)
    ax.text(7, 1.5, '4. Evaluation Agent', ha='center', fontsize=11, fontweight='bold')
    ax.text(7, 1.1, 'Analyze Results & Quality', ha='center', fontsize=9)
    
    # Output
    output_box = FancyBboxPatch((5.5, 0), 3, 0.6, boxstyle="round,pad=0.1",
                               edgecolor='#4CAF50', facecolor='#E8F5E9', linewidth=2)
    ax.add_patch(output_box)
    ax.text(7, 0.4, 'Output: Test Suite + Reports', ha='center', fontsize=10, fontweight='bold')
    
    arrow5 = FancyArrowPatch((7, 0.8), (7, 0.6), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow5)
    
    # Side annotations
    ax.text(0.3, 6.7, 'OpenAI GPT-4', fontsize=8, rotation=90, va='center', style='italic', color='#666')
    ax.text(0.3, 4.9, 'LangChain', fontsize=8, rotation=90, va='center', style='italic', color='#666')
    ax.text(13.7, 3.1, 'DOM Analysis', fontsize=8, rotation=90, va='center', style='italic', color='#666')
    ax.text(13.7, 1.3, 'Quality Metrics', fontsize=8, rotation=90, va='center', style='italic', color='#666')
    
    plt.tight_layout()
    plt.savefig('graphs/03_ai_agent_workflow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 03_ai_agent_workflow.png")


def create_data_flow():
    """Create Data Flow Diagram"""
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Data Flow Through System', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # External Sources (Top)
    sources = [
        (1.5, 8.5, 'PRD\nFiles', '#2196F3'),
        (4.5, 8.5, 'GitHub\nRepo', '#4CAF50'),
        (7.5, 8.5, 'User\nInput', '#9C27B0'),
        (10.5, 8.5, 'CI/CD\nWebhook', '#FF9800'),
    ]
    
    for x, y, label, color in sources:
        box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color+'20', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')
        # Arrow down
        arrow = FancyArrowPatch((x, y-0.3), (x, 7.2), arrowstyle='->', 
                               mutation_scale=15, linewidth=1.5, color=color)
        ax.add_patch(arrow)
    
    # API Layer
    api_layer = FancyBboxPatch((0.5, 6.5), 11, 0.7, boxstyle="round,pad=0.1",
                              edgecolor='#00BCD4', facecolor='#E0F7FA', linewidth=2)
    ax.add_patch(api_layer)
    ax.text(6, 6.85, 'API Endpoints Layer (100+ Routes)', ha='center', fontsize=11, fontweight='bold')
    
    # Processing Layer
    processing = FancyBboxPatch((0.5, 5), 11, 1.2, boxstyle="round,pad=0.1",
                               edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2)
    ax.add_patch(processing)
    ax.text(6, 5.9, 'Business Logic & AI Processing', ha='center', fontsize=11, fontweight='bold')
    ax.text(6, 5.5, 'Services • AI Agents • Validators • Transformers', 
           ha='center', fontsize=9)
    
    # Arrow
    arrow = FancyArrowPatch((6, 6.5), (6, 6.2), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow)
    arrow = FancyArrowPatch((6, 5), (6, 4.2), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow)
    
    # Storage Layer
    storage = FancyBboxPatch((0.5, 3), 5, 1.2, boxstyle="round,pad=0.1",
                            edgecolor='#795548', facecolor='#EFEBE9', linewidth=2)
    ax.add_patch(storage)
    ax.text(3, 3.9, 'Database Storage', ha='center', fontsize=11, fontweight='bold')
    ax.text(3, 3.5, 'SQLite • 17 Tables', ha='center', fontsize=9)
    ax.text(3, 3.2, '10,000+ Records', ha='center', fontsize=8, style='italic')
    
    file_storage = FancyBboxPatch((6.5, 3), 5, 1.2, boxstyle="round,pad=0.1",
                                 edgecolor='#607D8B', facecolor='#ECEFF1', linewidth=2)
    ax.add_patch(file_storage)
    ax.text(9, 3.9, 'File Storage', ha='center', fontsize=11, fontweight='bold')
    ax.text(9, 3.5, 'Screenshots • Traces • Reports', ha='center', fontsize=9)
    ax.text(9, 3.2, '500+ MB Artifacts', ha='center', fontsize=8, style='italic')
    
    # Bidirectional arrows
    arrow_up1 = FancyArrowPatch((3, 4.2), (4.5, 5), arrowstyle='<->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow_up1)
    arrow_up2 = FancyArrowPatch((9, 4.2), (7.5, 5), arrowstyle='<->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow_up2)
    
    # Output Layer
    outputs = [
        (1.5, 1.5, 'Dashboard\nUI', '#2196F3'),
        (4, 1.5, 'Reports\nPDF', '#4CAF50'),
        (6.5, 1.5, 'Email\nAlerts', '#9C27B0'),
        (9, 1.5, 'Slack\nNotifs', '#FF9800'),
        (11, 1.5, 'GitHub\nComments', '#E91E63'),
    ]
    
    for x, y, label, color in outputs:
        # Arrow down from storage
        arrow = FancyArrowPatch((6, 3), (x, 2), arrowstyle='->', 
                               mutation_scale=15, linewidth=1.5, color=color)
        ax.add_patch(arrow)
        
        box = FancyBboxPatch((x-0.6, y-0.3), 1.2, 0.6, boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color+'20', linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, label, ha='center', va='center', fontsize=8, fontweight='bold')
    
    # Data volume annotations
    annotations = [
        (0.2, 8.85, '📄 PRD: 5-50 MB'),
        (0.2, 6.85, '📊 API: 1000+ req/day'),
        (0.2, 5.6, '⚡ Processing: Real-time'),
        (0.2, 3.6, '💾 DB: 100 MB'),
        (0.2, 1.5, '📤 Output: Multi-channel'),
    ]
    
    for x, y, text in annotations:
        ax.text(x, y, text, fontsize=7, style='italic', color='#666')
    
    plt.tight_layout()
    plt.savefig('graphs/04_data_flow.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 04_data_flow.png")


def create_statistics_dashboard():
    """Create Statistics Dashboard with Charts"""
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('AutoTest AI - Analytics Dashboard', fontsize=18, fontweight='bold', y=0.98)
    
    # 1. Test Execution Success Rate (Line Chart)
    ax1 = plt.subplot(2, 3, 1)
    days = np.arange(1, 31)
    success_rate = 70 + 15 * np.sin(days / 5) + np.random.randn(30) * 3
    success_rate = np.clip(success_rate, 60, 95)
    
    ax1.plot(days, success_rate, linewidth=2.5, color='#4CAF50', marker='o', markersize=4)
    ax1.fill_between(days, success_rate, alpha=0.3, color='#4CAF50')
    ax1.axhline(y=80, color='#FF9800', linestyle='--', linewidth=1.5, label='Target: 80%')
    ax1.set_xlabel('Days', fontsize=10)
    ax1.set_ylabel('Success Rate (%)', fontsize=10)
    ax1.set_title('Test Success Rate Trend (30 Days)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_ylim(50, 100)
    
    # 2. Test Distribution by Type (Pie Chart)
    ax2 = plt.subplot(2, 3, 2)
    test_types = ['UI Tests', 'API Tests', 'Integration', 'E2E', 'Visual']
    test_counts = [150, 89, 65, 45, 32]
    colors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0', '#E91E63']
    
    wedges, texts, autotexts = ax2.pie(test_counts, labels=test_types, colors=colors,
                                        autopct='%1.1f%%', startangle=90)
    for text in texts:
        text.set_fontsize(10)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontsize(9)
        autotext.set_fontweight('bold')
    ax2.set_title('Test Distribution by Type', fontsize=12, fontweight='bold')
    
    # 3. Execution Time Comparison (Bar Chart)
    ax3 = plt.subplot(2, 3, 3)
    test_names = ['Login', 'Checkout', 'Search', 'Profile', 'Dashboard']
    exec_times = [12.5, 25.3, 8.7, 15.2, 18.9]
    colors_bar = ['#4CAF50' if t < 20 else '#FF9800' for t in exec_times]
    
    bars = ax3.bar(test_names, exec_times, color=colors_bar, edgecolor='black', linewidth=1.5)
    ax3.axhline(y=20, color='#F44336', linestyle='--', linewidth=2, label='SLA: 20s')
    ax3.set_ylabel('Time (seconds)', fontsize=10)
    ax3.set_title('Average Execution Time by Test', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, time in zip(bars, exec_times):
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{time}s', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    # 4. Bug Discovery Over Time (Stacked Area Chart)
    ax4 = plt.subplot(2, 3, 4)
    weeks = np.arange(1, 13)
    critical = np.array([3, 5, 2, 7, 4, 6, 3, 2, 5, 4, 3, 2])
    high = np.array([8, 12, 10, 15, 11, 14, 9, 8, 10, 9, 7, 6])
    medium = np.array([15, 18, 20, 22, 19, 21, 18, 16, 17, 15, 14, 12])
    low = np.array([10, 13, 15, 18, 16, 17, 14, 12, 13, 11, 10, 9])
    
    ax4.fill_between(weeks, 0, critical, label='Critical', color='#F44336', alpha=0.8)
    ax4.fill_between(weeks, critical, critical+high, label='High', color='#FF9800', alpha=0.8)
    ax4.fill_between(weeks, critical+high, critical+high+medium, label='Medium', color='#FFC107', alpha=0.8)
    ax4.fill_between(weeks, critical+high+medium, critical+high+medium+low, label='Low', color='#4CAF50', alpha=0.8)
    
    ax4.set_xlabel('Weeks', fontsize=10)
    ax4.set_ylabel('Bug Count', fontsize=10)
    ax4.set_title('Bug Discovery by Severity (12 Weeks)', fontsize=12, fontweight='bold')
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    
    # 5. Flaky Test Detection (Scatter Plot)
    ax5 = plt.subplot(2, 3, 5)
    num_tests = 50
    execution_count = np.random.randint(10, 100, num_tests)
    failure_rate = np.random.uniform(0, 40, num_tests)
    colors_scatter = ['#F44336' if f > 20 else '#FF9800' if f > 10 else '#4CAF50' for f in failure_rate]
    
    scatter = ax5.scatter(execution_count, failure_rate, s=100, c=colors_scatter, 
                         alpha=0.6, edgecolors='black', linewidth=1)
    ax5.axhline(y=20, color='#F44336', linestyle='--', linewidth=2, label='Flaky Threshold: 20%')
    ax5.set_xlabel('Execution Count', fontsize=10)
    ax5.set_ylabel('Failure Rate (%)', fontsize=10)
    ax5.set_title('Flaky Test Detection Matrix', fontsize=12, fontweight='bold')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Self-Healing Success Rate (Horizontal Bar)
    ax6 = plt.subplot(2, 3, 6)
    healing_types = ['Selector Fix', 'Timing Fix', 'Waits Added', 'Retry Logic', 'Element Swap']
    success_rates = [92, 88, 95, 85, 78]
    colors_heal = ['#4CAF50' if s >= 85 else '#FF9800' for s in success_rates]
    
    bars = ax6.barh(healing_types, success_rates, color=colors_heal, edgecolor='black', linewidth=1.5)
    ax6.set_xlabel('Success Rate (%)', fontsize=10)
    ax6.set_title('Self-Healing Success by Type', fontsize=12, fontweight='bold')
    ax6.set_xlim(0, 100)
    ax6.grid(True, axis='x', alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars, success_rates):
        width = bar.get_width()
        ax6.text(width + 2, bar.get_y() + bar.get_height()/2.,
                f'{rate}%', ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graphs/05_statistics_dashboard.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 05_statistics_dashboard.png")


def create_cicd_pipeline():
    """Create CI/CD Pipeline Visualization"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(7, 7.5, 'CI/CD Pipeline Integration', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # GitHub Event
    github = FancyBboxPatch((0.5, 5.5), 2, 1, boxstyle="round,pad=0.1",
                           edgecolor='#24292e', facecolor='#f6f8fa', linewidth=2)
    ax.add_patch(github)
    ax.text(1.5, 6.2, 'GitHub', ha='center', fontsize=11, fontweight='bold')
    ax.text(1.5, 5.8, 'Push/PR Event', ha='center', fontsize=8)
    
    # Arrow
    arrow1 = FancyArrowPatch((2.5, 6), (3.5, 6), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow1)
    
    # GitHub Actions
    actions = FancyBboxPatch((3.5, 5.5), 2.5, 1, boxstyle="round,pad=0.1",
                            edgecolor='#2088FF', facecolor='#dbedff', linewidth=2)
    ax.add_patch(actions)
    ax.text(4.75, 6.2, 'GitHub Actions', ha='center', fontsize=11, fontweight='bold')
    ax.text(4.75, 5.8, 'Workflow Triggered', ha='center', fontsize=8)
    
    # Arrow down
    arrow2 = FancyArrowPatch((4.75, 5.5), (4.75, 4.7), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow2)
    
    # Setup
    setup = FancyBboxPatch((3.5, 3.7), 2.5, 1, boxstyle="round,pad=0.1",
                          edgecolor='#4CAF50', facecolor='#E8F5E9', linewidth=2)
    ax.add_patch(setup)
    ax.text(4.75, 4.4, 'Setup', ha='center', fontsize=11, fontweight='bold')
    ax.text(4.75, 4, 'Install Dependencies', ha='center', fontsize=8)
    
    # Arrow right
    arrow3 = FancyArrowPatch((6, 4.2), (7, 4.2), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow3)
    
    # Fetch Tests
    fetch = FancyBboxPatch((7, 3.7), 2.5, 1, boxstyle="round,pad=0.1",
                          edgecolor='#9C27B0', facecolor='#F3E5F5', linewidth=2)
    ax.add_patch(fetch)
    ax.text(8.25, 4.4, 'Fetch Tests', ha='center', fontsize=11, fontweight='bold')
    ax.text(8.25, 4, 'AutoTest AI API', ha='center', fontsize=8)
    
    # Arrow right
    arrow4 = FancyArrowPatch((9.5, 4.2), (10.5, 4.2), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow4)
    
    # Run Tests
    run = FancyBboxPatch((10.5, 3.7), 2.5, 1, boxstyle="round,pad=0.1",
                        edgecolor='#FF9800', facecolor='#FFF3E0', linewidth=2)
    ax.add_patch(run)
    ax.text(11.75, 4.4, 'Run Tests', ha='center', fontsize=11, fontweight='bold')
    ax.text(11.75, 4, 'Playwright Execute', ha='center', fontsize=8)
    
    # Arrow down
    arrow5 = FancyArrowPatch((11.75, 3.7), (11.75, 2.9), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow5)
    
    # Upload Results
    upload = FancyBboxPatch((10.5, 1.9), 2.5, 1, boxstyle="round,pad=0.1",
                           edgecolor='#00BCD4', facecolor='#E0F7FA', linewidth=2)
    ax.add_patch(upload)
    ax.text(11.75, 2.6, 'Upload Results', ha='center', fontsize=11, fontweight='bold')
    ax.text(11.75, 2.2, 'Send to AutoTest AI', ha='center', fontsize=8)
    
    # Arrow left
    arrow6 = FancyArrowPatch((10.5, 2.4), (9.5, 2.4), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow6)
    
    # Notify
    notify = FancyBboxPatch((7, 1.9), 2.5, 1, boxstyle="round,pad=0.1",
                           edgecolor='#E91E63', facecolor='#FCE4EC', linewidth=2)
    ax.add_patch(notify)
    ax.text(8.25, 2.6, 'Notifications', ha='center', fontsize=11, fontweight='bold')
    ax.text(8.25, 2.2, 'Slack • Email • PR', ha='center', fontsize=8)
    
    # Arrow left
    arrow7 = FancyArrowPatch((7, 2.4), (6, 2.4), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666')
    ax.add_patch(arrow7)
    
    # PR Comment
    pr_comment = FancyBboxPatch((3.5, 1.9), 2.5, 1, boxstyle="round,pad=0.1",
                               edgecolor='#795548', facecolor='#EFEBE9', linewidth=2)
    ax.add_patch(pr_comment)
    ax.text(4.75, 2.6, 'PR Comment', ha='center', fontsize=11, fontweight='bold')
    ax.text(4.75, 2.2, '✓ 45 Passed  ✗ 3 Failed', ha='center', fontsize=8)
    
    # Arrow up to GitHub
    arrow8 = FancyArrowPatch((3.5, 2.4), (2.5, 6), arrowstyle='->', mutation_scale=20, linewidth=2, color='#666', linestyle='dashed')
    ax.add_patch(arrow8)
    
    # Status indicators
    statuses = [
        (1, 1, '✓ Build Success', '#4CAF50'),
        (1, 0.6, '✓ Tests: 45/48', '#4CAF50'),
        (1, 0.2, '✗ 3 Failures', '#F44336'),
    ]
    
    for x, y, text, color in statuses:
        ax.text(x, y, text, fontsize=9, color=color, fontweight='bold')
    
    # Timing annotations
    timings = [
        (2, 6.8, '0s'),
        (5.5, 6.8, '5s'),
        (8.75, 4.9, '30s'),
        (12.25, 4.9, '2m'),
        (12.25, 3.2, '5s'),
        (8.75, 3.2, '1s'),
        (5.25, 3.2, '2s'),
    ]
    
    for x, y, time in timings:
        ax.text(x, y, f'⏱ {time}', fontsize=7, style='italic', color='#666')
    
    plt.tight_layout()
    plt.savefig('graphs/06_cicd_pipeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 06_cicd_pipeline.png")


def create_database_schema():
    """Create Database Schema Visualization"""
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Database Schema (17 Tables)', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # Core tables
    tables = [
        # (x, y, width, height, name, fields, color)
        (0.5, 9, 2.5, 1.5, 'users', ['id', 'email', 'name', 'password_hash', 'is_active'], '#2196F3'),
        (3.5, 9, 2.5, 1.5, 'projects', ['id', 'name', 'description', 'user_id', 'created_at'], '#4CAF50'),
        (6.5, 9, 2.5, 1.5, 'requirements', ['id', 'project_id', 'content', 'parsed_data', 'status'], '#9C27B0'),
        (9.5, 9, 2.5, 1.5, 'test_cases', ['id', 'project_id', 'name', 'script', 'status'], '#FF9800'),
        (12.5, 9, 2.5, 1.5, 'test_executions', ['id', 'test_case_id', 'result', 'duration', 'logs'], '#E91E63'),
        
        (0.5, 6.5, 2.5, 1.3, 'bug_reports', ['id', 'test_execution_id', 'title', 'severity'], '#F44336'),
        (3.5, 6.5, 2.5, 1.3, 'visual_tests', ['id', 'project_id', 'url', 'viewport'], '#00BCD4'),
        (6.5, 6.5, 2.5, 1.3, 'visual_baselines', ['id', 'visual_test_id', 'screenshot_path'], '#795548'),
        (9.5, 6.5, 2.5, 1.3, 'visual_comparisons', ['id', 'baseline_id', 'diff_percentage'], '#607D8B'),
        (12.5, 6.5, 2.5, 1.3, 'cicd_configs', ['id', 'project_id', 'provider', 'config'], '#673AB7'),
        
        (0.5, 4.2, 2.5, 1.2, 'workflow_runs', ['id', 'cicd_config_id', 'status', 'logs'], '#3F51B5'),
        (3.5, 4.2, 2.5, 1.2, 'integrations', ['id', 'project_id', 'type', 'settings'], '#009688'),
        (6.5, 4.2, 2.5, 1.2, 'notifications', ['id', 'user_id', 'message', 'read'], '#FF5722'),
        (9.5, 4.2, 2.5, 1.2, 'platforms', ['id', 'name', 'type', 'config'], '#8BC34A'),
        (12.5, 4.2, 2.5, 1.2, 'tags', ['id', 'name', 'color'], '#FFC107'),
        
        (3.5, 1.8, 2.5, 1.1, 'test_case_tags', ['test_case_id', 'tag_id'], '#CDDC39'),
        (6.5, 1.8, 2.5, 1.1, 'self_healing_logs', ['id', 'execution_id', 'old_selector', 'new_selector'], '#FF4081'),
    ]
    
    for x, y, w, h, name, fields, color in tables:
        # Table box
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                            edgecolor=color, facecolor=color+'20', linewidth=2)
        ax.add_patch(box)
        
        # Table name
        ax.text(x + w/2, y + h - 0.15, name, ha='center', fontsize=9, fontweight='bold')
        
        # Fields
        field_y = y + h - 0.35
        for field in fields[:5]:  # Show max 5 fields
            ax.text(x + 0.1, field_y, f'• {field}', fontsize=6, va='top')
            field_y -= 0.15
    
    # Relationships (arrows)
    relationships = [
        # (from_table_idx, to_table_idx, label)
        (1, 0, 'user_id'),  # projects -> users
        (2, 1, 'project_id'),  # requirements -> projects
        (3, 1, 'project_id'),  # test_cases -> projects
        (4, 3, 'test_case_id'),  # executions -> test_cases
        (5, 4, 'execution_id'),  # bugs -> executions
        (6, 1, 'project_id'),  # visual_tests -> projects
        (7, 6, 'visual_test_id'),  # baselines -> visual_tests
        (8, 7, 'baseline_id'),  # comparisons -> baselines
        (9, 1, 'project_id'),  # cicd_configs -> projects
        (10, 9, 'cicd_config_id'),  # workflow_runs -> cicd_configs
        (11, 1, 'project_id'),  # integrations -> projects
        (12, 0, 'user_id'),  # notifications -> users
        (15, 3, 'test_case_id'),  # test_case_tags -> test_cases
        (16, 4, 'execution_id'),  # self_healing -> executions
    ]
    
    # Draw some key relationships
    key_relationships = [
        ((1.75, 9), (1.75, 10.5), '#2196F3'),  # users <- projects
        ((4.75, 9), (4.75, 10.5), '#4CAF50'),  # projects <- requirements
        ((10.75, 9), (10.75, 10.5), '#FF9800'),  # test_cases <- executions
        ((7.75, 6.5), (7.75, 7.8), '#00BCD4'),  # visual_tests <- baselines
    ]
    
    for (x1, y1), (x2, y2), color in key_relationships:
        arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='<->', 
                               mutation_scale=15, linewidth=1.5, color=color, alpha=0.6)
        ax.add_patch(arrow)
    
    # Legend
    legend_items = [
        (0.5, 0.8, 'Core Tables (Users, Projects)', '#2196F3'),
        (5, 0.8, 'Testing Tables (Tests, Executions)', '#FF9800'),
        (10, 0.8, 'Feature Tables (Visual, CI/CD)', '#00BCD4'),
    ]
    
    for x, y, label, color in legend_items:
        circle = Circle((x, y), 0.12, facecolor=color, edgecolor='black', linewidth=1)
        ax.add_patch(circle)
        ax.text(x + 0.25, y, label, fontsize=9, va='center')
    
    plt.tight_layout()
    plt.savefig('graphs/07_database_schema.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 07_database_schema.png")


def create_user_journey():
    """Create User Journey Timeline"""
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # Title
    ax.text(7, 7.5, 'User Journey: From Onboarding to Production', 
            ha='center', va='top', fontsize=16, fontweight='bold')
    
    # Timeline
    timeline_y = 4
    ax.plot([1, 13], [timeline_y, timeline_y], 'k-', linewidth=3)
    
    # Journey stages
    stages = [
        (1, 'Day 1\nSign Up', '#2196F3', ['Register', 'Create Project', 'Upload PRD']),
        (4, 'Day 2\nTest Gen', '#4CAF50', ['AI Generates', 'Review Tests', 'Execute']),
        (7, 'Week 1\nCI/CD', '#9C27B0', ['Connect GitHub', 'Setup Workflow', 'Auto Tests']),
        (10, 'Week 2\nVisual', '#FF9800', ['Add Baselines', 'Compare Screens', 'Approve']),
        (13, 'Month 1\nProd Ready', '#00BCD4', ['Full Coverage', 'Self-Healing', 'Monitoring']),
    ]
    
    for x, label, color, actions in stages:
        # Timeline marker
        circle = Circle((x, timeline_y), 0.25, facecolor=color, edgecolor='white', linewidth=3)
        ax.add_patch(circle)
        
        # Stage label
        ax.text(x, timeline_y + 1.5, label, ha='center', fontsize=10, fontweight='bold')
        
        # Action boxes
        for i, action in enumerate(actions):
            action_y = timeline_y - 1 - (i * 0.45)
            box = FancyBboxPatch((x - 0.6, action_y - 0.15), 1.2, 0.3, boxstyle="round,pad=0.05",
                                edgecolor=color, facecolor=color+'30', linewidth=1.5)
            ax.add_patch(box)
            ax.text(x, action_y, action, ha='center', va='center', fontsize=7)
    
    # Progress indicators
    progress = [
        (2.5, timeline_y + 2.5, '20% Complete', '#2196F3'),
        (5.5, timeline_y + 2.5, '40% Complete', '#4CAF50'),
        (8.5, timeline_y + 2.5, '60% Complete', '#9C27B0'),
        (11.5, timeline_y + 2.5, '80% Complete', '#FF9800'),
        (13, timeline_y + 2.5, '100% Ready', '#00BCD4'),
    ]
    
    for x, y, text, color in progress:
        ax.text(x, y, text, ha='center', fontsize=8, style='italic', color=color, fontweight='bold')
    
    # Experience indicators
    experiences = [
        (1, 0.8, '😊 Easy setup', '#4CAF50'),
        (4, 0.8, '🚀 Fast generation', '#4CAF50'),
        (7, 0.8, '🔗 Seamless integration', '#4CAF50'),
        (10, 0.8, '👁️ Visual confidence', '#4CAF50'),
        (13, 0.8, '✅ Production ready', '#00BCD4'),
    ]
    
    for x, y, text, color in experiences:
        ax.text(x, y, text, ha='center', fontsize=9, color=color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graphs/08_user_journey.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Created: 08_user_journey.png")


# Run all graph generators
if __name__ == "__main__":
    print("\n🎨 AutoTest AI - Graph Generator")
    print("=" * 50)
    print("\nGenerating professional graphs with white background...\n")
    
    create_system_architecture()
    create_test_execution_flow()
    create_ai_agent_workflow()
    create_data_flow()
    create_statistics_dashboard()
    create_cicd_pipeline()
    create_database_schema()
    create_user_journey()
    
    print("\n" + "=" * 50)
    print("✅ All 8 graphs generated successfully!")
    print(f"📁 Saved to: graphs/ directory")
    print("\nGenerated files:")
    print("  1. 01_system_architecture.png")
    print("  2. 02_test_execution_flow.png")
    print("  3. 03_ai_agent_workflow.png")
    print("  4. 04_data_flow.png")
    print("  5. 05_statistics_dashboard.png")
    print("  6. 06_cicd_pipeline.png")
    print("  7. 07_database_schema.png")
    print("  8. 08_user_journey.png")
    print("\n✨ Ready to use in documentation and presentations!")
