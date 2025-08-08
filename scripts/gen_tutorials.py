import pathlib  # noqa: D100
import re

import mkdocs_gen_files

tutorial_dir = pathlib.Path('examples')
output_dir = pathlib.Path('tutorials')  # This is inside `docs/` in the built site

with mkdocs_gen_files.open(output_dir / 'index.md', 'w') as f:
    f.write('# Tutorials\n\n')
    f.write(
        'Here you can find all tutorials on how to use the package '
        'and its different functionalities.\n\n'
    )
    f.write('## List of Tutorials\n\n')

with mkdocs_gen_files.open(output_dir / 'SUMMARY.md', 'w') as f:
    f.write('- [](index.md)\n')

for path in sorted(tutorial_dir.glob('*.py')):
    lines = path.read_text().splitlines()
    md_lines = []

    in_code = False
    first_line = True
    for line in lines:
        if line.strip().startswith('#'):
            if first_line:
                title = line.split('#', 2)[-1].strip()
                first_line = False
            if in_code:
                md_lines.append('```')
                md_lines.append('')
                in_code = False
            md_lines.append(re.sub(r'^#\s?', '', line))
        else:
            if not in_code:
                md_lines.append('')
                md_lines.append('``` { .python .copy }')
                in_code = True
            md_lines.append(line)
    if in_code:
        md_lines.append('```')

    # Write virtual markdown file
    md_path = output_dir / f'{path.stem}.md'
    with mkdocs_gen_files.open(md_path, 'w') as f:
        f.write('\n'.join(md_lines))

    with mkdocs_gen_files.open(output_dir / 'SUMMARY.md', 'a') as f:
        f.write(f'  - [{title}]({md_path.name})\n')

    with mkdocs_gen_files.open(output_dir / 'index.md', 'a') as f:
        f.write(f'- [{title}]({md_path.name})\n')
