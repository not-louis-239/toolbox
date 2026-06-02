# Repository Maintenance Rules
(even for myself, because I know I'm going to forget these at some point)

- `scripts/`: For single-file utilities. Must rely *only* on the language's standard library (no external dependencies).
- `projects/`: For multi-file tools or applications requiring external packages.
- `lib/`: generic shared tools across all projects

## Project Isolation Rules

Each subfolder inside `projects/` must be treated as an independent ecosystem. If applicable, it must include:
- A local `.venv/` for Python dependencies.
- A local `.gitignore` to handle project-specific secrets or data (e.g., journal entries, local file paths).
- A local dependency manifest (e.g., `requirements.txt`, `package.json`).

## Documentation & Licensing
- Global license applies to all subfolders unless a local `LICENSE` file is present.
- Root README acts as a directory; projects must maintain their own local setup READMEs.
