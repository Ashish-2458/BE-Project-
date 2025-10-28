#!/usr/bin/env python3
"""
Simple launcher for Assistive Vision System
Provides easy command-line interface
"""

import sys
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(
        description="AI-Powered Assistive Vision System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Run the main system
  python run.py --test            # Run system tests
  python run.py --setup           # Run setup/installation
  python run.py --headless        # Force headless mode
  python run.py --visual          # Force visual mode
        """
    )
    
    parser.add_argument('--test', action='store_true', 
                       help='Run system tests')
    parser.add_argument('--setup', action='store_true', 
                       help='Run setup and installation')
    parser.add_argument('--headless', action='store_true', 
                       help='Force headless mode (no visual display)')
    parser.add_argument('--visual', action='store_true', 
                       help='Force visual mode (show camera feed)')
    
    args = parser.parse_args()
    
    if args.setup:
        print("🔧 Running setup...")
        return subprocess.call([sys.executable, 'setup.py'])
    
    elif args.test:
        print("🧪 Running tests...")
        return subprocess.call([sys.executable, 'test_system.py'])
    
    else:
        # Run main system
        env = {}
        if args.headless:
            env['ASSISTIVE_VISION_MODE'] = 'headless'
        elif args.visual:
            env['ASSISTIVE_VISION_MODE'] = 'visual'
        
        print("🚀 Starting Assistive Vision System...")
        return subprocess.call([sys.executable, 'main.py'], env=env)

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)