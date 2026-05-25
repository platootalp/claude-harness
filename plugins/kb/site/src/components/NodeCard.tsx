import type { MouseEvent } from 'react';

interface NodeData {
  id: string;
  label: string;
  type: 'entity' | 'concept' | 'synthesis';
  dimension?: string;
  project: string;
}

interface NodeCardProps {
  node: NodeData;
  x: number;
  y: number;
}

const typeLabels: Record<string, string> = {
  entity: '实体',
  concept: '概念',
  synthesis: '综合',
};

const dimensionLabels: Record<string, string> = {
  topology: '拓扑',
  api: 'API',
  'data-model': '数据模型',
  flows: '流程',
  concepts: '概念',
};

export default function NodeCard({ node, x, y }: NodeCardProps) {
  const wikiHref = `/projects/${node.project}/wiki/${node.id.replace(/\.md$/, '')}`;
  const rawHref = `/projects/${node.project}/raw/${node.id.replace(/\.md$/, '')}`;

  return (
    <div
      className="fixed z-50 max-w-xs rounded-lg border border-[var(--color-border)] bg-[var(--color-bg)] p-3 shadow-lg text-sm"
      style={{ left: Math.min(x + 15, window.innerWidth - 250), top: Math.min(y + 15, window.innerHeight - 120) }}
    >
      <h5 className="font-semibold">{node.label}</h5>
      <p className="mt-1 text-xs text-[var(--color-text-muted)]">
        {typeLabels[node.type] || node.type}
        {node.dimension && ` · ${dimensionLabels[node.dimension] || node.dimension}`}
      </p>
      <div className="mt-2 flex gap-3">
        <a href={wikiHref} className="text-xs text-[var(--color-accent)] hover:underline">Wiki</a>
        <a href={rawHref} className="text-xs text-[var(--color-accent)] hover:underline">Raw</a>
      </div>
    </div>
  );
}
