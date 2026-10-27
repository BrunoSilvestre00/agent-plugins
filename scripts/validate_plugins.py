"""Check both package layouts and optionally install them in a disposable Codex home.

Usage: python scripts/validate_plugins.py [--codex] [--claude]
Uses the standard library only. Does not change the user's Codex configuration.
"""

import argparse
import json
import os
from pathlib import Path
import queue
import re
import shutil
import subprocess
import tempfile
import threading
import time

ROOT = Path(__file__).resolve().parents[1]


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def package_path(root, value):
    assert value.startswith('./'), f'Package path must start with ./: {value}'
    assert '..' not in Path(value).parts, f'Parent traversal: {value}'
    path = (root / value).resolve()
    assert path.is_relative_to(root.resolve()) and path.exists(), f'Missing package resource: {path}'
    return path


def frontmatter(path):
    text = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\n(.+?)\n---\n', text, re.S)
    assert match, f'Missing frontmatter: {path}'
    # These packages use scalar fields, folded descriptions and metadata.
    keys = set(re.findall(r'^([a-z-]+):', match[1], re.M))
    assert {'name', 'description'} <= keys, f'Missing skill identity: {path}'
    assert keys <= {'name', 'description', 'metadata', 'license', 'allowed-tools'}, f'Unsupported fields: {path}: {keys}'
    name = re.search(r'^name: (.+)$', match[1], re.M)[1]
    assert re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) and len(name) < 64, f'Invalid skill name: {name}'
    assert path.parent.name == name, f'Folder/name mismatch: {path}'
    return name


def check_links(plugin, path):
    text = path.read_text(encoding='utf-8')
    for target in re.findall(r'\]\(([^)]+)\)', text):
        if '://' in target or target.startswith('#') or '<' in target:
            continue
        resolved = (path.parent / target.split('#')[0]).resolve()
        assert resolved.is_relative_to(plugin.resolve()), f'Reference escapes package: {path}: {target}'
        assert resolved.exists(), f'Broken reference: {path}: {target}'


def validate():
    claude_market = read_json(ROOT / '.claude-plugin/marketplace.json')
    codex_market = read_json(ROOT / '.agents/plugins/marketplace.json')
    assert claude_market['name'] == codex_market['name']
    claude_entries = {entry['name']: entry for entry in claude_market['plugins']}
    codex_entries = {entry['name']: entry for entry in codex_market['plugins']}
    assert claude_entries.keys() == codex_entries.keys()
    all_names = set()
    command_count = 0
    shared_runtime = (ROOT / 'plugins/dev-patterns/references/runtime.md').read_text(encoding='utf-8').strip()
    for name, entry in claude_entries.items():
        plugin = package_path(ROOT, entry['source'])
        source = codex_entries[name]['source']
        assert source['source'] == 'local'
        assert package_path(ROOT, source['path']) == plugin
        assert codex_entries[name]['policy']['installation'] == 'AVAILABLE'
        assert codex_entries[name]['policy']['authentication'] in {'ON_INSTALL', 'ON_USE'}
        assert codex_entries[name]['category']
        claude = read_json(plugin / '.claude-plugin/plugin.json')
        codex = read_json(plugin / '.codex-plugin/plugin.json')
        assert claude['name'] == codex['name'] == name
        assert claude['version'] == codex['version'] == entry['version']
        assert codex['interface']['displayName'] and codex['interface']['shortDescription']
        assert (plugin / 'references/runtime.md').read_text(encoding='utf-8').startswith(shared_runtime), f'Shared runtime drift: {name}'
        skills = package_path(plugin, codex['skills'])
        for skill in skills.glob('*/SKILL.md'):
            skill_name = frontmatter(skill)
            assert skill_name not in all_names, f'Ambiguous skill: {skill_name}'
            all_names.add(skill_name)
        for command in (plugin / 'commands').glob('*.md'):
            skill = skills / f'{name}-{command.stem}' / 'SKILL.md'
            assert skill.exists(), f'Command without portable entry: {command}'
            assert f'{name}-{command.stem}' in command.read_text(encoding='utf-8')
            command_count += 1
        # Verify all new entrypoint/workflow/runtime links stay inside the installed plugin.
        paths = list((plugin / 'references').rglob('*.md'))
        paths += list((plugin / 'commands').glob('*.md'))
        paths += list((plugin / 'agents').glob('*.md'))
        paths += list(skills.rglob('*.md'))
        for path in paths:
            check_links(plugin, path)
        if name != 'dev-patterns':
            mcp = read_json(package_path(plugin, codex['mcpServers']))
            server = mcp['mcpServers']['atlassian']
            assert server == {'type': 'http', 'url': 'https://mcp.atlassian.com/v1/mcp'}
        for workflow in skills.glob('*/references/workflow.md'):
            content = workflow.read_text(encoding='utf-8')
            assert '$ARGUMENTS' not in content and '$1' not in content, f'Host-specific interpolation: {workflow}'
    for role in ('architect', 'implementer', 'verifier'):
        plugin = ROOT / 'plugins/dev-toolkit'
        assert (plugin / f'references/roles/{role}.md').exists()
        assert f'roles/{role}.md' in (plugin / f'agents/{role}.md').read_text(encoding='utf-8')
    print(f'Validated {len(claude_entries)} plugins, {len(all_names)} skills and {command_count} command adapters.')
    return claude_market['name'], list(claude_entries)


