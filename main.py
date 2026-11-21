"""Command-line entry point for the market research generator.

The complete CrewAI workflow will be implemented in later milestones.
"""
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Multi-Agent Market Research & Report Generator"
    )
    parser.add_argument(
        "--query",
        required=True,
        help='Research topic, for example: "Tech Sector Q3 Analysis"',
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print("Project scaffold is ready.")
    print(f"Requested research query: {args.query}")
    print("The research workflow will be added in a later milestone.")


if __name__ == "__main__":
    main()
