import { Badge } from "@/components/ui/badge";

interface SkillBadgeListProps {
  title: string;
  skills: string[];
  variant?: "default" | "secondary" | "outline" | "destructive";
  emptyText?: string;
}

export function SkillBadgeList({
  title,
  skills,
  variant = "secondary",
  emptyText = "None",
}: SkillBadgeListProps) {
  return (
    <div>
      <p className="mb-1.5 text-sm font-medium">{title}</p>
      {skills.length === 0 ? (
        <p className="text-sm text-muted-foreground">{emptyText}</p>
      ) : (
        <div className="flex flex-wrap gap-1.5">
          {skills.map((skill) => (
            <Badge key={skill} variant={variant}>
              {skill}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}