def codex_smoke(marketplace, plugins):
    executable = shutil.which('codex')
    assert executable, 'Codex CLI is required for --codex'
    # Temp home isolates cache and settings; no account credentials are copied.
    with tempfile.TemporaryDirectory(prefix='agent-plugins-codex-') as temp:
        temporary_root = Path(temp).resolve()
        assert temporary_root.parent == Path(tempfile.gettempdir()).resolve()
        assert temporary_root.name.startswith('agent-plugins-codex-')
        env = os.environ.copy()
        env['CODEX_HOME'] = temp

        def run(*args):
            result = subprocess.run([executable, *args], cwd=ROOT, env=env,
                                    capture_output=True, text=True, encoding='utf-8', timeout=45)
            assert result.returncode == 0, f'codex {args}:\n{result.stdout}\n{result.stderr}'
            return result.stdout

        print(run('--version').strip())
        run('plugin', 'marketplace', 'add', str(ROOT), '--json')
        for plugin in plugins:
            output = json.loads(run('plugin', 'add', f'{plugin}@{marketplace}', '--json'))
            print(f'Installed {plugin} in disposable CODEX_HOME: {json.dumps(output, ensure_ascii=False)}')
        listing = json.loads(run('plugin', 'list', '--marketplace', marketplace, '--json'))
        # Check cache contents, independently of the CLI's response field names.
        cache = Path(temp) / 'plugins/cache' / marketplace
        expected_skills = set()
        for plugin in plugins:
            copies = list((cache / plugin).glob('*/.codex-plugin/plugin.json'))
            assert copies, f'Plugin missing from installed cache: {plugin}'
            root = copies[0].parents[1]
            assert list((root / 'skills').glob('*/SKILL.md')), f'Installed skills missing: {plugin}'
            for path in (root / 'skills').rglob('SKILL.md'):
                check_links(root, path)
                expected_skills.add(f'{plugin}:{frontmatter(path)}')
        assert listing, 'Empty installed-plugin listing'
        consumer = Path(temp) / 'consumer'
        consumer.mkdir()
        discover_skills(executable, env, consumer, expected_skills)
        print('Codex install/list/cache/skill-discovery smoke test passed; no Jira or GitHub actions performed.')


