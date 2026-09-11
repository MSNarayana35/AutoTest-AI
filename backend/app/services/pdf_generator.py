"""
PDF Report Generation Service
Generates detailed test execution reports in PDF format
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any
import pytz

# Indian Standard Time
IST = pytz.timezone('Asia/Kolkata')


class PDFReportGenerator:
    """Generate detailed PDF reports for test executions"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#3b82f6'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=10,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Status passed
        self.styles.add(ParagraphStyle(
            name='StatusPassed',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold'
        ))
        
        # Status failed
        self.styles.add(ParagraphStyle(
            name='StatusFailed',
            parent=self.styles['Normal'],
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(self, project_data: Dict[str, Any], 
                       requirements: List[Dict], 
                       test_cases: List[Dict],
                       executions: List[Dict],
                       bugs: List[Dict]) -> BytesIO:
        """
        Generate comprehensive PDF report
        
        Args:
            project_data: Project information
            requirements: List of requirements
            test_cases: List of test cases
            executions: List of test executions
            bugs: List of reported bugs
        
        Returns:
            BytesIO: PDF file in memory
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add content
        elements.extend(self._create_title_page(project_data))
        elements.append(PageBreak())
        
        elements.extend(self._create_executive_summary(
            project_data, requirements, test_cases, executions, bugs
        ))
        elements.append(PageBreak())
        
        elements.extend(self._create_requirements_section(requirements))
        elements.append(PageBreak())
        
        elements.extend(self._create_test_cases_section(test_cases))
        elements.append(PageBreak())
        
        elements.extend(self._create_execution_results(executions, test_cases))
        
        if bugs:
            elements.append(PageBreak())
            elements.extend(self._create_bugs_section(bugs))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _create_title_page(self, project_data: Dict) -> List:
        """Create title page"""
        elements = []
        
        # Title
        elements.append(Spacer(1, 2*inch))
        title = Paragraph("AutoTest AI", self.styles['CustomTitle'])
        elements.append(title)
        
        subtitle = Paragraph("Test Execution Report", self.styles['CustomSubtitle'])
        elements.append(subtitle)
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Project info
        project_name = Paragraph(
            f"<b>Project:</b> {project_data.get('name', 'N/A')}",
            self.styles['Normal']
        )
        elements.append(project_name)
        elements.append(Spacer(1, 12))
        
        if project_data.get('description'):
            desc = Paragraph(
                f"<b>Description:</b> {project_data.get('description')}",
                self.styles['Normal']
            )
            elements.append(desc)
            elements.append(Spacer(1, 12))
        
        if project_data.get('repository_url'):
            repo = Paragraph(
                f"<b>Repository:</b> {project_data.get('repository_url')}",
                self.styles['Normal']
            )
            elements.append(repo)
            elements.append(Spacer(1, 12))
        
        # Date
        now_ist = datetime.now(IST)
        report_date = Paragraph(
            f"<b>Report Generated:</b> {now_ist.strftime('%d %B %Y at %I:%M %p IST')}",
            self.styles['Normal']
        )
        elements.append(report_date)
        
        return elements
    
    def _create_executive_summary(self, project_data, requirements, 
                                  test_cases, executions, bugs) -> List:
        """Create executive summary with key metrics"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
        
        # Calculate metrics
        total_tests = len(test_cases)
        total_executions = len(executions)
        passed = sum(1 for e in executions if e.get('status') == 'passed')
        failed = sum(1 for e in executions if e.get('status') == 'failed')
        pending = sum(1 for e in executions if e.get('status') == 'pending')
        success_rate = (passed / total_executions * 100) if total_executions > 0 else 0
        
        # Summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Requirements', str(len(requirements))],
            ['Total Test Cases', str(total_tests)],
            ['Total Executions', str(total_executions)],
            ['Passed', str(passed)],
            ['Failed', str(failed)],
            ['Pending', str(pending)],
            ['Success Rate', f'{success_rate:.1f}%'],
            ['Bugs Reported', str(len(bugs))],
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # Status interpretation
        if success_rate >= 90:
            status_text = "Excellent - The system is performing very well with minimal failures."
            status_color = colors.HexColor('#059669')
        elif success_rate >= 70:
            status_text = "Good - The system is stable with some issues that need attention."
            status_color = colors.HexColor('#f59e0b')
        elif success_rate >= 50:
            status_text = "Fair - Multiple issues detected that require immediate attention."
            status_color = colors.HexColor('#f59e0b')
        else:
            status_text = "Critical - Significant issues detected. Immediate action required."
            status_color = colors.HexColor('#dc2626')
        
        status_para = Paragraph(
            f"<b>Overall Status:</b> <font color='{status_color.hexval()}'>{status_text}</font>",
            self.styles['Normal']
        )
        elements.append(status_para)
        
        return elements
    
    def _create_requirements_section(self, requirements: List[Dict]) -> List:
        """Create requirements section"""
        elements = []
        
        elements.append(Paragraph("Requirements Analysis", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
        
        if not requirements:
            elements.append(Paragraph("No requirements documented.", self.styles['Normal']))
            return elements
        
        for idx, req in enumerate(requirements, 1):
            elements.append(Paragraph(
                f"<b>{idx}. {req.get('title', 'Untitled')}</b>",
                self.styles['SectionHeader']
            ))
            
            if req.get('content'):
                content_preview = req['content'][:500] + ('...' if len(req['content']) > 500 else '')
                elements.append(Paragraph(content_preview, self.styles['Normal']))
            
            elements.append(Spacer(1, 6))
            
            # Status badge
            status = req.get('status', 'pending')
            status_text = f"Status: {status.upper()}"
            elements.append(Paragraph(status_text, self.styles['Normal']))
            
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_test_cases_section(self, test_cases: List[Dict]) -> List:
        """Create test cases section"""
        elements = []
        
        elements.append(Paragraph("Test Cases", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
        
        if not test_cases:
            elements.append(Paragraph("No test cases generated.", self.styles['Normal']))
            return elements
        
        # Group by test type
        by_type = {}
        for tc in test_cases:
            test_type = tc.get('test_type', 'functional')
            if test_type not in by_type:
                by_type[test_type] = []
            by_type[test_type].append(tc)
        
        for test_type, cases in by_type.items():
            elements.append(Paragraph(
                f"{test_type.upper()} Tests ({len(cases)})",
                self.styles['SectionHeader']
            ))
            
            for idx, tc in enumerate(cases, 1):
                elements.append(Paragraph(
                    f"<b>{idx}. {tc.get('title', 'Untitled Test')}</b>",
                    self.styles['Normal']
                ))
                
                if tc.get('description'):
                    elements.append(Paragraph(
                        tc['description'][:300],
                        self.styles['Normal']
                    ))
                
                elements.append(Spacer(1, 8))
            
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_execution_results(self, executions: List[Dict], 
                                  test_cases: List[Dict]) -> List:
        """Create execution results section"""
        elements = []
        
        elements.append(Paragraph("Test Execution Results", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
        
        if not executions:
            elements.append(Paragraph("No test executions recorded.", self.styles['Normal']))
            return elements
        
        # Create test case lookup
        tc_lookup = {tc['id']: tc for tc in test_cases}
        
        # Execution table
        table_data = [['#', 'Test Case', 'Status', 'Execution Time', 'Date']]
        
        for idx, execution in enumerate(executions, 1):
            tc_id = execution.get('test_case_id')
            tc = tc_lookup.get(tc_id, {})
            tc_title = tc.get('title', f'Test #{tc_id}')[:50]
            
            status = execution.get('status', 'unknown')
            exec_time = execution.get('execution_time', 0)
            created_at = execution.get('created_at', '')
            
            # Format date in IST
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                else:
                    dt = created_at
                
                if dt.tzinfo is None:
                    dt = pytz.utc.localize(dt)
                
                ist_dt = dt.astimezone(IST)
                date_str = ist_dt.strftime('%d/%m %I:%M %p')
            except:
                date_str = 'N/A'
            
            table_data.append([
                str(idx),
                tc_title,
                status.upper(),
                f'{exec_time}ms' if exec_time else 'N/A',
                date_str
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ]))
        
        # Color code status
        for i, execution in enumerate(executions, 1):
            status = execution.get('status', '')
            if status == 'passed':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#059669')),
                    ('BACKGROUND', (2, i), (2, i), colors.HexColor('#d1fae5')),
                ]))
            elif status == 'failed':
                table.setStyle(TableStyle([
                    ('TEXTCOLOR', (2, i), (2, i), colors.HexColor('#dc2626')),
                    ('BACKGROUND', (2, i), (2, i), colors.HexColor('#fee2e2')),
                ]))
        
        elements.append(table)
        
        return elements
    
    def _create_bugs_section(self, bugs: List[Dict]) -> List:
        """Create bugs section"""
        elements = []
        
        elements.append(Paragraph("Reported Bugs", self.styles['CustomSubtitle']))
        elements.append(Spacer(1, 12))
        
        if not bugs:
            elements.append(Paragraph("No bugs reported.", self.styles['Normal']))
            return elements
        
        for idx, bug in enumerate(bugs, 1):
            severity = bug.get('severity', 'medium')
            severity_colors = {
                'critical': colors.HexColor('#dc2626'),
                'high': colors.HexColor('#f59e0b'),
                'medium': colors.HexColor('#3b82f6'),
                'low': colors.HexColor('#6b7280'),
            }
            severity_color = severity_colors.get(severity, colors.black)
            
            elements.append(Paragraph(
                f"<b>{idx}. {bug.get('title', 'Untitled Bug')}</b> "
                f"<font color='{severity_color.hexval()}'>[{severity.upper()}]</font>",
                self.styles['Normal']
            ))
            
            if bug.get('description'):
                elements.append(Paragraph(
                    bug['description'][:400],
                    self.styles['Normal']
                ))
            
            elements.append(Spacer(1, 12))
        
        return elements


# Global instance
pdf_generator = PDFReportGenerator()
