#!/usr/bin/env python3
"""
AI Product Generator - Creates PLR/MRR digital products automatically
Part of Nosyt WHOP Automation System
"""

import openai
import json
import os
from datetime import datetime
from typing import Dict, List, Any
import requests
from pathlib import Path

class AIProductGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        openai.api_key = self.api_key
        self.products_dir = Path('generated_products')
        self.products_dir.mkdir(exist_ok=True)
        
    def generate_ebook(self, topic: str, target_audience: str = "general") -> Dict[str, Any]:
        """
        Generate a complete PLR ebook with chapters, content, and metadata
        """
        print(f"🤖 Generating ebook: {topic}")
        
        # Generate ebook outline
        outline_prompt = f"""
        Create a detailed outline for a PLR ebook about "{topic}" targeting {target_audience}.
        
        Include:
        - Compelling title
        - 8-12 chapter titles
        - Brief description of each chapter
        - Target word count (2000-5000 words)
        - 3 bonus sections
        - Call-to-action ideas
        
        Format as JSON with keys: title, subtitle, chapters, target_words, bonus_sections, cta_ideas
        """
        
        try:
            outline_response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": outline_prompt}],
                temperature=0.7
            )
            
            outline = json.loads(outline_response.choices[0].message.content)
            
            # Generate full content
            content_sections = []
            for chapter in outline['chapters']:
                chapter_content = self._generate_chapter_content(chapter, topic, target_audience)
                content_sections.append({
                    'title': chapter['title'],
                    'content': chapter_content
                })
            
            # Create ebook package
            ebook_package = {
                'type': 'ebook',
                'title': outline['title'],
                'subtitle': outline.get('subtitle', ''),
                'topic': topic,
                'target_audience': target_audience,
                'chapters': content_sections,
                'bonus_sections': outline.get('bonus_sections', []),
                'word_count': sum(len(section['content'].split()) for section in content_sections),
                'created_at': datetime.now().isoformat(),
                'plr_rights': True,
                'mrr_rights': True,
                'suggested_price': self._calculate_price('ebook', len(content_sections)),
                'tags': self._generate_tags(topic),
                'description': self._generate_description(outline['title'], topic)
            }
            
            # Save to file
            filename = f"ebook_{topic.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.products_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(ebook_package, f, indent=2)
            
            print(f"✅ Ebook generated: {filepath}")
            return ebook_package
            
        except Exception as e:
            print(f"❌ Error generating ebook: {e}")
            return None
    
    def generate_notion_template(self, template_type: str, use_case: str) -> Dict[str, Any]:
        """
        Generate Notion template with structure and content
        """
        print(f"📋 Generating Notion template: {template_type} for {use_case}")
        
        template_prompt = f"""
        Create a comprehensive Notion template for {template_type} designed for {use_case}.
        
        Include:
        - Template name and description
        - Database structures with properties
        - Page layouts and sections
        - Formulas and automations
        - Visual elements (icons, covers)
        - Instructions for customization
        - Use case examples
        
        Make it professional and highly functional.
        Format as JSON with detailed structure.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": template_prompt}],
                temperature=0.6
            )
            
            template_data = json.loads(response.choices[0].message.content)
            
            # Create template package
            template_package = {
                'type': 'notion_template',
                'template_type': template_type,
                'use_case': use_case,
                'name': template_data.get('name', f"{template_type} Template"),
                'description': template_data.get('description', ''),
                'structure': template_data,
                'created_at': datetime.now().isoformat(),
                'plr_rights': True,
                'suggested_price': self._calculate_price('notion_template', 1),
                'tags': self._generate_tags(f"{template_type} {use_case}"),
                'instructions': template_data.get('instructions', []),
                'preview_images': []  # Will be generated separately
            }
            
            # Save template
            filename = f"notion_{template_type.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.products_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(template_package, f, indent=2)
            
            print(f"✅ Notion template generated: {filepath}")
            return template_package
            
        except Exception as e:
            print(f"❌ Error generating Notion template: {e}")
            return None
    
    def generate_planner_template(self, planner_type: str, period: str = "monthly") -> Dict[str, Any]:
        """
        Generate digital planner templates
        """
        print(f"📅 Generating {period} {planner_type} planner")
        
        planner_prompt = f"""
        Create a comprehensive {period} {planner_type} planner template.
        
        Include:
        - Cover design concepts
        - Monthly/weekly/daily layouts
        - Goal-setting sections
        - Tracking pages
        - Reflection prompts
        - Customizable elements
        - Print and digital versions
        
        Make it visually appealing and highly functional.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": planner_prompt}],
                temperature=0.6
            )
            
            planner_data = json.loads(response.choices[0].message.content)
            
            planner_package = {
                'type': 'digital_planner',
                'planner_type': planner_type,
                'period': period,
                'name': f"{period.title()} {planner_type.title()} Planner",
                'description': planner_data.get('description', ''),
                'layouts': planner_data,
                'created_at': datetime.now().isoformat(),
                'plr_rights': True,
                'suggested_price': self._calculate_price('planner', 1),
                'tags': self._generate_tags(f"{planner_type} planner {period}"),
                'formats': ['PDF', 'PNG', 'Notion', 'GoodNotes'],
                'customizable': True
            }
            
            # Save planner
            filename = f"planner_{planner_type.replace(' ', '_')}_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.products_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(planner_package, f, indent=2)
            
            print(f"✅ Planner generated: {filepath}")
            return planner_package
            
        except Exception as e:
            print(f"❌ Error generating planner: {e}")
            return None
    
    def generate_email_templates(self, industry: str, template_count: int = 10) -> Dict[str, Any]:
        """
        Generate email template collections
        """
        print(f"📧 Generating {template_count} email templates for {industry}")
        
        templates = []
        template_types = [
            'welcome_series', 'sales_sequence', 'nurture_campaign', 
            'abandoned_cart', 'promotional', 'newsletter', 'follow_up',
            'onboarding', 'feedback_request', 'seasonal_campaign'
        ]
        
        for i in range(template_count):
            template_type = template_types[i % len(template_types)]
            
            template_prompt = f"""
            Create a high-converting {template_type} email template for {industry} businesses.
            
            Include:
            - Compelling subject line
            - Email body with personalization
            - Clear call-to-action
            - Mobile-optimized format
            - A/B test variations
            
            Make it professional and conversion-focused.
            """
            
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": template_prompt}],
                    temperature=0.7
                )
                
                template_content = response.choices[0].message.content
                
                templates.append({
                    'type': template_type,
                    'subject_line': self._extract_subject_line(template_content),
                    'content': template_content,
                    'cta': self._extract_cta(template_content),
                    'personalization_fields': ['[FIRST_NAME]', '[COMPANY]', '[PRODUCT]']
                })
                
            except Exception as e:
                print(f"❌ Error generating template {i+1}: {e}")
                continue
        
        # Create email template package
        email_package = {
            'type': 'email_templates',
            'industry': industry,
            'template_count': len(templates),
            'templates': templates,
            'created_at': datetime.now().isoformat(),
            'plr_rights': True,
            'suggested_price': self._calculate_price('email_templates', len(templates)),
            'tags': self._generate_tags(f"email templates {industry}"),
            'formats': ['HTML', 'Plain Text', 'Mailchimp', 'ConvertKit']
        }
        
        # Save templates
        filename = f"email_templates_{industry.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.products_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(email_package, f, indent=2)
        
        print(f"✅ Email templates generated: {filepath}")
        return email_package
    
    def _generate_chapter_content(self, chapter: Dict, topic: str, audience: str) -> str:
        """
        Generate detailed content for a chapter
        """
        content_prompt = f"""
        Write a comprehensive chapter for a PLR ebook about "{topic}" targeting {audience}.
        
        Chapter: {chapter.get('title', 'Untitled Chapter')}
        Description: {chapter.get('description', 'No description provided')}
        
        Requirements:
        - 800-1200 words
        - Actionable advice
        - Professional tone
        - Include examples
        - Add bullet points and subheadings
        - End with key takeaways
        
        Make it valuable and engaging.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": content_prompt}],
                temperature=0.7,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error generating chapter content: {e}")
            return f"Chapter content for {chapter.get('title', 'Untitled')} - [Content generation failed]"
    
    def _calculate_price(self, product_type: str, quantity: int) -> int:
        """
        Calculate suggested pricing based on product type and quantity
        """
        base_prices = {
            'ebook': 15,
            'notion_template': 25,
            'planner': 20,
            'email_templates': 3,  # per template
            'course': 100,
            'bundle': 50
        }
        
        base_price = base_prices.get(product_type, 20)
        
        if product_type == 'email_templates':
            return base_price * quantity
        
        # Add value multiplier for comprehensive products
        if quantity > 5:
            return int(base_price * 1.5)
        
        return base_price
    
    def _generate_tags(self, content: str) -> List[str]:
        """
        Generate relevant tags for SEO and categorization
        """
        tag_categories = {
            'business': ['business', 'entrepreneur', 'startup', 'marketing', 'sales'],
            'productivity': ['productivity', 'organization', 'planning', 'efficiency', 'workflow'],
            'health': ['health', 'wellness', 'fitness', 'nutrition', 'lifestyle'],
            'finance': ['finance', 'money', 'investing', 'budgeting', 'wealth'],
            'social media': ['social media', 'content', 'instagram', 'tiktok', 'marketing'],
            'real estate': ['real estate', 'property', 'investing', 'landlord', 'rental']
        }
        
        content_lower = content.lower()
        tags = []
        
        for category, category_tags in tag_categories.items():
            if any(word in content_lower for word in category.split()):
                tags.extend(category_tags[:3])  # Add first 3 tags from matching category
        
        # Add generic tags
        tags.extend(['PLR', 'MRR', 'digital product', 'template', 'instant download'])
        
        return list(set(tags))[:10]  # Return unique tags, max 10
    
    def _generate_description(self, title: str, topic: str) -> str:
        """
        Generate product description for marketplace listing
        """
        description_prompt = f"""
        Write a compelling product description for a PLR digital product:
        
        Title: {title}
        Topic: {topic}
        
        Include:
        - Hook that grabs attention
        - Key benefits and features
        - What's included in the package
        - PLR/MRR rights explanation
        - Call-to-action
        
        Keep it under 200 words, sales-focused, and professional.
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": description_prompt}],
                temperature=0.8,
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error generating description: {e}")
            return f"Professional PLR digital product about {topic}. Includes full resell rights and ready-to-use content."
    
    def _extract_subject_line(self, email_content: str) -> str:
        """
        Extract subject line from email template
        """
        lines = email_content.split('\n')
        for line in lines:
            if 'subject' in line.lower() and ':' in line:
                return line.split(':', 1)[1].strip()
        return "[Subject Line Not Found]"
    
    def _extract_cta(self, email_content: str) -> str:
        """
        Extract call-to-action from email template
        """
        # Simple extraction - look for common CTA patterns
        cta_patterns = ['click here', 'get started', 'buy now', 'learn more', 'sign up']
        lines = email_content.lower().split('\n')
        
        for line in lines:
            for pattern in cta_patterns:
                if pattern in line:
                    return line.strip()
        
        return "Get Started Today"

