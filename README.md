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

## Minimal Reproduceable Example

`Pseudocode/select-sort.pseudocode`:

```pseudocode
ALGORITHM SelectSort(A[0..n-1])
for i <- 0 to n - 1 do
    SmallSub = i
    for j <- i + 1 to n - 1 do
        if A[j] < A[SmallSub]
            SmallSub = j

    temp = A[i]
    A[SmallSub] = temp

return A
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
