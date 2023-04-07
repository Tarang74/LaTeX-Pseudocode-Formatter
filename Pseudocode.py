from pygments.lexer import RegexLexer, words, include, bygroups
from pygments.formatter import Formatter

from pygments.token import Token, Keyword, Number, Name, Whitespace, Operator, Punctuation, Whitespace, Text

CustomComment = Token.CustomComment
CustomCommentPrefix = Token.CustomComment.Prefix
CustomCommentText = Token.CustomComment.Text

Math = Token.Math
MathDelimiter = Math.Delimiter
MathText = Math.Text

Algorithm = Token.Algorithm
AlgorithmName = Algorithm.Name
AlgorithmKeyword = Algorithm.Keyword


__all__ = [
    "PseudocodeLexer",
    "PseudocodeFormatter",
    "format_pseudocode"
]


class PseudocodeLexer(RegexLexer):
    """
    A Pygments lexer for the pseudocode syntax.
    """
    name = "PseudocodeLexer"
    alias = ["pseudocode", "pseudo"]
    filenames = ["*.pseudocode"]
    mimetypes = []

    ops = words(["**", "!=", "==", "<=", ">=", "<-",
                "!", "*", "/", "%", "+", "-", "<", ">"])

    keywords = words(
        ["if", "else", "while", "repeat", "for", "to", "do", "return",
         "until", "then"],
        prefix=r"\b", suffix=r"\b")

    tokens = {
        "special": [
            (r"\d+", Number.Integer),
            (r"\d*\.\d+", Number.Float),
            (r"(true|false)\b", Name.Builtin)
        ],
        "math": [
            (ops, Operator),
            (r"[^$]+", MathText),
            (r"\$", MathDelimiter, "#pop")
        ],
        "comment": [
            (r"\n", Whitespace, "#pop"),
            (r".*", CustomCommentText)
        ],
        "root": [
            (r"(ALGORITHM)(\s*)(\w*)", bygroups(AlgorithmKeyword, Whitespace, AlgorithmName)),
            (keywords, Keyword),
            (r"(//)(.*?)(\$)", bygroups(CustomCommentPrefix, CustomCommentText, MathDelimiter), ("comment", "math")),
            (r"(//)(.*)", bygroups(CustomCommentPrefix, CustomCommentText), "comment"),
            (r"\$", MathDelimiter, "math"),
            include("special"),
            (r"[\[\](){},.;]", Punctuation),
            (r"[A-Za-z]+", Text),
            (r"\s+", Whitespace)
        ]
    }


class PseudocodeFormatter(Formatter):
    escape_character = "?"

    def __init__(self, **options):
        Formatter.__init__(self, **options)

        # Custom styles
        self.styles = {
            MathDelimiter: ("", ""),
            MathText: (f"{self.escape_character}\\(", f"\\){self.escape_character}"),
            AlgorithmKeyword: (f"{self.escape_character}\\sffamily{{\\textbf{{", f"}}}}{self.escape_character}"),
            AlgorithmName: (f"{self.escape_character}\\textit{{", f"}}{self.escape_character}"),
            CustomCommentPrefix: ("", ""),
            CustomCommentText: (f"{self.escape_character}", f"{self.escape_character}"),
        }

        for token, style in self.style:
            start = end = ""

            if style['bold']:
                start += self.escape_character
                start += r"\textbf{"
                end += r"}"
                end += self.escape_character
            if style['italic']:
                start += self.escape_character
                start += r"\textit{"
                end += r"}"
                end += self.escape_character
            if style['underline']:
                start += self.escape_character
                start += r"\underline{"
                end += r"}"
                end += self.escape_character

            self.styles[token] = (start, end)

    def format(self, tokensource, outfile):
        lastval = ""
        lasttype = None

        outfile.write(
            f"\\begin{{minted}}[escapeinside={self.escape_character * 2}, fontfamily=lmr]{{text}}")
        outfile.write("\n")

        for ttype, value in tokensource:
            while ttype not in self.styles:
                print(ttype)
                ttype = ttype.parent

            if ttype == lasttype:
                lastval += value
            else:
                if lastval:
                    if all(
                            [lasttype != skip for skip in [MathDelimiter]]):
                        stylebegin, styleend = self.styles[lasttype]

                        if lasttype == CustomCommentPrefix:
                            outfile.write("?/\\!/?")
                        else:
                            outfile.write(
                                stylebegin + lastval + styleend)

                lastval = value
                lasttype = ttype

        outfile.write("\n")
        outfile.write(r"\end{minted}")


