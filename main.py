import json
import argparse
from pipeline import generate_daily_briefing

def main():
    parser = argparse.ArgumentParser(description="Telecom Operations System Demo")
    parser.add_argument("--role", type=str, default="Fleet Manager", 
                        help="Role for the briefing (Fleet Manager, NOC Analyst, Operations Head)")
    args = parser.parse_args()
    
    # Run the unified pipeline
    result = generate_daily_briefing(role=args.role)
    
    if result["status"] == "success":
        print("\n" + "=" * 60)
        print(f"TELECOM OPERATIONS DAILY BRIEFING - ROLE: {result['role']}")
        print("=" * 60)
        print(result["briefing"])
        print("=" * 60)
        
        # Optionally show the structured data (for debugging/dev)
        # print("\nStructured Data (Top 3 Priorities):")
        # print(json.dumps(result["top_priorities"], indent=2))
    else:
        print(f"PIPELINE ERROR: {result['message']}")

if __name__ == "__main__":
    main()
