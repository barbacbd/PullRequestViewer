"""
MIT License

Copyright (c) 2024 Brent Barbachem

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import argparse
from .config import create_config
from .report import build_report


def main():
    """Main execution point."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--config',
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        '--coordinate_with_jira',
        action=argparse.BooleanOptionalAction
    )
    parser.add_argument(
        "--input",
        dest="input_file",
        default="config.yaml",
        help="configuration yaml file"
    )
    parser.add_argument(
        "--output",
        dest="output_file",
        default="github.xlsx",
        help="output excel file"
    )
    args = parser.parse_args()

    if args.config:
        create_config(args.input_file, args.coordinate_with_jira)

    build_report(args.input_file, args.output_file)


if __name__ == '__main__':
    main()
