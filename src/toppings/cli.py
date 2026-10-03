import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="toppings", description="Digitise Granny Topping's recipe cards.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("preprocess", help="deskew, crop and clean up scans in data/scans/")
    commands.add_parser("transcribe", help="transcribe processed cards with Claude (Message Batches API)")
    review = commands.add_parser("review", help="open the review web app")
    review.add_argument("--port", type=int, default=8000)
    commands.add_parser("export", help="render approved recipes to output/cookbook.html")
    args = parser.parse_args()

    if args.command == "preprocess":
        from toppings import preprocess

        preprocess.run()
    elif args.command == "transcribe":
        from toppings import transcribe

        transcribe.run()
    elif args.command == "review":
        from toppings import review

        review.run(port=args.port)
    elif args.command == "export":
        from toppings import export

        export.run()
