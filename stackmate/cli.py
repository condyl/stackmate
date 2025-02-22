import click

@click.command()
def main():
    """Welcome to Stackmate!"""
    click.echo("Hello World")

if __name__ == "__main__":
    main() 