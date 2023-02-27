# Pseudocode to LaTeX

This repository provides a script to format Pseudocode using LaTeX.

## Requirements

### Programs

- [Python](https://www.python.org/downloads/)
- [LaTeX](https://www.latex-project.org/get/)

### Packages

For Python:

- [Pygments](https://pypi.org/project/Pygments/) --- For code tokenisation

For LaTeX:

- [nccmath](https://ctan.org/pkg/nccmath) --- For page alignment in math mode

## Usage

The provided script requires the user to specify a file extension and accepts both files or folders.

```bash
python pc2latex.py <file extension> <file | folder> [files | folders]...
```

This will generate a file within the same directory as the specified file with the `.tex` extension.

To optimise workflow, execute the above command within LaTeX by adding the following line in the documents preamble.

```tex
\immediate\write18{<command>}
```

where `<command>` is the shell command used above.

## Pseudocode Conventions

Only a select few keywords are recognised and all other words are treated as variables.
Operators and most symbols are automatically converted to their LaTeX macros.

For labelled braces (see the example), use the following syntax.

```bash
# At the end of the pseudocode file

# Right brace spanning multiple lines
:{<start line number>:<end line number>}<LaTeX>

# Right brace spanning a single line
:{<line number>}<LaTeX>
```

Intersection of ranges is not supported and encapsulating ranges must be placed after all inner ranges.

## Minimal Reproduceable Example

`Pseudocode/select-sort.pseudocode`:

```pseudocode
ALGORITHM SelectSort(A[0..n-1])
// Selection sort algorithm
for i <- 0 to n - 1 do
    SmallSub = i
    for j <- i + 1 to n - 1 do
        if A[j] < A[SmallSub]
            SmallSub = j

    temp = A[i]
    A[SmallSub] = temp

return A
:{6:7}O\left( 1 \right)
:{5:7}O\left( n \right)
:{3:10}O\left( n^2 \right)
```

Command-line (produces `.tex` file):

```bash
python pc2latex.py pseudocode Pseudocode/select-sort.pseudocode
```

Within LaTeX:

```tex
%!TEX TS-program = xelatex
%!TEX options = -aux-directory=aux -shell-escape -interaction=nonstopmode -synctex=1 "%DOC%"
\documentclass{article}
\usepackage{nccmath}

\immediate\write18{python pc2latex.py pseudocode Pseudocode/select-sort.pseudocode}

\begin{document}
\input{Pseudocode/select-sort.tex}
\end{document}
```

![Example output](example.png)
