#!/usr/bin/env python3
"""
WHOP API Integration - Automated product upload and management
Part of Nosyt WHOP Automation System
"""

import requests
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import time
from pathlib import Path

class WhopIntegration:
    def __init__(self, api_key: str = None, company_id: str = None):
        self.api_key = api_key or os.getenv('WHOP_API_KEY')
        self.company_id = company_id or os.getenv('WHOP_COMPANY_ID')
        self.base_url = "https://api.whop.com/api/v5"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Create logs directory
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
    def create_product(self, product_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new product on WHOP marketplace
        """
        print(f"📦 Creating product: {product_data.get('title', 'Untitled')}")
        
        # Map our product format to WHOP API format
        whop_product = self._format_for_whop_api(product_data)
        
        try:
            response = requests.post(
                f"{self.base_url}/companies/{self.company_id}/products",
                headers=self.headers,
                json=whop_product
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Product created successfully! ID: {result.get('id')}")
                
                # Log successful creation
                self._log_action('create_product', 'success', {
                    'product_id': result.get('id'),
                    'title': product_data.get('title'),
                    'price': whop_product.get('price')
                })
                
                return result
            else:
                error_msg = f"Failed to create product. Status: {response.status_code}, Response: {response.text}"
                print(f"❌ {error_msg}")
                
                # Log failure
                self._log_action('create_product', 'error', {
                    'title': product_data.get('title'),
                    'error': error_msg
                })
                
                return None
                
        except Exception as e:
            error_msg = f"Exception creating product: {str(e)}"
            print(f"❌ {error_msg}")
            self._log_action('create_product', 'error', {'error': error_msg})
            return None
    
    def upload_digital_asset(self, file_path: str, product_id: str) -> Optional[str]:
        """
        Upload digital file to WHOP for download delivery
        """
        print(f"📤 Uploading digital asset for product {product_id}")
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': file}
                
                response = requests.post(
                    f"{self.base_url}/products/{product_id}/assets",
                    headers={"Authorization": self.headers["Authorization"]},  # Remove Content-Type for file upload
                    files=files
                )
                
                if response.status_code == 201:
                    result = response.json()
                    asset_id = result.get('id')
                    print(f"✅ Asset uploaded successfully! ID: {asset_id}")
                    
                    self._log_action('upload_asset', 'success', {
                        'product_id': product_id,
                        'asset_id': asset_id,
                        'file_path': file_path
                    })
                    
                    return asset_id
                else:
                    error_msg = f"Failed to upload asset. Status: {response.status_code}"
                    print(f"❌ {error_msg}")
                    return None
                    
        except Exception as e:
            print(f"❌ Error uploading asset: {e}")
            return None
    
    def create_membership_product(self, membership_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a membership/subscription product
        """
        print(f"🎫 Creating membership: {membership_data.get('title')}")
        
        whop_membership = {
            "title": membership_data.get('title'),
            "description": membership_data.get('description'),
            "price": membership_data.get('price', 2997),  # Price in cents
            "type": "subscription",
            "billing_period": membership_data.get('billing_period', 'monthly'),
            "visibility": "public",
            "stock": -1,  # Unlimited
            "metadata": {
                "auto_generated": True,
                "product_type": "membership",
                "created_by": "nosyt_automation"
            },
            "apps": membership_data.get('apps', []),
            "roles": membership_data.get('roles', [])
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/companies/{self.company_id}/products",
                headers=self.headers,
                json=whop_membership
            )
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Membership created! ID: {result.get('id')}")
                return result
            else:
                print(f"❌ Failed to create membership: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating membership: {e}")
            return None
    
    def update_product_pricing(self, product_id: str, new_price: int) -> bool:
        """
        Update product pricing (for A/B testing)
        """
        print(f"💰 Updating price for product {product_id} to ${new_price/100:.2f}")
        
        try:
            response = requests.patch(
                f"{self.base_url}/products/{product_id}",
                headers=self.headers,
                json={"price": new_price}
            )
            
            if response.status_code == 200:
                print(f"✅ Price updated successfully")
                self._log_action('update_price', 'success', {
                    'product_id': product_id,
                    'new_price': new_price
                })
                return True
            else:
                print(f"❌ Failed to update price: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error updating price: {e}")
            return False
    
    def get_product_analytics(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch product performance analytics
        """
        try:
            response = requests.get(
                f"{self.base_url}/products/{product_id}/analytics",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to fetch analytics: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error fetching analytics: {e}")
            return None
    
    def list_products(self) -> List[Dict[str, Any]]:
        """
        List all products in the company
        """
        try:
            response = requests.get(
                f"{self.base_url}/companies/{self.company_id}/products",
                headers=self.headers
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                print(f"❌ Failed to list products: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing products: {e}")
            return []
    
    def setup_webhook(self, webhook_url: str, events: List[str]) -> Optional[str]:
        """
        Setup webhook for automated notifications
        """
        print(f"🔗 Setting up webhook: {webhook_url}")
        
        webhook_data = {
            "url": webhook_url,
            "events": events,
            "active": True
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/companies/{self.company_id}/webhooks",
                headers=self.headers,
                json=webhook_data
            )
            
            if response.status_code == 201:
                result = response.json()
                webhook_id = result.get('id')
                print(f"✅ Webhook created! ID: {webhook_id}")
                return webhook_id
            else:
                print(f"❌ Failed to create webhook: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating webhook: {e}")
            return None
    
    def _format_for_whop_api(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert our internal product format to WHOP API format
        """
        product_type = product_data.get('type', 'digital_product')
        
        # Base product structure
        whop_product = {
            "title": product_data.get('title', 'Untitled Product'),
            "description": product_data.get('description', 'Professional digital product with PLR/MRR rights'),
            "price": product_data.get('suggested_price', 2997) * 100,  # Convert to cents
            "type": "one_time",
            "visibility": "public",
            "stock": -1,  # Unlimited digital product
            "category": self._get_category(product_type),
            "tags": product_data.get('tags', []),
            "metadata": {
                "auto_generated": True,
                "product_type": product_type,
                "plr_rights": product_data.get('plr_rights', True),
                "mrr_rights": product_data.get('mrr_rights', True),
                "created_by": "nosyt_automation",
                "word_count": product_data.get('word_count', 0)
            }
        }
        
        # Add product-specific fields
        if product_type == 'ebook':
            whop_product["metadata"].update({
                "chapters": len(product_data.get('chapters', [])),
                "formats": ["PDF", "EPUB", "DOCX"]
            })
        elif product_type == 'notion_template':
            whop_product["metadata"].update({
                "template_type": product_data.get('template_type'),
                "use_case": product_data.get('use_case')
            })
        elif product_type == 'digital_planner':
            whop_product["metadata"].update({
                "planner_type": product_data.get('planner_type'),
                "period": product_data.get('period'),
                "formats": product_data.get('formats', [])
            })
        
        return whop_product
    
    def _get_category(self, product_type: str) -> str:
        """
        Map product types to WHOP categories
        """
        category_mapping = {
            'ebook': 'education',
            'notion_template': 'productivity',
            'digital_planner': 'productivity',
            'email_templates': 'marketing',
            'course': 'education',
            'membership': 'community'
        }
        
        return category_mapping.get(product_type, 'other')
    
    def _log_action(self, action: str, status: str, data: Dict[str, Any]):
        """
        Log API actions for monitoring and debugging
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'data': data
        }
        
        log_file = self.logs_dir / f"whop_api_{datetime.now().strftime('%Y%m%d')}.log"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

class BatchUploader:
    """
    Batch upload multiple products to WHOP with rate limiting
    """
    
    def __init__(self, whop_integration: WhopIntegration):
        self.whop = whop_integration
        self.upload_delay = 2  # Seconds between uploads to respect rate limits
    
    def upload_products_from_directory(self, products_dir: str) -> Dict[str, Any]:
        """
        Upload all generated products from a directory
        """
        products_path = Path(products_dir)
        if not products_path.exists():
            print(f"❌ Products directory not found: {products_dir}")
            return {'success': 0, 'failed': 0, 'products': []}
        
        json_files = list(products_path.glob('*.json'))
        print(f"📦 Found {len(json_files)} products to upload")
        
        results = {
            'success': 0,
            'failed': 0,
            'products': []
        }
        
        for file_path in json_files:
            try:
                with open(file_path, 'r') as f:
                    product_data = json.load(f)
                
                # Upload to WHOP
                result = self.whop.create_product(product_data)
                
                if result:
                    results['success'] += 1
                    results['products'].append({
                        'title': product_data.get('title'),
                        'whop_id': result.get('id'),
                        'status': 'success'
                    })
                    
                    # Generate and upload digital files if needed
                    self._create_digital_files(product_data, result.get('id'))
                else:
                    results['failed'] += 1
                    results['products'].append({
                        'title': product_data.get('title'),
                        'status': 'failed'
                    })
                
                # Rate limiting
                time.sleep(self.upload_delay)
                
            except Exception as e:
                print(f"❌ Error processing {file_path}: {e}")
                results['failed'] += 1
        
        print(f"\n🎉 Upload complete! Success: {results['success']}, Failed: {results['failed']}")
        return results
    
    def _create_digital_files(self, product_data: Dict[str, Any], product_id: str):
        """
        Create actual digital files from product data
        """
        product_type = product_data.get('type')
        
        if product_type == 'ebook':
            self._create_ebook_files(product_data, product_id)
        elif product_type == 'notion_template':
            self._create_notion_template_files(product_data, product_id)
        elif product_type == 'digital_planner':
            self._create_planner_files(product_data, product_id)
        elif product_type == 'email_templates':
            self._create_email_template_files(product_data, product_id)
    
    def _create_ebook_files(self, product_data: Dict[str, Any], product_id: str):
        """
        Create downloadable ebook files (PDF, DOCX, etc.)
        """
        # Create output directory
        output_dir = Path(f'output/{product_id}')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate HTML content
        html_content = self._generate_ebook_html(product_data)
        
        # Save HTML file
        html_file = output_dir / 'ebook.html'
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Create text version
        text_content = self._generate_ebook_text(product_data)
        text_file = output_dir / 'ebook.txt'
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Create markdown version
        md_content = self._generate_ebook_markdown(product_data)
        md_file = output_dir / 'ebook.md'
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"📚 Ebook files created in {output_dir}")
    
    def _generate_ebook_html(self, product_data: Dict[str, Any]) -> str:
        """
        Generate HTML version of ebook
        """
        title = product_data.get('title', 'Untitled Ebook')
        subtitle = product_data.get('subtitle', '')
        chapters = product_data.get('chapters', [])
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Georgia, serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1 {{ color: #333; border-bottom: 3px solid #007acc; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .subtitle {{ font-style: italic; color: #666; margin-bottom: 30px; }}
        .chapter {{ margin-bottom: 40px; page-break-after: always; }}
        .toc {{ background: #f9f9f9; padding: 20px; margin-bottom: 30px; }}
        .toc ul {{ list-style-type: none; }}
        .toc li {{ margin: 10px 0; }}
        .footer {{ text-align: center; margin-top: 50px; font-size: 0.9em; color: #666; }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    {f'<p class="subtitle">{subtitle}</p>' if subtitle else ''}
    
    <div class="toc">
        <h2>Table of Contents</h2>
        <ul>
        {''.join([f'<li>Chapter {i+1}: {chapter["title"]}</li>' for i, chapter in enumerate(chapters)])}
        </ul>
    </div>
    
    {''.join([f'<div class="chapter"><h2>Chapter {i+1}: {chapter["title"]}</h2><div>{chapter["content"]}</div></div>' for i, chapter in enumerate(chapters)])}
    
    <div class="footer">
        <p>This ebook comes with Private Label Rights (PLR). You may edit, rebrand, and resell this content.</p>
        <p>Generated by Nosyt Automation System</p>
    </div>
</body>
</html>
        """
        
        return html
    
    def _generate_ebook_text(self, product_data: Dict[str, Any]) -> str:
        """
        Generate plain text version of ebook
        """
        title = product_data.get('title', 'Untitled Ebook')
        subtitle = product_data.get('subtitle', '')
        chapters = product_data.get('chapters', [])
        
        text = f"{title}\n{'=' * len(title)}\n\n"
        
        if subtitle:
            text += f"{subtitle}\n\n"
        
        text += "TABLE OF CONTENTS\n-----------------\n"
        for i, chapter in enumerate(chapters):
            text += f"Chapter {i+1}: {chapter['title']}\n"
        
        text += "\n\n"
        
        for i, chapter in enumerate(chapters):
            text += f"Chapter {i+1}: {chapter['title']}\n"
            text += "-" * (len(chapter['title']) + 12) + "\n\n"
            text += chapter['content'] + "\n\n"
        
        text += "\n" + "=" * 50 + "\n"
        text += "This ebook comes with Private Label Rights (PLR).\n"
        text += "You may edit, rebrand, and resell this content.\n"
        text += "Generated by Nosyt Automation System\n"
        
        return text
    
    def _generate_ebook_markdown(self, product_data: Dict[str, Any]) -> str:
        """
        Generate Markdown version of ebook
        """
        title = product_data.get('title', 'Untitled Ebook')
        subtitle = product_data.get('subtitle', '')
        chapters = product_data.get('chapters', [])
        
        md = f"# {title}\n\n"
        
        if subtitle:
            md += f"*{subtitle}*\n\n"
        
        md += "## Table of Contents\n\n"
        for i, chapter in enumerate(chapters):
            md += f"{i+1}. {chapter['title']}\n"
        
        md += "\n---\n\n"
        
        for i, chapter in enumerate(chapters):
            md += f"## Chapter {i+1}: {chapter['title']}\n\n"
            md += chapter['content'] + "\n\n"
        
        md += "---\n\n"
        md += "**PLR License**: This ebook comes with Private Label Rights (PLR). "
        md += "You may edit, rebrand, and resell this content.\n\n"
        md += "*Generated by Nosyt Automation System*\n"
        
        return md
    
    def _create_notion_template_files(self, product_data: Dict[str, Any], product_id: str):
        """
        Create Notion template files
        """
        output_dir = Path(f'output/{product_id}')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create JSON structure file
        structure_file = output_dir / 'notion_structure.json'
        with open(structure_file, 'w') as f:
            json.dump(product_data.get('structure', {}), f, indent=2)
        
        # Create instructions file
        instructions = product_data.get('instructions', [])
        instructions_file = output_dir / 'setup_instructions.md'
        with open(instructions_file, 'w') as f:
            f.write(f"# {product_data.get('name', 'Notion Template')} - Setup Instructions\n\n")
            for i, instruction in enumerate(instructions, 1):
                f.write(f"{i}. {instruction}\n")
        
        print(f"📋 Notion template files created in {output_dir}")
    
    def _create_planner_files(self, product_data: Dict[str, Any], product_id: str):
        """
        Create digital planner files
        """
        output_dir = Path(f'output/{product_id}')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create planner structure file
        planner_file = output_dir / 'planner_layouts.json'
        with open(planner_file, 'w') as f:
            json.dump(product_data.get('layouts', {}), f, indent=2)
        
        # Create PDF instructions
        instructions_file = output_dir / 'planner_instructions.md'
        with open(instructions_file, 'w') as f:
            f.write(f"# {product_data.get('name', 'Digital Planner')}\n\n")
            f.write("## How to Use This Planner\n\n")
            f.write("This digital planner can be used with:\n")
            for format_type in product_data.get('formats', []):
                f.write(f"- {format_type}\n")
        
        print(f"📅 Planner files created in {output_dir}")
    
    def _create_email_template_files(self, product_data: Dict[str, Any], product_id: str):
        """
        Create email template files
        """
        output_dir = Path(f'output/{product_id}')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        templates = product_data.get('templates', [])
        
        for i, template in enumerate(templates, 1):
            # Create HTML version
            html_file = output_dir / f'template_{i}_{template["type"]}.html'
            with open(html_file, 'w') as f:
                f.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{template['subject_line']}</title>\n</head>\n<body>\n")
                f.write(template['content'].replace('\n', '<br>\n'))
                f.write("\n</body>\n</html>")
            
            # Create plain text version
            txt_file = output_dir / f'template_{i}_{template["type"]}.txt'
            with open(txt_file, 'w') as f:
                f.write(f"Subject: {template['subject_line']}\n\n")
                f.write(template['content'])
        
        print(f"📧 Email template files created in {output_dir}")

# Demo and testing functions
def main():
    """
    Demo the WHOP integration
    """
    # Initialize WHOP integration
    whop = WhopIntegration()
    
    # Check if we have valid credentials
    if not whop.api_key or not whop.company_id:
        print("❌ Please set WHOP_API_KEY and WHOP_COMPANY_ID environment variables")
        return
    
    print("🚀 WHOP Integration Demo")
    
    # List existing products
    products = whop.list_products()
    print(f"📦 Found {len(products)} existing products")
    
    # Test batch upload
    uploader = BatchUploader(whop)
    results = uploader.upload_products_from_directory('generated_products')
    
    print(f"\n📊 Upload Results:")
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['failed']}")
    
    # Setup webhooks for automation
    webhook_events = [
        'purchase.created',
        'membership.created',
        'membership.cancelled'
    ]
    
    webhook_url = "https://your-domain.com/webhook/whop"  # Replace with your webhook URL
    webhook_id = whop.setup_webhook(webhook_url, webhook_events)
    
    if webhook_id:
        print(f"🔗 Webhook setup complete: {webhook_id}")
    
    print("\n🎉 WHOP Integration setup complete!")

if __name__ == "__main__":
    main()
