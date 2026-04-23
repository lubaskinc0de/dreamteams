import argparse
import contextlib

import alembic.config

from dreamteams_exporter.adapters.db.alembic.config import get_alembic_config_path
from dreamteams_exporter.bootstrap.fast_api import run_api
from dreamteams_exporter.bootstrap.faststream import run_worker


def run_migrations() -> None:
    """Applies all pending Alembic migrations to the exporter schema."""
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(argv=["-c", alembic_path, "upgrade", "head"])

    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


def autogenerate_migrations(message: str) -> None:
    """Generates a new Alembic migration by detecting schema changes in the exporter models."""
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(argv=["-c", alembic_path, "revision", "--autogenerate", "-m", message])

    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


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
  %(prog)s migrations autogenerate "Add job table"  # Create migration
  %(prog)s migrations apply                         # Apply migrations
        """,
    )

    subparsers = parser.add_subparsers(title="commands", dest="command", help="available commands", required=True)

    run_parser = subparsers.add_parser("run", help="Run services")
    run_subparsers = run_parser.add_subparsers(dest="subcommand", help="service to run", required=True)
    run_subparsers.add_parser("api", help="Run the internal FastAPI server")
    run_subparsers.add_parser("worker", help="Run the FastStream NATS worker")

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
        if args.subcommand == "api":
            run_api()
        elif args.subcommand == "worker":
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
