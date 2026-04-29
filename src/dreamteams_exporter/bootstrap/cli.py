import argparse

from dreamteams_exporter.bootstrap.fast_api import run_api
from dreamteams_exporter.bootstrap.faststream import run_worker


def create_parser() -> argparse.ArgumentParser:
    """Creates and configures the command-line argument parser for the exporter CLI."""
    parser = argparse.ArgumentParser(
        prog="dreamteams-exporter",
        description="dreamteams-exporter CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run api                                  # Run the internal FastAPI server
  %(prog)s run worker                               # Run the FastStream NATS worker
        """,
    )

    subparsers = parser.add_subparsers(title="commands", dest="command", help="available commands", required=True)

    run_parser = subparsers.add_parser("run", help="Run services")
    run_subparsers = run_parser.add_subparsers(dest="subcommand", help="service to run", required=True)
    run_subparsers.add_parser("api", help="Run the internal FastAPI server")
    run_subparsers.add_parser("worker", help="Run the FastStream NATS worker")

    return parser


def main() -> None:
    """Main entry point for the exporter CLI: parses arguments and dispatches to the requested command."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "run":
        if args.subcommand == "api":
            run_api()
        elif args.subcommand == "worker":
            run_worker()
        else:
            parser.error(f"Unknown run subcommand: {args.subcommand}")

    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
