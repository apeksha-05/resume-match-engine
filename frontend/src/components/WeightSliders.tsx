import { Slider } from "@/components/ui/slider";
import type { CategoryKey, Weights } from "@/types";

interface WeightSlidersProps {
  weights: Weights;
  onChange: (weights: Weights) => void;
}

const labels: Record<CategoryKey, string> = {
  skills: "Skills coverage",
  semantic: "Semantic similarity",
  experience: "Experience relevance",
  education: "Education alignment",
};

function normalize(weights: Weights): Weights {
  const total = weights.skills + weights.semantic + weights.experience + weights.education;
  if (total === 0) {
    return { skills: 0.25, semantic: 0.25, experience: 0.25, education: 0.25 };
  }
  return {
    skills: weights.skills / total,
    semantic: weights.semantic / total,
    experience: weights.experience / total,
    education: weights.education / total,
  };
}

export function WeightSliders({ weights, onChange }: WeightSlidersProps) {
  const handleSlide = (key: CategoryKey, rawPercent: number) => {
    const updated: Weights = { ...weights, [key]: rawPercent / 100 };
    onChange(normalize(updated));
  };

  return (
    <div className="space-y-5">
      {(Object.keys(labels) as CategoryKey[]).map((key) => (
        <div key={key}>
          <div className="mb-1 flex justify-between text-sm">
            <span>{labels[key]}</span>
            <span className="font-medium">
              {Math.round(weights[key] * 100)}%
            </span>
          </div>
          <Slider
            value={[Math.round(weights[key] * 100)]}
            max={100}
            step={1}
            onValueChange={(value) => handleSlide(key, value[0])}
          />
        </div>
      ))}
      <p className="text-xs text-muted-foreground">
        Weights are automatically rescaled so they always add up to 100%.
      </p>
    </div>
  );
}