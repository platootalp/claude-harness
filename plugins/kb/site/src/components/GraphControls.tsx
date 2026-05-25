interface GraphControlsProps {
  colorMode: 'dimension' | 'type';
  onColorModeChange: (mode: 'dimension' | 'type') => void;
  nodeCount: number;
  edgeCount: number;
}

export default function GraphControls({
  colorMode, onColorModeChange, nodeCount, edgeCount,
}: GraphControlsProps) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-3 text-sm">
      <label className="text-[var(--color-text-muted)]">着色:</label>
      <select
        value={colorMode}
        onChange={e => onColorModeChange(e.target.value as 'dimension' | 'type')}
        className="rounded border border-[var(--color-border)] bg-transparent px-2 py-1 text-[var(--color-text)]"
      >
        <option value="dimension">维度</option>
        <option value="type">类型</option>
      </select>
      <span className="text-[var(--color-text-muted)]">
        {nodeCount} 节点 · {edgeCount} 边
      </span>
    </div>
  );
}
