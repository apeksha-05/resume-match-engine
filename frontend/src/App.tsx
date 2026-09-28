import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

function App() {
  return (
    <div className="mx-auto flex min-h-screen max-w-md items-center p-6">
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Setup check</CardTitle>
          <CardDescription>
            If you can see styled components, Tailwind and shadcn/ui work.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Badge>Python</Badge>
            <Badge variant="secondary">FastAPI</Badge>
            <Badge variant="outline">Docker</Badge>
          </div>
          <Progress value={72} />
          <Button>Looks good</Button>
        </CardContent>
      </Card>
    </div>
  );
}

export default App;