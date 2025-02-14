import click

from .convert import convert_to_diggs


@click.command()
@click.argument("bor_input", type=click.File("rb"))
@click.option("-o", "--output", type=click.Path(writable=True, dir_okay=False), required=False)
def main(bor_input, output):
    """Convert BOR file to a DIGGS."""
    diggs_content = convert_to_diggs(bor_input)
    if not output:
        # sys.stdout.buffer
        print(diggs_content)
    else:
        with click.open_file(output, "w") as f:
            f.write(diggs_content)


if __name__ == "__main__":
    main()
