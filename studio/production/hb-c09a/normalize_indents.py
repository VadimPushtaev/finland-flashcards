"""Normalize owned compact suites to four spaces, proving identical Python ASTs."""
from pathlib import Path
import ast
import io
import json
import tokenize

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
paths = sorted(HERE.glob('*.py'))
paths += sorted((ROOT / 'studio/episodes').glob('hb-c09-*/prepare*.py'))
report = []
for path in paths:
    source = path.read_text()
    tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    depth = 0
    mapping = {0: 0}
    protected = set()
    conflict = False
    for token in tokens:
        if token.type == tokenize.INDENT:
            depth += 1
            actual = len(token.string)
            target = 4 * depth
            if actual in mapping and mapping[actual] != target:
                conflict = True
            mapping[actual] = target
        elif token.type == tokenize.DEDENT:
            depth -= 1
        elif token.type == tokenize.STRING and token.end[0] > token.start[0]:
            protected.update(range(token.start[0] + 1, token.end[0] + 1))
    if conflict:
        report.append(dict(path=str(path.relative_to(ROOT)), status='mixed indentation left unchanged'))
        continue
    output = []
    for number, line in enumerate(source.splitlines(keepends=True), 1):
        if number not in protected and line.strip():
            prefix = len(line) - len(line.lstrip(' '))
            if prefix in mapping:
                line = ' ' * mapping[prefix] + line[prefix:]
        output.append(line)
    normalized = ''.join(output)
    assert ast.dump(ast.parse(source), include_attributes=False) == ast.dump(
        ast.parse(normalized), include_attributes=False), path
    compile(normalized, str(path), 'exec')
    if normalized != source:
        path.write_text(normalized)
        report.append(dict(path=str(path.relative_to(ROOT)), status='four-space suites; AST identical'))
(HERE / 'indent-normalization.json').write_text(json.dumps(report, indent=2) + '\n')
print('Normalized', sum(row['status'].startswith('four-space') for row in report),
      'owned helpers; semantic AST and compilation checks passed.')