from pygments import highlight
import os
import sys
import pathlib
import re

DEBUG = True
DEBUG_DIRECTORY = "aux"
BRACE_THICKNESS = "1.25"


def format_pseudocode(pseudocode: str, filename: str) -> str:
    # Brace horizontal shift
    horz_shift = "0.0"
    level_offsets = {}

    # Look from bottom of file
    for line in reversed(pseudocode.split("\n")):
        if line != "":
            if re.search(
                r"(?<=>)\{(\d+(?:\.\d+)?)\}\{?((?:\d+\.?\d*,? *)*)\}?$",
                    line):
                search = re.search(
                    r"(?<=>)\{(\d+(?:\.\d+)?)\}\{?((?:\d+\.?\d*,? *)*)\}?$",
                    pseudocode)
                horz_shift = search.groups()[0]

                cumulative_offset = 0.0
                for i, x in enumerate(
                        search.groups()[1].strip(" ").split(",")):
                    level_offsets[i + 1] = float(x) + cumulative_offset
                    cumulative_offset += float(x)

                # Delete lines
                pseudocode = pseudocode[:search.span()[0] - 1]
                break

    # Split brace definitions
    use_brace = False

    # Look from bottom of file
    for line in reversed(pseudocode.split("\n")):
        if line != "":
            if re.search(r"(?<=\:)\{(\d+)\}\{(\d+):(\d+)\}(.*)", line):
                use_brace = True
                break

    if use_brace and not level_offsets:
        raise AttributeError(
            "No horizontal offsets provided in pseudocode file.")


    brace_definitions = []

    if use_brace:
        matches = re.finditer(
            r"(?<=\:)\{(\d+)\}\{(\d+):(\d+)\}(.*)", pseudocode)
        found_first_match = False
        for match in matches:
            brace_definitions.append(match.groups())

            # Remove brace definitions from code
            if not found_first_match:
                pseudocode = pseudocode[:match.span()[0] - 1]
                found_first_match = True

    # Save lexer information
    if DEBUG:
        from pygments import lex

        lex_path = pathlib.Path(
            f"{DEBUG_DIRECTORY}/Pseudocode/{filename}.lex")
        lex_path.parent.mkdir(exist_ok=True)

        with lex_path.open("w") as f:
            for token in lex(pseudocode, PseudocodeLexer()):
                f.write(repr(token))
                f.write("\n")

    # Spaces/special characters/numbers are not allowed in file name
    if re.search(r"[0-9]", filename):
        raise Exception("Input filenames should not contain numbers.")

    filename = re.sub(r"[^a-zA-Z]", "", filename)

    # Generate formatted text
    formatted_lines = highlight(
        pseudocode, PseudocodeLexer(),
        PseudocodeFormatter()).split("\n")

    # Keep track of lines where marker has already been added
    markers = set({})

    tikzpicture = ""

    if use_brace:
        tikzpicture = "\\begin{tikzpicture}[remember picture,overlay]\n"

        # Get coordinate of first and second line to determine
        # line spacing and y-coordinate of first line
        marker1 = f"{filename}L{1}"
        marker2 = f"{filename}L{2}"

        formatted_lines[1] = f"{formatted_lines[1]}?\\tikzmark[{marker1}]{{{marker1}}}?"
        formatted_lines[2] = f"{formatted_lines[2]}?\\tikzmark[{marker2}]{{{marker2}}}?"

        markers.add(marker1)
        markers.add(marker2)

        base_x_coord = f"\\coordinate ({filename}BASEX) at ({horz_shift}, 0);\n"
        tikzpicture += base_x_coord

        # halfway between marker1 & marker2
        tikzpicture += f"\\draw ({{pic cs:{marker1}}}-|{filename}BASEX) coordinate ({filename}A);\n"
        tikzpicture += f"\\draw ({{pic cs:{marker2}}}-|{filename}BASEX) coordinate ({filename}B);\n"

        line_distance = f"""\\tikzmath{{coordinate \\{filename}DVEC;
    \\{filename}DVEC = ({filename}A)-({filename}B);
    \\{filename}D = (\\{filename}DVECy);
    \\{filename}D = \\convertto{{cm}}{{\\{filename}D pt}};
}}\n"""

        tikzpicture += line_distance

        del marker1, marker2

        # Store last horizontal offset in case length of provided list is too small
        prev_level_offset = 0

        # Add tikzmarkers on relevant lines
        for (level, start, end, label) in brace_definitions:
            level = int(level)
            start = int(start)
            end = int(end)

            draw = ""

            level_offset = 0
            if level > 0:
                # If fewer offsets are provided, use provided offsets and add last offset (levels - len(level_offsets)) times
                if level not in level_offsets.keys():
                    available = len(level_offsets.values())
                    missing = level - available

                    level_offset = sum(level_offsets.values())
                    level_offset += missing * level_offsets[available]
                else:
                    level_offset = level_offsets[level]

            # L: line
            if start != end:
                marker1 = f"{filename}L{start}"
                marker2 = f"{filename}L{end}"

                if marker1 not in markers:
                    formatted_lines[start] = f"{formatted_lines[start]}?\\tikzmark{{{marker1}}}?"
                    markers.add(marker1)

                if marker2 not in markers:
                    formatted_lines[end] = f"{formatted_lines[end]}?\\tikzmark{{{marker2}}}?"
                    markers.add(marker2)
            else:
                marker = f"{filename}L{start}"

                if marker not in markers:
                    formatted_lines[start] = f"{formatted_lines[start]}?\\tikzmark{{{marker}}}?"
                    markers.add(marker)

            # Draw command
            draw = f"\\draw ({filename}A) ++ ({level_offset}, {{0.75cm*\\{filename}D}}) "

            # Draw brace top to bottom
            draw += f"""[decorate, decoration = {{calligraphic brace, amplitude=5pt}}, line width={BRACE_THICKNESS}pt]
++ (0, {{-{start-1}*\\{filename}D}}) --++ (0, {{-{end-start+1}*\\{filename}D}})"""

            # Label
            draw += f" node [black,midway,xshift=0.2cm,anchor=west] {{{label}}}"

            tikzpicture += draw + ";\n"
        tikzpicture += "\\end{tikzpicture}"

    formatted = "\n".join(formatted_lines)

    if use_brace:
        return formatted + "\n" + tikzpicture
    else:
        return formatted


