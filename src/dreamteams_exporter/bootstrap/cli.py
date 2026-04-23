import argparse


def run_worker() -> None:
    """Starts the FastStream worker subscribed to NATS subjects for export jobs."""
    raise NotImplementedError


def run_migrations() -> None:
    """Applies all pending Alembic migrations to the exporter schema."""
    raise NotImplementedError


def autogenerate_migrations(message: str) -> None:
    """Generates a new Alembic migration by detecting schema changes in the exporter models."""
    raise NotImplementedError(message)


def create_parser() -> argparse.ArgumentParser:
    """Creates and configures the command-line argument parser for the exporter CLI."""
    parser = argparse.ArgumentParser(
        prog="dreamteams-exporter",
        description="dreamteams-exporter CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run worker                               # Run the FastStream NATS worker
  %(prog)s migrations autogenerate "Add job table"  # Create migration
  %(prog)s migrations apply                         # Apply migrations
        """,
    )

    subparsers = parser.add_subparsers(title="commands", dest="command", help="available commands", required=True)

    run_parser = subparsers.add_parser("run", help="Run services")
    run_subparsers = run_parser.add_subparsers(dest="subcommand", help="service to run", required=True)
    run_subparsers.add_parser("worker", help="Run FastStream NATS worker")

    migrations_parser = subparsers.add_parser("migrations", help="Database migrations")
    migrations_subparsers = migrations_parser.add_subparsers(
        dest="subcommand",
        help="migration operation",
        required=True,
    )

    autogenerate_parser = migrations_subparsers.add_parser("autogenerate", help="Autogenerate migration")
    autogenerate_parser.add_argument("message", help="Migration message/description")

    migrations_subparsers.add_parser("apply", help="Apply migrations")

    return parser


def main() -> None:
    """Main entry point for the exporter CLI: parses arguments and dispatches to the requested command."""
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "run":
        if args.subcommand == "worker":
            run_worker()
        else:
            parser.error(f"Unknown run subcommand: {args.subcommand}")

    elif args.command == "migrations":
        if args.subcommand == "autogenerate":
            autogenerate_migrations(args.message)
        elif args.subcommand == "apply":
            run_migrations()
        else:
            parser.error(f"Unknown migrations subcommand: {args.subcommand}")

    else:
        parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
