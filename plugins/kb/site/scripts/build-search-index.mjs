#!/usr/bin/env node

import { readdirSync, readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join, relative } from 'node:path';

const RAW_ROOT = resolve(import.meta.dirname, '..', 'data-raw');
const WIKI_ROOT = resolve(import.meta.dirname, '..', 'data-wiki');
const OUTPUT = resolve(import.meta.dirname, '..', 'public', 'search-index.json');

function walkDir(dir, ext = '.md') {
  const files = [];
  try {
    for (const entry of readdirSync(dir)) {
      const full = join(dir, entry);
      if (statSync(full).isDirectory()) {
        files.push(...walkDir(full, ext));
      } else if (entry.endsWith(ext)) {
        files.push(full);
      }
    }
  } catch {}
  return files;
}

function parseFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { data: {}, body: content };
  const fm = {};
  for (const line of match[1].split('\n')) {
    const m = line.match(/^(\w[\w-]*):\s*(.+)$/);
    if (m) fm[m[1]] = m[2].trim().replace(/^\[(.+)\]$/, '$1').split(',').map(s => s.trim());
  }
  return { data: fm, body: match[2] };
}

const index = [];

// Index raw documents
for (const file of walkDir(RAW_ROOT)) {
  const content = readFileSync(file, 'utf-8');
  const { data, body } = parseFrontmatter(content);
  const relPath = relative(RAW_ROOT, file).replace(/\.md$/, '');
  const project = relPath.split('/')[0];
  index.push({
    type: 'raw',
    id: relPath,
    project,
    title: data.title || relPath.split('/').pop(),
    dimension: data.dimension || '',
    content: body.slice(0, 2000),
    href: `/projects/${project}/raw/${relPath.slice(project.length + 1)}`,
  });
}

// Index wiki documents
for (const file of walkDir(WIKI_ROOT)) {
  const content = readFileSync(file, 'utf-8');
  const { data, body } = parseFrontmatter(content);
  const relPath = relative(WIKI_ROOT, file).replace(/\.md$/, '');
  const projectMatch = relPath.match(/^projects\/([^/]+)\//);
  const project = projectMatch ? projectMatch[1] : '';
  index.push({
    type: 'wiki',
    id: relPath,
    project,
    title: data.title || relPath.split('/').pop(),
    page_type: data.page_type || '',
    dimension: data.dimension || '',
    content: body.slice(0, 2000),
    href: `/projects/${project}/wiki/${relPath.replace(/^projects\/[^/]+\//, '')}`,
  });
}

mkdirSync(resolve(import.meta.dirname, '..', 'public'), { recursive: true });
writeFileSync(OUTPUT, JSON.stringify(index, null, 2));
console.log(`Search index: ${index.length} entries written to ${OUTPUT}`);