if len(sys.argv) < 2:
    if False:
        with open("Pseudocode/select-sort.pseudocode", "r") as f:
            print(format_pseudocode(f.read(), "select-sort"))
        quit()
    else:
        print(
            f"Usage: python {os.path.basename(__file__)} <filename | folder> [filename | folder]...")
        sys.exit(0)

help_commands = ["-h", "--help", "/?",
                 "/help", "-man", "/h", "/help", "-?"]

if len(sys.argv) == 1 and any(sys.argv[2] == h for h in help_commands):
    print(
        f"Usage: python {os.path.basename(__file__)} <filename | folder> [filename | folder]...")
    print("View on GitHub: https://github.com/Tarang74/Pseudocode-to-LaTeX")
    sys.exit(0)


def process_file(input_file):
    output_file = os.path.splitext(input_file)[0] + ".tex"
    with open(input_file, "r") as f:
        formatted_latex = format_pseudocode(
            f.read(), pathlib.Path(os.path.splitext(input_file)[0]).stem)
    with open(output_file, "w") as f:
        f.write(formatted_latex)


file_exts = ['pseudo', 'pseudocode']
input_paths = sys.argv[1:]

# Collect all the input files
input_files = []
for input_path in input_paths:
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if any(
                    [file.endswith(f".{file_ext}")
                     for file_ext in file_exts]):
                    input_files.append(os.path.join(root, file))
    elif os.path.isfile(input_path) and any([input_path.endswith(f".{file_ext}") for file_ext in file_exts]):
        input_files.append(input_path)
    else:
        print(
            f"Warning: {input_path} is not a valid file or directory")

# Process each input file
for input_file in input_files:
    process_file(input_file)