# Usage examples and batch generation
def main():
    """
    Demo the AI Product Generator
    """
    generator = AIProductGenerator()
    
    # High-profit niches for WHOP
    profitable_niches = [
        ('Personal Finance for Millennials', 'millennials'),
        ('Social Media Marketing for Small Business', 'small business owners'),
        ('Productivity Hacks for Entrepreneurs', 'entrepreneurs'),
        ('Real Estate Investment Guide', 'beginner investors'),
        ('Wellness and Self-Care Planner', 'wellness enthusiasts')
    ]
    
    print("🚀 Starting AI Product Generation...")
    
    for topic, audience in profitable_niches:
        print(f"\n📚 Generating products for: {topic}")
        
        # Generate ebook
        ebook = generator.generate_ebook(topic, audience)
        
        # Generate related Notion template
        template_type = "productivity dashboard" if "productivity" in topic.lower() else "planning template"
        notion_template = generator.generate_notion_template(template_type, topic)
        
        # Generate planner if applicable
        if any(word in topic.lower() for word in ['finance', 'wellness', 'productivity']):
            planner = generator.generate_planner_template(topic.split()[0].lower(), "monthly")
        
        print(f"✅ Products generated for {topic}")
    
    print("\n🎉 All products generated successfully!")
    print(f"📁 Check the '{generator.products_dir}' folder for your products")

if __name__ == "__main__":
    main()
