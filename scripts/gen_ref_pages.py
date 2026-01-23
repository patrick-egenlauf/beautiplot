"""Generate the code reference pages and navigation."""

import importlib.util
import inspect
from pathlib import Path

import mkdocs_gen_files

nav = mkdocs_gen_files.Nav()

root = Path(__file__).parent.parent
src = root / 'src'

for path in sorted(src.rglob('*.py')):
    module_path = path.relative_to(src).with_suffix('')
    doc_path = path.relative_to(src).with_suffix('.md')
    full_doc_path = Path('reference', doc_path)

    parts = tuple(module_path.parts)
    module_name = '.'.join(parts)

    if parts[-1] == '__init__':
        parts = parts[:-1]
        doc_path = doc_path.with_name('index.md')
        full_doc_path = full_doc_path.with_name('index.md')
        module_name = '.'.join(parts) if parts else 'root'
        nav[parts] = doc_path.as_posix()
        with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
            ident = '.'.join(parts)
            fd.write(f'# ::: {ident}')
        mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))
        continue
    elif parts[-1] == '__main__':
        continue

    nav_parts = list(parts)
    if nav_parts[-1] == '_config':
        nav_parts[-1] = 'Configuration'

    try:
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f'Could not find spec or loader for {module_name}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        print(f'Skipping {module_name}: import failed with {e}')
        continue

    nav[tuple(nav_parts)] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, 'w') as fd:
        ident = '.'.join(parts)
        if parts[-1] == '_config':
            title = 'Configuration'
            fd.write(f'# {title}\n')
            fd.write(
                f'::: {ident}\n    options:\n      members: no\n      show_root_heading: false'
            )
        else:
            fd.write(f'# ::: {ident}\n    options:\n      members: no')

    doc_dir = Path('reference', *parts)

    # Collect local (not imported) members
    local_members = []
    for name, obj in inspect.getmembers(module):
        if (inspect.isfunction(obj) or inspect.isclass(obj)) and getattr(
            obj, '__module__', None
        ) == module_name:
            identifier = f'{module_name}.{name}'
            local_members.append((name, identifier))

            # Create a page for each function/class except for private
            # ones except _Config
            if name.startswith('_') and name != '_Config':
                continue
            obj_doc_path = (
                doc_dir / 'config.md' if name == '_Config' else doc_dir / f'{name}.md'
            )
            with mkdocs_gen_files.open(obj_doc_path, 'w') as fd:
                if name == '_Config':
                    display_name = 'Configuration Object'
                    fd.write(f'# {display_name}\n\n')
                    fd.write(
                        f'::: {identifier}\n    options:\n      show_root_heading: false\n'
                    )
                else:
                    fd.write(f'# `{identifier}`\n\n')
                    fd.write(f'::: {identifier}\n')
            mkdocs_gen_files.set_edit_path(obj_doc_path, path.relative_to(root))

            # Add function/class to nav
            nav_name = 'Configuration Object' if name == '_Config' else name
            nav[(*nav_parts, nav_name)] = obj_doc_path.relative_to(
                'reference'
            ).as_posix()

with mkdocs_gen_files.open('reference/SUMMARY.md', 'w') as nav_file:
    nav_file.writelines(nav.build_literate_nav())
