#!/usr/bin/env python3
"""
Auto Launcher - Fully automated product creation and upload system
Runs continuously to generate and upload profitable digital products
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from generators.ai_product_generator import AIProductGenerator
from whop_api.whop_integration import WhopIntegration, BatchUploader
import time
import schedule
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

class AutoLauncher:
    def __init__(self):
        self.generator = AIProductGenerator()
        self.whop = WhopIntegration()
        self.uploader = BatchUploader(self.whop)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/automation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self._load_config()
        
        # High-converting product niches based on WHOP research
        self.profitable_niches = [
            # Business & Entrepreneurship (Highest ROI)
            ('Social Media Marketing Mastery', 'entrepreneurs', 'business'),
            ('Dropshipping Empire Blueprint', 'ecommerce beginners', 'business'),
            ('Real Estate Investment Guide', 'investors', 'finance'),
            ('Affiliate Marketing Secrets', 'online marketers', 'business'),
            ('Email Marketing Templates', 'business owners', 'marketing'),
            
            # Personal Development & Productivity
            ('Ultimate Productivity Planner', 'professionals', 'productivity'),
            ('Digital Detox Challenge', 'wellness seekers', 'wellness'),
            ('Goal Setting Workbook', 'achievers', 'productivity'),
            ('Time Management Mastery', 'busy professionals', 'productivity'),
            ('Habit Tracker Templates', 'self-improvement', 'wellness'),
            
            # Health & Wellness
            ('30-Day Fitness Planner', 'fitness enthusiasts', 'wellness'),
            ('Meal Prep Made Simple', 'health conscious', 'wellness'),
            ('Mental Health Journal', 'wellness seekers', 'wellness'),
            ('Stress Management Guide', 'professionals', 'wellness'),
            ('Sleep Optimization Blueprint', 'health optimizers', 'wellness'),
            
            # Finance & Investment
            ('Personal Finance Tracker', 'young adults', 'finance'),
            ('Cryptocurrency Basics', 'crypto beginners', 'finance'),
            ('Retirement Planning Guide', 'adults 30+', 'finance'),
            ('Side Hustle Starter Kit', 'income seekers', 'business'),
            ('Budgeting Templates Bundle', 'savers', 'finance')
        ]
        
        self.daily_targets = {
            'ebooks': 2,
            'templates': 3,
            'planners': 1,
            'email_templates': 1
        }
    
    def _load_config(self) -> dict:
        """Load automation configuration"""
        config_file = Path('config/automation_config.json')
        
        default_config = {
            'auto_generate': True,
            'auto_upload': True,
            'generation_interval_hours': 6,
            'upload_interval_hours': 2,
            'max_daily_products': 10,
            'price_optimization': True,
            'seo_optimization': True,
            'webhook_notifications': True
        }
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def run_daily_automation(self):
        """Main automation routine - runs daily"""
        self.logger.info("🚀 Starting daily automation cycle")
        
        try:
            # Generate new products
            if self.config['auto_generate']:
                generated_count = self._generate_daily_products()
                self.logger.info(f"🎯 Generated {generated_count} products")
            
            # Upload products to WHOP
            if self.config['auto_upload']:
                upload_results = self._upload_pending_products()
                self.logger.info(f"📦 Upload results: {upload_results['success']} success, {upload_results['failed']} failed")
            
            # Optimize existing products
            if self.config['price_optimization']:
                self._optimize_product_prices()
            
            # Generate daily report
            self._generate_daily_report()
            
            self.logger.info("✅ Daily automation cycle completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Daily automation failed: {e}")
    
    def _generate_daily_products(self) -> int:
        """Generate daily quota of products"""
        generated_count = 0
        
        for product_type, target_count in self.daily_targets.items():
            for i in range(target_count):
                try:
                    # Select random niche
                    niche_data = self.profitable_niches[generated_count % len(self.profitable_niches)]
                    topic, audience, category = niche_data
                    
                    if product_type == 'ebooks':
                        result = self.generator.generate_ebook(topic, audience)
                    elif product_type == 'templates':
                        template_types = ['productivity dashboard', 'project tracker', 'content calendar', 'business planner']
                        template_type = template_types[i % len(template_types)]
                        result = self.generator.generate_notion_template(template_type, topic)
                    elif product_type == 'planners':
                        periods = ['daily', 'weekly', 'monthly']
                        period = periods[i % len(periods)]
                        result = self.generator.generate_planner_template(category, period)
                    elif product_type == 'email_templates':
                        result = self.generator.generate_email_templates(category, 5)
                    
                    if result:
                        generated_count += 1
                        self.logger.info(f"✅ Generated {product_type}: {result.get('title', 'Untitled')}")
                    
                    # Small delay to avoid rate limits
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to generate {product_type}: {e}")
        
        return generated_count
    
    def _upload_pending_products(self) -> dict:
        """Upload all pending products to WHOP"""
        return self.uploader.upload_products_from_directory('generated_products')
    
    def _optimize_product_prices(self):
        """Optimize pricing based on performance data"""
        self.logger.info("💰 Starting price optimization")
        
        try:
            products = self.whop.list_products()
            
            for product in products:
                if product.get('metadata', {}).get('auto_generated'):
                    # Get analytics
                    analytics = self.whop.get_product_analytics(product['id'])
                    
                    if analytics:
                        # Simple optimization logic
                        views = analytics.get('views', 0)
                        purchases = analytics.get('purchases', 0)
                        current_price = product.get('price', 0)
                        
                        # If high views but low conversion, reduce price
                        if views > 100 and purchases < 5:
                            new_price = int(current_price * 0.8)  # 20% reduction
                            self.whop.update_product_pricing(product['id'], new_price)
                            self.logger.info(f"💰 Reduced price for {product['title']}")
                        
                        # If good conversion rate, increase price
                        elif views > 50 and purchases > 10:
                            conversion_rate = purchases / views
                            if conversion_rate > 0.1:  # 10% conversion rate
                                new_price = int(current_price * 1.2)  # 20% increase
                                self.whop.update_product_pricing(product['id'], new_price)
                                self.logger.info(f"💰 Increased price for {product['title']}")
                    
                    time.sleep(1)  # Rate limiting
        
        except Exception as e:
            self.logger.error(f"❌ Price optimization failed: {e}")
    
    def _generate_daily_report(self):
        """Generate daily performance report"""
        self.logger.info("📊 Generating daily report")
        
        try:
            # Get all products
            products = self.whop.list_products()
            auto_generated = [p for p in products if p.get('metadata', {}).get('auto_generated')]
            
            # Calculate metrics
            total_products = len(auto_generated)
            total_revenue = 0
            total_sales = 0
            
            for product in auto_generated:
                analytics = self.whop.get_product_analytics(product['id'])
                if analytics:
                    total_sales += analytics.get('purchases', 0)
                    total_revenue += analytics.get('revenue', 0)
            
            # Create report
            report = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total_products': total_products,
                'total_sales': total_sales,
                'total_revenue': total_revenue / 100 if total_revenue else 0,  # Convert from cents
                'average_price': (total_revenue / total_sales / 100) if total_sales else 0,
                'generated_today': len(list(Path('generated_products').glob(f"*{datetime.now().strftime('%Y%m%d')}*.json")))
            }
            
            # Save report
            reports_dir = Path('reports')
            reports_dir.mkdir(exist_ok=True)
            
            report_file = reports_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"📊 Report saved: ${report['total_revenue']:.2f} revenue, {report['total_sales']} sales")
            
        except Exception as e:
            self.logger.error(f"❌ Report generation failed: {e}")
    
    def run_continuous(self):
        """Run continuous automation with scheduling"""
        self.logger.info("🎆 Starting continuous automation system")
        
        # Schedule daily full automation
        schedule.every().day.at("09:00").do(self.run_daily_automation)
        
        # Schedule hourly mini-generations
        schedule.every(2).hours.do(self._mini_generation_cycle)
        
        # Schedule price optimization
        schedule.every().day.at("15:00").do(self._optimize_product_prices)
        
        # Schedule uploads
        schedule.every(3).hours.do(self._upload_pending_products)
        
        self.logger.info("🔄 Automation schedules set up")
        
        # Run initial cycle
        self.run_daily_automation()
        
        # Keep running
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("🛑 Automation stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Automation error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _mini_generation_cycle(self):
        """Generate 1-2 products every few hours"""
        self.logger.info("🔄 Running mini generation cycle")
        
        try:
            # Generate 1-2 quick products
            niche_data = self.profitable_niches[datetime.now().hour % len(self.profitable_niches)]
            topic, audience, category = niche_data
            
            # Alternate between product types
            if datetime.now().hour % 2 == 0:
                result = self.generator.generate_ebook(topic, audience)
            else:
                result = self.generator.generate_notion_template('productivity template', topic)
            
            if result:
                self.logger.info(f"✅ Mini-cycle generated: {result.get('title')}")
        
        except Exception as e:
            self.logger.error(f"❌ Mini-cycle failed: {e}")
    
    def setup_webhooks(self):
        """Setup WHOP webhooks for real-time notifications"""
        webhook_events = [
            'purchase.created',
            'membership.created',
            'subscription.created',
            'payment.succeeded'
        ]
        
        # You would replace this with your actual webhook URL
        webhook_url = "https://your-domain.com/webhook/whop"
        
        webhook_id = self.whop.setup_webhook(webhook_url, webhook_events)
        
        if webhook_id:
            self.logger.info(f"🔗 Webhooks configured: {webhook_id}")
        else:
            self.logger.error("❌ Failed to setup webhooks")
    
    def get_performance_summary(self) -> dict:
        """Get current performance summary"""
        try:
            products = self.whop.list_products()
            auto_generated = [p for p in products if p.get('metadata', {}).get('auto_generated')]
            
            total_revenue = 0
            total_sales = 0
            
            for product in auto_generated[:10]:  # Sample first 10 for performance
                analytics = self.whop.get_product_analytics(product['id'])
                if analytics:
                    total_sales += analytics.get('purchases', 0)
                    total_revenue += analytics.get('revenue', 0)
            
            return {
                'total_products': len(auto_generated),
                'estimated_sales': total_sales * (len(auto_generated) / min(10, len(auto_generated))),
                'estimated_revenue': (total_revenue / 100) * (len(auto_generated) / min(10, len(auto_generated))),
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            self.logger.error(f"❌ Performance summary failed: {e}")
            return {'error': str(e)}

def main():
    """
    Main entry point for automation
    """
    print("🚀 Nosyt WHOP Automation System")
    print("=" * 40)
    
    launcher = AutoLauncher()
    
    # Check configuration
    if not launcher.whop.api_key or not launcher.whop.company_id:
        print("❌ Missing WHOP API credentials!")
        print("Please set WHOP_API_KEY and WHOP_COMPANY_ID environment variables")
        return
    
    print("Choose an option:")
    print("1. Run once (generate and upload products now)")
    print("2. Run continuous automation (24/7)")
    print("3. Setup webhooks only")
    print("4. View performance summary")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        launcher.run_daily_automation()
    elif choice == '2':
        launcher.run_continuous()
    elif choice == '3':
        launcher.setup_webhooks()
    elif choice == '4':
        summary = launcher.get_performance_summary()
        print(f"\n📊 Performance Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
