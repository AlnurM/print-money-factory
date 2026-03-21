#!/usr/bin/env node

import { fileURLToPath } from 'url';
import { dirname, join, resolve } from 'path';
import { homedir, platform } from 'os';
import { existsSync, mkdirSync, copyFileSync, readdirSync, statSync, readFileSync, writeFileSync } from 'fs';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PKG_ROOT = resolve(__dirname, '..');
const HOME = homedir();
const COMMANDS_DIR = join(HOME, '.claude', 'commands', 'brrr');
const PMF_DIR = join(HOME, '.pmf');
const VENV_DIR = join(PMF_DIR, 'venv');
const IS_WIN = platform() === 'win32';
const PYTHON_BIN = join(VENV_DIR, IS_WIN ? 'Scripts' : 'bin', IS_WIN ? 'python.exe' : 'python');
const PIP_BIN = join(VENV_DIR, IS_WIN ? 'Scripts' : 'bin', IS_WIN ? 'pip.exe' : 'pip');

/**
 * Recursively copy a directory from src to dest.
 * Creates dest and all intermediate directories as needed.
 * @param {string} src - Source directory path
 * @param {string} dest - Destination directory path
 * @returns {number} Number of files copied
 */
function copyDirRecursive(src, dest) {
  let count = 0;

  if (!existsSync(src)) {
    return count;
  }

  mkdirSync(dest, { recursive: true });

  const entries = readdirSync(src);
  for (const entry of entries) {
    const srcPath = join(src, entry);
    const destPath = join(dest, entry);
    const stat = statSync(srcPath);

    if (stat.isDirectory()) {
      count += copyDirRecursive(srcPath, destPath);
    } else {
      copyFileSync(srcPath, destPath);
      count++;
    }
  }

  return count;
}

/**
 * Detect a Python 3.10+ installation.
 * Tries python3, python, and py -3 (Windows) in order.
 * @returns {{ path: string, version: string }} Python path and version string
 */
function detectPython() {
  const candidates = ['python3', 'python'];
  if (IS_WIN) {
    candidates.push('py -3');
  }

  for (const candidate of candidates) {
    try {
      const versionOutput = execSync(
        `${candidate} -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}')"`,
        { stdio: ['pipe', 'pipe', 'pipe'], encoding: 'utf8' }
      ).trim();

      const [major, minor] = versionOutput.split('.').map(Number);

      if (major >= 3 && minor >= 10) {
        return { path: candidate, version: versionOutput };
      }
    } catch {
      // Command not found or failed — try next candidate
    }
  }

  console.error(`
Error: Python 3.10+ is required but was not found.

Install Python 3.10 or later:
  macOS:   brew install python@3.12
  Ubuntu:  sudo apt install python3.12 python3.12-venv
  Windows: https://www.python.org/downloads/

Then run this command again.
`);
  process.exit(1);
}

/**
 * Main install function.
 * Copies commands, workflows, templates, references to their target locations,
 * creates/updates a Python venv, and verifies the installation.
 */
function main() {
  // Accept "install" arg or no args (npx calls without args)
  const cmd = process.argv[2];
  if (cmd && cmd !== 'install') {
    console.log('Usage: npx @print-money-factory/cli [install]');
    process.exit(1);
  }

  console.log('\nPrint Money Factory - Installing...\n');

  // 1. Copy commands/ -> ~/.claude/commands/brrr/
  const cmdCount = copyDirRecursive(join(PKG_ROOT, 'commands'), COMMANDS_DIR);
  console.log(`  [OK] Commands -> ~/.claude/commands/brrr/ (${cmdCount} files)`);

  // 2. Copy workflows/, templates/, references/ -> ~/.pmf/
  for (const dir of ['workflows', 'templates', 'references']) {
    const srcDir = join(PKG_ROOT, dir);
    if (existsSync(srcDir)) {
      const count = copyDirRecursive(srcDir, join(PMF_DIR, dir));
      console.log(`  [OK] ${dir}/ -> ~/.pmf/${dir}/ (${count} files)`);
    } else {
      console.log(`  [--] ${dir}/ skipped (not in package yet)`);
    }
  }

  // 3. Write version file
  const pkg = JSON.parse(readFileSync(join(PKG_ROOT, 'package.json'), 'utf8'));
  writeFileSync(join(PMF_DIR, '.version'), JSON.stringify({
    version: pkg.version,
    installed: new Date().toISOString(),
    package: 'print-money-factory'
  }, null, 2));
  console.log(`  [OK] Version file written (v${pkg.version})`);

  // 4. Detect Python
  const python = detectPython();
  console.log(`  [OK] Python found: ${python.path} (${python.version})`);

  // 5. Create or update venv
  if (existsSync(VENV_DIR) && existsSync(PYTHON_BIN)) {
    console.log('\n  Updating existing venv...');
    try {
      execSync(`"${PIP_BIN}" install --upgrade -r "${join(PKG_ROOT, 'requirements.txt')}"`, { stdio: 'inherit' });
    } catch (e) {
      console.error('\nError: Failed to update Python dependencies.');
      console.error(`  Try manually: ${PIP_BIN} install --upgrade -r ${join(PKG_ROOT, 'requirements.txt')}`);
      process.exit(1);
    }
  } else {
    console.log('\n  Creating Python venv...');
    try {
      execSync(`"${python.path}" -m venv "${VENV_DIR}"`, { stdio: 'inherit' });
    } catch (e) {
      console.error('\nError: Failed to create venv. On Ubuntu/Debian, install:');
      console.error('  sudo apt install python3-venv');
      console.error('\nThen run this command again.');
      process.exit(1);
    }

    console.log('  Installing Python dependencies...');
    try {
      execSync(`"${PIP_BIN}" install -r "${join(PKG_ROOT, 'requirements.txt')}"`, { stdio: 'inherit' });
    } catch (e) {
      console.error('\nError: Failed to install Python dependencies.');
      console.error(`  Try manually: ${PIP_BIN} install -r ${join(PKG_ROOT, 'requirements.txt')}`);
      process.exit(1);
    }
  }

  // 6. Verify installation
  try {
    execSync(`"${PYTHON_BIN}" -c "import pandas; import numpy; import ccxt; import yfinance; print('OK')"`, { stdio: 'pipe' });
    console.log('  [OK] Python dependencies verified');
  } catch (e) {
    console.error('\nWarning: Some Python dependencies failed to import. Run:');
    console.error(`  ${PYTHON_BIN} -m pip install -r ${join(PKG_ROOT, 'requirements.txt')}`);
  }

  // 7. Print summary
  console.log(`
Install complete!

  Commands installed:  ~/.claude/commands/brrr/
  PMF home:           ~/.pmf/
  Python venv:        ~/.pmf/venv/

  Get started: use /brrr:new-milestone to create your first strategy.
`);
}

main();
