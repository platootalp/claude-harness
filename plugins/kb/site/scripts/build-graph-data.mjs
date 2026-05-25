#!/usr/bin/env node

import { readdirSync, readFileSync, statSync, writeFileSync, mkdirSync } from 'node:fs';
import { resolve, join, relative } from 'node:path';

const WIKI_ROOT = resolve(import.meta.dirname, '..', 'data-wiki');
const OUTPUT = resolve(import.meta.dirname, '..', 'public', 'graph.json');

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
    if (m) fm[m[1]] = m[2].trim();
  }
  return { data: fm, body: match[2] };
}

const nodes = [];
const edges = [];
const nodeMap = new Map();

for (const file of walkDir(WIKI_ROOT)) {
  const content = readFileSync(file, 'utf-8');
  const { data, body } = parseFrontmatter(content);
  const relPath = relative(WIKI_ROOT, file).replace(/\.md$/, '');
  const projectMatch = relPath.match(/^projects\/([^/]+)\//);
  const project = projectMatch ? projectMatch[1] : '';

  const nodeId = relPath;
  const node = {
    id: nodeId,
    label: data.title || relPath.split('/').pop(),
    type: data.page_type || 'entity',
    dimension: data.dimension || '',
    project,
  };
  nodes.push(node);
  nodeMap.set(nodeId, node);

  // Extract cross-references from "另见" or "交叉引用" sections
  const seeAlsoMatch = body.match(/##\s*(?:另见|交叉引用)[\s\S]*?(?=##|$)/);
  if (seeAlsoMatch) {
    const links = seeAlsoMatch[0].matchAll(/\[([^\]]+)\]\(([^)]+)\)/g);
    for (const link of links) {
      const targetPath = link[2].replace(/^\.\.\//, '').replace(/\.md$/, '');
      edges.push({
        source: nodeId,
        target: targetPath,
        signal: 'cross-reference',
      });
    }
  }
}

// Also generate a projects.json for the ProjectSwitcher
const projects = [...new Set(nodes.map(n => n.project).filter(Boolean))].map(p => ({
  name: p,
  href: `/projects/${p}/`,
}));

mkdirSync(resolve(import.meta.dirname, '..', 'public'), { recursive: true });
writeFileSync(OUTPUT, JSON.stringify({ nodes, edges }, null, 2));
writeFileSync(resolve(import.meta.dirname, '..', 'public', 'projects.json'), JSON.stringify(projects, null, 2));
console.log(`Graph: ${nodes.length} nodes, ${edges.length} edges written to ${OUTPUT}`);
console.log(`Projects: ${projects.length} written to projects.json`);