def discover_skills(executable, env, consumer, expected_skills):
    """Ask the actual Codex skill loader, without a model turn or credentials."""
    messages = queue.Queue()
    with tempfile.TemporaryFile(mode='w+', encoding='utf-8') as errors:
        process = subprocess.Popen([executable, 'app-server', '--listen', 'stdio://'],
                                   cwd=consumer, env=env, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=errors,
                                   text=True, encoding='utf-8')

        def receive():
            for line in process.stdout:
                messages.put(json.loads(line))

        reader = threading.Thread(target=receive, daemon=True)
        reader.start()

        def send(message):
            process.stdin.write(json.dumps(message) + '\n')
            process.stdin.flush()

        def response(request_id):
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    message = messages.get(timeout=max(0.1, deadline - time.monotonic()))
                except queue.Empty:
                    break
                if message.get('id') == request_id:
                    assert 'error' not in message, message
                    return message['result']
            errors.seek(0)
            raise AssertionError(f'Codex app-server did not answer request {request_id}: {errors.read()}')

        try:
            send({'id': 1, 'method': 'initialize', 'params': {
                'clientInfo': {'name': 'agent_plugins_validation', 'title': 'Plugin validation', 'version': '1.0.0'},
                'capabilities': {'experimentalApi': True}}})
            response(1)
            send({'method': 'initialized', 'params': {}})
            send({'id': 2, 'method': 'skills/list', 'params': {'cwds': [str(consumer)], 'forceReload': True}})
            result = response(2)
            entries = result['data']
            failures = [error for entry in entries for error in entry.get('errors', [])]
            assert not failures, f'Skill loader errors: {failures}'
            loaded = {skill['name'] for entry in entries for skill in entry['skills'] if skill.get('enabled', True)}
            assert expected_skills <= loaded, f'Skills missing from Codex runtime: {sorted(expected_skills - loaded)}'
            print(f'Codex runtime discovered all {len(expected_skills)} installed skills in a clean consumer directory.')
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)
            reader.join(timeout=2)
            process.stdin.close()
            process.stdout.close()


def claude_smoke(plugins):
    """Validate manifests and load component inventories without a model turn."""
    executable = shutil.which('claude')
    if not executable:
        native_install = Path.home() / '.local/bin/claude.exe'
        if native_install.is_file():
            executable = str(native_install)
    assert executable, 'Claude Code CLI is required for --claude'

    def run(*args):
        result = subprocess.run([executable, *args], cwd=ROOT, capture_output=True,
                                text=True, encoding='utf-8', timeout=45)
        assert result.returncode == 0, f'claude {args}:\n{result.stdout}\n{result.stderr}'
        return result.stdout

    print(run('--version').strip())
    for target in (ROOT, *(ROOT / 'plugins' / name for name in plugins)):
        report = json.loads(run('plugin', 'validate', str(target), '--json', '--strict'))
        assert report['success'], f'Claude manifest validation failed: {report}'
        notices = (report.get('directory') or {}).get('findings', [])
        print(f'Claude validated {target.name}; directory notices: '
              + (', '.join(item['code'] for item in notices) or 'none'))
    for name in plugins:
        plugin = ROOT / 'plugins' / name
        inventory = run('--plugin-dir', str(plugin), 'plugin', 'details', name)
        for label, expected in (
            ('Skills', {path.parent.name for path in (plugin / 'skills').glob('*/SKILL.md')}
             | {path.stem for path in (plugin / 'commands').glob('*.md')}),
            ('Agents', {path.stem for path in (plugin / 'agents').glob('*.md')}),
        ):
            match = re.search(r'^\s+' + label + r' \((\d+)\)([^\n]*)', inventory, re.M)
            assert match, f'Claude did not report {label} for {name}'
            loaded = {item.strip() for item in match[2].split(',') if item.strip()}
            assert int(match[1]) == len(expected) and loaded == expected, f'Claude {label} mismatch for {name}: {loaded} != {expected}'
        expected_mcp = 0 if name == 'dev-patterns' else 1
        assert f'MCP servers ({expected_mcp})' in inventory, f'Claude MCP inventory mismatch: {name}'
        if expected_mcp:
            assert re.search(r'MCP servers \(1\)\s+atlassian\b', inventory)
        print(f'Claude loaded all expected skills/commands, agents and MCP declarations for {name}.')
    print('Claude manifest/component-loading smoke test passed; no model, Jira or GitHub actions performed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex', action='store_true', help='Install into a temporary CODEX_HOME (no user config changes)')
    parser.add_argument('--claude', action='store_true', help='Validate manifests and load local Claude component inventories (no installation or model turn)')
    args = parser.parse_args()
    marketplace, plugins = validate()
    if args.codex:
        codex_smoke(marketplace, plugins)
    if args.claude:
        claude_smoke(plugins)
