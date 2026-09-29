import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScoreDonut } from "./ScoreDonut";

describe("ScoreDonut", () => {
  it("displays the numeric score", () => {
    render(<ScoreDonut score={71} />);
    expect(screen.getByText("71")).toBeInTheDocument();
    expect(screen.getByText("out of 100")).toBeInTheDocument();
  });

  it("displays a different score correctly", () => {
    render(<ScoreDonut score={38} />);
    expect(screen.getByText("38")).toBeInTheDocument();
  });
});