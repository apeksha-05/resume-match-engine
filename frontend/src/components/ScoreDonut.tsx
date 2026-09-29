import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

interface ScoreDonutProps {
  score: number; // 0 to 100
}

function colorForScore(score: number): string {
  if (score >= 75) return "#16a34a"; // green
  if (score >= 50) return "#ca8a04"; // amber
  return "#dc2626"; // red
}

export function ScoreDonut({ score }: ScoreDonutProps) {
  const color = colorForScore(score);
  const data = [
    { name: "score", value: score },
    { name: "remainder", value: 100 - score },
  ];

  return (
    <div className="relative mx-auto h-48 w-48">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            dataKey="value"
            innerRadius="70%"
            outerRadius="100%"
            startAngle={90}
            endAngle={-270}
            stroke="none"
          >
            <Cell fill={color} />
            <Cell fill="var(--muted)" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-4xl font-bold">{score}</span>
        <span className="text-xs text-muted-foreground">out of 100</span>
      </div>
    </div>
  );
}