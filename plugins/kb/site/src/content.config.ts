import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = resolve(fileURLToPath(import.meta.url), '..');
const RAW_ROOT = resolve(__dirname, '../../data-raw');
const WIKI_ROOT = resolve(__dirname, '../../data-wiki');

const raw = defineCollection({
  loader: glob({ pattern: '**/*.md', base: RAW_ROOT, ignore: ['**/_map.md'] }),
  schema: z.object({
    title: z.string().optional(),
    project: z.string().optional(),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']).optional(),
    date: z.string().optional(),
    status: z.enum(['unprocessed', 'processed']).optional(),
    tags: z.array(z.string()).optional(),
  }),
});

const wiki = defineCollection({
  loader: glob({ pattern: 'projects/**/*.md', base: WIKI_ROOT }),
  schema: z.object({
    page_type: z.enum(['entity', 'concept', 'synthesis']).optional(),
    dimension: z.enum(['topology', 'api', 'data-model', 'flows', 'concepts']).optional(),
    project: z.string().optional(),
    tags: z.array(z.string()).optional(),
    sources: z.array(z.string()).optional(),
    date: z.string().optional(),
    last_updated: z.string().optional(),
    status: z.string().optional(),
  }),
});

export const collections = { raw, wiki };
