"""Tests for the OC Debug findings tool. Standard library unittest only.

Run inside the Docker image (see README). Every file is created under the
system temporary directory; the package itself is never written to.
"""

import json
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / 'skills' / 'oc-debug' / 'tools'
TOOL = TOOLS / 'oc_debug.py'
sys.path.insert(0, str(TOOLS))

import oc_debug  # noqa: E402


def run_cli(*args):
    return subprocess.run(
        [sys.executable, '-B', str(TOOL)] + [str(arg) for arg in args],
        capture_output=True, encoding='utf-8', check=False,
    )


class TempDirTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='oc-debug-test-')
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(tmp.name)

    def write(self, name, content):
        path = self.tmp / name
        path.write_text(content, encoding='utf-8')
        return path

    def load(self, path):
        return json.loads(path.read_text(encoding='utf-8'))

    def by_signal(self, doc):
        return {rec['signal']: rec for rec in doc}

    def collected(self):
        error = self.write('error.txt', 'TypeError: synthetic failure')
        findings = self.tmp / 'findings.json'
        result = run_cli('collect', '--error', error, '--out', findings)
        self.assertEqual(result.returncode, 0, result.stderr)
        return findings


class CollectTests(TempDirTestCase):
    def test_valid_collection(self):
        error = self.write('error.txt', 'TypeError: synthetic failure\n  at example (demo.js:1:1)\n')
        logs = self.write('logs.txt', 'WARN demo-0001 retrying synthetic job\n')
        out = self.tmp / 'out' / 'findings.json'
        result = run_cli('collect', '--error', error, '--logs', logs,
                         '--correlation-id', 'demo-0001', '--out', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = self.load(out)
        self.assertEqual(oc_debug.validate_document(doc), [])
        self.assertEqual([rec['signal'] for rec in doc], list(oc_debug.SIGNALS))
        records = self.by_signal(doc)
        baseline = records['baseline']
        self.assertEqual((baseline['status'], baseline['proof_of_work']), ('PASS', 'verified'))
        self.assertIn('TypeError: synthetic failure', baseline['detail'])
        self.assertIn('not redacted', baseline['detail'])
        self.assertEqual(baseline['logfile'], str(error))
        self.assertEqual(records['logs']['status'], 'PASS')
        for name in ('code-surface', 'change', 'apm', 'browser', 'docs'):
            self.assertEqual((records[name]['status'], records[name]['proof_of_work']),
                             ('SKIP', 'unverified'))
            self.assertIsNone(records[name]['logfile'])
        self.assertTrue(all(rec['correlation_id'] == 'demo-0001' for rec in doc))
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(out.parent.stat().st_mode) & 0o077, 0)
        self.assertEqual(run_cli('validate', out).returncode, 0)

    def test_absent_and_empty_inputs_are_skipped(self):
        error = self.write('error.txt', '  \n\n')
        out = self.tmp / 'findings.json'
        result = run_cli('collect', '--error', error, '--out', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        records = self.by_signal(self.load(out))
        self.assertEqual((records['baseline']['status'], records['baseline']['proof_of_work']),
                         ('SKIP', 'unverified'))
        self.assertEqual((records['logs']['status'], records['logs']['proof_of_work']),
                         ('SKIP', 'unverified'))
        self.assertIsNone(records['logs']['logfile'])
        self.assertIsNone(records['logs']['correlation_id'])

    def test_missing_and_unreadable_inputs_fail_as_evidence(self):
        out = self.tmp / 'findings.json'
        result = run_cli('collect', '--error', self.tmp / 'missing.txt', '--logs', self.tmp,
                         '--out', out)
        self.assertEqual(result.returncode, 0, result.stderr)
        records = self.by_signal(self.load(out))
        self.assertEqual((records['baseline']['status'], records['baseline']['proof_of_work']),
                         ('FAIL', 'failed'))
        self.assertIn('Could not read', records['baseline']['detail'])
        self.assertEqual((records['logs']['status'], records['logs']['proof_of_work']),
                         ('FAIL', 'failed'))

    def test_refuses_to_overwrite(self):
        error = self.write('error.txt', 'synthetic error')
        out = self.write('findings.json', 'keep me')
        result = run_cli('collect', '--error', error, '--out', out)
        self.assertEqual(result.returncode, 2)
        self.assertIn('refusing to overwrite', result.stderr)
        self.assertEqual(out.read_text(encoding='utf-8'), 'keep me')

    def test_long_input_is_truncated(self):
        error = self.write('error.txt', 'x' * 50000)
        detail = oc_debug.collect_records(str(error))[0]['detail']
        self.assertLessEqual(len(detail), oc_debug.MAX_DETAIL_CHARS)
        self.assertIn('truncated', detail)


class AppendTests(TempDirTestCase):
    def test_valid_append(self):
        findings = self.collected()
        detail = 'Synthetic: failure began after bumping example-lib 2.3 to 2.4.'
        result = run_cli('append', findings, '--signal', 'change', '--status', 'PASS',
                         '--detail', detail, '--correlation-id', 'demo-0001')
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = self.load(findings)
        self.assertEqual(len(doc), len(oc_debug.SIGNALS) + 1)
        self.assertEqual(doc[-1], {
            'signal': 'change', 'status': 'PASS', 'proof_of_work': 'verified',
            'correlation_id': 'demo-0001', 'logfile': None, 'detail': detail,
        })
        self.assertEqual(oc_debug.validate_document(doc), [])

    def test_malformed_document_is_left_unchanged(self):
        findings = self.tmp / 'bad.json'
        for content in (b'[{"signal": ', b'{"not": "an array"}', b'[{"signal": "baseline"}]'):
            with self.subTest(content=content):
                findings.write_bytes(content)
                result = run_cli('append', findings, '--signal', 'docs', '--status', 'SKIP',
                                 '--detail', 'No documentation consulted.')
                self.assertEqual(result.returncode, 1)
                self.assertIn('unchanged', result.stderr)
                self.assertEqual(findings.read_bytes(), content)

    def test_empty_detail_is_rejected(self):
        findings = self.collected()
        before = findings.read_bytes()
        result = run_cli('append', findings, '--signal', 'docs', '--status', 'SKIP', '--detail', '   ')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(findings.read_bytes(), before)


class ValidateTests(TempDirTestCase):
    def test_inconsistent_status_and_proof(self):
        record = oc_debug.make_record('baseline', 'PASS', 'synthetic')
        record['proof_of_work'] = 'unverified'
        path = self.write('findings.json', json.dumps([record]))
        result = run_cli('validate', path)
        self.assertEqual(result.returncode, 1)
        self.assertIn('requires proof_of_work', result.stderr)

    def test_invalid_fields(self):
        good = oc_debug.make_record('baseline', 'SKIP', 'synthetic')
        cases = {
            'missing field': ({k: v for k, v in good.items() if k != 'detail'}, 'missing field'),
            'unexpected field': (dict(good, extra='x'), 'unexpected field'),
            'unknown signal': (dict(good, signal='database'), 'signal'),
            'unknown status': (dict(good, status='OK'), 'status'),
            'unknown proof': (dict(good, proof_of_work='maybe'), 'proof_of_work'),
            'non-string logfile': (dict(good, logfile=42), 'logfile'),
            'null detail': (dict(good, detail=None), 'detail'),
            'non-object record': ('baseline', 'must be an object'),
        }
        for name, (record, needle) in cases.items():
            with self.subTest(name):
                errors = oc_debug.validate_document([record])
                self.assertTrue(any(needle in error for error in errors), errors)
        self.assertTrue(oc_debug.validate_document({'records': []}))
        doc, errors = oc_debug.parse_document(b'[{"signal": "baseline", "signal": "logs"}]')
        self.assertIsNone(doc)
        self.assertTrue(any('duplicate' in error for error in errors))
        path = self.write('findings.json', json.dumps([dict(good, logfile=42)]))
        self.assertEqual(run_cli('validate', path).returncode, 1)

    def test_example_findings_is_valid(self):
        result = run_cli('validate', ROOT / 'examples' / 'findings.json')
        self.assertEqual(result.returncode, 0, result.stderr)


class RenderTests(TempDirTestCase):
    HOSTILE = 'a|b\nline2 <script>alert(1)</script> `x` [y](z) *z* \x07 \u202e &amp; \\|'

    def test_escape_cell(self):
        cell = oc_debug.escape_cell(self.HOSTILE)
        self.assertNotIn('\n', cell)
        self.assertNotIn('<script', cell)
        self.assertIn('&lt;script&gt;', cell)
        self.assertIn('a\\|b', cell)
        self.assertIn('<br>', cell)
        self.assertIn('&amp;amp;', cell)
        self.assertIn('\\u{0007}', cell)
        self.assertIn('\\u{202E}', cell)
        self.assertNotIn('\x07', cell)
        self.assertNotIn('\u202e', cell)

    def test_render_keeps_table_intact(self):
        record = oc_debug.make_record('logs', 'PASS', self.HOSTILE, 'id|1', 'in|logs.txt')
        findings = self.write('findings.json', json.dumps([record]))
        result = run_cli('render', findings)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [line for line in result.stdout.splitlines() if line.startswith('|')]
        self.assertEqual(len(rows), 3)
        for row in rows:
            unescaped = re.sub(r'\\.', '', row)
            self.assertEqual(unescaped.count('|'), len(oc_debug.COLUMNS) + 1, row)
        self.assertNotIn('<script', result.stdout)
        self.assertIn('no overall verdict', result.stdout)

    def test_render_refuses_invalid_and_existing_output(self):
        bad = self.write('bad.json', '[1]')
        self.assertEqual(run_cli('render', bad).returncode, 1)
        findings = self.collected()
        report = self.write('report.md', 'keep me')
        result = run_cli('render', findings, '--out', report)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(report.read_text(encoding='utf-8'), 'keep me')


class CliTests(TempDirTestCase):
    def test_cli_errors_exit_nonzero(self):
        cases = [
            (),
            ('frobnicate',),
            ('collect',),
            ('append', self.tmp / 'x.json', '--signal', 'logs', '--status', 'DONE', '--detail', 'd'),
            ('append', self.tmp / 'missing.json', '--signal', 'logs', '--status', 'SKIP', '--detail', 'd'),
            ('validate', self.tmp / 'missing.json'),
        ]
        for args in cases:
            with self.subTest(args=args):
                result = run_cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr.strip())


if __name__ == '__main__':
    unittest.main()
