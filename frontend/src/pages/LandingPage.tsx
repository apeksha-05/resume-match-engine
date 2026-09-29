import { Gauge, Lightbulb, Upload } from "lucide-react";
import { Link } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const features = [
  {
    icon: Upload,
    title: "Upload and parse",
    text: "Add your PDF resume and a job description. We extract skills, experience and education with evidence from your own text.",
  },
  {
    icon: Gauge,
    title: "Explainable score",
    text: "See exactly how the estimated fit score was calculated, category by category, with adjustable weights.",
  },
  {
    icon: Lightbulb,
    title: "Truthful improvements",
    text: "Get bullet-point suggestions and a learning roadmap that never invent skills or achievements.",
  },
];

export function LandingPage() {
  return (
    <div className="space-y-12">
      <section className="mx-auto max-w-2xl py-8 text-center">
        <h1 className="text-4xl font-bold tracking-tight">
          Understand how well your resume fits a job
        </h1>
        <p className="mt-4 text-lg text-muted-foreground">
          An explainable resume and job description matching engine. No
          black-box score, and no promises about hiring outcomes.
        </p>
        <div className="mt-6 flex justify-center gap-3">
          <Button asChild size="lg">
            <Link to="/results/demo">Try the demo</Link>
          </Button>
          <Button asChild size="lg" variant="outline">
            <Link to="/analyze">Analyze my resume</Link>
          </Button>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {features.map((feature) => (
          <Card key={feature.title}>
            <CardHeader>
              <feature.icon className="mb-2 size-6" />
              <CardTitle>{feature.title}</CardTitle>
              <CardDescription>{feature.text}</CardDescription>
            </CardHeader>
          </Card>
        ))}
      </section>
    </div>
  );
}