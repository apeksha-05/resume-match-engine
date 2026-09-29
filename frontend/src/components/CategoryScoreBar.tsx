import { Progress } from "@/components/ui/progress";
import type { CategoryScore } from "@/types";

export function CategoryScoreBar({ category }: { category: CategoryScore }) {
  return (
    <div>
      <div className="mb-1 flex items-baseline justify-between text-sm">
        <span className="font-medium">{category.label}</span>
        <span className="text-muted-foreground">
          {Math.round(category.score * 100)}% · weight{" "}
          {Math.round(category.weight * 100)}%
        </span>
      </div>
      <Progress value={category.score * 100} />
      <p className="mt-1 text-xs text-muted-foreground">
        {category.explanation}
      </p>
    </div>
  );
}