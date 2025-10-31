"""
Cost Analysis Dashboard and Reporting Tool
Provides web interface and detailed reports for cost analysis
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import csv
import io
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg
import base64

from cost_analysis_tool import CostAnalyzer, PRICING
from database import get_db
from models.user_models import UserDB
from core.user import get_current_user

router = APIRouter(prefix="/cost-dashboard", tags=["Cost Dashboard"])

class CostDashboard:
    """Cost analysis dashboard and reporting"""
    
    def __init__(self, db):
        self.db = db
        self.analyzer = CostAnalyzer(db)
    
    async def get_dashboard_data(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get cost report
        cost_report = await self.analyzer.generate_cost_report(
            user_id, start_date.isoformat(), end_date.isoformat()
        )
        
        # Get daily breakdown
        daily_costs = await self.get_daily_cost_breakdown(user_id, start_date, end_date)
        
        # Get service breakdown
        service_breakdown = await self.get_service_cost_breakdown(user_id, start_date, end_date)
        
        # Get usage trends
        usage_trends = await self.get_usage_trends(user_id, start_date, end_date)
        
        return {
            "summary": cost_report["summary"],
            "usage_breakdown": cost_report["usage_breakdown"],
            "daily_costs": daily_costs,
            "service_breakdown": service_breakdown,
            "usage_trends": usage_trends,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            }
        }
    
    async def get_daily_cost_breakdown(self, user_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get daily cost breakdown"""
        daily_costs = []
        current_date = start_date
        
        while current_date <= end_date:
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = current_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # Get costs for this day
            day_report = await self.analyzer.generate_cost_report(
                user_id, day_start.isoformat(), day_end.isoformat()
            )
            
            daily_costs.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "total_cost": day_report["summary"]["total_cost_usd"],
                "scenario_cost": day_report["summary"]["scenario_creation_cost"],
                "conversation_cost": day_report["summary"]["conversation_cost"],
                "scenarios_created": day_report["summary"]["scenarios_created"],
                "conversations": day_report["summary"]["conversations_completed"]
            })
            
            current_date += timedelta(days=1)
        
        return daily_costs
    
    async def get_service_cost_breakdown(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        """Get cost breakdown by service type"""
        # Get all token usage
        token_records = await self.db.cost_tracking.find({
            "type": "token_usage",
            "data.user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).to_list(length=None)
        
        # Get all speech usage
        speech_records = await self.db.cost_tracking.find({
            "type": "speech_usage",
            "data.user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).to_list(length=None)
        
        # Calculate costs by service
        service_costs = {
            "gpt_4o": 0.0,
            "gpt_4": 0.0,
            "embeddings": 0.0,
            "speech_to_text": 0.0,
            "text_to_speech": 0.0,
            "search": 0.0
        }
        
        # Process token usage
        for record in token_records:
            data = record["data"]
            model = data.get("model", "gpt-4o")
            cost = data.get("cost_usd", 0)
            
            if "gpt-4o" in model:
                service_costs["gpt_4o"] += cost
            elif "gpt-4" in model:
                service_costs["gpt_4"] += cost
            elif "embedding" in model:
                service_costs["embeddings"] += cost
        
        # Process speech usage
        for record in speech_records:
            data = record["data"]
            operation = data.get("operation")
            cost = data.get("cost_usd", 0)
            
            if operation == "stt":
                service_costs["speech_to_text"] += cost
            elif operation == "tts":
                service_costs["text_to_speech"] += cost
        
        return service_costs
    
    async def get_usage_trends(self, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, List]:
        """Get usage trends over time"""
        # Get token usage over time
        token_records = await self.db.cost_tracking.find({
            "type": "token_usage",
            "data.user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("timestamp", 1).to_list(length=None)
        
        # Get speech usage over time
        speech_records = await self.db.cost_tracking.find({
            "type": "speech_usage",
            "data.user_id": user_id,
            "timestamp": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort("timestamp", 1).to_list(length=None)
        
        # Process trends
        token_trend = []
        speech_trend = []
        
        for record in token_records:
            token_trend.append({
                "timestamp": record["timestamp"].isoformat(),
                "tokens": record["data"].get("total_tokens", 0),
                "cost": record["data"].get("cost_usd", 0),
                "operation": record["data"].get("operation", "")
            })
        
        for record in speech_records:
            speech_trend.append({
                "timestamp": record["timestamp"].isoformat(),
                "operation": record["data"].get("operation", ""),
                "duration": record["data"].get("duration_seconds", 0),
                "characters": record["data"].get("character_count", 0),
                "cost": record["data"].get("cost_usd", 0)
            })
        
        return {
            "token_usage": token_trend,
            "speech_usage": speech_trend
        }
    
    def generate_cost_chart(self, daily_costs: List[Dict]) -> str:
        """Generate cost chart as base64 image"""
        plt.style.use('seaborn-v0_8')
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        dates = [item["date"] for item in daily_costs]
        total_costs = [item["total_cost"] for item in daily_costs]
        scenario_costs = [item["scenario_cost"] for item in daily_costs]
        conversation_costs = [item["conversation_cost"] for item in daily_costs]
        
        # Cost over time
        ax1.plot(dates, total_costs, marker='o', label='Total Cost', linewidth=2)
        ax1.plot(dates, scenario_costs, marker='s', label='Scenario Creation', alpha=0.7)
        ax1.plot(dates, conversation_costs, marker='^', label='Conversations', alpha=0.7)
        ax1.set_title('Daily Cost Breakdown')
        ax1.set_ylabel('Cost (USD)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Usage counts
        scenarios_created = [item["scenarios_created"] for item in daily_costs]
        conversations = [item["conversations"] for item in daily_costs]
        
        ax2.bar([d + " S" for d in dates], scenarios_created, alpha=0.7, label='Scenarios Created')
        ax2.bar([d + " C" for d in dates], conversations, alpha=0.7, label='Conversations')
        ax2.set_title('Daily Usage Counts')
        ax2.set_ylabel('Count')
        ax2.legend()
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    def generate_service_breakdown_chart(self, service_breakdown: Dict[str, float]) -> str:
        """Generate service breakdown pie chart"""
        plt.style.use('seaborn-v0_8')
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Filter out zero costs
        filtered_services = {k: v for k, v in service_breakdown.items() if v > 0}
        
        if filtered_services:
            labels = list(filtered_services.keys())
            sizes = list(filtered_services.values())
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            ax.set_title('Cost Breakdown by Service')
            
            # Add cost values to labels
            for i, (label, size) in enumerate(zip(labels, sizes)):
                texts[i].set_text(f'{label}\n${size:.4f}')
        else:
            ax.text(0.5, 0.5, 'No usage data available', ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Cost Breakdown by Service')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
    
    async def export_detailed_report(self, user_id: str, start_date: str, end_date: str, format: str = "csv") -> str:
        """Export detailed cost report"""
        cost_report = await self.analyzer.generate_cost_report(user_id, start_date, end_date)
        
        if format == "csv":
            return await self.export_csv_report(cost_report)
        elif format == "json":
            return await self.export_json_report(cost_report)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def export_csv_report(self, cost_report: Dict) -> str:
        """Export cost report as CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cost_report_{timestamp}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Summary section
            writer.writerow(["COST REPORT SUMMARY"])
            writer.writerow(["Report Period", f"{cost_report['report_period']['start_date']} to {cost_report['report_period']['end_date']}"])
            writer.writerow(["Total Cost (USD)", cost_report['summary']['total_cost_usd']])
            writer.writerow(["Scenario Creation Cost", cost_report['summary']['scenario_creation_cost']])
            writer.writerow(["Conversation Cost", cost_report['summary']['conversation_cost']])
            writer.writerow(["Scenarios Created", cost_report['summary']['scenarios_created']])
            writer.writerow(["Conversations Completed", cost_report['summary']['conversations_completed']])
            writer.writerow([])
            
            # Usage breakdown
            writer.writerow(["USAGE BREAKDOWN"])
            writer.writerow(["Total Tokens", cost_report['usage_breakdown']['total_tokens']])
            writer.writerow(["Total STT Minutes", cost_report['usage_breakdown']['total_stt_minutes']])
            writer.writerow(["Total TTS Characters", cost_report['usage_breakdown']['total_tts_characters']])
            writer.writerow([])
            
            # Detailed scenarios
            if cost_report['detailed_scenarios']:
                writer.writerow(["SCENARIO DETAILS"])
                writer.writerow(["Scenario ID", "Name", "Total Cost", "Total Tokens", "Start Time"])
                for scenario in cost_report['detailed_scenarios']:
                    writer.writerow([
                        scenario.get('scenario_id', ''),
                        scenario.get('scenario_name', ''),
                        scenario.get('total_cost', 0),
                        sum(usage.get('total_tokens', 0) for usage in scenario.get('token_usage', [])),
                        scenario.get('start_timestamp', '')
                    ])
                writer.writerow([])
            
            # Detailed conversations
            if cost_report['detailed_conversations']:
                writer.writerow(["CONVERSATION DETAILS"])
                writer.writerow(["Session ID", "Scenario", "Mode", "Total Cost", "Messages", "Duration"])
                for conv in cost_report['detailed_conversations']:
                    writer.writerow([
                        conv.get('session_id', ''),
                        conv.get('scenario_name', ''),
                        conv.get('mode', ''),
                        conv.get('total_cost', 0),
                        conv.get('message_count', 0),
                        conv.get('duration_minutes', 0)
                    ])
        
        return filename
    
    async def export_json_report(self, cost_report: Dict) -> str:
        """Export cost report as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"cost_report_{timestamp}.json"
        
        with open(filename, 'w') as jsonfile:
            json.dump(cost_report, jsonfile, indent=2)
        
        return filename

# FastAPI Routes

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Cost analysis dashboard home page"""
    dashboard = CostDashboard(db)
    dashboard_data = await dashboard.get_dashboard_data(str(current_user.id), days)
    
    # Generate charts
    cost_chart = dashboard.generate_cost_chart(dashboard_data["daily_costs"])
    service_chart = dashboard.generate_service_breakdown_chart(dashboard_data["service_breakdown"])
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Cost Analysis Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .card {{ background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }}
            .metric {{ text-align: center; padding: 15px; background: #f8f9fa; border-radius: 6px; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .metric-label {{ font-size: 14px; color: #666; margin-top: 5px; }}
            .chart {{ text-align: center; margin: 20px 0; }}
            .chart img {{ max-width: 100%; height: auto; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f8f9fa; }}
            .export-buttons {{ margin: 20px 0; }}
            .btn {{ padding: 10px 20px; margin: 5px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
            .btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💰 Cost Analysis Dashboard</h1>
            <p>Period: {dashboard_data['period']['start_date'][:10]} to {dashboard_data['period']['end_date'][:10]} ({days} days)</p>
            
            <div class="card">
                <h2>📊 Summary</h2>
                <div class="summary">
                    <div class="metric">
                        <div class="metric-value">${dashboard_data['summary']['total_cost_usd']:.4f}</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{dashboard_data['summary']['scenarios_created']}</div>
                        <div class="metric-label">Scenarios Created</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{dashboard_data['summary']['conversations_completed']}</div>
                        <div class="metric-label">Conversations</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{dashboard_data['usage_breakdown']['total_tokens']:,}</div>
                        <div class="metric-label">Total Tokens</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{dashboard_data['usage_breakdown']['total_stt_minutes']:.1f}</div>
                        <div class="metric-label">STT Minutes</div>
                    </div>
                    <div class="metric">
                        <div class="metric-value">{dashboard_data['usage_breakdown']['total_tts_characters']:,}</div>
                        <div class="metric-label">TTS Characters</div>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>📈 Cost Trends</h2>
                <div class="chart">
                    <img src="data:image/png;base64,{cost_chart}" alt="Cost Trends Chart">
                </div>
            </div>
            
            <div class="card">
                <h2>🔧 Service Breakdown</h2>
                <div class="chart">
                    <img src="data:image/png;base64,{service_chart}" alt="Service Breakdown Chart">
                </div>
                
                <table>
                    <tr><th>Service</th><th>Cost (USD)</th><th>Percentage</th></tr>
    """
    
    total_service_cost = sum(dashboard_data["service_breakdown"].values())
    for service, cost in dashboard_data["service_breakdown"].items():
        if cost > 0:
            percentage = (cost / total_service_cost * 100) if total_service_cost > 0 else 0
            html_content += f"<tr><td>{service.replace('_', ' ').title()}</td><td>${cost:.4f}</td><td>{percentage:.1f}%</td></tr>"
    
    html_content += f"""
                </table>
            </div>
            
            <div class="card">
                <h2>📋 Export Reports</h2>
                <div class="export-buttons">
                    <a href="/cost-dashboard/export?format=csv&days={days}" class="btn">📄 Export CSV</a>
                    <a href="/cost-dashboard/export?format=json&days={days}" class="btn">📋 Export JSON</a>
                    <a href="/cost-dashboard/pricing" class="btn">💰 View Pricing</a>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Current Pricing</h2>
                <table>
                    <tr><th>Service</th><th>Unit</th><th>Cost</th></tr>
                    <tr><td>GPT-4o Input</td><td>1K tokens</td><td>${PRICING['gpt-4o']['input']:.4f}</td></tr>
                    <tr><td>GPT-4o Output</td><td>1K tokens</td><td>${PRICING['gpt-4o']['output']:.4f}</td></tr>
                    <tr><td>Speech-to-Text</td><td>Per minute</td><td>${PRICING['speech']['stt_per_minute']:.4f}</td></tr>
                    <tr><td>Text-to-Speech</td><td>Per character</td><td>${PRICING['speech']['tts_per_character']:.6f}</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

@router.get("/export")
async def export_report(
    format: str = Query("csv", description="Export format: csv or json"),
    days: int = Query(30, description="Number of days to analyze"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Export detailed cost report"""
    dashboard = CostDashboard(db)
    
    end_date = datetime.now().isoformat()
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    filename = await dashboard.export_detailed_report(str(current_user.id), start_date, end_date, format)
    
    return FileResponse(
        filename,
        media_type='application/octet-stream',
        filename=filename
    )

@router.get("/api/data")
async def get_dashboard_api_data(
    days: int = Query(30, description="Number of days to analyze"),
    current_user: UserDB = Depends(get_current_user),
    db: Any = Depends(get_db)
):
    """Get dashboard data as JSON API"""
    dashboard = CostDashboard(db)
    return await dashboard.get_dashboard_data(str(current_user.id), days)

@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page():
    """Display current pricing information"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Services Pricing</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background-color: #f8f9fa; }
            .example { background: #e7f3ff; padding: 15px; border-radius: 6px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>💰 AI Services Pricing</h1>
            
            <div class="card">
                <h2>🤖 OpenAI Models</h2>
                <table>
                    <tr><th>Model</th><th>Input (per 1K tokens)</th><th>Output (per 1K tokens)</th></tr>
    """
    
    for model, pricing in PRICING.items():
        if model in ["gpt-4o", "gpt-4", "text-embedding-ada-002"]:
            html_content += f"<tr><td>{model}</td><td>${pricing['input']:.4f}</td><td>${pricing['output']:.4f}</td></tr>"
    
    html_content += f"""
                </table>
            </div>
            
            <div class="card">
                <h2>🎤 Speech Services</h2>
                <table>
                    <tr><th>Service</th><th>Unit</th><th>Cost</th></tr>
                    <tr><td>Speech-to-Text</td><td>Per minute</td><td>${PRICING['speech']['stt_per_minute']:.4f}</td></tr>
                    <tr><td>Text-to-Speech</td><td>Per character</td><td>${PRICING['speech']['tts_per_character']:.6f}</td></tr>
                </table>
            </div>
            
            <div class="card">
                <h2>📊 Cost Examples</h2>
                
                <div class="example">
                    <h3>Scenario Creation</h3>
                    <p><strong>Typical scenario creation:</strong> $0.10 - $0.50</p>
                    <ul>
                        <li>Template analysis: ~2,000 tokens → $0.01-0.03</li>
                        <li>Persona generation: ~3,000 tokens → $0.02-0.05</li>
                        <li>Prompt generation: ~5,000 tokens → $0.03-0.08</li>
                    </ul>
                </div>
                
                <div class="example">
                    <h3>Conversation Session</h3>
                    <p><strong>10-message conversation:</strong> $0.05 - $0.20</p>
                    <ul>
                        <li>Chat responses: ~3,000 tokens → $0.02-0.05</li>
                        <li>STT (5 minutes): ~$0.12</li>
                        <li>TTS (1,000 characters): ~$0.016</li>
                    </ul>
                </div>
                
                <div class="example">
                    <h3>Daily Usage Estimates</h3>
                    <ul>
                        <li><strong>Light usage:</strong> 2 scenarios, 5 conversations → $1-3/day</li>
                        <li><strong>Moderate usage:</strong> 5 scenarios, 15 conversations → $3-8/day</li>
                        <li><strong>Heavy usage:</strong> 10 scenarios, 30 conversations → $8-20/day</li>
                    </ul>
                </div>
            </div>
            
            <div class="card">
                <h2>💡 Cost Optimization Tips</h2>
                <ul>
                    <li><strong>Use GPT-4o instead of GPT-4:</strong> ~5x cheaper for similar quality</li>
                    <li><strong>Optimize prompts:</strong> Shorter, more focused prompts reduce token usage</li>
                    <li><strong>Cache scenarios:</strong> Reuse generated scenarios instead of recreating</li>
                    <li><strong>Batch operations:</strong> Process multiple items in single API calls</li>
                    <li><strong>Monitor usage:</strong> Use the dashboard to track and optimize costs</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content

# Export the router
__all__ = ['router', 'CostDashboard']