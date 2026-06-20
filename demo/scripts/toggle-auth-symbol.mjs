import { readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const mode = process.argv[2];
const servicePath = resolve(
  "demo/backend/app/services/session_service.py",
);
const source = await readFile(servicePath, "utf8");

if (mode === "break") {
  if (source.includes("def validate_session(")) {
    await writeFile(
      servicePath,
      source.replace("def validate_session(", "def validate_demo_session("),
    );
    console.log("Demo broken: validate_session was renamed in the service.");
  } else {
    console.log("Demo is already broken.");
  }
} else if (mode === "restore") {
  if (source.includes("def validate_demo_session(")) {
    await writeFile(
      servicePath,
      source.replace("def validate_demo_session(", "def validate_session("),
    );
    console.log("Demo restored: validate_session is available again.");
  } else {
    console.log("Demo is already restored.");
  }
} else {
  throw new Error("Use `break` or `restore`.");
}
