#!/usr/bin/env python3
"""
Quick Launch Script - Get your WHOP automation business running in 5 minutes
Nosyt WHOP Automation System
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import time

def print_banner():
    print("""
██████╗ ██████╗ ███████╗██╗   ██╗███████╗
██╔══██╗██╔══██╗██╔════╝╚██╗ ██╔╝██╔════╝
██████╔╝██║  ██║█████╗   ╚████╔╝ █████╗  
██╔══██╗██║  ██║██╔══╝    ╚██╔╝  ██╔══╝  
██║  ██║╚██████╔╝███████╗ ██║   ███████╗
╚═╝  ╚═╝ ╚═════╝ ╚══════╝ ╚═╝   ╚══════╝

🚀 WHOP AUTOMATION SYSTEM - QUICK LAUNCHER
💰 AI-Powered Digital Product Empire
⚙️  Complete Setup in 5 Minutes
""")

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} - Compatible")

def setup_environment():
    """Setup the virtual environment and install dependencies"""
    print("\n🛠  Setting up environment...")
    
    # Create directories if they don't exist
    directories = [
        'generated_products',
        'output',
        'logs',
        'reports',
        'config'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create requirements.txt if it doesn't exist
    requirements_file = Path('requirements.txt')
    if not requirements_file.exists():
        requirements = """
openai>=1.0.0
requests>=2.28.0
schedule>=1.2.0
numpy>=1.21.0
pandas>=1.3.0
fastapi>=0.95.0
uvicorn>=0.20.0
python-dotenv>=1.0.0
aiofiles>=23.0.0
jinja2>=3.1.0
"""
        with open(requirements_file, 'w') as f:
            f.write(requirements)
        print("✅ Created requirements.txt")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: Some dependencies might not have installed correctly")
        print(f"Error: {e}")

def create_env_file():
    """Create .env file with user configuration"""
    print("\n🔑 Setting up API credentials...")
    
    env_file = Path('.env')
    
    # Check if .env already exists
    if env_file.exists():
        print("✅ Found existing .env file")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'WHOP_API_KEY' in content and 'OPENAI_API_KEY' in content:
                print("✅ API keys already configured")
                return
    
    print("\n🔑 Please provide your API credentials:")
    print("(You can always update these later in the .env file)")
    
    # Get API keys from user
    openai_key = input("\nOpenAI API Key (for AI generation): ").strip()
    whop_api_key = input("WHOP API Key (get from https://dev.whop.com): ").strip()
    whop_company_id = input("WHOP Company ID: ").strip()
    
    # Create .env content
    env_content = f"""
# Nosyt WHOP Automation - API Configuration

# OpenAI API (for AI product generation)
OPENAI_API_KEY={openai_key}

# WHOP API (for marketplace integration)
WHOP_API_KEY={whop_api_key}
WHOP_COMPANY_ID={whop_company_id}

# Optional: Webhook URL for notifications
WEBHOOK_URL=https://your-domain.com/webhook/whop

# System Settings
AUTO_GENERATE=true
AUTO_UPLOAD=true
DEBUG=false
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file with your API keys")
    print("⚠️  Keep your .env file secure and never share it publicly!")

def quick_test():
    """Run a quick test to ensure everything is working"""
    print("\n🧪 Running quick test...")
    
    try:
        # Test OpenAI import
        import openai
        print("✅ OpenAI library imported")
        
        # Test requests import
        import requests
        print("✅ Requests library imported")
        
        # Test our modules
        sys.path.append('.')
        from generators.ai_product_generator import AIProductGenerator
        from whop_api.whop_integration import WhopIntegration
        print("✅ Custom modules imported")
        
        # Test API key loading
        from dotenv import load_dotenv
        load_dotenv()
        
        if os.getenv('OPENAI_API_KEY'):
            print("✅ OpenAI API key loaded")
        else:
            print("⚠️  OpenAI API key not found in environment")
        
        if os.getenv('WHOP_API_KEY'):
            print("✅ WHOP API key loaded")
        else:
            print("⚠️  WHOP API key not found in environment")
        
        print("✅ System test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE! Your WHOP automation system is ready!")
    print("=" * 60)
    
    print("\n🚀 QUICK START OPTIONS:")
    print("\n1. 📚 Generate your first products:")
    print("   python automation/auto_launcher.py")
    print("   Choose option 1 to generate and upload products immediately")
    
    print("\n2. 🔄 Start 24/7 automation:")
    print("   python automation/auto_launcher.py")
    print("   Choose option 2 to run continuous automation")
    
    print("\n3. 📊 View web dashboard:")
    print("   Open web/dashboard.html in your browser")
    print("   Monitor your earnings and system status")
    
    print("\n💰 PROFIT TARGETS:")
    print("   Week 1-2: $500-1,500/month (PLR reselling)")
    print("   Week 3-4: $1,500-5,000/month (AI products)")
    print("   Month 2+: $5,000-15,000+/month (memberships)")
    
    print("\n🔧 CONFIGURATION:")
    print("   - Edit config/automation_config.json for settings")
    print("   - Update .env file with API keys if needed")
    print("   - Check logs/ folder for system activity")
    
    print("\n🎯 TOP PERFORMING NICHES (Based on WHOP data):")
    niches = [
        "Social Media Marketing", "Personal Finance", "Productivity",
        "Real Estate Investment", "Dropshipping", "Email Marketing",
        "Cryptocurrency", "Affiliate Marketing", "Wellness", "Time Management"
    ]
    for i, niche in enumerate(niches, 1):
        print(f"   {i:2d}. {niche}")
    
    print("\n📧 SUPPORT:")
    print("   - Documentation: ./docs/ folder")
    print("   - GitHub Issues: For bug reports")
    print("   - Email: support@nosyt.com")
    
    print("\n" + "=" * 60)
    print("🚀 Ready to build your digital product empire!")
    print("=" * 60)

def main():
    """Main launcher function"""
    print_banner()
    
    # Step 1: Check Python version
    print("🔍 Step 1: Checking Python version...")
    check_python_version()
    
    # Step 2: Setup environment
    print("\n🛠  Step 2: Setting up environment...")
    setup_environment()
    
    # Step 3: Create .env file
    print("\n🔑 Step 3: Configuring API credentials...")
    create_env_file()
    
    # Step 4: Quick test
    print("\n🧪 Step 4: Testing system...")
    if not quick_test():
        print("❌ Setup incomplete. Please check the errors above.")
        return
    
    # Step 5: Show next steps
    show_next_steps()
    
    # Ask user what they want to do
    print("\n\nWhat would you like to do now?")
    print("1. Generate products immediately")
    print("2. Start continuous automation")
    print("3. Exit and configure manually")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        print("\n🚀 Starting product generation...")
        try:
            subprocess.run([sys.executable, 'automation/auto_launcher.py'], input='1\n', text=True)
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
    elif choice == '2':
        print("\n🔄 Starting continuous automation...")
        print("Press Ctrl+C to stop")
        try:
            subprocess.run([sys.executable, 'automation/auto_launcher.py'], input='2\n', text=True)
        except KeyboardInterrupt:
            print("\n🛑 Automation stopped")
    else:
        print("\n👍 Setup complete! Run the commands above when ready.")

if __name__ == "__main__":
    main()
