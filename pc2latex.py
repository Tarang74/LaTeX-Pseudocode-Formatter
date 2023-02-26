from pygments.lexer import RegexLexer, words, include, bygroups
from pygments.token import Keyword, Number, Name, Whitespace, Comment, Operator, Punctuation


class PseudocodeLexer(RegexLexer):
    """
    A Pygments lexer for the pseudocode syntax.
    """
    name = "PseudocodeLexer"
    alias = ["pseudocode", "pseudo"]
    filenames = ["*.pseudocode"]
    mimetypes = []

    ops = words(["**", "!=", "==", "<=", ">=", "<-", "!", "*", "/", "%", "+", "-", "<", ">"])

    keywords = words([
        "if", "else", "while", "repeat", "for", "to", "do", "return"
    ], suffix=r"\b")

    tokens = {
        "special": [
            (r"\d+", Number.Integer),
            (r"\d*\.\d+", Number.Float),
            (r"(true|false)\b", Name.Builtin)
        ],
        "whitespace-comment": [
            (r"\s+", Whitespace),
            (r"(//)(.*?)$", bygroups(Punctuation, Comment.Singleline))
        ],
        "identifiers": [
            (r"\b[A-Z]+\b", Name.Variable),
            (r"[a-z]+", Name.Variable)
        ],
        "root": [
            include("special"),
            include("whitespace-comment"),
            (r"ALGORITHM", Name.Label),
            (keywords, Keyword),
            include("identifiers"),
            (ops, Operator),
            (r"\.{3}|[\[\](){},.]", Punctuation)
        ]
    }


def style_text(s: str, style: str) -> str:
    """
    Applies the given style to the given text and returns the formatted string.
    """
    if style == "bold":
        return f"\\textbf{{{s}}}"
    elif style == "italics":
        return f"\\textit{{{s}}}"
    elif style == "sans":
        return f"\\textsf{{{s}}}"
    else:
        return s


TAB_SIZE = 4

def pseudocode_to_latex(filename: str):
    operators = {
        r"**": "\\ast\\ast",
        r"!=": "\\neq",
        r"==": "\\eq",
        r"<=": "\\leq",
        r">=": "\\geq",
        r"<-": "\\leftarrow",
        r"!": "\neg",
        r"*": "\\ast",
        r"/": "\\div",
        r"%": "\\percent",
        r"+": "+",
        r"-": "-",
        r"<": "<",
        r">": ">",
    }

    punctuation = {
        "(": r"\left( ",
        ")": r" \right)",
        "[": r"\left[ \,",
        "]": r"\, \right]",
        ",": r",\:",
        "...": r"\dots",
        ".": r".",
        "//": r"\mathbin{/\mkern-3mu/} \text{",
    }

    with open(filename, "r") as f:
        code = f.read()

    lexer = PseudocodeLexer()

    formatted = "\\begin{fleqn}\n\t\\begin{align*}\n\t\t& "

    tokens = lexer.get_tokens_unprocessed(code)
    final_idx = list(tokens)[-1][0]

    for (idx, tokenType, text) in lexer.get_tokens_unprocessed(code):
        text_to_add = ""
        if tokenType is Whitespace:
            if "\n" in text:
                if idx != final_idx:
                    text_to_add = f" \\\\\n\t\t& "
                else:
                    text_to_add = text
            else:
                text_to_add = text

            extra_whitespace = text.split("\n")[-1]
            if extra_whitespace:
                text_to_add += r'\qquad ' * (len(extra_whitespace) // TAB_SIZE)
        elif tokenType is Comment.Singleline:
            text_to_add = text + r"}"
        elif tokenType is Name.Label:
            if text == "ALGORITHM":
                text = style_text(text, "sans")
                text = style_text(text, "bold")
                text_to_add = f"\\text{{{text}}} \\"
        elif tokenType is Punctuation and text in punctuation:
            text_to_add = punctuation[text]
        elif tokenType is Operator:
            text_to_add = operators[text]
        elif tokenType is Keyword:
            # If not start of line
            if not formatted.endswith("& ") and not formatted.endswith(
                    "\\qquad "):
                text_to_add = "\\ "
            text_to_add += f"\\text{{\\textbf{{{text}}}}} \\"
        else:
            text_to_add = text

        formatted += text_to_add

    formatted += "\t\\end{align*}\n\\end{fleqn}"

    return formatted


import sys
import os

if len(sys.argv) < 3:
    print(
        f"Usage: python {os.path.basename(__file__)} <file extension> <filename | folder> [filename | folder]...")
    sys.exit(0)

if len(sys.argv) == 3 and any(sys.argv[2] == h for h in ["-h", "--help", "/?", "/help", "-man", "/h", "/help", "-?"]):
    print(
        f"Usage: python {os.path.basename(__file__)} <file extension> <filename | folder> [filename | folder]...")
    print("View on GitHub: https://github.com/Tarang74/Pseudocode-to-LaTeX")
    sys.exit(0)



def process_file(input_file):
    output_file = os.path.splitext(input_file)[0] + ".tex"
    formatted_latex = pseudocode_to_latex(input_file)
    with open(output_file, "w") as f:
        f.write(formatted_latex)


file_ext = sys.argv[1]
input_paths = sys.argv[2:]

# Collect all the input files
input_files = []
for input_path in input_paths:
    if os.path.isdir(input_path):
        for root, dirs, files in os.walk(input_path):
            for file in files:
                if file.endswith(f".{file_ext}"):
                    input_files.append(os.path.join(root, file))
    elif os.path.isfile(input_path) and input_path.endswith(f".{file_ext}"):
        input_files.append(input_path)
    else:
        print(
            f"Warning: {input_path} is not a valid file or directory")

# Process each input file
for input_file in input_files:
    process_file(input_file)
