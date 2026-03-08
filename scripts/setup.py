#!/usr/bin/env python3
"""
Setup Script
Validates environment and dependencies
"""

import sys
from pathlib import Path
import subprocess


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required, found {version.major}.{version.minor}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_file():
    """Check if .env file exists"""
    print("\nChecking environment configuration...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Creating .env from .env.example...")
        
        example = Path(".env.example")
        if example.exists():
            with open(example, 'r') as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✓ .env file created")
            print("⚠️  Please edit .env and add your GEMINI_API_KEY")
            return False
        else:
            print("❌ .env.example not found")
            return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        if 'your_gemini_api_key_here' in content or 'GEMINI_API_KEY=' not in content:
            print("⚠️  GEMINI_API_KEY not configured in .env")
            print("   Please add your API key to .env file")
            return False
    
    print("✓ .env file configured")
    return True


def check_data_file():
    """Check if OKR data file exists"""
    print("\nChecking data files...")
    data_file = Path("./data/okr_samples_500.txt")
    
    if not data_file.exists():
        print(f"❌ Data file not found: {data_file}")
        return False
    
    print(f"✓ Data file found: {data_file}")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True
        )
        print("✓ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def main():
    print("=" * 80)
    print("🎯 OKR ANALYSIS SYSTEM - SETUP")
    print("=" * 80)
    print()
    
    checks = [
        check_python_version(),
        check_data_file()
    ]
    
    if not all(checks):
        print("\n❌ Setup incomplete. Please fix the issues above.")
        sys.exit(1)
    
    install_deps = input("\nInstall/update dependencies? (y/n): ").lower().strip()
    if install_deps == 'y':
        if not install_dependencies():
            sys.exit(1)
    
    env_check = check_env_file()
    
    print("\n" + "=" * 80)
    if env_check:
        print("✅ Setup complete! Ready to run analysis.")
        print("\nNext steps:")
        print("1. Run analysis: python scripts/run_analysis.py")
        print("2. View dashboard: streamlit run src/app/dashboard.py")
    else:
        print("⚠️  Setup incomplete. Please configure your GEMINI_API_KEY in .env")
        print("\nAfter adding your API key:")
        print("1. Run analysis: python scripts/run_analysis.py")
        print("2. View dashboard: streamlit run src/app/dashboard.py")
    print("=" * 80)


if __name__ == "__main__":
    main()
