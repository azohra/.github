"""Prove cliff.toml and the release-draft configs implement one change table."""

import json
import re
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The table from the commit reference: which types a user can notice, and where
# the changelog files them. Internal types are skipped by both tools.
TABLE = {'feat': 'Added', 'fix': 'Fixed', 'perf': 'Performance', 'revert': 'Reverted'}
INTERNAL = {'build', 'chore', 'ci', 'docs', 'refactor', 'style', 'test'}
LABELS = {'feat': 'feature', 'fix': 'fix', 'perf': 'performance', 'revert': 'reverted'}
SECTIONS = {'Performance': 'Improved'}


def types(pattern):
    match = re.search(r'\^\(?([a-z|]+)\)?', pattern)
    return set(match.group(1).split('|')) if match else set()


def read_yaml(path):
    return json.loads(subprocess.run(['yq', '-o', 'json', str(path)],
                                    capture_output=True, text=True, check=True).stdout)


def check_cliff():
    parsers = tomllib.loads((ROOT / 'cliff.toml').read_text())['git']['commit_parsers']
    skipped = set().union(*(types(p['message']) for p in parsers if p.get('skip')))
    grouped = {t: p['group'] for p in parsers if 'group' in p for t in types(p['message'])}
    assert skipped == INTERNAL, f'cliff.toml skips {sorted(skipped)}'
    assert grouped == TABLE, f'cliff.toml groups {grouped}'
    body = tomllib.loads((ROOT / 'cliff.toml').read_text())['changelog']['body']
    for group in TABLE.values():
        assert f'"{group}"' in body, f'cliff.toml never renders {group}'


def check_drafter(path):
    config = read_yaml(path)
    labelled = {}
    for rule in config['autolabeler']:
        for pattern in rule['title']:
            for kind in types(pattern):
                labelled[kind] = rule['label']
    assert {k for k, v in labelled.items() if v == 'internal'} == INTERNAL, f'{path.name} internal types'
    assert {k: v for k, v in labelled.items() if v not in {'internal', 'breaking'}} == LABELS, f'{path.name} labels'
    excluded = [c for c in config['categories'] if c.get('type') == 'pre-exclude']
    assert [c['when']['label'] for c in excluded] == ['internal'], f'{path.name} excludes'
    shown = {c['when']['label']: c['title'] for c in config['categories'] if 'title' in c}
    expected = {LABELS[t]: SECTIONS.get(group, group) for t, group in TABLE.items()}
    assert shown == expected, f'{path.name} sections {shown}'


def main():
    check_cliff()
    for name in ('release-drafter.yml', 'release-drafter-pre-v1.yml'):
        check_drafter(ROOT / '.github' / name)
    workflow = read_yaml(ROOT / '.github/workflows/title.yml')
    label = workflow['jobs']['label']
    assert label['steps'][0]['with']['config-name'] == 'azohra/.github:release-drafter.yml@main', \
        'The shared label config must resolve to its provider across repository owners'
    assert 'needs' not in workflow['jobs']['title'], 'Labeling must not gate title validation'
    contract = json.loads((ROOT / 'shared-workflows.json').read_text())
    assert contract['path'] == '.github/workflows/conventional-pr.yml'
    caller = read_yaml(ROOT / contract['path'])
    assert caller['jobs']['title']['uses'] == './.github/workflows/title.yml'
    caller['jobs']['title']['uses'] = 'azohra/.github/.github/workflows/title.yml@main'
    assert {k: v for k, v in caller.items() if k != 'name'} == contract['workflow'], \
        'The audit contract must match the shared title caller'
    print('taxonomy: changelog, draft and shared label configuration agree')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as error:
        print(f'taxonomy: {error}', file=sys.stderr)
        sys.exit(1)
